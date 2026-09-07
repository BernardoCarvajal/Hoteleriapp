"""Regression checks for authentication and the security dependency upgrade."""
import os
from datetime import timedelta
from io import BytesIO

os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['SECRET_KEY'] = 'test-only-secret-key-at-least-thirty-two-bytes'

import jwt
import pytest
import qrcode
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from werkzeug.security import generate_password_hash

from app.api import create_app
from app.database import Base, get_db
from app.models.user_orm import RoleORM, UserORM
from app.routers import usuarios


@pytest.fixture
def client():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine)
    with sessions() as db:
        role = RoleORM(nombre='cliente')
        db.add(UserORM(id=1, nombre='Test', apellido='User', email='test@example.com',
                       password_hash=generate_password_hash('Test-password-123', method='pbkdf2:sha256:600000'),
                       es_activo=True, roles=[role]))
        db.add(RoleORM(nombre='empleado'))
        db.add(UserORM(id=2, nombre='Test', apellido='Admin', email='owner@example.com',
                       password_hash=generate_password_hash('Test-password-123'),
                       es_activo=True, roles=[RoleORM(nombre='admin')]))
        db.commit()
    def test_db():
        with sessions() as db:
            yield db
    app = create_app()
    app.dependency_overrides[get_db] = test_db
    with TestClient(app) as test_client:
        yield test_client
    engine.dispose()


def test_login_and_profile_with_existing_password_hash(client):
    response = client.post('/api/usuarios/login', json={'email': 'test@example.com', 'password': 'Test-password-123'})
    assert response.status_code == 200
    token = response.json()['access_token']
    profile = client.get('/api/usuarios/perfil', headers={'Authorization': f'Bearer {token}'})
    assert profile.status_code == 200
    assert profile.json()['email'] == 'test@example.com'
    assert client.post('/api/usuarios/login', json={'email': 'test@example.com', 'password': 'Wrong-password'}).status_code == 401


@pytest.mark.parametrize('kind', ['expired', 'wrong-signature', 'missing-sub', 'unsigned', 'malformed'])
def test_reject_invalid_tokens(client, kind):
    if kind == 'expired':
        token = usuarios.crear_token_acceso({'sub': '1'}, timedelta(minutes=-1))
    elif kind == 'wrong-signature':
        token = jwt.encode({'sub': '1'}, 'different-test-secret-at-least-32-bytes', algorithm='HS256')
    elif kind == 'missing-sub':
        token = usuarios.crear_token_acceso({})
    elif kind == 'unsigned':
        token = jwt.encode({'sub': '1'}, None, algorithm='none')
    else:
        token = 'not-a-jwt'
    assert client.get('/api/usuarios/perfil', headers={'Authorization': f'Bearer {token}'}).status_code == 401


@pytest.mark.parametrize('path,body', [
    ('/api/usuarios/admin', {'nombre': 'Test', 'apellido': 'Admin', 'email': 'admin@example.com', 'password': 'Test-password-123'}),
    ('/api/usuarios/empleados', {'nombre': 'Test', 'apellido': 'Staff', 'email': 'staff@example.com', 'password': 'Test-password-123'}),
    ('/api/usuarios/1/roles', [1]),
])
def test_privileged_operations_require_admin(client, path, body):
    method = 'PUT' if path.endswith('/roles') else 'POST'
    assert client.request(method, path, json=body).status_code in (401, 403)
    token = usuarios.crear_token_acceso({'sub': '1'})
    assert client.request(method, path, json=body, headers={'Authorization': f'Bearer {token}'}).status_code == 403
    admin_token = usuarios.crear_token_acceso({'sub': '2'})
    response = client.request(method, path, json=body, headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == (200 if method == 'PUT' else 201)


def test_api_schema_and_health(client):
    assert client.get('/health').json() == {'status': 'ok'}
    schema = client.get('/openapi.json')
    assert schema.status_code == 200
    assert '/api/usuarios/login' in schema.json()['paths']


def test_qr_png_roundtrip():
    output = BytesIO()
    qrcode.make('reservation-test-123').save(output, 'PNG')
    output.seek(0)
    with Image.open(output) as image:
        assert image.format == 'PNG'
        image.verify()
