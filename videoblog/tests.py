from . import client


def test_simple():
    mylist = [1, 2, 3, 4, 5]

    assert 1 in mylist


def test_get():
    res = client.get('/tutorials')

    assert res.status_code == 200
    assert len(res.get_json()) == 2
    assert res.get_json()[0]['id'] == 1


def test_post():
    data = {
        'id': 3,
        'title': 'Unit Tests',
        'description': 'Pytest tutorial'
    }

    res = client.post('/tutorials', json=data)

    assert res.status_code == 200

    assert len(res.get_json()) == 3
    assert res.get_json()[-1]['title'] == data['title']
