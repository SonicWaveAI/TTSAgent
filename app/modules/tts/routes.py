from flask import Blueprint, Response, request
from pkg.util import common
from .service import tts_impl
import os
from werkzeug.utils import secure_filename

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
    model_type = data.get('model_type', None)
    method = data.get("method", "default")

    if method == "default":
        if model_type is None:
            model_type = "马云"
        if not tts_impl.check_model(model_type):
            return common.new_failed(404, 'model not exists')
        voice_path = tts_impl.generate_voice(model_type, text)
    else:
        if model_type is None:
            return common.new_failed(404, 'please upload voice')
        else:
            voice_path = tts_impl.generate_voice_custom(model_type, text)

    return Response(
        tts_impl.read_clean(voice_path),
        mimetype='audio/wav',
        headers={
            'Content-Disposition': f'attachment; filename={os.path.basename(voice_path)}'
        }
    )


@tts_bp.route('/upload', methods=['POST'])
def upload_voice():
    if 'voice' not in request.files:
        return common.new_failed(400, 'No voice file uploaded')

    voice_file = request.files['voice']
    if voice_file.filename == '':
        return common.new_failed(400, 'No selected file')

    allowed_extensions = ['.wav', '.m4a']
    file_ext = os.path.splitext(voice_file.filename.lower())[1]
    if file_ext not in allowed_extensions:
        return common.new_failed(400, f'Only {", ".join(allowed_extensions)} files are allowed')

    try:
        unique_id = tts_impl.upload_voice(voice_file)
        return common.new_success({'id': unique_id})
    except Exception as e:
        return common.new_failed(500, str(e))
