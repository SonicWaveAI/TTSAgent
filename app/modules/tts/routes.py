from flask import Blueprint, Response, request
from pkg.util import common
from .service import tts_impl
import os

tts_bp = Blueprint('tts', __name__)


@tts_bp.route('/models', methods=['GET'])
def list_models():
    models = tts_impl.get_models()
    if len(models) == 0:
        return common.new_failed(404, 'No model found')
    else:
        return common.new_success(models)


@tts_bp.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    if not data or 'content' not in data:
        return common.new_failed(404, 'content cannot be empty')

    text = data['content']
    model_type = data.get('model_type', '马云')
    if not tts_impl.check_model(model_type):
        return common.new_failed(404, 'model not exists')
    voice_path = tts_impl.generate_voice(model_type, text)

    return Response(
        tts_impl.read_clean(voice_path),
        mimetype='audio/wav',
        headers={
            'Content-Disposition': f'attachment; filename={os.path.basename(voice_path)}'
        }
    )
