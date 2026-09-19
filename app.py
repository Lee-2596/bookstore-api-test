"""
BookStore API 主入口
启动方式（项目根目录下）：
    python app.py
"""
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from config import Config
from models import db
from routes import api


def create_app():
    """工厂函数：创建 Flask 应用"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化扩展
    db.init_app(app)
    JWTManager(app)
    CORS(app)  # 允许跨域（接口测试时方便）

    # 注册蓝图
    app.register_blueprint(api)

    # 根路径提示
    @app.route('/')
    def index():
        return {
            'name': 'BookStore API',
            'version': '1.0.0',
            'docs': '请访问 /api/health 检查服务状态'
        }

    # 友好错误页
    @app.errorhandler(404)
    def page_not_found(e):
        return {'code': 404, 'message': '页面不存在'}, 404

    return app


if __name__ == '__main__':
    app = create_app()

    # 自动建表（第一次启动时执行）
    with app.app_context():
        db.create_all()
        print('=' * 60)
        print('✅ 数据库表已创建/已存在')
        print('=' * 60)

    print('=' * 60)
    print('🚀 BookStore API 启动中...')
    print('📍 地址: http://127.0.0.1:5000')
    print('💡 健康检查: http://127.0.0.1:5000/api/health')
    print('💡 接口文档请见: README.md')
    print('=' * 60)

    app.run(host='0.0.0.0', port=5000, debug=True)