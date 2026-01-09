#録画・録音
from flask import Blueprint
interview_bp = Blueprint('interview', __name__)
from . import routes