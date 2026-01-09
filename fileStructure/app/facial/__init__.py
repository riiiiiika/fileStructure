from flask import Flask, Blueprint

facial_bp = Blueprint('facial', __name__)

from . import routes