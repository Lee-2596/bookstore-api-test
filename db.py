"""数据库工具"""
import pymysql
from contextlib import contextmanager

# ⚠️ 改成你自己的 MySQL 密码
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "你的密码",
    "database": "bookstore",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}


@contextmanager
def get_db():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


def query_one(sql, *args):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            return cur.fetchone()


def query_all(sql, *args):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            return cur.fetchall()


def execute(sql, *args):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            conn.commit()
            return cur.rowcount


def get_book_stock(book_id):
    row = query_one("SELECT stock FROM books WHERE id=%s", book_id)
    return row["stock"] if row else None


def get_user_by_name(username):
    return query_one("SELECT * FROM users WHERE username=%s", username)


def get_order_by_no(order_no):
    return query_one("SELECT * FROM orders WHERE order_no=%s", order_no)


def get_order_items(order_id):
    return query_all("SELECT * FROM order_items WHERE order_id=%s", order_id)