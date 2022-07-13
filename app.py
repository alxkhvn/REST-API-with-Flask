from flask import Flask, jsonify, request  # imported Flask class
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity  # libs for authentication
from config import Config
# from apispec.ext.marshmallow import MarshmallowPlugin  # for apispec and marshmallow work together
# from apispec import APISpec  # for apispec and flask app work together
# from flask_apispec.extension import FlaskApiSpec  # helps to create swagger docs for every route of app

app = Flask(__name__)
app.config.from_object(Config)  # даём доступ к secret key

client = app.test_client()  # тестовый клиент flask

engine = create_engine('sqlite:///db.sqlite')  # Создаём привязку к базе

session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))


Base = declarative_base()  # базовый класс для описание моделей данных
Base.query = session.query_property()

jwt = JWTManager(app)

# docs = FlaskApiSpec()
#
# docs.init_app(app)
#
# app.config.update({
#     'APISPEC_SPEC': APISpec(
#         title='videoblog',
#         version='v1',
#         openapi_version='2.0',
#         plugins=[MarshmallowPlugin()],
#     ),
#     'APISPEC_SWAGGER_URL': '/swagger/'
# })

from models import *

Base.metadata.create_all(bind=engine)  # Создаёт схему базы данных в в базе


@app.route('/tutorials', methods=['GET'])  # route() decorator tells Flask what URL should trigger our function
@jwt_required()  # данный декоратор даёт доступ к роуту только авторизованным пользователям(неавт-ный юзер получит 401)
def get_list():
    user_id = get_jwt_identity()
    videos = Video.query.filter(Video.user_id == user_id)  # возвращяем данные только этого пользователя
    serialized = []
    for video in videos:
        serialized.append({
            'id': video.id,
            'name': video.name,
            'description': video.description
        })

    return jsonify(serialized)


@app.route('/tutorials', methods=['POST'])
@jwt_required()
def update_list():
    user_id = get_jwt_identity()  # извлекает из токена поле identity и получает доступ к userid
    new_one = Video(user_id=user_id, **request.json)
    session.add(new_one)
    session.commit()
    serialized = {
        'id': new_one.id,
        'user_id': new_one.user_id,
        'name': new_one.name,
        'description': new_one.description
    }
    return jsonify(serialized)


@app.route('/tutorials/<int:tutorial_id>', methods=['PUT'])
@jwt_required()
def update_tutorial(tutorial_id):
    user_id = get_jwt_identity()
    # только пользователь указанный в user_id может совершать операции с данной записью
    item = Video.query.filter(Video.id == tutorial_id,
                              Video.user_id == user_id).first()
    params = request.json
    if not item:
        return {'message': 'No tutorials with such id'}, 400
    for key, value in params.items():
        setattr(item, key, value)
    session.commit()
    serialized = {
        'id': item.id,
        'name': item.name,
        'description': item.description
    }
    return serialized


@app.route('/tutorials/<int:tutorial_id>', methods=['DELETE'])
@jwt_required()
def delete_tutorial(tutorial_id):
    user_id = get_jwt_identity()
    item = Video.query.filter(Video.id == tutorial_id,
                              Video.user_id == user_id).first()
    if not item:
        return {'message': 'No tutorials with such id'}, 400
    session.delete(item)
    session.commit()
    return '', 204


@app.route('/register', methods=['POST'])
def register():
    params = request.json
    user = User(**params)
    session.add(user)
    session.commit()
    token = user.get_token()
    return {'access_token': token}


@app.route('/login', methods=['POST'])
def login():
    params = request.json
    user = User.authenticate(**params)
    token = user.get_token()
    return {'access_token': token}


@app.teardown_appcontext
def shutdown_session(exception=None):
    '''Закрываем сессию'''
    session.remove()


if __name__ == '__main__':
    app.run()
