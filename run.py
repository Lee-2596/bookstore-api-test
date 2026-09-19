"""
一键运行入口
用法：
    python run.py [smoke|all|auth|book|order]
"""
import os
import sys
import pytest


def ensure_dirs():
    """创建必要的目录"""
    os.makedirs("reports/allure_raw", exist_ok=True)
    os.makedirs("reports/allure_html", exist_ok=True)
    os.makedirs("logs", exist_ok=True)


def check_service():
    """检查 BookStore 服务是否启动"""
    import requests
    try:
        r = requests.get("http://127.0.0.1:5000/api/health", timeout=3)
        if r.status_code == 200:
            print("✅ BookStore 服务正常")
            return True
    except Exception:
        pass
    print("❌ BookStore 服务未启动！")
    print("   请先在 00-项目源码 目录运行：python app.py")
    return False


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    ensure_dirs()

    print("=" * 60)
    print(f"🚀 BookStore 接口自动化 - 运行模式：{mode}")
    print("=" * 60)

    if not check_service():
        sys.exit(1)

    # 决定运行哪些用例
    if mode == "smoke":
        args = ["-v", "-m", "smoke", "--alluredir=reports/allure_raw"]
    elif mode == "auth":
        args = ["-v", "cases/test_auth.py", "--alluredir=reports/allure_raw"]
    elif mode == "book":
        args = ["-v", "cases/test_book.py", "--alluredir=reports/allure_raw"]
    elif mode == "order":
        args = ["-v", "cases/test_order.py", "--alluredir=reports/allure_raw"]
    elif mode == "no-allure":
        args = ["-v", "cases/"]
    else:  # all
        args = ["-v", "cases/", "--alluredir=reports/allure_raw"]

    exit_code = pytest.main(args)

    # 生成 Allure 报告
    if "--alluredir" in args:
        print("\n📊 生成 Allure 报告...")
        os.system("allure generate reports/allure_raw -o reports/allure_html --clean")
        print("📍 报告路径：08-Pytest自动化/reports/allure_html/index.html")
        print("   用浏览器打开此文件即可")

    sys.exit(exit_code)