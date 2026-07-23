import pytest
from app.models.user import User
from app.models.scan import Scan
from app.models.recommendation import Recommendation
from app import db


def test_user_creation_and_password(app):
    with app.app_context():
        user = User(
            username='john_doe',
            email='john@example.com',
            first_name='John',
            last_name='Doe'
        )
        user.set_password('SecretPass123!')
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.check_password('SecretPass123!') is True
        assert user.check_password('WrongPass') is False
        assert user.full_name == 'John Doe'
        assert user.is_active is True
        assert user.role == 'user'

        user_dict = user.to_dict()
        assert user_dict['username'] == 'john_doe'
        assert 'password_hash' not in user_dict


def test_scan_model(app, test_user):
    with app.app_context():
        scan = Scan(
            user_id=test_user.id,
            status='in_progress'
        )
        db.session.add(scan)
        db.session.commit()

        assert scan.id is not None
        assert scan.status == 'in_progress'

        scan.set_data('system_info', {'os': 'Windows 11'})
        scan.set_data('cpu_data', {'usage': 15.2})
        scan.set_data('ram_data', {'usage': 45.0})
        scan.set_data('disk_data', {'usage': 60.0})
        scan.set_data('network_data', {'connected': True})
        scan.set_data('battery_data', {'percent': 100})
        scan.set_data('process_data', {'count': 120})
        scan.mark_completed(health_score=88)
        db.session.commit()

        assert scan.status == 'completed'
        assert scan.health_score == 88
        assert scan.health_category == 'Excellent'
        assert scan.duration is not None

        sys_data = scan.get_data('system_info')
        assert sys_data['os'] == 'Windows 11'

        scan_dict = scan.to_dict()
        assert scan_dict['health_score'] == 88
        assert scan_dict['status'] == 'completed'


def test_recommendation_model(app, test_user):
    with app.app_context():
        scan = Scan(user_id=test_user.id, status='completed', health_score=50)
        db.session.add(scan)
        db.session.commit()

        rec = Recommendation(
            scan_id=scan.id,
            component='ram',
            severity='warning',
            title='High Memory Usage',
            description='RAM usage exceeds 90%',
            action_items=['Close background applications', 'Restart system']
        )
        db.session.add(rec)
        db.session.commit()

        assert rec.id is not None
        assert rec.scan_id == scan.id
        assert len(rec.get_action_items()) == 2

        rec_dict = rec.to_dict()
        assert rec_dict['component'] == 'ram'
        assert rec_dict['severity'] == 'warning'

