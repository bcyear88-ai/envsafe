from flask import Blueprint, request, jsonify
from models import db, WorkPlan
from routes.utils import login_required
from datetime import datetime, date

work_plan_bp = Blueprint('work_plan', __name__)


@work_plan_bp.route('/list', methods=['GET'])
@login_required
def list_plans():
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    type_ = request.args.get('type')
    status = request.args.get('status')
    category = request.args.get('category')
    responsible = request.args.get('responsible')
    keyword = request.args.get('keyword', '')

    query = WorkPlan.query
    if year:
        query = query.filter(WorkPlan.plan_year == year)
    if month:
        query = query.filter(WorkPlan.plan_month == month)
    if type_:
        query = query.filter(WorkPlan.type == type_)
    if status:
        query = query.filter(WorkPlan.status == status)
    if category:
        query = query.filter(WorkPlan.category == category)
    if responsible:
        query = query.filter(WorkPlan.responsible == responsible)
    if keyword:
        query = query.filter(db.or_(WorkPlan.title.contains(keyword), WorkPlan.content.contains(keyword), WorkPlan.law_basis.contains(keyword)))

    plans = query.order_by(WorkPlan.plan_year.desc(), WorkPlan.plan_month.asc(), WorkPlan.deadline.asc()).all()
    return jsonify({'code': 0, 'data': [p.to_dict() for p in plans]})


@work_plan_bp.route('/<int:pid>', methods=['GET'])
@login_required
def get_plan(pid):
    plan = WorkPlan.query.get(pid)
    if not plan:
        return jsonify({'code': 404, 'msg': '计划不存在'}), 404
    return jsonify({'code': 0, 'data': plan.to_dict()})


@work_plan_bp.route('/', methods=['POST'])
@login_required
def create_plan():
    data = request.get_json()
    plan = WorkPlan(
        title=data.get('title'),
        category=data.get('category'),
        type=data.get('type'),
        plan_year=data.get('plan_year'),
        plan_month=data.get('plan_month'),
        content=data.get('content'),
        law_basis=data.get('law_basis'),
        responsible=data.get('responsible'),
        deadline=datetime.strptime(data['deadline'], '%Y-%m-%d').date() if data.get('deadline') else None,
        progress=data.get('progress', 0),
        status=data.get('status', 'pending'),
        remark=data.get('remark')
    )
    db.session.add(plan)
    db.session.commit()
    return jsonify({'code': 0, 'data': plan.id})


@work_plan_bp.route('/<int:pid>', methods=['PUT'])
@login_required
def update_plan(pid):
    plan = WorkPlan.query.get(pid)
    if not plan:
        return jsonify({'code': 404, 'msg': '计划不存在'}), 404
    data = request.get_json()
    for key in ['title', 'category', 'type', 'plan_year', 'plan_month', 'content', 'law_basis',
                'responsible', 'progress', 'status', 'remark']:
        if key in data:
            setattr(plan, key, data[key])
    if data.get('deadline'):
        plan.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
    if data.get('status') == 'completed' and not plan.completion_date:
        plan.completion_date = date.today()
    plan.updated_at = datetime.now()
    db.session.commit()
    return jsonify({'code': 0, 'msg': '更新成功'})


@work_plan_bp.route('/<int:pid>', methods=['DELETE'])
@login_required
def delete_plan(pid):
    plan = WorkPlan.query.get(pid)
    if not plan:
        return jsonify({'code': 404, 'msg': '计划不存在'}), 404
    db.session.delete(plan)
    db.session.commit()
    return jsonify({'code': 0, 'msg': '删除成功'})
