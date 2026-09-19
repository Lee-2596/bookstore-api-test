"""
BookStore API 路由定义
所有接口按业务分组，路径前缀 /api
"""
from datetime import datetime
from functools import wraps
import uuid

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_, and_

from models import db, User, Category, Book, Order, OrderItem

api = Blueprint('api', __name__, url_prefix='/api')


# ============ 通用工具 ============

def admin_required(fn):
    """自定义装饰器：要求当前用户是管理员（username=admin）"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.username != 'admin':
            return jsonify({'code': 403, 'message': '需要管理员权限'}), 403
        return fn(*args, **kwargs)
    return wrapper


def success(data=None, message='success', code=200, status=200):
    return jsonify({'code': code, 'message': message, 'data': data}), status


def fail(message='fail', code=400, status=400, data=None):
    return jsonify({'code': code, 'message': message, 'data': data}), status


# ============ 1. 用户认证 ============

@api.route('/auth/register', methods=['POST'])
def register():
    """注册新用户
    请求体：{"username":"xxx","password":"xxx","email":"","phone":""}
    """
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    email = data.get('email')
    phone = data.get('phone')

    # 参数校验（典型 Bug 来源：缺校验会导致后续出错）
    if not username or not password:
        return fail('用户名和密码不能为空', code=4001)
    if len(username) < 3 or len(username) > 20:
        return fail('用户名长度需在 3-20 之间', code=4002)
    if len(password) < 6:
        return fail('密码长度至少 6 位', code=4003)
    if User.query.filter_by(username=username).first():
        return fail('用户名已存在', code=4004)
    if email and User.query.filter_by(email=email).first():
        return fail('邮箱已被注册', code=4005)

    user = User(
        username=username,
        password=generate_password_hash(password),
        email=email,
        phone=phone
    )
    db.session.add(user)
    db.session.commit()

    return success(user.to_dict(), '注册成功', code=2001)


@api.route('/auth/login', methods=['POST'])
def login():
    """登录，返回 JWT Token
    请求体：{"username":"xxx","password":"xxx"}
    """
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return fail('用户名和密码不能为空', code=4001)

    user = User.query.filter_by(username=username).first()
    # 注意：密码错误也返回同样的提示（避免用户名枚举）
    if not user or not check_password_hash(user.password, password):
        return fail('用户名或密码错误', code=4006)
    if not user.is_active:
        return fail('账号已被禁用', code=4007)

    # 生成 token，identity 必须是字符串
    token = create_access_token(identity=str(user.id))

    return success({
        'token': token,
        'user': user.to_dict()
    }, '登录成功')


@api.route('/auth/profile', methods=['GET'])
@jwt_required()
def profile():
    """获取当前登录用户信息（需要 Token）"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return fail('用户不存在', code=4041, status=404)
    return success(user.to_dict())


# ============ 2. 分类 ============

@api.route('/categories', methods=['GET'])
def list_categories():
    """获取所有分类（公开接口）"""
    categories = Category.query.all()
    return success([c.to_dict() for c in categories])


@api.route('/categories', methods=['POST'])
@admin_required
def create_category():
    """新建分类（管理员）"""
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    description = data.get('description')

    if not name:
        return fail('分类名不能为空', code=4001)
    if Category.query.filter_by(name=name).first():
        return fail('分类已存在', code=4008)

    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()
    return success(category.to_dict(), '创建成功', code=2001)


# ============ 3. 商品（图书）============

@api.route('/books', methods=['GET'])
def list_books():
    """获取商品列表（支持分页、搜索、筛选）
    Query 参数：
        page：页码，默认 1
        page_size：每页数量，默认 10，最大 100
        keyword：按书名或作者模糊搜索
        category_id：按分类筛选
        min_price / max_price：价格区间
        is_on_sale：是否在售
    """
    page = int(request.args.get('page', 1))
    page_size = min(int(request.args.get('page_size', 10)), 100)
    keyword = request.args.get('keyword', '').strip()
    category_id = request.args.get('category_id')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    is_on_sale = request.args.get('is_on_sale')

    query = Book.query

    if keyword:
        query = query.filter(or_(Book.title.contains(keyword), Book.author.contains(keyword)))
    if category_id:
        query = query.filter(Book.category_id == int(category_id))
    if min_price:
        query = query.filter(Book.price >= float(min_price))
    if max_price:
        query = query.filter(Book.price <= float(max_price))
    if is_on_sale is not None:
        query = query.filter(Book.is_on_sale == (is_on_sale.lower() == 'true'))

    # 分页
    pagination = query.order_by(Book.id.desc()).paginate(page=page, per_page=page_size, error_out=False)

    return success({
        'list': [b.to_dict() for b in pagination.items],
        'total': pagination.total,
        'page': page,
        'page_size': page_size,
        'total_pages': pagination.pages
    })


@api.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """获取单个商品详情"""
    book = Book.query.get(book_id)
    if not book:
        return fail('商品不存在', code=4041, status=404)
    return success(book.to_dict())


