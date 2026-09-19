"""
BookStore API 数据模型
- User：用户表（对应测试中的鉴权模块）
- Category：商品分类（一对多关联 Book）
- Book：商品表（多对一关联 Category）
- Order：订单表（用于 MySQL 事务测试）
- OrderItem：订单明细表（订单与商品的多对多关联）

> 名词解释：
> - ORM（对象关系映射）：用 Python 类来表示数据库表，对类的操作会自动变成 SQL 语句
> - 一对多：一个分类下有多个商品，一个商品只属于一个分类
> - 外键：表之间的关联字段，比如 Book 表里的 category_id 指向 Category 表的 id
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """用户表"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, comment='用户名')
    password = db.Column(db.String(255), nullable=False, comment='密码（已哈希）')
    email = db.Column(db.String(120), unique=True, nullable=True, comment='邮箱')
    phone = db.Column(db.String(20), nullable=True, comment='手机号')
    is_active = db.Column(db.Boolean, default=True, comment='账号是否启用')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='注册时间')

    # 关联：一个用户有多个订单
    orders = db.relationship('Order', backref='user', lazy=True)

    def to_dict(self):
        """把对象转成字典，方便返回给前端"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Category(db.Model):
    """商品分类表"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, comment='分类名')
    description = db.Column(db.String(200), nullable=True, comment='分类描述')
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 反向关联：拿到分类时能直接拿到所有商品
    books = db.relationship('Book', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'book_count': len(self.books)  # 这个分类下有多少本书
        }


class Book(db.Model):
    """商品（图书）表"""
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, comment='书名')
    author = db.Column(db.String(100), nullable=False, comment='作者')
    price = db.Column(db.Numeric(10, 2), nullable=False, comment='价格')
    stock = db.Column(db.Integer, default=0, comment='库存')
    description = db.Column(db.Text, nullable=True, comment='描述')
    cover_url = db.Column(db.String(500), nullable=True, comment='封面图链接')
    is_on_sale = db.Column(db.Boolean, default=True, comment='是否在售')
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 外键：关联到分类表
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'price': float(self.price),
            'stock': self.stock,
            'description': self.description,
            'cover_url': self.cover_url,
            'is_on_sale': self.is_on_sale,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Order(db.Model):
    """订单表"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(50), unique=True, nullable=False, comment='订单号')
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, comment='订单总金额')
    status = db.Column(db.String(20), default='pending', comment='订单状态：pending/paid/cancelled')
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 外键：这个订单属于哪个用户
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 关联订单明细
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'order_no': self.order_no,
            'total_amount': float(self.total_amount),
            'status': self.status,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'items': [item.to_dict() for item in self.items]
        }


class OrderItem(db.Model):
    """订单明细表（订单与商品的多对多中间表）"""
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, comment='购买数量')
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, comment='下单时的单价')

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)

    # 冗余字段：方便直接拿到书名，不必再 join
    book_title = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'book_title': self.book_title,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'subtotal': float(self.unit_price * self.quantity)
        }
