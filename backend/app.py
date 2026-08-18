import os
import sys
from flask import Flask, send_from_directory, request, g

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config
from models import db

def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)
    app.config['SESSION_PERMANENT'] = True

    db.init_app(app)

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    @app.after_request
    def add_cors(resp):
        resp.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        if request.path.startswith('/libs/') or request.path == '/' or request.path.endswith('.html'):
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
        return resp

    from routes.auth import auth_bp
    from routes.work_plan import work_plan_bp
    from routes.inspection import inspection_bp
    from routes.hazard import hazard_bp
    from routes.report import report_bp
    from routes.system import system_bp
    from routes.secondary import secondary_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(work_plan_bp, url_prefix='/api/workplan')
    app.register_blueprint(inspection_bp, url_prefix='/api/inspection')
    app.register_blueprint(hazard_bp, url_prefix='/api/hazard')
    app.register_blueprint(report_bp, url_prefix='/api/report')
    app.register_blueprint(system_bp, url_prefix='/api/system')
    app.register_blueprint(secondary_bp, url_prefix='/api/secondary')

    @app.route('/api/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(Config.UPLOAD_FOLDER, filename)

    @app.route('/')
    def index():
        return send_from_directory(os.path.join(os.path.dirname(__file__), '..', 'frontend'), 'index.html')

    @app.route('/<path:path>')
    def static_files(path):
        front_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
        file_path = os.path.join(front_dir, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return send_from_directory(front_dir, path)
        return send_from_directory(front_dir, 'index.html')

    return app


def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        db.session.commit()
        _seed_data(db)
    return app


def _seed_data(db):
    from models import User, Role, Permission, WorkPlan, CheckTemplate, Inspection, Hazard
    from datetime import datetime, date, timedelta

    def _has_table(name):
        try:
            db.session.execute('SELECT 1 FROM {}'.format(name))
            return True
        except Exception:
            return False

    def _has_data(model):
        if not _has_table(model.__tablename__):
            return False
        try:
            return model.query.first() is not None
        except Exception:
            return False

    if not _has_data(Role):
        roles = [
            Role(id=1, name='安环部人员', description='负责日常安全环保工作填报'),
            Role(id=2, name='安环部负责人', description='负责工作计划审核和隐患整改验收'),
            Role(id=3, name='分管副总', description='分管副总，监督安环部工作'),
            Role(id=4, name='总经理', description='总经理，查看全部统计数据')
        ]
        for r in roles:
            db.session.add(r)

    if not _has_data(Permission):
        perms = [
            Permission(code='dashboard.view', name='首页看板', module='看板', description='查看首页数据概览'),
            Permission(code='workplan.view', name='工作计划管理', module='计划', description='查看工作计划'),
            Permission(code='workplan.edit', name='工作计划编辑', module='计划', description='创建、编辑工作计划'),
            Permission(code='inspection.view', name='安全检查记录', module='检查', description='查看检查记录'),
            Permission(code='inspection.edit', name='安全检查编辑', module='检查', description='创建、编辑检查记录'),
            Permission(code='hazard.view', name='隐患台账', module='隐患', description='查看隐患台账'),
            Permission(code='hazard.edit', name='隐患编辑', module='隐患', description='登记、整改隐患'),
            Permission(code='permit.view', name='危险作业票', module='作业票', description='查看危险作业票'),
            Permission(code='permit.edit', name='危险作业票编辑', module='作业票', description='申请、审批作业票'),
            Permission(code='contractor.view', name='承包商档案', module='承包商', description='查看承包商信息'),
            Permission(code='contractor.edit', name='承包商编辑', module='承包商', description='维护承包商资质'),
            Permission(code='cost.view', name='安全投入台账', module='投入', description='查看安全投入'),
            Permission(code='cost.edit', name='安全投入编辑', module='投入', description='登记安全投入'),
            Permission(code='accident.view', name='事故记录', module='事故', description='查看事故记录'),
            Permission(code='accident.edit', name='事故记录编辑', module='事故', description='登记事故记录'),
            Permission(code='report.view', name='统计报表', module='报表', description='查看统计报表'),
            Permission(code='law.view', name='法律法规库', module='法规', description='查看法律法规'),
            Permission(code='law.edit', name='法律法规管理', module='法规', description='维护法律法规'),
            Permission(code='standard.view', name='检查标准库', module='标准', description='查看检查标准'),
            Permission(code='system.user', name='用户管理', module='系统', description='管理系统用户'),
            Permission(code='system.role', name='角色权限管理', module='系统', description='管理角色和权限'),
        ]
        for p in perms:
            db.session.add(p)

        db.session.flush()

        role_perms = {
            1: ['dashboard.view', 'workplan.view', 'workplan.edit',
                'inspection.view', 'inspection.edit',
                'hazard.view', 'hazard.edit',
                'permit.view', 'permit.edit',
                'contractor.view', 'cost.view', 'cost.edit',
                'accident.view', 'law.view', 'standard.view'],
            2: ['dashboard.view', 'workplan.view', 'workplan.edit',
                'inspection.view', 'inspection.edit',
                'hazard.view', 'hazard.edit',
                'permit.view', 'permit.edit',
                'contractor.view', 'contractor.edit',
                'cost.view', 'cost.edit',
                'accident.view', 'accident.edit',
                'report.view', 'law.view', 'standard.view',
                'system.user'],
            3: ['dashboard.view', 'workplan.view',
                'inspection.view', 'hazard.view',
                'permit.view', 'contractor.view',
                'cost.view', 'accident.view',
                'report.view', 'law.view', 'standard.view',
                'system.user', 'system.role'],
            4: ['dashboard.view', 'workplan.view',
                'inspection.view', 'hazard.view',
                'permit.view', 'contractor.view',
                'cost.view', 'accident.view',
                'report.view', 'law.view', 'standard.view'],
        }
        for rid, codes in role_perms.items():
            role = Role.query.get(rid)
            if role:
                role.permissions = Permission.query.filter(Permission.code.in_(codes)).all()
        db.session.flush()

    if not _has_data(User):
        users = [
            User(username='admin', real_name='系统管理员', role_id=3, department='分管领导', phone='13800000001'),
            User(username='anhuabu', real_name='安环部张三', role_id=2, department='安环部', phone='13800000002'),
            User(username='staff', real_name='安环部李四', role_id=1, department='安环部', phone='13800000003'),
            User(username='ceo', real_name='总经理王五', role_id=4, department='公司领导', phone='13800000004')
        ]
        for u in users:
            u.set_password('123456')
            db.session.add(u)

    if not _has_data(CheckTemplate):
        templates = [
            CheckTemplate(category='作业安全', item='回转窑入口检查-落实安全措施',
                         standard='入窑前必须办理危险作业申请，与中控保持联系，确认预热器无堵料，锁紧翻板阀，挂"禁止合闸"警示牌，使用安全照明，专人监护',
                         law_basis='GB/T 33000-2016《企业安全生产标准化基本规范》', is_key=True),
            CheckTemplate(category='作业安全', item='预热器清堵作业安全控制',
                         standard='清堵作业前办理危险作业申请，穿戴防火隔热劳保用品，与中控联系，现场设安全管理人员监控，篦冷机和斜拉链区域禁止无关人员作业',
                         law_basis='《水泥企业安全生产标准化评定标准》作业安全条款', is_key=True),
            CheckTemplate(category='设备设施', item='带式输送机安全防护',
                         standard='输送机头部、尾部、拉紧部位、改向部位应设置防护装置；滚筒采用防护罩或防夹楔；托辊采用防护板',
                         law_basis='GB 14784-2013《带式输送机安全规范》第4.1条', is_key=True),
            CheckTemplate(category='设备设施', item='收尘设备运行状况',
                         standard='布袋除尘器定期更换滤袋，电除尘器定期检修维护极板、极丝、振打清灰装置，设备完好率≥95%',
                         law_basis='《水泥行业超低排放改造意见》有组织排放控制要求', is_key=True),
            CheckTemplate(category='设备设施', item='安全阀、压力表校验',
                         standard='安全阀、压力表、压力开关等安全附件应定期校验，确保在有效期内使用',
                         law_basis='《特种设备安全法》第二十五条', is_key=True),
            CheckTemplate(category='电气安全', item='变配电系统安全',
                         standard='变配电间门向外开，高压间门向低压间开，相邻配电间门双向开；电气设备接地良好',
                         law_basis='GB 50053-2013《20kV及以下变电所设计规范》', is_key=False),
            CheckTemplate(category='职业健康', item='职业危害因素监测',
                         standard='定期对粉尘、噪声等职业危害因素进行检测，检测结果在公示栏公布，超标点应有防护措施',
                         law_basis='《职业病防治法》第二十六条', is_key=True),
            CheckTemplate(category='应急管理', item='应急预案备案及演练',
                         standard='制定生产安全事故应急预案并报主管部门备案，每年至少组织1次综合或专项应急预案演练',
                         law_basis='《生产安全事故应急预案管理办法》第二十六条', is_key=True),
            CheckTemplate(category='环保管理', item='有组织排放达标情况',
                         standard='水泥窑颗粒物≤10mg/m³、SO₂≤35mg/m³、NOₓ≤50mg/m³；排放口在线监测装置正常运行',
                         law_basis='《水泥行业超低排放改造意见》及GB 4915-2013', is_key=True),
            CheckTemplate(category='环保管理', item='无组织排放控制',
                         standard='粉状物料密闭储存，皮带通廊封闭，各转载下料口设集气罩+除尘器，厂区无可见烟粉尘',
                         law_basis='《水泥行业超低排放改造意见》无组织排放措施', is_key=True),
            CheckTemplate(category='环保管理', item='噪声排放达标',
                         standard='厂界昼间≤65dB(A)，夜间≤55dB(A)，优先选用低噪声设备，高噪声设备合理布置',
                         law_basis='GB 12348-2008《工业企业厂界环境噪声排放标准》', is_key=False),
            CheckTemplate(category='教育培训', item='新员工三级安全教育',
                         standard='新入厂人员必须经过厂级、车间级、班组级三级安全教育培训，考核合格后方可上岗',
                         law_basis='《安全生产法》第二十八条', is_key=True),
            CheckTemplate(category='教育培训', item='特种作业人员持证上岗',
                         standard='特种作业人员应取得特种作业操作资格证书，证书定期审核，保持有效',
                         law_basis='《特种作业人员安全技术培训考核管理规定》', is_key=True),
            CheckTemplate(category='重大危险源', item='重大危险源建档及监控',
                         standard='重大危险源应登记建档，进行定期检测、评估、监控，制定应急预案，告知从业人员和相关人员',
                         law_basis='《安全生产法》第四十条', is_key=True),
            CheckTemplate(category='隐患排查', item='定期开展隐患排查治理',
                         standard='建立隐患排查治理制度，采取技术、管理措施及时发现消除事故隐患，排查治理情况如实记录并通报',
                         law_basis='《安全生产法》第四十一条第二款', is_key=True),
            CheckTemplate(category='安全投入', item='安全生产费用提取使用',
                         standard='按规定足额提取安全生产费用，建立安全费用使用台账，专项用于安全投入',
                         law_basis='《企业安全生产费用提取和使用管理办法》财企〔2012〕16号', is_key=True),
        ]
        for t in templates:
            db.session.add(t)

    if not _has_data(WorkPlan):
        sample_plans = [
            WorkPlan(title='年度安全生产目标制定与分解', category='安全生产目标', type='年度',
                    plan_year=2026, content='制定2026年度安全生产目标（死亡事故为零、重伤事故≤2起、隐患整改率≥98%、员工培训覆盖率100%），分解到各部门和车间，制定实施计划和考核办法',
                    law_basis='GB/T 33000-2016《企业安全生产标准化基本规范》/ 水泥标准化1.1目标',
                    responsible='安环部负责人', deadline=date(2026, 1, 31), progress=100, status='completed',
                    completion_date=date(2026, 1, 25)),
            WorkPlan(title='月度安全生产例会召开', category='组织机构', type='月度',
                    plan_year=2026, plan_month=8, content='组织召开8月份安全生产例会，传达上级安全生产文件精神，通报上月安全情况，布置本月安全工作',
                    law_basis='水泥标准化2.1组织机构和人员',
                    responsible='安环部负责人', deadline=date(2026, 8, 20), progress=80, status='in_progress'),
            WorkPlan(title='新员工三级安全教育培训', category='教育培训', type='月度',
                    plan_year=2026, plan_month=8, content='对8月新入厂员工进行厂级、车间级、班组级三级安全教育培训，考核合格后颁发上岗证',
                    law_basis='《安全生产法》第二十八条 / 水泥标准化5.教育培训',
                    responsible='安环部人员', deadline=date(2026, 8, 31), progress=50, status='in_progress'),
            WorkPlan(title='回转窑、预热器专项安全检查', category='设备设施', type='月度',
                    plan_year=2026, plan_month=8, content='对回转窑传动装置防护罩、预热器翻板阀锁紧装置、篦冷机安全防护设施进行专项检查，发现隐患及时整改',
                    law_basis='《水泥企业安全生产标准化评定标准》6.生产设备设施',
                    responsible='安环部人员', deadline=date(2026, 8, 25), progress=0, status='pending'),
            WorkPlan(title='收尘设备运行维护巡检', category='环保管理', type='月度',
                    plan_year=2026, plan_month=8, content='对窑尾布袋除尘器、窑头电袋复合除尘器、各库顶除尘器进行巡检，检查滤袋磨损情况、极板极丝完好性，确保排放达标',
                    law_basis='《水泥行业超低排放改造意见》有组织排放控制',
                    responsible='设备部+安环部', deadline=date(2026, 8, 31), progress=30, status='in_progress'),
            WorkPlan(title='职业危害因素检测与公告', category='职业健康', type='季度',
                    plan_year=2026, content='组织第三方检测机构对各作业场所粉尘、噪声浓度进行检测，检测结果在职业危害告知栏公告，对超标场所制定防护措施',
                    law_basis='《职业病防治法》第二十六条',
                    responsible='安环部', deadline=date(2026, 9, 30), progress=20, status='in_progress'),
            WorkPlan(title='应急预案修订与备案', category='应急管理', type='年度',
                    plan_year=2026, content='根据最新法律法规和企业实际情况，修订生产安全事故综合应急预案、专项应急预案和现场处置方案，报属地应急管理部门备案',
                    law_basis='《生产安全事故应急预案管理办法》第二十六条',
                    responsible='安环部负责人', deadline=date(2026, 10, 31), progress=0, status='pending'),
            WorkPlan(title='特种作业人员资质排查', category='作业安全', type='月度',
                    plan_year=2026, plan_month=8, content='对全厂特种作业人员（电工、焊工、高处作业、压力容器等）资质进行排查，建立台账，督促证书到期人员及时复审换证',
                    law_basis='《特种作业人员安全技术培训考核管理规定》',
                    responsible='安环部+人力资源部', deadline=date(2026, 8, 31), progress=60, status='in_progress'),
            WorkPlan(title='安全生产费用提取使用统计', category='安全投入', type='月度',
                    plan_year=2026, plan_month=8, content='统计8月份安全生产费用提取和使用情况，建立安全费用台账，确保专项专用，符合《企业安全生产费用提取和使用管理办法》要求',
                    law_basis='财企〔2012〕16号《企业安全生产费用提取和使用管理办法》',
                    responsible='安环部+财务部', deadline=date(2026, 9, 5), progress=10, status='pending'),
        ]
        for p in sample_plans:
            db.session.add(p)

    if not _has_data(Inspection):
        insp1 = Inspection(title='8月回转窑系统专项安全检查', inspect_type='专项检查',
                           inspect_date=date(2026, 8, 10), location='回转窑车间',
                           inspector='安环部张三',
                           check_list='1.回转窑传动装置防护罩完好性\n2.预热器翻板阀锁紧装置\n3.篦冷机安全防护设施\n4.窑尾密封装置\n5.中控报警系统测试',
                           result='不合格', remark='发现3项隐患，已下达整改通知书')
        insp2 = Inspection(title='收尘设备日常巡检', inspect_type='日常检查',
                           inspect_date=date(2026, 8, 12), location='窑尾、窑头、库顶',
                           inspector='安环部李四',
                           check_list='1.窑尾布袋除尘器运行参数\n2.窑头电袋复合除尘器\n3.各库顶单机除尘器\n4.在线监测数据比对',
                           result='合格', remark='排放数据正常，设备运行稳定')
        insp3 = Inspection(title='电气系统安全检查', inspect_type='季节性检查',
                           inspect_date=date(2026, 8, 5), location='总降压站、各配电室',
                           inspector='安环部张三+电工班',
                           check_list='1.变配电系统接地电阻\n2.绝缘工具有效期\n3.配电柜温升检查\n4.电缆桥架防火封堵\n5.应急照明系统',
                           result='不合格', remark='发现配电室通风不良，需加装排风装置')
        db.session.add_all([insp1, insp2, insp3])
        db.session.flush()

        hz1 = Hazard(check_date=date(2026, 8, 10), title='回转窑传动皮带防护罩缺失',
                     description='回转窑主传动皮带轮防护罩变形缺失，人员靠近旋转部位有卷入风险',
                     level='major', location='回转窑主传动', source='专项检查',
                     law_basis='GB 14784-2013《带式输送机安全规范》4.1条',
                     rectify_measure='更换新防护罩，加警示标识',
                     responsible='设备部王工', deadline=date(2026, 8, 25),
                     rectify_progress=80, status='rectifying')
        hz2 = Hazard(check_date=date(2026, 8, 10), title='预热器C3翻板阀未完全锁紧',
                     description='预热器C3翻板阀锁紧装置失灵，存在误操作风险',
                     level='general', location='预热器C3', source='专项检查',
                     law_basis='水泥企业安全生产标准化评定标准',
                     rectify_measure='更换锁紧装置，加挂"禁止操作"警示牌',
                     responsible='设备部李工', deadline=date(2026, 8, 18),
                     rectify_progress=100, status='rectified',
                     rectify_date=date(2026, 8, 17))
        hz3 = Hazard(check_date=date(2026, 8, 5), title='配电室通风不良温度超标',
                     description='生料磨配电室温度达38℃，超过规定的35℃上限，可能影响电气设备绝缘',
                     level='general', location='生料磨配电室', source='季节性检查',
                     law_basis='GB 50053-2013《20kV及以下变电所设计规范》',
                     rectify_measure='加装轴流风机排风，增设温度监控报警',
                     responsible='电气班张班长', deadline=date(2026, 8, 22),
                     rectify_progress=30, status='rectifying')
        hz4 = Hazard(check_date=date(2026, 7, 20), title='布袋除尘器滤袋磨损超标',
                     description='窑尾除尘器5#室滤袋磨损率达15%，超过10%的控制指标',
                     level='major', location='窑尾布袋除尘器5#室', source='日常检查',
                     law_basis='《水泥行业超低排放改造意见》有组织排放控制',
                     rectify_measure='更换全部5#室滤袋，加强运行监控',
                     responsible='设备部+除尘班组', deadline=date(2026, 8, 8),
                     rectify_progress=100, status='closed',
                     rectify_date=date(2026, 8, 5), acceptor='安环部负责人',
                     accept_date=date(2026, 8, 7), accept_result='通过')
        hz5 = Hazard(check_date=date(2026, 7, 28), title='高处作业平台防护栏杆松动',
                     description='生料库顶巡检平台防护栏杆多处松动，高度不足1.2m',
                     level='major', location='生料库顶', source='日常检查',
                     law_basis='GB 2894-2008《安全标志及其使用导则》+水泥标准化作业安全',
                     rectify_measure='加固栏杆，补焊加高到1.2m以上',
                     responsible='维修班赵班长', deadline=date(2026, 8, 5),
                     rectify_progress=100, status='closed',
                     rectify_date=date(2026, 8, 4), acceptor='安环部负责人',
                     accept_date=date(2026, 8, 5), accept_result='通过')
        hz6 = Hazard(check_date=date(2026, 8, 12), title='在线监测数据异常偏差',
                     description='NOx在线监测数据与CEMS比对偏差超过20%，需校准',
                     level='general', location='窑尾排放口CEMS', source='日常检查',
                     law_basis='《水泥行业超低排放改造意见》在线监测要求',
                     rectify_measure='联系计量检定机构校准，重新比对',
                     responsible='安环部+环保班组', deadline=date(2026, 9, 1),
                     rectify_progress=0, status='pending')
        db.session.add_all([hz1, hz2, hz3, hz4, hz5, hz6])

    db.session.commit()


if __name__ == '__main__':
    print('=' * 60)
    print('  水泥企业安全环保工作监督系统 启动中...')
    app = init_db()
    print('  访问地址: http://localhost:5000')
    print('  默认账号: admin / 123456  (分管副总)')
    print('            anhuabu / 123456  (安环部负责人)')
    print('=' * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
