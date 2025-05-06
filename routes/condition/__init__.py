from flask import Blueprint
from .finalize_condition import finalize_conditions
from .filter_routes import filter_routes
from .update_condition_temp import update_condition_temp

# Khai báo Blueprint cho 'condition'
condition_bp = Blueprint('condition_bp', __name__)

# Đăng ký các route với Blueprint
condition_bp.add_url_rule('/filter_routes', 'filter_routes', filter_routes, methods=['POST'])
condition_bp.add_url_rule('/update_condition_temp', 'update_condition_temp', update_condition_temp, methods=['POST'])
condition_bp.add_url_rule('/finalize_conditions', 'finalize_conditions', finalize_conditions, methods=['POST'])
