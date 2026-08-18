from flask import Blueprint, request, jsonify
from models import db, WorkPermit, SafetyCost, Accident, Contractor
from routes.utils import login_required
from datetime import datetime, date

secondary_bp = Blueprint('secondary', __name__)


# ============================================================
# 危险作业票 WorkPermit
# ============================================================

@secondary_bp.route('/work-permit/list', methods=['GET'])
@login_required
def list_work_permits():
    keyword = request.args.get('keyword', '')
    permit_type = request.args.get('permit_type')
    status = request.args.get('status')
    year = request.args.get('year', type=int)

    q = WorkPermit.query
    if keyword:
        like = f'%{keyword}%'
        q = q.filter(db.or_(
            WorkPermit.permit_no.like(like),
            WorkPermit.work_location.like(like),
            WorkPermit.contractor.like(like)
        ))
    if permit_type:
        q = q.filter(WorkPermit.permit_type == permit_type)
    if status:
        q = q.filter(WorkPermit.status == status)
    if year:
        q = q.filter(db.extract('year', WorkPermit.apply_date) == year)

    items = q.order_by(WorkPermit.apply_date.desc().nullslast(), WorkPermit.id.desc()).all()
    return jsonify({'code': 0, 'data': [i.to_dict() for i in items]})


@secondary_bp.route('/work-permit', methods=['POST'])
@login_required
def create_work_permit():
    data = request.get_json()
    p = WorkPermit(
        permit_no=data.get('permit_no') or f'WP-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        permit_type=data.get('permit_type'),
        risk_level=data.get('risk_level'),
        work_location=data.get('work_location'),
        work_content=data.get('work_content'),
        contractor=data.get('contractor'),
        workers=data.get('workers', 0),
        work_personnel=data.get('work_personnel'),
        gas_test=data.get('gas_test'),
        safety_measures=data.get('safety_measures'),
        permit_holder=data.get('permit_holder'),
        guardian=data.get('guardian'),
        approver=data.get('approver'),
        apply_date=datetime.strptime(data['apply_date'], '%Y-%m-%d').date() if data.get('apply_date') else date.today(),
        start_time=datetime.strptime(data['start_time'], '%Y-%m-%dT%H:%M') if data.get('start_time') else None,
        end_time=datetime.strptime(data['end_time'], '%Y-%m-%dT%H:%M') if data.get('end_time') else None,
        status=data.get('status', 'pending'),
        reject_reason=data.get('reject_reason'),
        remark=data.get('remark')
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({'code': 0, 'data': p.permit_no})


@secondary_bp.route('/work-permit/<int:pid>', methods=['PUT'])
@login_required
def update_work_permit(pid):
    p = WorkPermit.query.get_or_404(pid)
    data = request.get_json()
    for k in ['permit_type', 'risk_level', 'work_location', 'work_content', 'contractor',
              'workers', 'work_personnel', 'gas_test', 'safety_measures',
              'permit_holder', 'guardian', 'approver', 'status', 'reject_reason', 'remark', 'permit_no']:
        if k in data:
            setattr(p, k, data[k])
    for d in ['apply_date']:
        if data.get(d):
            setattr(p, d, datetime.strptime(data[d], '%Y-%m-%d').date())
    for d in ['start_time', 'end_time']:
        if data.get(d):
            setattr(p, d, datetime.strptime(data[d], '%Y-%m-%dT%H:%M'))
    db.session.commit()
    return jsonify({'code': 0, 'msg': '更新成功'})


@secondary_bp.route('/work-permit/<int:pid>', methods=['DELETE'])
@login_required
def delete_work_permit(pid):
    p = WorkPermit.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    return jsonify({'code': 0, 'msg': '删除成功'})


# ============================================================
# 安全投入台账 SafetyCost
# ============================================================

@secondary_bp.route('/safety-cost/list', methods=['GET'])
@login_required
def list_safety_cost():
    keyword = request.args.get('keyword', '')
    category = request.args.get('category')
    year = request.args.get('year', type=int)

    q = SafetyCost.query
    if keyword:
        q = q.filter(db.or_(SafetyCost.item.contains(keyword), SafetyCost.remark.contains(keyword)))
    if category:
        q = q.filter(SafetyCost.category == category)
    if year:
        q = q.filter(db.extract('year', SafetyCost.occur_date) == year)

    items = q.order_by(SafetyCost.occur_date.desc().nullslast()).all()
    total_amount = sum(i.amount or 0 for i in items)
    cat_stats = {}
    for i in items:
        c = i.category or '其他'
        cat_stats[c] = cat_stats.get(c, 0) + (i.amount or 0)
    return jsonify({'code': 0, 'data': {'list': [i.to_dict() for i in items],
                    'total_amount': round(total_amount, 2), 'cat_stats': cat_stats}})


@secondary_bp.route('/safety-cost', methods=['POST'])
@login_required
def create_safety_cost():
    data = request.get_json()
    c = SafetyCost(
        item=data.get('item'),
        category=data.get('category'),
        amount=float(data.get('amount') or 0),
        occur_date=datetime.strptime(data['occur_date'], '%Y-%m-%d').date() if data.get('occur_date') else date.today(),
        payer=data.get('payer'),
        voucher_no=data.get('voucher_no'),
        remark=data.get('remark')
    )
    db.session.add(c)
    db.session.commit()
    return jsonify({'code': 0, 'data': c.id})


@secondary_bp.route('/safety-cost/<int:cid>', methods=['PUT', 'DELETE'])
@login_required
def safety_cost_ops(cid):
    c = SafetyCost.query.get_or_404(cid)
    if request.method == 'DELETE':
        db.session.delete(c)
        db.session.commit()
        return jsonify({'code': 0, 'msg': '删除成功'})
    data = request.get_json()
    for k in ['item', 'category', 'payer', 'voucher_no', 'remark']:
        if k in data:
            setattr(c, k, data[k])
    if 'amount' in data:
        c.amount = float(data['amount'] or 0)
    if data.get('occur_date'):
        c.occur_date = datetime.strptime(data['occur_date'], '%Y-%m-%d').date()
    db.session.commit()
    return jsonify({'code': 0, 'msg': '更新成功'})


# ============================================================
# 事故记录 Accident
# ============================================================

@secondary_bp.route('/accident/list', methods=['GET'])
@login_required
def list_accidents():
    keyword = request.args.get('keyword', '')
    level = request.args.get('level')
    type_ = request.args.get('type')
    year = request.args.get('year', type=int)

    q = Accident.query
    if keyword:
        like = f'%{keyword}%'
        q = q.filter(db.or_(Accident.accident_no.like(like), Accident.location.like(like),
                            Accident.brief.like(like)))
    if level:
        q = q.filter(Accident.level == level)
    if type_:
        q = q.filter(Accident.type == type_)
    if year:
        q = q.filter(db.extract('year', Accident.time) == year)

    items = q.order_by(Accident.time.desc().nullslast()).all()
    deaths = sum(i.deaths or 0 for i in items)
    injuries = sum(i.injuries or 0 for i in items)
    return jsonify({'code': 0, 'data': {'list': [i.to_dict() for i in items],
                    'deaths': deaths, 'injuries': injuries}})


@secondary_bp.route('/accident', methods=['POST'])
@login_required
def create_accident():
    data = request.get_json()
    a = Accident(
        accident_no=data.get('accident_no') or f'AC-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        level=data.get('level'), type=data.get('type'),
        location=data.get('location'),
        time=datetime.strptime(data['time'], '%Y-%m-%dT%H:%M') if data.get('time') else datetime.now(),
        deaths=int(data.get('deaths') or 0),
        injuries=int(data.get('injuries') or 0),
        direct_loss=float(data.get('direct_loss') or 0),
        brief=data.get('brief'),
        cause_analysis=data.get('cause_analysis'),
        rectify_measures=data.get('rectify_measures'),
        responsible=data.get('responsible'),
        report_status=data.get('report_status', 'pending'),
        report_date=datetime.strptime(data['report_date'], '%Y-%m-%d').date() if data.get('report_date') else None,
        remark=data.get('remark')
    )
    db.session.add(a)
    db.session.commit()
    return jsonify({'code': 0, 'data': a.id})


@secondary_bp.route('/accident/<int:aid>', methods=['PUT', 'DELETE'])
@login_required
def accident_ops(aid):
    a = Accident.query.get_or_404(aid)
    if request.method == 'DELETE':
        db.session.delete(a)
        db.session.commit()
        return jsonify({'code': 0, 'msg': '删除成功'})
    data = request.get_json()
    for k in ['accident_no', 'level', 'type', 'location', 'brief', 'cause_analysis',
              'rectify_measures', 'responsible', 'report_status', 'remark']:
        if k in data:
            setattr(a, k, data[k])
    if 'deaths' in data:
        a.deaths = int(data['deaths'] or 0)
    if 'injuries' in data:
        a.injuries = int(data['injuries'] or 0)
    if 'direct_loss' in data:
        a.direct_loss = float(data['direct_loss'] or 0)
    if data.get('time'):
        a.time = datetime.strptime(data['time'], '%Y-%m-%dT%H:%M')
    if data.get('report_date'):
        a.report_date = datetime.strptime(data['report_date'], '%Y-%m-%d').date()
    db.session.commit()
    return jsonify({'code': 0, 'msg': '更新成功'})


# ============================================================
# 承包商资质档案 Contractor
# ============================================================

@secondary_bp.route('/contractor/list', methods=['GET'])
@login_required
def list_contractors():
    keyword = request.args.get('keyword', '')
    status = request.args.get('status')
    has_license = request.args.get('has_license')

    q = Contractor.query
    if keyword:
        like = f'%{keyword}%'
        q = q.filter(db.or_(Contractor.name.like(like), Contractor.contact.like(like),
                            Contractor.business_scope.like(like)))
    if status:
        q = q.filter(Contractor.status == status)
    if has_license == 'true':
        q = q.filter(Contractor.has_safety_license == True)

    items = q.order_by(Contractor.created_at.desc()).all()
    active_count = Contractor.query.filter_by(status='active').count()
    with_license = Contractor.query.filter_by(has_safety_license=True).count()
    with_agreement = Contractor.query.filter_by(safety_agreement=True).count()
    return jsonify({'code': 0, 'data': [i.to_dict() for i in items],
                    'active_count': active_count, 'with_license': with_license,
                    'with_agreement': with_agreement})


@secondary_bp.route('/contractor', methods=['POST'])
@login_required
def create_contractor():
    data = request.get_json()
    c = Contractor(
        name=data.get('name'),
        contact=data.get('contact'), phone=data.get('phone'),
        business_scope=data.get('business_scope'),
        has_safety_license=data.get('has_safety_license', False),
        safety_license_no=data.get('safety_license_no'),
        safety_license_expire=datetime.strptime(data['safety_license_expire'], '%Y-%m-%d').date() if data.get('safety_license_expire') else None,
        qualification=data.get('qualification'),
        last_3y_accidents=data.get('last_3y_accidents'),
        special_workers_count=int(data.get('special_workers_count') or 0),
        workers_count=int(data.get('workers_count') or 0),
        enter_date=datetime.strptime(data['enter_date'], '%Y-%m-%d').date() if data.get('enter_date') else None,
        expire_date=datetime.strptime(data['expire_date'], '%Y-%m-%d').date() if data.get('expire_date') else None,
        safety_agreement=data.get('safety_agreement', False),
        safety_trained=data.get('safety_trained', False),
        status=data.get('status', 'active'),
        performance_score=int(data.get('performance_score') or 80),
        remark=data.get('remark')
    )
    db.session.add(c)
    db.session.commit()
    return jsonify({'code': 0, 'data': c.id})


@secondary_bp.route('/contractor/<int:cid>', methods=['PUT', 'DELETE'])
@login_required
def contractor_ops(cid):
    c = Contractor.query.get_or_404(cid)
    if request.method == 'DELETE':
        db.session.delete(c)
        db.session.commit()
        return jsonify({'code': 0, 'msg': '删除成功'})
    data = request.get_json()
    for k in ['name', 'contact', 'phone', 'business_scope', 'safety_license_no',
              'qualification', 'last_3y_accidents', 'status', 'remark']:
        if k in data:
            setattr(c, k, data[k])
    for k in ['has_safety_license', 'safety_agreement', 'safety_trained']:
        if k in data:
            setattr(c, k, bool(data[k]))
    for k in ['special_workers_count', 'workers_count', 'performance_score']:
        if k in data:
            setattr(c, k, int(data[k] or 0))
    for d in ['safety_license_expire', 'enter_date', 'expire_date']:
        if data.get(d):
            setattr(c, d, datetime.strptime(data[d], '%Y-%m-%d').date())
        elif d in data and data[d] is None:
            setattr(c, d, None)
    db.session.commit()
    return jsonify({'code': 0, 'msg': '更新成功'})
