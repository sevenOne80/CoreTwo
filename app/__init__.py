import os
from flask import Flask, request, session, g
from config import config
from app.extensions import db, login_manager, babel, mail, csrf


def get_locale():
    if 'lang' in session:
        return session['lang']
    return request.accept_languages.best_match(['fr', 'nl', 'en'], default='fr')


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    mail.init_app(app)
    csrf.init_app(app)

    from app.main import main as main_bp
    from app.auth import auth as auth_bp
    from app.portal import portal as portal_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(portal_bp, url_prefix='/portal')

    @app.context_processor
    def inject_globals():
        return {
            'current_lang': session.get('lang', 'fr'),
            'languages': app.config['LANGUAGES'],
        }

    with app.app_context():
        db.create_all()

    return app
