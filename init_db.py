"""
初始化数据库，插入示例数据
运行方式：python init_db.py
"""
from app import create_app
from models import db, User, Category, Book
from werkzeug.security import generate_password_hash


def init_sample_data():
    """插入测试用样本数据"""
    app = create_app()
    with app.app_context():
        db.create_all()

        # 如果已有数据则跳过
        if User.query.count() > 0:
            print('⚠️  数据库已有数据，跳过初始化')
            return

        print('📦 开始插入示例数据...')

        # 1. 创建管理员账号
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            email='admin@bookstore.com',
            phone='13800000000'
        )
        db.session.add(admin)

        # 2. 创建测试用户
        test_user = User(
            username='testuser',
            password=generate_password_hash('test123'),
            email='test@bookstore.com',
            phone='13900000000'
        )
        db.session.add(test_user)

        # 3. 创建分类
        categories_data = [
            {'name': '计算机', 'description': '编程、技术、计算机科学'},
            {'name': '文学', 'description': '小说、散文、诗歌'},
            {'name': '历史', 'description': '历史、人文、传记'},
            {'name': '经管', 'description': '经济、管理、商业'}
        ]
        categories = []
        for cat in categories_data:
            c = Category(**cat)
            db.session.add(c)
            categories.append(c)

        db.session.flush()  # 拿到分类的 id

        # 4. 创建图书（每个分类几本）
        books_data = [
            # 计算机
            {'title': 'Python编程：从入门到实践', 'author': 'Eric Matthes', 'price': 89.00, 'stock': 50, 'category_id': categories[0].id},
            {'title': '算法导论', 'author': 'Thomas H. Cormen', 'price': 128.00, 'stock': 30, 'category_id': categories[0].id},
            {'title': '深入理解计算机系统', 'author': 'Randal E. Bryant', 'price': 139.00, 'stock': 20, 'category_id': categories[0].id},
            {'title': '代码大全', 'author': 'Steve McConnell', 'price': 98.00, 'stock': 0, 'category_id': categories[0].id},  # 库存为 0，测试用
            # 文学
            {'title': '活着', 'author': '余华', 'price': 28.00, 'stock': 100, 'category_id': categories[1].id},
            {'title': '百年孤独', 'author': '加西亚·马尔克斯', 'price': 55.00, 'stock': 60, 'category_id': categories[1].id},
            # 历史
            {'title': '史记', 'author': '司马迁', 'price': 99.00, 'stock': 25, 'category_id': categories[2].id},
            {'title': '万历十五年', 'author': '黄仁宇', 'price': 38.00, 'stock': 40, 'category_id': categories[2].id},
            # 经管
            {'title': '穷查理宝典', 'author': '查理·芒格', 'price': 168.00, 'stock': 15, 'category_id': categories[3].id},
            {'title': '原则', 'author': '瑞·达利欧', 'price': 98.00, 'stock': 35, 'category_id': categories[3].id},
            # 边界值数据：极小价格
            {'title': '测试用书-0.01元', 'author': '边界值测试', 'price': 0.01, 'stock': 1, 'category_id': categories[1].id},
            # 边界值数据：极大价格
            {'title': '测试用书-9999元', 'author': '边界值测试', 'price': 9999.00, 'stock': 1, 'category_id': categories[1].id}
        ]

        for b in books_data:
            book = Book(**b, is_on_sale=True)
            db.session.add(book)

        db.session.commit()
        print('=' * 60)
        print('✅ 示例数据插入完成')
        print('   管理员账号：admin / admin123')
        print('   测试账号：testuser / test123')
        print('   数据库：sqlite:///bookstore.db')
        print('=' * 60)


if __name__ == '__main__':
    init_sample_data()