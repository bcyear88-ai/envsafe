import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory
from models import db, Hazard
from routes.utils import login_required
from datetime import datetime, date
from config import Config

hazard_bp = Blueprint('hazard', __name__)
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


@hazard_bp.route('/upload', methods=['POST'])
@login_required
def upload_photo():
    if 'file' not in request.files:
        return jsonify({'code': 400, 'msg': '无文件'}), 400
    f = request.files['file']
    if f.filename == '' or not allowed_file(f.filename):
        return jsonify({'code': 400, 'msg': '文件格式不支持'}), 400
    ext = f.filename.rsplit('.', 1)[1].lower()
    filename = '{}.{}'.format(uuid.uuid4().hex, ext)
    f.save(os.path.join(Config.UPLOAD_FOLDER, filename))
    return jsonify({'code': 0, 'data': '/api/uploads/' + filename})


@hazard_bp.route('/list', methods=['GET'])
@login_required
def list_hazards():
    keyword = request.args.get('keyword', '')
    level = request.args.get('level')
    status = request.args.get('status')
    location = request.args.get('location')

    query = Hazard.query
    if keyword:
        query = query.filter(Hazard.description.contains(keyword) | Hazard.title.contains(keyword))
    if level:
        query = query.filter(Hazard.level == level)
    if status:
        query = query.filter(Hazard.status == status)
    if location:
        query = query.filter(Hazard.location.contains(location))

    items = query.order_by(Hazard.deadline.asc()).all()
    today = date.today()
    result = []
    for h in items:
        d = h.to_dict()
        if h.status not in ['rectified', 'closed'] and h.deadline:
            if h.deadline < today:
                d['overdue'] = True
            elif (h.deadline - today).days <= 7:
                d['soon'] = True
        result.append(d)
    return jsonify({'code': 0, 'data': result})


@hazard_bp.route('/<int:hid>', methods=['GET'])
@login_required
def get_hazard(hid):
    item = Hazard.query.get(hid)
    if not item:
        return jsonify({'code': 404, 'msg': '隐患不存在'}), 404
    return jsonify({'code': 0, 'data': item.to_dict()})


@hazard_bp.route('/', methods=['POST'])
@login_required
def create_hazard():
    data = request.get_json()
    item = Hazard(
        inspection_id=data.get('inspection_id'),
        check_date=datetime.strptime(data['check_date'], '%Y-%m-%d').date() if data.get('check_date') else None,
        title=data.get('title') or (data.get('description','')[:50] if data.get('description') else '未命名隐患'),
        description=data.get('description'),
        level=data.get('level', 'general'),
        location=data.get('location'),
        source=data.get('source', '日常检查'),
        law_basis=data.get('law_basis'),
        rectify_measure=data.get('rectify_measure'),
        responsible=data.get('responsible'),
        deadline=datetime.strptime(data['deadline'], '%Y-%m-%d').date() if data.get('deadline') else None,
        rectify_progress=data.get('rectify_progress', 0),
        status=data.get('status', 'pending'),
        before_photo=data.get('before_photo')
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'code': 0, 'data': item.id})


@hazard_bp.route('/<int:hid>', methods=['PUT'])
@login_required
def update_hazard(hid):
    item = Hazard.query.get(hid)
    if not item:
        return jsonify({'code': 404, 'msg': '隐患不存在'}), 404
    data = request.get_json()
    for key in ['title', 'description', 'level', 'location', 'source', 'law_basis',
                'rectify_measure', 'responsible', 'rectify_content', 'rectify_progress', 'status',
                'before_photo', 'after_photo', 'acceptor', 'accept_result', 'accept_note']:
        if key in data:
            setattr(item, key, data[key])
    if data.get('deadline'):
        item.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
    if data.get('check_date'):
        item.check_date = datetime.strptime(data['check_date'], '%Y-%m-%d').date()
    if data.get('status') == 'rectified' and not item.rectify_date:
        item.rectify_date = date.today()
    if data.get('status') == 'closed' and not item.accept_date:
        item.accept_date = date.today()
        item.acceptor = item.acceptor or '安环部负责人'
        item.accept_result = item.accept_result or '通过'
    item.updated_at = datetime.now()
    db.session.commit()
    return jsonify({'code': 0, 'msg': '更新成功'})


@hazard_bp.route('/<int:hid>', methods=['DELETE'])
@login_required
def delete_hazard(hid):
    item = Hazard.query.get(hid)
    if not item:
        return jsonify({'code': 404, 'msg': '隐患不存在'}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({'code': 0, 'msg': '删除成功'})
