from src import db, login, bcrypt, Config
from flask_login import UserMixin
from sqlalchemy import Enum, func

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    email = db.Column(db.String(64), index=True, unique=True, nullable=True)
    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def validate_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Memory(db.Model):
    __tablename__ = 'memories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prompt = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    training_status = db.Column(Enum('active', 'inactive', 'completed', name='training_status'), nullable=False, default='active')
    recall_duration_days = db.Column(db.Integer, nullable=False, default=0)
    total_recall_count = db.Column(db.Integer, nullable=False, default=0)
    perfect_recall_count = db.Column(db.Integer, nullable=False, default=0)
    partial_recall_count = db.Column(db.Integer, nullable=False, default=0)
    failed_recall_count = db.Column(db.Integer, nullable=False, default=0)
    last_recall_outcome = db.Column(Enum('perfect', 'partial', 'failed', name='recall_outcome'), nullable=True)
    next_recall_at = db.Column(db.DateTime(timezone=True), nullable=False, default=func.timezone('UTC', func.current_timestamp()))
    last_recall_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=func.timezone('UTC', func.current_timestamp()))
    last_modified_at = db.Column(db.DateTime(timezone=True), nullable=False, default=func.timezone('UTC', func.current_timestamp()))

    user = db.relationship('User', backref='memories', lazy=True)
    