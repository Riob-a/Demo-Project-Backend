from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    artworks = db.relationship('Artwork', backref='owner', lazy=True)  # Relationship to Artwork

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"
    def to_dict(self):
        return {
            'id':self.id,
            'username':self.username,
            'email':self.email,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S'), 
        }
    
class Artwork(db.Model):
    __tablename__='art'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=False)
    email = db.Column(db.String(80), nullable=False, unique=False)
    style = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Foreign key to User

    def __repr__(self):
        return f"<Art {self.name}>"
    
    def to_dict(self):
        return {
            'id':self.id,
            'name':self.name,
            'email':self.email,
            'style':self.style,
            'image_url':self.image_url,
            'description':self.description,
            "user_id": self.user_id
        }

class Contact(db.Model):
    __tablename__='contact'
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), nullable=False, unique=False)
    email=db.Column(db.String(100), nullable=False)
    message=db.Column(db.Text, nullable=False)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Contact {self.name}>"
    
    def to_dict(self):
        return {
            'id':self.id,
            'name':self.name,
            'email':self.email,
            'message':self.message,
            'posted_at':self.posted_at.strftime('%d-%m-%Y %H:%M:%S'),
        }
    
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='admin')  # Roles like 'admin', 'superadmin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Admin {self.username}>"

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
        }

