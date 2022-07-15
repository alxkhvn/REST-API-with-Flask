from flask import Flask, jsonify, request  # imported Flask class
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity  # libs for authentication
from config import Config
from apispec.ext.marshmallow import MarshmallowPlugin  # for apispec and marshmallow work together
from apispec import APISpec  # for apispec and flask app work together
from flask_apispec.extension import FlaskApiSpec  # helps to create swagger docs for every route of app
from schemas import VideoSchema, UserSchema, AuthSchema
from flask_apispec import use_kwargs, marshal_with

app = Flask(__name__)
app.config.from_object(Config)  # даём доступ к secret key

client = app.test_client()  # тестовый клиент flask

engine = create_engine('sqlite:///db.sqlite')  # Создаём привязку к базе

session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))


Base = declarative_base()  # базовый класс для описание моделей данных
Base.query = session.query_property()

jwt = JWTManager(app)

docs = FlaskApiSpec()

docs.init_app(app)

app.config.update({
    'APISPEC_SPEC': APISpec(
        title='videoblog',
        version='v1',
        openapi_version='2.0',
        plugins=[MarshmallowPlugin()],
    ),
    'APISPEC_SWAGGER_URL': '/swagger/'
})

from models import *

Base.metadata.create_all(bind=engine)  # Создаёт схему базы данных в в базе


@app.route('/tutorials', methods=['GET'])  # route() decorator tells Flask what URL should trigger our function
@jwt_required()  # данный декоратор даёт доступ к роуту только авторизованным пользователям(неавт-ный юзер получит 401)
@marshal_with(VideoSchema(many=True))  # декоратор отвечает за сериализацию many=True потому что роут возвращяет не один json а массив из них
def get_list():
    user_id = get_jwt_identity()
    videos = Video.query.filter(Video.user_id == user_id)  # возвращяем данные только этого пользователя
    return videos


@app.route('/tutorials', methods=['POST'])
@jwt_required()
@use_kwargs(VideoSchema)  # тут не указываем many=True потому что на вход даём только один json
@marshal_with(VideoSchema)
def update_list(**kwargs):
    user_id = get_jwt_identity()  # извлекает из токена поле identity и получает доступ к userid
    new_one = Video(user_id=user_id, **kwargs)
    session.add(new_one)
    session.commit()
    return new_one


@app.route('/tutorials/<int:tutorial_id>', methods=['PUT'])
@jwt_required()
@use_kwargs(VideoSchema)
@marshal_with(VideoSchema)
def update_tutorial(tutorial_id, **kwargs):
    user_id = get_jwt_identity()
    # только пользователь указанный в user_id может совершать операции с данной записью
    item = Video.query.filter(
        Video.id == tutorial_id,
        Video.user_id == user_id).first()
    if not item:
        return {'message': 'No tutorials with such id'}, 400
    for key, value in kwargs.items():
        setattr(item, key, value)
    session.commit()
    return item


@app.route('/tutorials/<int:tutorial_id>', methods=['DELETE'])
@jwt_required()
@marshal_with(VideoSchema)
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
@use_kwargs(UserSchema)
@marshal_with(AuthSchema)
def register(**kwargs):
    user = User(**kwargs)
    session.add(user)
    session.commit()
    token = user.get_token()
    return {'access_token': token}


@app.route('/login', methods=['POST'])
@use_kwargs(UserSchema(only=('email', 'password')))
@marshal_with(AuthSchema)
def login(**kwargs):
    user = User.authenticate(**kwargs)
    token = user.get_token()
    return {'access_token': token}


@app.teardown_appcontext
def shutdown_session(exception=None):
    '''Закрываем сессию'''
    session.remove()


docs.register(get_list) #генерирует swagger документацию для роута get_list
docs.register(update_list)
docs.register(update_tutorial)
docs.register(delete_tutorial)
docs.register(register)
docs.register(login)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000')
