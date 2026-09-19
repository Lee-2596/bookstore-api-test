"""
BookStore 手工接口测试脚本
用法：
    python manual_test.py
"""
import requests

BASE = "http://127.0.0.1:5000"


def test(name, url, method="GET", **kwargs):
    """统一测试函数"""
    print(f"\n{'='*60}")
    print(f"🧪 {name}")
    print(f"   {method} {url}")
    if "json" in kwargs:
        print(f"   请求体: {kwargs['json']}")
    if "params" in kwargs:
        print(f"   参数: {kwargs['params']}")
    
    # 发起请求
    r = requests.request(method, BASE + url, timeout=5, **kwargs)
    
    # 显示结果
    print(f"   HTTP 状态: {r.status_code}")
    try:
        body = r.json()
        print(f"   业务码: {body.get('code')}")
        print(f"   消息: {body.get('message')}")
        print(f"   数据: {body.get('data')}")
        return body
    except Exception:
        print(f"   响应: {r.text}")
        return None


# ============ 1. 健康检查 ============
test("健康检查", "/api/health")


# ============ 2. 注册接口 ============
test("注册-正常", "/api/auth/register", "POST",
     json={"username": "u_test001", "password": "test123456", "email": "t1@test.com"})

test("注册-用户名为空", "/api/auth/register", "POST",
     json={"username": "", "password": "test123456"})

test("注册-密码太短", "/api/auth/register", "POST",
     json={"username": "u_test002", "password": "12345"})

test("注册-重复用户名", "/api/auth/register", "POST",
     json={"username": "admin", "password": "test123456"})


# ============ 3. 登录接口 ============
login = test("登录-正常", "/api/auth/login", "POST",
             json={"username": "admin", "password": "admin123"})

# 拿到 token
token = login["data"]["token"] if login and login["code"] == 200 else None
HEADERS = {"Authorization": f"Bearer {token}"} if token else {}


# ============ 4. 商品列表 ============
test("商品列表-默认", "/api/books")
test("商品列表-搜索Python", "/api/books", params={"keyword": "Python"})
test("商品列表-按分类筛选", "/api/books", params={"category_id": 1})
test("商品列表-价格区间", "/api/books", params={"min_price": 50, "max_price": 100})
test("商品列表-分页", "/api/books", params={"page": 1, "page_size": 5})

test("商品详情-存在", "/api/books/1")
test("商品详情-不存在", "/api/books/99999")


# ============ 5. 鉴权相关（用到 token） ============
if token:
    test("获取个人信息-带token", "/api/auth/profile", headers=HEADERS)
else:
    print("\n⚠️  跳过 token 相关测试（登录失败）")

test("获取个人信息-不带token（应失败）", "/api/auth/profile")


# ============ 6. 订单接口 ============
if token:
    # 用 testuser 下单
    user_login = test("登录-testuser", "/api/auth/login", "POST",
                      json={"username": "testuser", "password": "test123"})
    user_token = user_login["data"]["token"] if user_login["code"] == 200 else None
    user_headers = {"Authorization": f"Bearer {user_token}"} if user_token else {}
    
    test("下单-正常", "/api/orders", "POST",
         json={"items": [{"book_id": 1, "quantity": 1}]}, headers=user_headers)
    
    test("下单-不带token（应失败）", "/api/orders", "POST",
         json={"items": [{"book_id": 1, "quantity": 1}]})
    
    test("下单-库存不足", "/api/orders", "POST",
         json={"items": [{"book_id": 4, "quantity": 1}]}, headers=user_headers)
    
    test("下单-商品不存在", "/api/orders", "POST",
         json={"items": [{"book_id": 99999, "quantity": 1}]}, headers=user_headers)
else:
    print("\n⚠️  跳过订单测试")


print("\n" + "="*60)
print("✅ 所有手工测试完成")
print("="*60)