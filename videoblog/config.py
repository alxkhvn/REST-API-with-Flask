import os
import json


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')  # используется в качестве криптографической соли при хешировании
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')

#cbdd4d3f977b4da4a680ac4e3cd15dc0 old secret_key