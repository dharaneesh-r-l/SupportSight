import pytest
from app.models.scan import Scan
from app.services.scan_service import ScanService
from app import db


def test_auth_routes(client, app, test_user):
    # GET login page
    res = client.get('/auth/login')
    assert res.status_code == 200
    assert b'Login' in res.data or b'login' in res.data

    # POST login success
    res = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'TestPassword123!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Dashboard' in res.data or b'dashboard' in res.data

    # GET profile
    res = client.get('/auth/profile')
    assert res.status_code == 200

    # GET change password
    res = client.get('/auth/change-password')
    assert res.status_code == 200

    # POST change password
    res = client.post('/auth/change-password', data={
        'current_password': 'TestPassword123!',
        'new_password': 'NewPassword123!',
        'confirm_password': 'NewPassword123!'
    }, follow_redirects=True)
    assert res.status_code == 200

    # GET logout
    res = client.get('/auth/logout', follow_redirects=True)
    assert res.status_code == 200

    # Registration route
    res = client.get('/auth/register')
    assert res.status_code == 200

    res = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'NewPassword123!',
        'confirm_password': 'NewPassword123!',
        'first_name': 'New',
        'last_name': 'User'
    }, follow_redirects=True)
    assert res.status_code == 200


def test_dashboard_routes(auth_client, app, test_user):
    res = auth_client.get('/')
    assert res.status_code == 302

    res = auth_client.get('/dashboard')
    assert res.status_code == 200

    res = auth_client.get('/home')
    assert res.status_code == 200

    res = auth_client.get('/diagnostics')
    assert res.status_code == 200

    res = auth_client.get('/scan-history')
    assert res.status_code == 200

    # Run quick scan route
    res = auth_client.get('/quick-scan', follow_redirects=True)
    assert res.status_code == 200

    # View scan result
    with app.app_context():
        scan = Scan.query.filter_by(user_id=test_user.id).first()
        assert scan is not None
        scan_id = scan.id

    res = auth_client.get(f'/scan/{scan_id}')
    assert res.status_code == 200


def test_diagnostics_routes(auth_client):
    routes = [
        '/diagnostics/cpu',
        '/diagnostics/ram',
        '/diagnostics/disk',
        '/diagnostics/network',
        '/diagnostics/battery',
        '/diagnostics/processes',
        '/diagnostics/system'
    ]
    for route in routes:
        res = auth_client.get(route)
        assert res.status_code == 200, f"Route {route} returned status {res.status_code}"


def test_api_routes(auth_client, app, test_user):
    # POST new scan via API first to ensure user has a scan
    res = auth_client.post('/api/scan')
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data['success'] is True
    scan_id = json_data['scan_id']

    endpoints = [
        '/api/system',
        '/api/cpu',
        '/api/cpu/history',
        '/api/ram',
        '/api/ram/history',
        '/api/disk',
        '/api/network',
        '/api/network/ping?host=127.0.0.1&count=1',
        '/api/battery',
        '/api/processes',
        '/api/health',
        '/api/status'
    ]
    for ep in endpoints:
        res = auth_client.get(ep)
        assert res.status_code == 200, f"API {ep} failed with {res.status_code}"

    # GET scan details via API
    res = auth_client.get(f'/api/scan/{scan_id}')
    assert res.status_code == 200

    # GET scan component
    res = auth_client.get(f'/api/scan/{scan_id}/component/cpu')
    assert res.status_code == 200

    # GET scan history API
    res = auth_client.get('/api/scans')
    assert res.status_code == 200

    # GET latest scan API
    res = auth_client.get('/api/scans/latest')
    assert res.status_code == 200

    # Export scan API
    res = auth_client.get(f'/api/export/{scan_id}')
    assert res.status_code == 200


def test_reports_routes(auth_client, app, test_user):
    # Run scan first
    with app.app_context():
        scan = ScanService.run_full_scan(test_user.id)
        scan_id = scan.id

    res = auth_client.get(f'/reports/report/{scan_id}')
    assert res.status_code == 200

    res = auth_client.get('/reports/reports')
    assert res.status_code == 200

    # Download report
    res = auth_client.get(f'/reports/report/{scan_id}/download')
    assert res.status_code == 200
    assert res.headers['Content-Type'] == 'application/pdf'
