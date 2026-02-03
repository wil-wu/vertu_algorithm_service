import orjson
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, Query
from fastapi.responses import Response

from app.core.managers import async_job_manager
from app.core.enum import JobType
from .jobs import generate_qa
from .service import QAGenerationService
from .deps import get_qa_generation_service
from .models import QAGenerationBody
from .utils import build_contexts

router = APIRouter(
    prefix="/api/v1/qa",
    tags=["QA Generation"],
)


async def _generate_qa(
    records: list[dict], metadata: dict, qa_generation_service: QAGenerationService
) -> list[dict]:
    """生成QA"""
    contexts = build_contexts(records)

    qas_result = await qa_generation_service.generate_qa(contexts)
    for qa_pair in qas_result["qas"]:
        qa_pair["metadata"] = metadata
    return qas_result


@router.post("/sync/generate_from_body", response_model=None)
async def generate_qa_from_body(
    body: QAGenerationBody,
    return_file: bool = Query(default=False, description="是否返回文件"),
    qa_generation_service: QAGenerationService = Depends(get_qa_generation_service),
) -> Response:
    """从Body生成QA"""

    records = body.data.get("RECORDS", [])
    metadata = body.metadata
    if not metadata:
        metadata = {
            "source": "http request",
            "datetime": datetime.now().isoformat(),
        }

    qas_result = await _generate_qa(records, metadata, qa_generation_service)
    content = orjson.dumps(
        {
            "code": 200,
            "message": "success",
            "data": qas_result,
        }
    )

    if return_file:
        filename = f"qa_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        return Response(
            content=content,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    else:
        return Response(content=content, media_type="application/json")


@router.post("/sync/generate_from_file", response_model=None)
async def generate_qa_from_file(
    file: UploadFile,
    return_file: bool = Query(default=False, description="是否返回文件"),
    qa_generation_service: QAGenerationService = Depends(get_qa_generation_service),
) -> Response:
    """从文件生成QA"""

    records = orjson.loads(await file.read()).get("RECORDS", [])
    metadata = {
        "source": file.filename,
        "datetime": datetime.now().isoformat(),
    }

    qas_result = await _generate_qa(records, metadata, qa_generation_service)
    content = orjson.dumps(
        {
            "code": 200,
            "message": "success",
            "data": qas_result,
        }
    )

    if return_file:
        filename = f"qa_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        return Response(
            content=content,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    else:
        return Response(content=content, media_type="application/json")


@router.post("/async/generate_from_body")
async def generate_qa_from_body_async(
    body: QAGenerationBody,
    qa_generation_service: QAGenerationService = Depends(get_qa_generation_service),
) -> dict:
    """从Body异步生成QA"""
    records = body.data.get("RECORDS", [])
    metadata = body.metadata
    if not metadata:
        metadata = {
            "source": "http request",
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    job_id = await async_job_manager.create_async_job(
        JobType.QA_GENERATION, generate_qa, records, metadata, qa_generation_service
    )

    return {
        "code": 200,
        "message": "success",
        "data": {"job_id": job_id},
    }


@router.post("/async/generate_from_file")
async def generate_qa_from_file_async(
    file: UploadFile,
    qa_generation_service: QAGenerationService = Depends(get_qa_generation_service),
) -> dict:
    """从文件异步生成QA"""
    records = orjson.loads(await file.read()).get("RECORDS", [])
    metadata = {
        "source": file.filename,
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    job_id = await async_job_manager.create_async_job(
        JobType.QA_GENERATION, generate_qa, records, metadata, qa_generation_service
    )

    return {
        "code": 200,
        "message": "success",
        "data": {"job_id": job_id},
    }
