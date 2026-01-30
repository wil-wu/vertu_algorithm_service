"""接口集成测试：仅验证接口能否正常返回（无 mock）"""

import io
import orjson


def test_root(client):
    """根路径能正常返回"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data.get("status") == "running"


def test_health(client):
    """健康检查能正常返回"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"
    assert "app_name" in data
    assert "version" in data


def test_answer_enhance_single(client):
    """答案增强接口（单条）能正常返回"""
    response = client.post(
        "/api/v1/answer/enhance",
        json={"question": "测试问题", "answer": "测试答案"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("code") == 200
    assert data.get("message") == "success"
    assert "data" in data
    assert "enhanced_answers" in data["data"]
    assert "total" in data["data"]


def test_answer_enhance_list(client):
    """答案增强接口（列表）能正常返回"""
    response = client.post(
        "/api/v1/answer/enhance",
        json=[
            {"question": "问题1", "answer": "答案1"},
            {"question": "问题2", "answer": "答案2"},
        ],
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("code") == 200
    assert data.get("message") == "success"
    assert "data" in data
    assert "enhanced_answers" in data["data"]
    assert data["data"]["total"] == 2


def test_qa_generate_from_body(client):
    """QA 生成接口（Body）能正常返回"""
    body = {
        "data": {
            "RECORDS": [
                {
                    "消息内容": [
                        {"sender": "用户", "content": "你好"},
                        {"sender": "客服", "content": "您好，请问有什么可以帮您？"},
                    ]
                }
            ]
        },
        "metadata": {"source": "test"},
    }
    response = client.post(
        "/api/v1/qa/generate_from_body",
        json=body,
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("code") == 200
    assert data.get("message") == "success"
    assert "data" in data
    assert "qas" in data["data"]
    assert "total" in data["data"]


def test_qa_generate_from_file(client):
    """QA 生成接口（文件上传）能正常返回"""
    file_content = orjson.dumps(
        {
            "RECORDS": [
                {
                    "消息内容": [
                        {"sender": "用户", "content": "咨询一下"},
                        {"sender": "客服", "content": "好的，请说。"},
                    ]
                }
            ]
        }
    )
    response = client.post(
        "/api/v1/qa/generate_from_file",
        files={"file": ("test.json", io.BytesIO(file_content), "application/json")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("code") == 200
    assert data.get("message") == "success"
    assert "data" in data
    assert "qas" in data["data"]
    assert "total" in data["data"]
