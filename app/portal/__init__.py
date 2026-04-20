from flask import Blueprint

portal = Blueprint('portal', __name__)

from app.portal import routes  # noqa
