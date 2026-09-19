"""API 客户端封装"""
import requests
from requests.exceptions import RequestException
from loguru import logger


class ApiClient:
    """BookStore API 客户端，封装所有接口调用"""

    BASE_URL = "http://127.0.0.1:5000"

    def __init__(self, token=None):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    # ======================== 用户认证 ========================
    def register(self, username, password, email=None, phone=None):
        return self._post("/api/auth/register",
                          json={"username": username, "password": password,
                                "email": email, "phone": phone})

    def login(self, username, password):
        return self._post("/api/auth/login",
                          json={"username": username, "password": password})

    def profile(self):
        return self._get("/api/auth/profile")

    @classmethod
    def login_as_admin(cls):
        client = cls()
        r = client.login("admin", "admin123")
        token = r.json()["data"]["token"]
        return cls(token=token)

    @classmethod
    def login_as_user(cls):
        client = cls()
        r = client.login("testuser", "test123")
        token = r.json()["data"]["token"]
        return cls(token=token)

    # ======================== 商品 ========================
    def list_books(self, **kwargs):
        return self._get("/api/books", params=kwargs)

    def get_book(self, book_id):
        return self._get(f"/api/books/{book_id}")

    def create_book(self, **data):
        return self._post("/api/books", json=data)

    def update_book(self, book_id, **data):
        return self._put(f"/api/books/{book_id}", json=data)

    def delete_book(self, book_id):
        return self._delete(f"/api/books/{book_id}")

    # ======================== 订单 ========================
    def create_order(self, items):
        return self._post("/api/orders", json={"items": items})

    def list_orders(self, **kwargs):
        return self._get("/api/orders", params=kwargs)

    def pay_order(self, order_id):
        return self._post(f"/api/orders/{order_id}/pay")

    # ======================== 底层方法 ========================
    def _get(self, path, **kwargs):
        return self._request("GET", path, **kwargs)

    def _post(self, path, **kwargs):
        return self._request("POST", path, **kwargs)

    def _put(self, path, **kwargs):
        return self._request("PUT", path, **kwargs)

    def _delete(self, path, **kwargs):
        return self._request("DELETE", path, **kwargs)

    def _request(self, method, path, **kwargs):
        url = f"{self.BASE_URL}{path}"
        try:
            r = self.session.request(method, url, timeout=10, **kwargs)
            logger.debug(f"{method} {path} -> {r.status_code} | {r.text[:200]}")
            return r
        except RequestException as e:
            logger.error(f"请求失败 {method} {path}: {e}")
            raise