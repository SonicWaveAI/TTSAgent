from flask import jsonify


def new_response(code=0, message="success", data=None):
    return jsonify({'message': message, 'code': code, 'data': data})


def new_success(data=None):
    return new_response(0, "success", data)


def new_failed(code, message):
    return new_response(code=code, message=message, data=None)