@api.route('/books', methods=['POST'])
@admin_required
def create_book():
    """新建商品（管理员）"""
    data = request.get_json() or {}
    required = ['title', 'author', 'price', 'category_id']
    for key in required:
        if data.get(key) is None or data.get(key) == '':
            return fail(f'字段 {key} 不能为空', code=4001)

    category = Category.query.get(data['category_id'])
    if not category:
        return fail('分类不存在', code=4041, status=404)

    book = Book(
        title=data['title'].strip(),
        author=data['author'].strip(),
        price=float(data['price']),
        stock=int(data.get('stock', 0)),
        description=data.get('description'),
        cover_url=data.get('cover_url'),
        is_on_sale=bool(data.get('is_on_sale', True)),
        category_id=category.id
    )
    db.session.add(book)
    db.session.commit()
    return success(book.to_dict(), '创建成功', code=2001)


@api.route('/books/<int:book_id>', methods=['PUT'])
@admin_required
def update_book(book_id):
    """更新商品（管理员）"""
    book = Book.query.get(book_id)
    if not book:
        return fail('商品不存在', code=4041, status=404)

    data = request.get_json() or {}
    if 'title' in data:
        book.title = data['title'].strip()
    if 'author' in data:
        book.author = data['author'].strip()
    if 'price' in data:
        book.price = float(data['price'])
    if 'stock' in data:
        book.stock = int(data['stock'])
    if 'description' in data:
        book.description = data['description']
    if 'cover_url' in data:
        book.cover_url = data['cover_url']
    if 'is_on_sale' in data:
        book.is_on_sale = bool(data['is_on_sale'])
    if 'category_id' in data:
        category = Category.query.get(data['category_id'])
        if not category:
            return fail('分类不存在', code=4041, status=404)
        book.category_id = category.id

    db.session.commit()
    return success(book.to_dict(), '更新成功', code=2002)


@api.route('/books/<int:book_id>', methods=['DELETE'])
@admin_required
def delete_book(book_id):
    """删除商品（管理员，软删除：下架）"""
    book = Book.query.get(book_id)
    if not book:
        return fail('商品不存在', code=4041, status=404)

    book.is_on_sale = False
    db.session.commit()
    return success(None, '下架成功', code=2003)


# ============ 4. 订单（用于事务测试）============

@api.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    """下单（事务：库存扣减 + 创建订单 + 订单明细，要全部成功才提交）
    请求体：{"items":[{"book_id":1,"quantity":2},...]}
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    items = data.get('items', [])

    if not items:
        return fail('订单明细不能为空', code=4001)

    try:
        total_amount = 0
        order = Order(
            order_no=f'O{datetime.now().strftime("%Y%m%d%H%M%S")}{uuid.uuid4().hex[:6]}',
            total_amount=0,  # 先占位，下方计算
            status='pending',
            user_id=user_id
        )
        db.session.add(order)
        db.session.flush()  # 拿到 order.id，但不提交事务

        for item in items:
            book = Book.query.get(item.get('book_id'))
            quantity = int(item.get('quantity', 1))

            if not book:
                return fail(f'商品不存在：{item.get("book_id")}', code=4041, status=404)
            if not book.is_on_sale:
                return fail(f'商品已下架：{book.title}', code=4009)
            if book.stock < quantity:
                return fail(f'库存不足：{book.title} 剩余 {book.stock}', code=4010)

            # 库存扣减
            book.stock -= quantity

            # 创建订单明细
            order_item = OrderItem(
                quantity=quantity,
                unit_price=book.price,
                book_id=book.id,
                book_title=book.title,
                order_id=order.id
            )
            db.session.add(order_item)
            total_amount += float(book.price) * quantity

        order.total_amount = total_amount
        db.session.commit()  # 事务提交
        return success(order.to_dict(), '下单成功', code=2001)

    except Exception as e:
        db.session.rollback()  # 出错回滚
        current_app.logger.error(f'下单失败: {e}')
        return fail(f'下单失败：{str(e)}', code=5001, status=500)


@api.route('/orders', methods=['GET'])
@jwt_required()
def list_orders():
    """当前用户订单列表（支持按状态筛选）"""
    user_id = get_jwt_identity()
    status_filter = request.args.get('status')
    page = int(request.args.get('page', 1))
    page_size = min(int(request.args.get('page_size', 10)), 100)

    query = Order.query.filter_by(user_id=user_id)
    if status_filter:
        query = query.filter(Order.status == status_filter)

    pagination = query.order_by(Order.id.desc()).paginate(page=page, per_page=page_size, error_out=False)

    return success({
        'list': [o.to_dict() for o in pagination.items],
        'total': pagination.total,
        'page': page,
        'page_size': page_size
    })


@api.route('/orders/<int:order_id>/pay', methods=['POST'])
@jwt_required()
def pay_order(order_id):
    """支付订单（修改状态）"""
    user_id = get_jwt_identity()
    order = Order.query.get(order_id)
    if not order:
        return fail('订单不存在', code=4041, status=404)
    if order.user_id != int(user_id):
        return fail('无权操作该订单', code=4031, status=403)
    if order.status != 'pending':
        return fail(f'订单状态为 {order.status}，不能支付', code=4011)

    order.status = 'paid'
    db.session.commit()
    return success(order.to_dict(), '支付成功', code=2002)


# ============ 5. 健康检查 ============

@api.route('/health', methods=['GET'])
def health():
    """健康检查（用于接口测试中的连通性验证）"""
    return success({'status': 'ok', 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})


# ============ 全局错误处理 ============

@api.errorhandler(404)
def not_found(e):
    return fail('接口不存在', code=4042, status=404)


@api.errorhandler(500)
def server_error(e):
    return fail('服务器内部错误', code=5001, status=500)