"""pytest 公共配置与 fixture"""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """
    使用上下文管理器以触发 lifespan，确保 app.state 正确初始化。
    """
    with TestClient(app) as client:
        yield client
