from flask import Flask, jsonify, request  # imported Flask class
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_jwt_extended import JWTManager  # lib for authentication
from .config import Config
from apispec.ext.marshmallow import MarshmallowPlugin  # for apispec and marshmallow work together
from apispec import APISpec  # for apispec and flask app work together
from flask_apispec.extension import FlaskApiSpec  # helps to create swagger docs for every route of app

import logging

app = Flask(__name__)
app.config.from_object(Config)  # даём доступ к secret key

client = app.test_client()  # тестовый клиент flask

engine = Config.SQLALCHEMY_DATABASE_URI


session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))


Base = declarative_base()  # базовый класс для описание моделей данных
Base.query = session.query_property()

jwt = JWTManager()

docs = FlaskApiSpec()


app.config.update({
    'APISPEC_SPEC': APISpec(
        title='videoblog',
        version='v1',
        openapi_version='2.0',
        plugins=[MarshmallowPlugin()],
    ),
    'APISPEC_SWAGGER_URL': '/swagger/'
})

from .models import *
Base.metadata.create_all(bind=engine)  # Создаёт схему базы данных в в базе


def setup_logger():
    logger = logging.getLogger(__name__)  # получаем экземпляр логера
    logger.setLevel(logging.DEBUG)  # Устанавливаем уровень логирования

    formatter = logging.Formatter(
        '%(asctime)s:%(name)s:%(levelname)s:%(message)s')  # определяем формат логов
    file_handler = logging.FileHandler('log/api.log')  # создаем filehandler чтоб выводить логи в файл
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()


@app.teardown_appcontext
def shutdown_session(exception=None):
    '''Закрываем сессию'''
    session.remove()


from .main.views import videos
from .users.views import users

app.register_blueprint(videos)  # регистрируем blueprint videos
app.register_blueprint(users)

docs.init_app(app)
jwt.init_app(app)
