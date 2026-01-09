from flask import Flask, Blueprint
#nameの中はprofileで固定、__name__はこのファイルの場所を示す

profile_bp = Blueprint('profile', __name__)

from . import routes