from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    real_name = db.Column(db.String(50))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), default=1)
    department = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.now)

    role = db.relationship('Role', backref='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        perms = []
        if self.role:
            perms = [p.code for p in self.role.permissions]
        return {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'role_id': self.role_id,
            'role_name': self.role.name if self.role else '',
            'department': self.department,
            'phone': self.phone,
            'permissions': perms
        }


role_permission = db.Table('role_permission',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
)


class Permission(db.Model):
    __tablename__ = 'permission'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    module = db.Column(db.String(50))
    description = db.Column(db.String(200))

    def to_dict(self):
        return {'id': self.id, 'code': self.code, 'name': self.name,
                'module': self.module, 'description': self.description}


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))

    permissions = db.relationship('Permission', secondary=role_permission, backref='roles')

    def to_dict(self, with_perms=False):
        d = {'id': self.id, 'name': self.name, 'description': self.description}
        if with_perms:
            d['permissions'] = [p.code for p in self.permissions]
        return d


class WorkPlan(db.Model):
    __tablename__ = 'work_plan'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    type = db.Column(db.String(20))
    plan_year = db.Column(db.Integer)
    plan_month = db.Column(db.Integer)
    content = db.Column(db.Text)
    law_basis = db.Column(db.String(500))
    responsible = db.Column(db.String(100))
    deadline = db.Column(db.Date)
    progress = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='pending')
    completion_date = db.Column(db.Date)
    remark = db.Column(db.Text)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'type': self.type,
            'plan_year': self.plan_year,
            'plan_month': self.plan_month,
            'content': self.content,
            'law_basis': self.law_basis,
            'responsible': self.responsible,
            'deadline': self.deadline.strftime('%Y-%m-%d') if self.deadline else '',
            'progress': self.progress,
            'status': self.status,
            'completion_date': self.completion_date.strftime('%Y-%m-%d') if self.completion_date else '',
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''
        }


class Inspection(db.Model):
    __tablename__ = 'inspection'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    inspect_type = db.Column(db.String(50), default='日常检查')
    inspect_date = db.Column(db.Date)
    location = db.Column(db.String(200))
    inspector = db.Column(db.String(100))
    check_list = db.Column(db.Text)
    result = db.Column(db.String(20), default='合格')
    remark = db.Column(db.Text)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now)

    hazards = db.relationship('Hazard', backref='inspection', lazy=True,
                              foreign_keys='Hazard.inspection_id')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'inspect_type': self.inspect_type,
            'inspect_date': self.inspect_date.strftime('%Y-%m-%d') if self.inspect_date else '',
            'location': self.location,
            'inspector': self.inspector,
            'check_list': self.check_list,
            'result': self.result,
            'remark': self.remark,
            'hazard_count': len(self.hazards),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }


class Hazard(db.Model):
    __tablename__ = 'hazard'
    id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspection.id'))
    check_date = db.Column(db.Date)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    level = db.Column(db.String(20), default='general')
    location = db.Column(db.String(200))
    source = db.Column(db.String(50), default='日常检查')
    law_basis = db.Column(db.String(500))
    rectify_measure = db.Column(db.Text)
    responsible = db.Column(db.String(100))
    deadline = db.Column(db.Date)
    rectify_progress = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='pending')
    rectify_content = db.Column(db.Text)
    rectify_date = db.Column(db.Date)
    before_photo = db.Column(db.String(500))
    after_photo = db.Column(db.String(500))
    acceptor = db.Column(db.String(100))
    accept_date = db.Column(db.Date)
    accept_result = db.Column(db.String(20))
    accept_note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'inspection_id': self.inspection_id,
            'check_date': self.check_date.strftime('%Y-%m-%d') if self.check_date else '',
            'title': self.title,
            'description': self.description,
            'level': self.level,
            'location': self.location,
            'source': self.source,
            'law_basis': self.law_basis,
            'rectify_measure': self.rectify_measure,
            'responsible': self.responsible,
            'deadline': self.deadline.strftime('%Y-%m-%d') if self.deadline else '',
            'rectify_progress': self.rectify_progress,
            'status': self.status,
            'rectify_content': self.rectify_content,
            'rectify_date': self.rectify_date.strftime('%Y-%m-%d') if self.rectify_date else '',
            'before_photo': self.before_photo,
            'after_photo': self.after_photo,
            'acceptor': self.acceptor,
            'accept_date': self.accept_date.strftime('%Y-%m-%d') if self.accept_date else '',
            'accept_result': self.accept_result,
            'accept_note': self.accept_note,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''
        }


class CheckTemplate(db.Model):
    __tablename__ = 'check_template'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100))
    item = db.Column(db.String(500))
    standard = db.Column(db.Text)
    law_basis = db.Column(db.String(500))
    is_key = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'item': self.item,
            'standard': self.standard,
            'law_basis': self.law_basis,
            'is_key': self.is_key
        }


class LawReference(db.Model):
    __tablename__ = 'law_reference'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    doc_type = db.Column(db.String(20))
    issuing_authority = db.Column(db.String(200))
    effective_date = db.Column(db.Date)
    applicable = db.Column(db.Text)
    summary = db.Column(db.Text)
    key_points = db.Column(db.Text)
    industry = db.Column(db.String(50), default='工贸')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'doc_type': self.doc_type,
            'issuing_authority': self.issuing_authority,
            'effective_date': self.effective_date.strftime('%Y-%m-%d') if self.effective_date else '',
            'applicable': self.applicable,
            'summary': self.summary,
            'key_points': self.key_points,
            'industry': self.industry,
            'is_active': self.is_active
        }


