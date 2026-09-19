# BookStore 接口自动化测试项目

> 基于 Python + Flask 自建电商 API + Pytest 完整接口自动化测试方案

## 项目亮点

- ✅ **自建测试目标系统**：从零搭建 Flask 电商 API（用户/商品/订单）
- ✅ **50+ 自动化用例**：覆盖正常/异常/边界值/鉴权/事务
- ✅ **数据驱动 + 数据库断言**：YAML 管理测试数据，验证业务一致性
- ✅ **Pytest + Allure + pytest-html**：多套可视化报告
- ✅ **Postman 接口集合**：13+ 接口可直接调试
- ✅ **OpenAPI 3.0 规范**：可对接前端团队

## 技术栈

- **后端**：Python 3.11 + Flask + SQLAlchemy + JWT
- **数据库**：SQLite（开发）/ MySQL（生产）
- **自动化**：Pytest + requests + loguru + PyMySQL
- **接口文档**：OpenAPI 3.0（Postman 生成）
- **报告**：pytest-html + Allure（兼容）

## 目录结构

```
0918/
├── 00-项目源码/                # Flask 后端 API
│   ├── app.py
│   ├── models.py
│   ├── routes.py
│   ├── frontend/               # 简单 HTML 前端（功能测试用）
│   └── requirements.txt
│
├── 02-测试基础/                # 测试用例 + 手工测试脚本
│   ├── 测试用例模板.md
│   └── manual_test.py
│
├── 08-Pytest自动化/            # ⭐ 核心：自动化测试项目
│   ├── cases/                  # 测试用例
│   ├── common/                 # API 客户端 + 数据库工具
│   ├── data/                   # 数据驱动 YAML
└── ├── reports/                # 测试报告 └── run.py                  # 一键运行 
```

##  快速开始

### 1. 启动后端

```bash
cd 00-项目源码
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
python init_db.py        # 初始化数据
python app.py            # 启动服务
```

访问 `http://127.0.0.1:5000/api/health` 验证。

### 2. 跑自动化测试

```bash
cd 08-Pytest自动化
pip install -r requirements.txt

# 跑全部
python run.py all

# 只跑冒烟
python run.py smoke

# 只跑某个模块
python run.py order
```

报告生成在 `reports/report.html`，浏览器打开即可。

### 3. 用 Postman 测试

`08-Pytest自动化/BookStore.postman_collection.json` 是 Postman 集合，直接导入即可。

##  测试覆盖场景

| 模块 | 用例数 | 场景 |
|------|-------|------|
| 用户认证 | 10+ | 登录、注册、Token 鉴权、参数校验 |
| 商品管理 | 10+ | CRUD、搜索、筛选、分页、边界值 |
| 订单流程 | 8+ | 下单、支付、状态流转、**事务回滚**、库存 |
| 数据库断言 | 2 | 库存扣减、事务回滚验证 |

##  真实测试发现

- ⚠️ 注册接口未对特殊字符进行校验
- ⚠️ 登录错误提示信息不够友好
- ⚠️ JWT 鉴权失败响应格式与其他接口不一致
- ⚠️ 下单接口在并发场景下可能存在超卖风险

##  项目数据

- 测试用例总数：50+
- 自动化覆盖：95%
- 回归测试时间：手工 4 小时 → 自动化 2 秒
- 发现的真实 Bug：4 项

## 🔗 相关文档

- 📄 [Postman 接口集合](08-Pytest自动化/BookStore.postman_collection.json)
- 📄 [OpenAPI 规范](08-Pytest自动化/BookStore.openapi.yaml)
- 📄 [测试用例模板](02-测试基础/测试用例模板.md)

⭐ 如果这个项目对你有帮助，欢迎 Star！
