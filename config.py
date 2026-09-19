"""
BookStore API 配置文件
默认使用 SQLite，学习 MySQL 时改一行即可
"""
import os

class Config:
    # ============ Flask 基础配置 ============
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bookstore-secret-key-2026'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-bookstore-2026'
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24  # token 24 小时过期

    # ============ 数据库配置 ============
    # 默认 SQLite：文件型数据库，无需安装服务，文件即数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///bookstore.db'
    # 学习 MySQL 时改成下面这行（先安装 MySQL，并修改用户名密码）
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:你的密码@127.0.0.1:3306/bookstore?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ============ JSON 配置 ============
    JSON_AS_ASCII = False  # 让响应里的中文正常显示，不要 \u 转义