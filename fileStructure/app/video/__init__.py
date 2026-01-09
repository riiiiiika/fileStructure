from flask import Flask, Blueprint

video_bp = Blueprint('video', __name__)

from . import routes