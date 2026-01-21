"""答案增强服务路由"""

from fastapi import APIRouter, Depends

from .models import AnswerEnhancementBody
from .service import AnswerEnhancementService
from .deps import get_enhancement_service


# 创建路由器 - 支持 API 版本化
router = APIRouter(
    prefix="/api/v1/answer",
    tags=["Answer Enhancement"],
)


@router.post("/enhance")
async def answer_enhancement(
    body: AnswerEnhancementBody,
    service: AnswerEnhancementService = Depends(get_enhancement_service),
) -> dict:
    """答案增强"""
    enhanced_answer = await service.execute(body.question, body.answer)

    return {
        "code": 200,
        "message": "success",
        "data": {"enhanced_answer": enhanced_answer},
    }
