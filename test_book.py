"""商品管理测试"""
import pytest
import allure
from common.api_client import ApiClient


@allure.feature("商品管理")
class TestBook:

    @allure.story("商品列表")
    @pytest.mark.p0
    def test_list_books_default(self, admin_client):
        """默认查询"""
        r = admin_client.list_books()
        assert r.json()["code"] == 200
        assert r.json()["data"]["total"] >= 1

    @allure.story("商品列表")
    @pytest.mark.p1
    def test_search_by_keyword(self, admin_client):
        """关键词搜索"""
        r = admin_client.list_books(keyword="Python")
        for book in r.json()["data"]["list"]:
            assert "Python" in book["title"] or "Python" in book["author"]

    @allure.story("商品列表")
    @pytest.mark.p1
    def test_filter_by_category(self, admin_client):
        """按分类筛选"""
        r = admin_client.list_books(category_id=1)
        for book in r.json()["data"]["list"]:
            assert book["category_id"] == 1

    @allure.story("商品列表")
    @pytest.mark.p1
    def test_price_range(self, admin_client):
        """价格区间"""
        r = admin_client.list_books(min_price=50, max_price=100)
        for book in r.json()["data"]["list"]:
            assert 50 <= book["price"] <= 100

    @allure.story("商品详情")
    @pytest.mark.p0
    def test_get_book_success(self, admin_client, created_book):
        """获取存在的商品"""
        r = admin_client.get_book(created_book["id"])
        assert r.json()["code"] == 200
        assert r.json()["data"]["id"] == created_book["id"]

    @allure.story("商品详情")
    @pytest.mark.p1
    def test_get_book_not_found(self, admin_client):
        """获取不存在的商品"""
        r = admin_client.get_book(99999)
        assert r.json()["code"] == 4041

    @allure.story("新建商品")
    @pytest.mark.p0
    def test_create_book_success(self, admin_client):
        """管理员新建商品"""
        import uuid
        payload = {
            "title": f"自动化测试-{uuid.uuid4().hex[:6]}",
            "author": "测试作者",
            "price": 99.0,
            "stock": 50,
            "category_id": 1
        }
        r = admin_client.create_book(**payload)
        assert r.json()["code"] == 2001
        book_id = r.json()["data"]["id"]
        admin_client.delete_book(book_id)

    @allure.story("新建商品")
    @pytest.mark.p1
    def test_create_book_without_login(self):
        """未登录不能新建"""
        r = ApiClient().create_book(title="x", author="y", price=1, category_id=1)
        assert r.status_code == 401

    @allure.story("新建商品")
    @pytest.mark.p1
    def test_create_book_normal_user_forbidden(self, user_client):
        """普通用户不能新建"""
        r = user_client.create_book(title="x", author="y", price=1, category_id=1)
        assert r.json()["code"] == 403

    @allure.story("新建商品")
    @pytest.mark.p1
    @pytest.mark.parametrize("missing", ["title", "author", "price", "category_id"])
    def test_create_book_missing_field(self, admin_client, missing):
        """缺少必填字段"""
        payload = {"title": "x", "author": "y", "price": 1, "category_id": 1}
        payload.pop(missing)
        r = admin_client.create_book(**payload)
        assert r.json()["code"] == 4001