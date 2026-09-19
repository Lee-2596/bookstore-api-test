"""全局 fixture"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from common.api_client import ApiClient


@pytest.fixture(scope="session")
def admin_client():
    """整个会话共享一个 admin 客户端"""
    return ApiClient.login_as_admin()


@pytest.fixture(scope="session")
def user_client():
    return ApiClient.login_as_user()


@pytest.fixture
def fresh_user():
    """每次测试创建一个全新的普通用户"""
    import uuid
    username = f"u_{uuid.uuid4().hex[:8]}"
    password = "test123"

    client = ApiClient()
    r = client.register(username, password, email=f"{username}@test.com")
    assert r.status_code == 200, f"注册失败：{r.text}"

    user_client = ApiClient()
    user_client.login(username, password)

    yield {"username": username, "password": password, "client": user_client}


@pytest.fixture
def created_book(admin_client):
    """自动创建一本测试商品，测试结束后下架"""
    import uuid
    payload = {
        "title": f"自动化测试书_{uuid.uuid4().hex[:6]}",
        "author": "测试作者",
        "price": 99.0,
        "stock": 100,
        "category_id": 1
    }
    r = admin_client.create_book(**payload)
    book_id = r.json()["data"]["id"]
    yield r.json()["data"]
    admin_client.delete_book(book_id)