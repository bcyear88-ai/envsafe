from flask import Blueprint, request, jsonify, session, g
from models import db, User
from routes.utils import login_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'code': 401, 'msg': '用户名或密码错误'}), 401
    session['user_id'] = user.id
    return jsonify({'code': 0, 'data': {'token': str(user.id), 'user': user.to_dict()}})


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'code': 0, 'msg': '已退出登录'})


@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    return jsonify({'code': 0, 'data': g.current_user.to_dict()})
