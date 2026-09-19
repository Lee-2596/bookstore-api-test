"""用户认证测试"""
import pytest
import allure
import yaml
from common.api_client import ApiClient


def load_login_data():
    with open("data/login_data.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["login_cases"]


@allure.feature("用户认证")
class TestAuth:

    @allure.story("登录接口")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.p0
    @pytest.mark.smoke
    def test_login_success_admin(self):
        """管理员正常登录"""
        with allure.step("发起登录请求"):
            r = ApiClient().login("admin", "admin123")
        with allure.step("断言业务码"):
            assert r.json()["code"] == 200
        with allure.step("断言返回了 token"):
            assert "token" in r.json()["data"]
            assert len(r.json()["data"]["token"]) > 50

    @allure.story("登录接口")
    @pytest.mark.p0
    @pytest.mark.parametrize("case", load_login_data(),
                             ids=[c["case_name"] for c in load_login_data()])
    def test_login_data_driven(self, case):
        """登录接口 - 数据驱动"""
        r = ApiClient().login(case["username"], case["password"])
        body = r.json()
        assert body["code"] == case["expected_code"], \
            f"用例【{case['case_name']}】失败：预期 {case['expected_code']}，实际 {body['code']}"

    @allure.story("登录接口")
    @pytest.mark.p1
    def test_login_response_time(self):
        """登录响应时间 < 1 秒"""
        import time
        start = time.time()
        ApiClient().login("admin", "admin123")
        cost = time.time() - start
        assert cost < 1.0, f"登录耗时 {cost:.2f}s 超过 1s"

    @allure.story("我的信息")
    @pytest.mark.p0
    def test_get_profile(self, admin_client):
        """带 token 获取个人信息"""
        r = admin_client.profile()
        assert r.json()["code"] == 200
        assert r.json()["data"]["username"] == "admin"

    @allure.story("我的信息")
    @pytest.mark.p1
    def test_get_profile_without_token(self):
        """不带 token 应返回 401"""
        r = ApiClient().profile()
        assert r.status_code == 401