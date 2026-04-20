from datetime import datetime
import json
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(20))
    national_number = db.Column(db.String(20))  # NISS belgique
    birth_date = db.Column(db.Date)
    language = db.Column(db.String(2), default='fr')
    is_verified = db.Column(db.Boolean, default=False)
    kyc_status = db.Column(db.String(20), default='pending')  # pending/verified/rejected
    onboarding_step = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    gdpr_consent = db.Column(db.Boolean, default=False)
    gdpr_consent_at = db.Column(db.DateTime)

    extracts = db.relationship('PensionExtract', backref='user', lazy='dynamic')
    profile = db.relationship('InvestorProfile', backref='user', uselist=False)
    subscriptions = db.relationship('Subscription', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def latest_extract(self):
        return self.extracts.order_by(PensionExtract.uploaded_at.desc()).first()

    @property
    def latest_eligibility(self):
        extract = self.latest_extract
        if extract:
            return EligibilityResult.query.filter_by(extract_id=extract.id).first()
        return None


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class PensionExtract(db.Model):
    __tablename__ = 'pension_extracts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    _parsed_data = db.Column('parsed_data', db.Text)

    eligibility = db.relationship('EligibilityResult', backref='extract', uselist=False)

    @property
    def parsed_data(self):
        if self._parsed_data:
            return json.loads(self._parsed_data)
        return {}

    @parsed_data.setter
    def parsed_data(self, value):
        self._parsed_data = json.dumps(value)


class EligibilityResult(db.Model):
    __tablename__ = 'eligibility_results'

    id = db.Column(db.Integer, primary_key=True)
    extract_id = db.Column(db.Integer, db.ForeignKey('pension_extracts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_eligible = db.Column(db.Boolean, nullable=False)
    transferable_amount = db.Column(db.Numeric(12, 2))
    current_institution = db.Column(db.String(256))
    branch21_contracts = db.Column(db.Text)  # JSON list
    reason = db.Column(db.Text)
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def contracts(self):
        if self.branch21_contracts:
            return json.loads(self.branch21_contracts)
        return []


class InvestorProfile(db.Model):
    __tablename__ = 'investor_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    risk_score = db.Column(db.Integer)  # 0-100
    profile_type = db.Column(db.String(20))  # defensive/conservative/balanced/dynamic/aggressive
    _questionnaire_answers = db.Column('questionnaire_answers', db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def questionnaire_answers(self):
        if self._questionnaire_answers:
            return json.loads(self._questionnaire_answers)
        return {}

    @questionnaire_answers.setter
    def questionnaire_answers(self, value):
        self._questionnaire_answers = json.dumps(value)

    PROFILE_LABELS = {
        'defensive': {'fr': 'Défensif', 'nl': 'Defensief', 'en': 'Defensive'},
        'conservative': {'fr': 'Conservateur', 'nl': 'Conservatief', 'en': 'Conservative'},
        'balanced': {'fr': 'Équilibré', 'nl': 'Gebalanceerd', 'en': 'Balanced'},
        'dynamic': {'fr': 'Dynamique', 'nl': 'Dynamisch', 'en': 'Dynamic'},
        'aggressive': {'fr': 'Agressif', 'nl': 'Agressief', 'en': 'Aggressive'},
    }


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), unique=True, nullable=False)
    branch = db.Column(db.Integer, default=23)
    risk_level = db.Column(db.String(20))  # matches profile_type
    min_amount = db.Column(db.Numeric(10, 2), default=1000)
    expected_return_min = db.Column(db.Float)
    expected_return_max = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    name_fr = db.Column(db.String(128))
    name_nl = db.Column(db.String(128))
    name_en = db.Column(db.String(128))
    description_fr = db.Column(db.Text)
    description_nl = db.Column(db.Text)
    description_en = db.Column(db.Text)

    def name(self, lang='fr'):
        return getattr(self, f'name_{lang}', self.name_fr)

    def description(self, lang='fr'):
        return getattr(self, f'description_{lang}', self.description_fr)


class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    amount = db.Column(db.Numeric(12, 2))
    status = db.Column(db.String(30), default='draft')  # draft/pending_signature/signed/active/rejected
    reference = db.Column(db.String(64), unique=True)
    signed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = db.relationship('Product', backref='subscriptions')

    STATUS_LABELS = {
        'draft': {'fr': 'Brouillon', 'nl': 'Concept', 'en': 'Draft'},
        'pending_signature': {'fr': 'En attente de signature', 'nl': 'Wachten op handtekening', 'en': 'Pending signature'},
        'signed': {'fr': 'Signé', 'nl': 'Ondertekend', 'en': 'Signed'},
        'active': {'fr': 'Actif', 'nl': 'Actief', 'en': 'Active'},
        'rejected': {'fr': 'Refusé', 'nl': 'Geweigerd', 'en': 'Rejected'},
    }
