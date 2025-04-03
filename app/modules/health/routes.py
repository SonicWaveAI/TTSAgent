from flask import Blueprint, jsonify
from pkg.util import common

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health():
    return common.new_success(data="Service Normal")