# ============ 8. 危险作业票 ============
class WorkPermit(db.Model):
    __tablename__ = 'work_permit'
    id = db.Column(db.Integer, primary_key=True)
    permit_no = db.Column(db.String(50), unique=True)
    permit_type = db.Column(db.String(30))  # 动火/有限空间/高处/吊装/临时用电/盲板抽堵/动土/断路
    risk_level = db.Column(db.String(20))   # 特级/一级/二级/一般
    work_location = db.Column(db.String(300))
    work_content = db.Column(db.Text)
    contractor = db.Column(db.String(200))
    workers = db.Column(db.Integer, default=0)
    work_personnel = db.Column(db.String(500))
    gas_test = db.Column(db.Text)           # O2/CO/H2S/LEL 检测数据
    safety_measures = db.Column(db.Text)
    permit_holder = db.Column(db.String(100))
    guardian = db.Column(db.String(100))
    approver = db.Column(db.String(100))
    apply_date = db.Column(db.Date)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending/approved/rejected/in_progress/completed/cancelled
    reject_reason = db.Column(db.Text)
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id, 'permit_no': self.permit_no,
            'permit_type': self.permit_type, 'risk_level': self.risk_level,
            'work_location': self.work_location, 'work_content': self.work_content,
            'contractor': self.contractor, 'workers': self.workers,
            'work_personnel': self.work_personnel, 'gas_test': self.gas_test,
            'safety_measures': self.safety_measures,
            'permit_holder': self.permit_holder, 'guardian': self.guardian,
            'approver': self.approver,
            'apply_date': self.apply_date.strftime('%Y-%m-%d') if self.apply_date else '',
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M') if self.start_time else '',
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M') if self.end_time else '',
            'status': self.status, 'reject_reason': self.reject_reason,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }


# ============ 9. 安全投入台账 ============
class SafetyCost(db.Model):
    __tablename__ = 'safety_cost'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(300))
    category = db.Column(db.String(50))  # 教育培训/防护用品/隐患整改/安全设施/应急演练/检测检验/职业健康/其他
    amount = db.Column(db.Float, default=0)
    occur_date = db.Column(db.Date)
    payer = db.Column(db.String(100))
    voucher_no = db.Column(db.String(100))
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id, 'item': self.item, 'category': self.category,
            'amount': self.amount,
            'occur_date': self.occur_date.strftime('%Y-%m-%d') if self.occur_date else '',
            'payer': self.payer, 'voucher_no': self.voucher_no,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }


# ============ 10. 事故记录 ============
class Accident(db.Model):
    __tablename__ = 'accident'
    id = db.Column(db.Integer, primary_key=True)
    accident_no = db.Column(db.String(50))
    level = db.Column(db.String(20))     # 特别重大/重大/较大/一般/轻微/未遂
    type = db.Column(db.String(30))     # 机械伤害/高处坠落/物体打击/起重伤害/触电/灼烫/中毒窒息/坍塌/其他
    location = db.Column(db.String(300))
    time = db.Column(db.DateTime)
    deaths = db.Column(db.Integer, default=0)
    injuries = db.Column(db.Integer, default=0)
    direct_loss = db.Column(db.Float, default=0)
    brief = db.Column(db.Text)
    cause_analysis = db.Column(db.Text)
    rectify_measures = db.Column(db.Text)
    responsible = db.Column(db.String(200))
    report_status = db.Column(db.String(20), default='pending')  # pending/reported/investigated/closed
    report_date = db.Column(db.Date)
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id, 'accident_no': self.accident_no,
            'level': self.level, 'type': self.type,
            'location': self.location,
            'time': self.time.strftime('%Y-%m-%d %H:%M') if self.time else '',
            'deaths': self.deaths, 'injuries': self.injuries,
            'direct_loss': self.direct_loss,
            'brief': self.brief, 'cause_analysis': self.cause_analysis,
            'rectify_measures': self.rectify_measures,
            'responsible': self.responsible,
            'report_status': self.report_status,
            'report_date': self.report_date.strftime('%Y-%m-%d') if self.report_date else '',
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }


# ============ 11. 承包商资质档案 ============
class Contractor(db.Model):
    __tablename__ = 'contractor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    contact = db.Column(db.String(50))
    phone = db.Column(db.String(30))
    business_scope = db.Column(db.String(500))
    has_safety_license = db.Column(db.Boolean, default=False)
    safety_license_no = db.Column(db.String(100))
    safety_license_expire = db.Column(db.Date)
    qualification = db.Column(db.String(200))
    last_3y_accidents = db.Column(db.String(200))
    special_workers_count = db.Column(db.Integer, default=0)
    workers_count = db.Column(db.Integer, default=0)
    enter_date = db.Column(db.Date)
    expire_date = db.Column(db.Date)
    safety_agreement = db.Column(db.Boolean, default=False)
    safety_trained = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='active')  # active/pending/blacklist
    performance_score = db.Column(db.Integer, default=80)
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name,
            'contact': self.contact, 'phone': self.phone,
            'business_scope': self.business_scope,
            'has_safety_license': self.has_safety_license,
            'safety_license_no': self.safety_license_no,
            'safety_license_expire': self.safety_license_expire.strftime('%Y-%m-%d') if self.safety_license_expire else '',
            'qualification': self.qualification,
            'last_3y_accidents': self.last_3y_accidents,
            'special_workers_count': self.special_workers_count,
            'workers_count': self.workers_count,
            'enter_date': self.enter_date.strftime('%Y-%m-%d') if self.enter_date else '',
            'expire_date': self.expire_date.strftime('%Y-%m-%d') if self.expire_date else '',
            'safety_agreement': self.safety_agreement,
            'safety_trained': self.safety_trained,
            'status': self.status,
            'performance_score': self.performance_score,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
