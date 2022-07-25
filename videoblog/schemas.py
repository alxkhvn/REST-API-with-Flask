from marshmallow import Schema, validate, fields


class VideoSchema(Schema):
    ''' благодаря схемам клиент не может передавать неподходящий тип данных для параметра
    или вовсе передавать базе несуществующий параметр (будет получать 422 ошибку)'''
    id = fields.Integer(dump_only=True)
    # dump_only=True для параметров которые нужно только сериализовать (не принимать их в качестве входящих параметров)
    user_id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[
        validate.Length(max=250)])
    description = fields.String(required=True, validate=[
        validate.Length(max=500)])
    message = fields.String(dump_only=True)


class UserSchema(Schema):
    name = fields.String(required=True, validate=[
        validate.Length(max=250)])
    email = fields.String(required=True, validate=[
        validate.Length(max=250)])
    password = fields.String(required=True, validate=[
        validate.Length(max=100)], load_only=True)  #load_only=True для того чтоб пароль не возвращался в json
    videos = fields.Nested(VideoSchema, many=True, dump_only=True)


class AuthSchema(Schema):
    access_token = fields.String(dump_only=True)
    message = fields.String(dump_only=True)
