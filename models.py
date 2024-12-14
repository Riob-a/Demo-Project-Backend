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
    profile_image = db.Column(db.String(500), nullable=True) 
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
            "created_at": self.created_at.strftime('%d-%m-%Y %H:%M:%S'),
            'profile_image': self.profile_image  
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
    username = db.Column(db.String(225), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(500), nullable=False)
    role = db.Column(db.String(250), nullable=False, default='admin')  # Roles like 'admin', 'superadmin'
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

# @app.route('/api/users/<int:id>', methods=['PUT'])
# @jwt_required()
# def update_user(id):
#     current_user_id = get_jwt_identity().get("id")
#     if current_user_id != id:
#         return jsonify({"message": "You can only update your own profile"}), 403
    
#     user = User.query.get(id)
#     if not user:
#         return jsonify({"message": "User not found"}), 404
    
#     data = request.json
#     user.username = data.get('username', user.username)
#     user.email = data.get('email', user.email)
    
#     if 'password' in data:
#         user.set_password(data['password'])
    
#     # Handle profile image upload
#     profile_image = request.files.get('profile_image')
#     if profile_image:
#         try:
#             upload_result = upload(profile_image)
#             user.profile_image = upload_result.get('secure_url')
#         except Exception as e:
#             return jsonify({"message": f"Image upload failed: {str(e)}"}), 400

#     db.session.commit()
#     return jsonify({"message": "User profile updated successfully"}), 200