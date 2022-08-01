from conftests import *


def test_model(user):
    assert user.name == 'Testuser'


def test_user_login(user, client):
    res = client.post('/login', json={
        'email': user.email,
        'password': 'password'
    })
    assert res.status_code == 200
    assert res.get_json().get('access_token')


def test_user_reg(client):
    res = client.post('/register', json={
        'name': 'Testuser',
        'email': 'test@test.ru',
        'password': 'password'
    })
    assert res.status_code == 200
    assert res.get_json().get('access_token')