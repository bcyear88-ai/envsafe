# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import create_app
from models import db, WorkPermit, SafetyCost, Accident, Contractor
from datetime import date, datetime

app = create_app()

def seed():
    with app.app_context():
        print('=' * 60)
        print('  导入二级模块种子数据')
        print('=' * 60)

        # === WorkPermit ===
        permits = [
            dict(permit_no='WP-20260801001', permit_type='动火作业', risk_level='一级',
                 work_location='煤粉制备系统煤磨机入口',
                 work_content='煤磨外壳保温层修复焊接作业',
                 contractor='安徽XX建设工程有限公司', workers=3,
                 work_personnel='张三(焊工), 李四(辅助), 王五(监护)',
                 gas_test='O2:20.9%, CO:3ppm, LEL:5%',
                 safety_measures='1.停机断电挂牌；2.煤粉清理干净；3.配备2具干粉灭火器；4.监护人员全程监护',
                 permit_holder='张三', guardian='安环部-陈强', approver='分管副总-李明',
                 apply_date=date(2026, 8, 1),
                 start_time=datetime(2026, 8, 2, 8, 0),
                 end_time=datetime(2026, 8, 2, 17, 0), status='completed'),
            dict(permit_no='WP-20260815001', permit_type='有限空间作业', risk_level='一级',
                 work_location='1号水泥库内部（清理下料口结壁）',
                 work_content='水泥库下料口结壁清理，需进入库内作业',
                 contractor='北京XX机械有限公司（机械清库）', workers=4,
                 work_personnel='赵六(机操), 孙七(辅助), 周八(监护), 吴九(气体检测)',
                 gas_test='O2:20.7%, CO:5ppm, H2S:未检出, LEL:3%',
                 safety_measures='1.卸料口封闭挂牌；2.机械通风30min；3.气体检测合格；4.生命绳挂设独立锚点；5.监护人员全程监控生命绳；6.配备救援三脚架和空气呼吸器',
                 permit_holder='赵六', guardian='安环部-陈强', approver='分管副总-李明',
                 apply_date=date(2026, 8, 15),
                 start_time=datetime(2026, 8, 16, 7, 30),
                 end_time=datetime(2026, 8, 16, 16, 30), status='in_progress'),
            dict(permit_no='WP-20260816001', permit_type='高处作业', risk_level='二级',
                 work_location='窑尾预热器C3旋风筒检修平台',
                 work_content='预热器内衬砖修补作业，作业高度约35米',
                 contractor='山东XX耐火材料有限公司', workers=2,
                 work_personnel='郑十(砖工), 刘一(辅助)',
                 gas_test='O2:20.8%, CO:8ppm',
                 safety_measures='1.佩戴全身式安全带，双钩挂在独立锚点；2.作业平台搭设脚手板；3.设置警示标识；4.下方禁止无关人员通行',
                 permit_holder='郑十', guardian='安环部-张伟', approver='安环部长-王磊',
                 apply_date=date(2026, 8, 16),
                 start_time=datetime(2026, 8, 17, 8, 0),
                 end_time=datetime(2026, 8, 17, 17, 0), status='approved'),
        ]
        added = 0
        existing = {p.permit_no for p in WorkPermit.query.all()}
        for item in permits:
            if item['permit_no'] in existing:
                continue
            db.session.add(WorkPermit(**item)); added += 1
        db.session.commit()
        print(f'  ✅ WorkPermit: +{added} 条，合计 {WorkPermit.query.count()} 条')

        # === SafetyCost ===
        costs = [
            dict(item='三级安全教育培训（新员工5人）', category='教育培训', amount=12500,
                 occur_date=date(2026, 1, 15), payer='安环部', voucher_no='PZ-20260115001'),
            dict(item='特种作业人员复审（电工3人、焊工2人）', category='教育培训', amount=8600,
                 occur_date=date(2026, 3, 20), payer='安环部', voucher_no='PZ-20260320001'),
            dict(item='安全帽100顶 + 安全带30条', category='防护用品', amount=15200,
                 occur_date=date(2026, 2, 28), payer='采购部', voucher_no='PZ-20260228003'),
            dict(item='有限空间救援装备（三脚架+空气呼吸器）', category='应急演练', amount=28800,
                 occur_date=date(2026, 4, 10), payer='安环部', voucher_no='PZ-20260410001'),
            dict(item='收尘系统火花探测器更换', category='隐患整改', amount=35000,
                 occur_date=date(2026, 5, 5), payer='设备部', voucher_no='PZ-20260505002'),
            dict(item='职业健康体检（接触粉尘120人）', category='职业健康', amount=48000,
                 occur_date=date(2026, 6, 1), payer='安环部', voucher_no='PZ-20260601001'),
            dict(item='防雷接地年度检测', category='检测检验', amount=9600,
                 occur_date=date(2026, 6, 20), payer='安环部', voucher_no='PZ-20260620001'),
            dict(item='年度应急预案综合演练', category='应急演练', amount=15000,
                 occur_date=date(2026, 7, 10), payer='安环部', voucher_no='PZ-20260710001'),
        ]
        added = 0
        for item in costs:
            key = (item['item'], item['occur_date'])
            existing_keys = {(c.item, c.occur_date) for c in SafetyCost.query.all()}
            if key in existing_keys: continue
            db.session.add(SafetyCost(**item)); added += 1
        db.session.commit()
        print(f'  ✅ SafetyCost: +{added} 条，合计 {SafetyCost.query.count()} 条')
        total = sum(c.amount or 0 for c in SafetyCost.query.all())
        print(f'     累计投入：¥{total:,.2f}')

        # === Accident ===
        accidents = [
            dict(accident_no='AC-20260315001', level='一般事故', type='机械伤害',
                 location='包装车间1号皮带机',
                 time=datetime(2026, 3, 15, 14, 30),
                 deaths=0, injuries=1, direct_loss=50000,
                 brief='包装工张某在清理皮带机滚轮积料时，违规用手清理，被运转中的滚轮卷入左臂，造成左前臂骨折',
                 cause_analysis='1.张某违章作业，未停机处理；2.皮带机缺少滚轮防护盖板；3.班长现场监督不到位；4.安全教育培训不到位',
                 rectify_measures='1.对全厂皮带机加装滚轮防护装置；2.组织全厂违章作业专项整治；3.对张某进行批评教育并重新培训；4.对班长给予处罚；5.完善停机挂牌制度',
                 responsible='包装车间-主任刘XX', report_status='closed',
                 report_date=date(2026, 3, 16)),
            dict(accident_no='AC-20260520001', level='轻微事故', type='灼烫',
                 location='回转窑窑头看火平台',
                 time=datetime(2026, 5, 20, 10, 15),
                 deaths=0, injuries=1, direct_loss=8000,
                 brief='看火工王某在观察窑内燃烧情况时，被突然喷出的火焰灼伤面部（浅二度）',
                 cause_analysis='1.窑内压力波动导致正压喷料；2.看火工观察时未佩戴防护面罩；3.看火门密封不严',
                 rectify_measures='1.所有看火工佩戴防护面罩；2.检修看火门密封；3.加强窑系统压力监控报警；4.修订看火安全操作规程',
                 responsible='烧成车间-主任陈XX', report_status='closed',
                 report_date=date(2026, 5, 21)),
            dict(accident_no='AC-20260708001', level='未遂事故', type='中毒窒息',
                 location='预热器分解炉内部检修',
                 time=datetime(2026, 7, 8, 9, 0),
                 deaths=0, injuries=0, direct_loss=0,
                 brief='外包检修人员进入分解炉作业后约20分钟，监护人员发现其有头晕恶心症状，立即叫停作业并撤离，经检测CO浓度达58ppm（正常应<24ppm）',
                 cause_analysis='1.通风置换时间不足（原计划30min实际仅20min）；2.气体检测点设置不足（只测了1点未测上下部）；3.作业中未持续通风',
                 rectify_measures='1.修订有限空间作业审批流程，增加"签字确认通风时间"环节；2.气体检测至少3点（上中下）；3.作业中必须持续通风；4.对外包监护人员重新培训考核',
                 responsible='分管副总-李明', report_status='investigated',
                 report_date=date(2026, 7, 10)),
        ]
        added = 0
        for item in accidents:
            if Accident.query.filter_by(accident_no=item['accident_no']).first(): continue
            db.session.add(Accident(**item)); added += 1
        db.session.commit()
        print(f'  ✅ Accident: +{added} 条，合计 {Accident.query.count()} 条')

        # === Contractor ===
        contractors = [
            dict(name='安徽XX建设工程有限公司', contact='王经理', phone='139-5555-0001',
                 business_scope='水泥生产线土建工程、设备安装',
                 has_safety_license=True, safety_license_no='（皖）JZ安许证字[2024]001234',
                 safety_license_expire=date(2027, 5, 15),
                 qualification='建筑工程施工总承包贰级',
                 last_3y_accidents='近3年无较大以上事故，2024年发生1起轻伤',
                 special_workers_count=25, workers_count=120,
                 enter_date=date(2026, 1, 1), expire_date=date(2026, 12, 31),
                 safety_agreement=True, safety_trained=True,
                 status='active', performance_score=92),
            dict(name='山东XX耐火材料有限公司', contact='李总监', phone='138-6666-0002',
                 business_scope='回转窑耐火材料砌筑、预热器内衬修补',
                 has_safety_license=True, safety_license_no='（鲁）JZ安许证字[2024]005678',
                 safety_license_expire=date(2027, 8, 20),
                 qualification='冶金工程专业承包壹级',
                 last_3y_accidents='近3年无生产安全事故',
                 special_workers_count=18, workers_count=85,
                 enter_date=date(2026, 3, 1), expire_date=date(2026, 11, 30),
                 safety_agreement=True, safety_trained=True,
                 status='active', performance_score=88),
            dict(name='北京XX机械清库有限公司', contact='赵主任', phone='137-7777-0003',
                 business_scope='水泥筒型储存库机械清库、均化库清理',
                 has_safety_license=True, safety_license_no='（京）JZ安许证字[2025]003456',
                 safety_license_expire=date(2028, 2, 28),
                 qualification='特种设备安装改造维修',
                 last_3y_accidents='近3年无生产安全事故',
                 special_workers_count=12, workers_count=45,
                 enter_date=date(2026, 6, 15), expire_date=date(2027, 6, 14),
                 safety_agreement=True, safety_trained=True,
                 status='active', performance_score=95),
            dict(name='河南XX机电设备安装公司', contact='钱经理', phone='136-8888-0004',
                 business_scope='余热发电设备检修、电气仪表安装',
                 has_safety_license=False, safety_license_no='',
                 safety_license_expire=None,
                 qualification='机电工程施工总承包叁级',
                 last_3y_accidents='2024年1起一般高处坠落事故（已结案）',
                 special_workers_count=8, workers_count=30,
                 enter_date=date(2026, 8, 1), expire_date=date(2026, 10, 31),
                 safety_agreement=True, safety_trained=False,
                 status='pending', performance_score=72,
                 remark='正在补办安全生产许可证，期间仅限承包低风险辅助作业'),
        ]
        added = 0
        for item in contractors:
            if Contractor.query.filter_by(name=item['name']).first(): continue
            db.session.add(Contractor(**item)); added += 1
        db.session.commit()
        print(f'  ✅ Contractor: +{added} 条，合计 {Contractor.query.count()} 条')

        print('=' * 60)
        print('  种子数据导入完成！')
        print('=' * 60)

if __name__ == '__main__':
    seed()
