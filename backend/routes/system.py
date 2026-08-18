from flask import Blueprint, request, jsonify
from models import db, User, Role, Permission, CheckTemplate, LawReference
from routes.utils import login_required

system_bp = Blueprint('system', __name__)


@system_bp.route('/roles', methods=['GET'])
@login_required
def list_roles():
    with_perms = request.args.get('with_perms', '1') == '1'
    roles = Role.query.all()
    return jsonify({'code': 0, 'data': [r.to_dict(with_perms=with_perms) for r in roles]})


@system_bp.route('/roles', methods=['POST'])
@login_required
def create_role():
    data = request.get_json()
    if Role.query.filter_by(name=data.get('name')).first():
        return jsonify({'code': 400, 'msg': '角色已存在'}), 400
    r = Role(name=data.get('name'), description=data.get('description'))
    codes = data.get('permissions', [])
    if codes:
        perms = Permission.query.filter(Permission.code.in_(codes)).all()
        r.permissions = perms
    db.session.add(r)
    db.session.commit()
    return jsonify({'code': 0, 'data': r.id})


@system_bp.route('/roles/<int:rid>', methods=['PUT'])
@login_required
def update_role(rid):
    r = Role.query.get(rid)
    if not r:
        return jsonify({'code': 404, 'msg': '角色不存在'}), 404
    data = request.get_json()
    if 'name' in data and data['name'] != r.name:
        if Role.query.filter_by(name=data['name']).first():
            return jsonify({'code': 400, 'msg': '角色名已存在'}), 400
        r.name = data['name']
    if 'description' in data:
        r.description = data['description']
    if 'permissions' in data:
        codes = data['permissions']
        if codes:
            r.permissions = Permission.query.filter(Permission.code.in_(codes)).all()
        else:
            r.permissions = []
    db.session.commit()
    return jsonify({'code': 0, 'msg': '更新成功'})


@system_bp.route('/roles/<int:rid>', methods=['DELETE'])
@login_required
def delete_role(rid):
    r = Role.query.get(rid)
    if not r:
        return jsonify({'code': 404, 'msg': '角色不存在'}), 404
    if User.query.filter_by(role_id=rid).first():
        return jsonify({'code': 400, 'msg': '该角色下仍有用户，不能删除'}), 400
    db.session.delete(r)
    db.session.commit()
    return jsonify({'code': 0, 'msg': '删除成功'})


@system_bp.route('/permissions', methods=['GET'])
@login_required
def list_permissions():
    perms = Permission.query.order_by(Permission.module, Permission.id).all()
    return jsonify({'code': 0, 'data': [p.to_dict() for p in perms]})


@system_bp.route('/users', methods=['GET'])
@login_required
def list_users():
    users = User.query.all()
    return jsonify({'code': 0, 'data': [u.to_dict() for u in users]})


@system_bp.route('/users', methods=['POST'])
@login_required
def create_user():
    data = request.get_json()
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'code': 400, 'msg': '用户名已存在'}), 400
    u = User(username=data.get('username'), real_name=data.get('real_name'),
             role_id=data.get('role_id', 1), department=data.get('department'),
             phone=data.get('phone'))
    u.set_password(data.get('password', '123456'))
    db.session.add(u)
    db.session.commit()
    return jsonify({'code': 0, 'data': u.id})


@system_bp.route('/users/<int:uid>', methods=['PUT'])
@login_required
def update_user(uid):
    u = User.query.get(uid)
    if not u:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    data = request.get_json()
    for key in ['real_name', 'role_id', 'department', 'phone']:
        if key in data:
            setattr(u, key, data[key])
    if data.get('password'):
        u.set_password(data['password'])
    db.session.commit()
    return jsonify({'code': 0, 'msg': '更新成功'})


@system_bp.route('/users/<int:uid>', methods=['DELETE'])
@login_required
def delete_user(uid):
    u = User.query.get(uid)
    if not u:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    db.session.delete(u)
    db.session.commit()
    return jsonify({'code': 0, 'msg': '删除成功'})


@system_bp.route('/check-templates', methods=['GET'])
@login_required
def list_templates():
    category = request.args.get('category')
    query = CheckTemplate.query
    if category:
        query = query.filter(CheckTemplate.category == category)
    items = query.all()
    categories = list(set(t.category for t in CheckTemplate.query.all()))
    return jsonify({'code': 0, 'data': [t.to_dict() for t in items], 'categories': categories})


@system_bp.route('/check-templates', methods=['POST'])
@login_required
def create_template():
    data = request.get_json()
    t = CheckTemplate(category=data.get('category'), item=data.get('item'),
                      standard=data.get('standard'), law_basis=data.get('law_basis'),
                      is_key=data.get('is_key', False))
    db.session.add(t)
    db.session.commit()
    return jsonify({'code': 0, 'data': t.id})


@system_bp.route('/law-references', methods=['GET'])
@login_required
def list_law_references():
    keyword = request.args.get('keyword', '')
    doc_type = request.args.get('doc_type')
    industry = request.args.get('industry')
    query = LawReference.query
    if keyword:
        like = f'%{keyword}%'
        query = query.filter(db.or_(LawReference.name.like(like), LawReference.summary.like(like)))
    if doc_type:
        query = query.filter(LawReference.doc_type == doc_type)
    if industry:
        query = query.filter(LawReference.industry == industry)
    items = query.order_by(LawReference.effective_date.desc().nullslast()).all()
    return jsonify({'code': 0, 'data': [l.to_dict() for l in items]})


@system_bp.route('/law-references', methods=['POST'])
@login_required
def create_law_reference():
    data = request.get_json()
    eff = data.get('effective_date')
    from datetime import date
    l = LawReference(name=data.get('name'), doc_type=data.get('doc_type'),
                     issuing_authority=data.get('issuing_authority'),
                     effective_date=date.fromisoformat(eff) if eff else None,
                     applicable=data.get('applicable'), summary=data.get('summary'),
                     key_points=data.get('key_points'), industry=data.get('industry', '工贸'),
                     is_active=data.get('is_active', True))
    db.session.add(l)
    db.session.commit()
    return jsonify({'code': 0, 'data': l.id})


@system_bp.route('/law-references/<int:lid>', methods=['PUT'])
@login_required
def update_law_reference(lid):
    l = LawReference.query.get(lid)
    if not l:
        return jsonify({'code': 404, 'msg': '法规不存在'}), 404
    data = request.get_json()
    for key in ['name', 'doc_type', 'issuing_authority', 'applicable', 'summary', 'key_points', 'industry', 'is_active']:
        if key in data:
            setattr(l, key, data[key])
    eff = data.get('effective_date')
    if eff:
        from datetime import date
        l.effective_date = date.fromisoformat(eff)
    db.session.commit()
    return jsonify({'code': 0, 'msg': '更新成功'})


@system_bp.route('/law-references/<int:lid>', methods=['DELETE'])
@login_required
def delete_law_reference(lid):
    l = LawReference.query.get(lid)
    if not l:
        return jsonify({'code': 404, 'msg': '法规不存在'}), 404
    db.session.delete(l)
    db.session.commit()
    return jsonify({'code': 0, 'msg': '删除成功'})
