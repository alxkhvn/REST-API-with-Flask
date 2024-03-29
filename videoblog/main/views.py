from flask import Blueprint, jsonify
from videoblog import logger, docs
from videoblog.schemas import VideoSchema
from flask_apispec import use_kwargs, marshal_with
from videoblog.models import Video
from flask_jwt_extended import jwt_required, get_jwt_identity  # libs for authentication
from videoblog.base_view import BaseView

videos = Blueprint('videos', __name__)


class ListView(BaseView):
    @marshal_with(VideoSchema(many=True))
    def get(self):
        try:
            videos = Video.get_list()  # возвращяем данные только этого пользователя
        except Exception as e:
            logger.warning(
                f'tutorials - read action failed with errors: {e}')
            return {'message': str(e)}, 400
        return videos


@videos.route('/tutorials', methods=['GET'])  # route() decorator tells Flask what URL should trigger our function
@jwt_required()  # данный декоратор даёт доступ к роуту только авторизованным пользователям(неавт-ный юзер получит 401)
@marshal_with(VideoSchema(many=True))  # декоратор отвечает за сериализацию, many=True потому что роут возвращяет не один json а массив из них
def get_list():
    try:
        user_id = get_jwt_identity()
        videos = Video.get_user_list(user_id=user_id)  # возвращяем данные только этого пользователя
    except Exception as e:
        logger.warning(
            f'user:{user_id} tutorials - read action failed with errors: {e}')
        return {'message': str(e)}, 400
    return videos


@videos.route('/tutorials', methods=['POST'])
@jwt_required()
@use_kwargs(VideoSchema)  # тут не указываем many=True потому что на вход даём только один json
@marshal_with(VideoSchema)
def update_list(**kwargs):
    try:
        user_id = get_jwt_identity()  # извлекает из токена поле identity и получает доступ к userid
        new_one = Video(user_id=user_id, **kwargs)
        new_one.save()
    except Exception as e:
        logger.warning(
            f'user:{user_id} tutorials - create action failed with errors: {e}')
        return {'message': str(e)}, 400
    return new_one


@videos.route('/tutorials/<int:tutorial_id>', methods=['PUT'])
@jwt_required()
@use_kwargs(VideoSchema)
@marshal_with(VideoSchema)
def update_tutorial(tutorial_id, **kwargs):
    try:
        user_id = get_jwt_identity()
        # только пользователь указанный в user_id может совершать операции с данной записью
        item = Video.get(tutorial_id, user_id)
        item.update(**kwargs)
    except Exception as e:
        logger.warning(
            f'user:{user_id} tutorial:{tutorial_id} - update action failed with errors: {e}')
        return {'message': str(e)}, 400
    return item


@videos.route('/tutorials/<int:tutorial_id>', methods=['DELETE'])
@jwt_required()
@marshal_with(VideoSchema)
def delete_tutorial(tutorial_id):
    try:
        user_id = get_jwt_identity()
        item = Video.get(tutorial_id, user_id)
        item.delete()
    except Exception as e:
        logger.warning(
            f'user:{user_id} tutorial:{tutorial_id} - read action failed with errors: {e}')
        return {'message': str(e)}, 400
    return '', 204


@videos.errorhandler(422)
def error_handler(err):
    headers = err.data.get('headers', None)
    messages = err.data.get('messages', ['Invalid request'])
    logger.warning(f'Invalid input params: {messages}')  # логгируем все ошибки связанные с валидацией схем
    if headers:
        return jsonify({'message': messages}), 400, headers
    else:
        return jsonify({'message': messages}), 400


docs.register(get_list, blueprint='videos')  # генерирует swagger документацию для роута get_list
docs.register(update_list, blueprint='videos')
docs.register(update_tutorial, blueprint='videos')
docs.register(delete_tutorial, blueprint='videos')
ListView.register(videos, docs, '/main', 'listview')
