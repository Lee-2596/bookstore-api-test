"""订单测试（含数据库断言）"""
import pytest
import allure
from common.api_client import ApiClient
from common import db


@allure.feature("订单管理")
class TestOrder:

    @allure.story("下单")
    @pytest.mark.p0
    @pytest.mark.smoke
    def test_create_order_success(self, user_client):
        """正常下单"""
        # 选一本库存 > 5 的书，避免重复测试时库存耗尽
        books = user_client.list_books(is_on_sale="true", page_size=50).json()["data"]["list"]
        book = next((b for b in books if b["stock"] >= 5), None)
        assert book is not None, "没有库存充足的图书可测试"
        r = user_client.create_order([{"book_id": book["id"], "quantity": 1}])
        body = r.json()
        assert body["code"] == 2001  # 下单成功 = 2001
        assert body["data"]["status"] == "pending"
        assert body["data"]["total_amount"] == book["price"]

    @allure.story("下单")
    @pytest.mark.p1
    def test_create_order_without_login(self):
        """未登录不能下单"""
        r = ApiClient().create_order([{"book_id": 1, "quantity": 1}])
        assert r.status_code == 401

    @allure.story("下单")
    @pytest.mark.p1
    def test_create_order_insufficient_stock(self, user_client):
        """库存不足"""
        r = user_client.create_order([{"book_id": 4, "quantity": 1}])
        assert r.json()["code"] == 4010

    @allure.story("下单")
    @pytest.mark.p1
    def test_create_order_book_not_found(self, user_client):
        """商品不存在"""
        r = user_client.create_order([{"book_id": 99999, "quantity": 1}])
        assert r.json()["code"] == 4041

    @allure.story("下单")
    @pytest.mark.p0
    def test_create_order_reduces_stock(self, user_client):
        """下单后库存正确扣减（数据库断言）"""
        books = user_client.list_books(is_on_sale="true", page_size=20).json()["data"]["list"]
        target = next(b for b in books if b["stock"] >= 5)

        stock_before = db.get_book_stock(target["id"])
        user_client.create_order([{"book_id": target["id"], "quantity": 3}])
        stock_after = db.get_book_stock(target["id"])

        assert stock_after == stock_before - 3, \
            f"库存未正确扣减：{stock_before} -> {stock_after}"

    @allure.story("下单")
    @pytest.mark.p0
    def test_create_order_rollback_on_failure(self, admin_client, user_client):
        """下单失败时事务回滚"""
        books = admin_client.list_books(is_on_sale="true", page_size=20).json()["data"]["list"]
        normal = next(b for b in books if b["stock"] >= 10)
        out_of_stock = next((b for b in books if b["id"] != normal["id"] and b["stock"] == 0), None)
        if not out_of_stock:
            pytest.skip("需要库存为 0 的书")

        stock_before = db.get_book_stock(normal["id"])

        r = user_client.create_order([
            {"book_id": normal["id"], "quantity": 2},
            {"book_id": out_of_stock["id"], "quantity": 1}
        ])
        assert r.json()["code"] != 200

        stock_after = db.get_book_stock(normal["id"])
        assert stock_after == stock_before, \
            f"事务未回滚！库存从 {stock_before} 变到 {stock_after}"

    @allure.story("支付")
    @pytest.mark.p0
    def test_pay_order_success(self, user_client):
        """支付成功"""
        books = user_client.list_books(is_on_sale="true", page_size=50).json()["data"]["list"]
        book = next((b for b in books if b["stock"] >= 5), None)
        assert book is not None
        order = user_client.create_order([{"book_id": book["id"], "quantity": 1}]).json()["data"]
        r = user_client.pay_order(order["id"])
        assert r.json()["code"] == 2002  # 支付成功 = 2002
        assert r.json()["data"]["status"] == "paid"

    @allure.story("支付")
    @pytest.mark.p1
    def test_pay_order_twice(self, user_client):
        """重复支付应失败"""
        books = user_client.list_books(is_on_sale="true", page_size=50).json()["data"]["list"]
        book = next((b for b in books if b["stock"] >= 5), None)
        assert book is not None
        order = user_client.create_order([{"book_id": book["id"], "quantity": 1}]).json()["data"]
        user_client.pay_order(order["id"])
        r = user_client.pay_order(order["id"])
        assert r.json()["code"] == 4011