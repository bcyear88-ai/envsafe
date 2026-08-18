from flask import Blueprint, request, jsonify
from models import db, Inspection
from routes.utils import login_required
from datetime import datetime

inspection_bp = Blueprint('inspection', __name__)


@inspection_bp.route('/list', methods=['GET'])
@login_required
def list_inspections():
    keyword = request.args.get('keyword', '')
    inspect_type = request.args.get('inspect_type')
    query = Inspection.query
    if keyword:
        query = query.filter(Inspection.title.contains(keyword))
    if inspect_type:
        query = query.filter(Inspection.inspect_type == inspect_type)
    items = query.order_by(Inspection.inspect_date.desc()).all()
    return jsonify({'code': 0, 'data': [i.to_dict() for i in items]})


@inspection_bp.route('/<int:iid>', methods=['GET'])
@login_required
def get_inspection(iid):
    item = Inspection.query.get(iid)
    if not item:
        return jsonify({'code': 404, 'msg': '检查记录不存在'}), 404
    data = item.to_dict()
    data['hazards'] = [h.to_dict() for h in item.hazards]
    return jsonify({'code': 0, 'data': data})


@inspection_bp.route('/', methods=['POST'])
@login_required
def create_inspection():
    data = request.get_json()
    item = Inspection(
        title=data.get('title'),
        inspect_type=data.get('inspect_type', '日常检查'),
        inspect_date=datetime.strptime(data['inspect_date'], '%Y-%m-%d').date() if data.get('inspect_date') else None,
        location=data.get('location'),
        inspector=data.get('inspector'),
        check_list=data.get('check_list') or data.get('checklist'),
        result=data.get('result', '合格'),
        remark=data.get('remark')
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'code': 0, 'data': item.id})


@inspection_bp.route('/<int:iid>', methods=['PUT'])
@login_required
def update_inspection(iid):
    item = Inspection.query.get(iid)
    if not item:
        return jsonify({'code': 404, 'msg': '检查记录不存在'}), 404
    data = request.get_json()
    for key in ['title', 'inspect_type', 'location', 'inspector', 'check_list', 'result', 'remark']:
        if key in data:
            setattr(item, key, data[key])
    if data.get('inspect_date'):
        item.inspect_date = datetime.strptime(data['inspect_date'], '%Y-%m-%d').date()
    db.session.commit()
    return jsonify({'code': 0, 'msg': '更新成功'})


@inspection_bp.route('/<int:iid>', methods=['DELETE'])
@login_required
def delete_inspection(iid):
    item = Inspection.query.get(iid)
    if not item:
        return jsonify({'code': 404, 'msg': '检查记录不存在'}), 404
    for h in item.hazards:
        db.session.delete(h)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'code': 0, 'msg': '删除成功'})
