from functools import wraps
from flask import request, jsonify, session, g
from models import User


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            token = request.headers.get('Authorization', '')
            if token.startswith('Bearer '):
                user_id = token[7:]
        if not user_id:
            return jsonify({'code': 401, 'msg': '未登录或登录已过期'}), 401
        user = User.query.get(int(user_id))
        if not user:
            return jsonify({'code': 401, 'msg': '用户不存在'}), 401
        g.current_user = user
        return f(*args, **kwargs)
    return wrapper
