from conftests import *


def test_list(video,  client, user_headers):
    res = client.get('/tutorials', headers=user_headers)

    assert res.status_code == 200
    assert len(res.get_json()) == 1

    assert res.get_json()[0] == {
        'description': 'Описание',
        'id': 1,
        'name': 'Видео 1',
        'user_id': 1
    }


def test_new_video(user, client, user_headers):
    res = client.post('/tutorials', json={
        'description': 'Описание',
        'name': 'Видео 1'
    }, headers=user_headers)
    assert res.status_code == 200
    assert res.get_json()['name'] == 'Видео 1'
    assert res.get_json()['description'] == 'Описание'
    assert res.get_json()['user_id'] == user.id


def test_edit_video(video, client, user_headers):
    res = client.put(f'/tutorials/{video.id}',
                     json={'name': 'Видео upd',
                           'description': 'Описание upd'},
                     headers=user_headers)
    assert res.status_code == 200
    assert res.get_json()['name'] == 'Видео upd'
    assert res.get_json()['description'] == 'Описание upd'


def test_delete_video(video, client, user_headers):
    res = client.delete(
        f'/tutorials/{video.id}',
        headers=user_headers
    )
    assert res.status_code == 204
