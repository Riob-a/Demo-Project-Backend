from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from functools import wraps
from models import db, User, Artwork, ArtworkLike, Contact, Admin
from werkzeug.security import generate_password_hash, check_password_hash
import cloudinary
from cloudinary.uploader import upload
import cloudinary.api
from dotenv import load_dotenv
# from flask_mail import Mail, Message
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Replace with a strong secret key

# Load environment variables from .env file
load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)
# Mail configurations
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("EMAIL_USER")  # Store in .env file
app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASS")  # Store in .env file
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("EMAIL_USER")

mail = Mail(app)

# Send grid
sendgrid_client = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)
jwt = JWTManager(app)

# Set to keep track of revoked tokens
revoked_tokens = set()

# Admin decorator
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        if identity.get("role") != "admin":
            return jsonify({"message": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper

#fetch kijes helper
def get_artwork_data_with_likes(artwork, user_id):
    """Returns artwork data with like count and user like status."""
    like_count = ArtworkLike.query.filter_by(artwork_id=artwork.id).count()
    user_has_liked = ArtworkLike.query.filter_by(artwork_id=artwork.id, user_id=user_id).first() is not None

    artwork_data = artwork.to_dict()
    artwork_data["likes"] = like_count
    artwork_data["user_has_liked"] = user_has_liked
    return artwork_data

# INDEX ROUTE
@app.route('/')
def home():
    return jsonify({"message": "Welcome to Derrick's Demo"}), 200

# USER ROUTES
@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.form
    image_file = request.files.get('profile_image')  # Retrieve the image file
    profile_image = None

    if image_file:
        try:
            upload_result = upload(image_file)
            profile_image = upload_result.get('secure_url')
        except Exception as e:
            return jsonify({"message": "Image upload failed", "error": str(e)}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered"}), 409

    new_user = User(
        username=data['username'],
        email=data['email'],
        profile_image=profile_image  # Add profile image URL
    )
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    # Send confirmation email
    send_confirmation_email(new_user.email, new_user.username)

    return jsonify({"message": "User registered successfully"}), 201


def send_confirmation_email(to_email, username):
    subject = "Welcome to Derrick's Demo App!"
    body = f"Hello {username},\n\nThank you for registering! We're excited to have you on board.\n\nBest regards,\nDerrick's Demo Team"

    # Create a new message object
    message = Mail(
        from_email=os.getenv("EMAIL_USER"),  # Sender's email (registered with SendGrid)
        to_emails=to_email,
        subject=subject,
        plain_text_content=body
    )

    # Send the email using SendGrid
    try:
        sendgrid_client = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sendgrid_client.send(message)
        print(f"Email sent! Status Code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")

    # # Send the email
    # with app.app_context():
    #     mail.send(msg)

@app.route('/api/signin', methods=['POST'])
def sign_in():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    admin = Admin.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity={"id": user.id})   # Create a token with user ID
        return jsonify({
            "message": "Sign-in successful",
            "user": user.to_dict(),
            "access_token": access_token
        }), 200
    elif admin and admin.check_password(data['password']):
        access_token= create_access_token(identity={"id": admin.id, "role": "admin"})
        return jsonify({
            "message": "Sign-in successful (Admin)",
            "user": admin.to_dict(),
            "access_token": access_token
        }),200
    else:
        return jsonify({"message": "Invalid email or password"}), 401

@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']  # Get JWT identity
    response = jsonify({"message":"Logged out successfully"})
    revoked_tokens.add(jti)    # Add the token ID to the revoked list
    
    return response, 200

# JWT Revocation Check
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return jwt_payload['jti'] in revoked_tokens

@app.route('/api/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@app.route('/api/users/<int:id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message':'User not Found'}),404
    return jsonify(user.to_dict()),200

@app.route('/api/users/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"message":"User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message':'User deleted succesfully'}),200
# put goes here

@app.route('/api/users/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    current_user_id = get_jwt_identity().get("id")
    if current_user_id != id:
        return jsonify({"message": "You can only update your own profile"}), 403
    
    user = User.query.get(id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # Handle form fields
    user.username = request.form.get('username', user.username)
    user.email = request.form.get('email', user.email)
    
    # Handle password if provided
    if 'password' in request.form:
        user.set_password(request.form['password'])
    
    # Handle profile image upload
    profile_image = request.files.get('profile_image')
    if profile_image:
        try:
            upload_result = upload(profile_image)  # Ensure this is properly defined
            user.profile_image = upload_result.get('secure_url')
        except Exception as e:
            return jsonify({"message": f"Image upload failed: {str(e)}"}), 400
    
    db.session.commit()
    return jsonify({"message": "User profile updated successfully"}), 200

@app.route('/api/users/me', methods=['GET'])
@jwt_required()
def get_user_profile():
    current_user_id = get_jwt_identity().get("id")
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify(user.to_dict()), 200

# me goes here

@app.route('/api/users/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity().get("id")
    data = request.get_json()
    
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    if not old_password or not new_password:
        return jsonify({"message": "Old password and new password are required"}), 400
    
    user = User.query.get(current_user_id)
    if not user or not user.check_password(old_password):
        return jsonify({"message": "Incorrect old password"}), 403
    
    user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Password updated successfully"}), 200

@app.route('/api/users/me/liked-artworks', methods=['GET'])
@jwt_required()
def get_liked_artworks():
    """
    Fetch all artworks liked by the currently authenticated user.
    """
    current_user_id = get_jwt_identity().get("id")  # Get the current user's ID

    # Get all liked artwork records for the user
    liked_artworks = ArtworkLike.query.filter_by(user_id=current_user_id).all()

    if not liked_artworks:
        return jsonify({"message": "No liked artworks found"}), 404

    # Fetch artwork details for each liked record
    liked_artwork_details = [
        get_artwork_data_with_likes(artwork_like.artwork, current_user_id)
        for artwork_like in liked_artworks
    ]

    return jsonify(liked_artwork_details), 200


# ARTWORK ROUTES
@app.route('/api/artworks/submit', methods=['POST', 'OPTIONS'])
@jwt_required()
# @admin_required

def submit_artwork():
    if request.method == 'OPTIONS':
        return '', 200  # CORS preflight handling
    
    current_user_id = get_jwt_identity().get("id")  # Get the current user's ID
    data = request.form
    image_file = request.files.get('image')  # Retrieve the image file from the form data

    
    if not image_file:
        return jsonify({"message": "No image file provided"}), 400
    
    # Upload the image to Cloudinary
    upload_result = upload(image_file)
    image_url = upload_result.get('secure_url')  # Get the secure URL from Cloudinary

    new_artwork = Artwork(
        name=data['name'],
        email=data['email'],
        image_url=image_url,  # Save the Cloudinary URL
        style=data['style'],
        description=data['description'],
        user_id=current_user_id  # Link to the logged-in user
    )
    db.session.add(new_artwork)
    db.session.commit()

    return jsonify({"message": "Artwork submitted successfully", "image_url": image_url}), 201

@app.route('/api/artworks/<style>', methods=['GET'])
@jwt_required()
# @admin_required

def get_artworks_by_style(style):
    """
    Fetch artworks by style with their total likes.
    """
    current_user_id = get_jwt_identity().get("id")
    artworks = Artwork.query.filter_by(style=style).all()

    artworks_with_likes = [get_artwork_data_with_likes(artwork, current_user_id) for artwork in artworks]
    return jsonify(artworks_with_likes), 200

@app.route('/api/artworks/<int:id>', methods=['GET'])
@jwt_required()
@admin_required

def get_artwork(id):
    """
    Fetch a single artwork by ID with its total likes.
    """
    current_user_id = get_jwt_identity().get("id")
    artwork = Artwork.query.get(id)
    if not artwork:
        return jsonify({"message": "Artwork not found"}), 404

    artwork_data = get_artwork_data_with_likes(artwork, current_user_id)
    return jsonify(artwork_data), 200

@app.route('/api/users/<int:user_id>/artworks', methods=['GET'])
@jwt_required()
# @admin_required  # Or allow users to fetch their own artworks
def get_user_artworks(user_id):
    """
    Fetch all artworks by a specific user with their total likes.
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    current_user_id = get_jwt_identity().get("id")
    artworks = Artwork.query.filter_by(user_id=user_id).all()

    artworks_with_likes = [get_artwork_data_with_likes(artwork, current_user_id) for artwork in artworks]
    return jsonify(artworks_with_likes), 200

@app.route('/api/artworks/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_artwork(id):
    artwork = Artwork.query.get(id)
    if not artwork:
        return jsonify({"message": "Artwork not found"}), 404
    db.session.delete(artwork)
    db.session.commit()
    return jsonify({"message": "Artwork deleted successfully"}), 200

@app.route('/api/artworks/<int:id>/like', methods=['POST'])
@jwt_required()
def like_artwork(id):
    """
    Handle liking an artwork by ID.
    """
    current_user_id = get_jwt_identity().get("id")  # Get the current user's ID

    # Check if the artwork exists
    artwork = Artwork.query.get(id)
    if not artwork:
        return jsonify({"message": "Artwork not found"}), 404

    # Check if the user has already liked the artwork
    existing_like = ArtworkLike.query.filter_by(artwork_id=id, user_id=current_user_id).first()
    if existing_like:
        like_count = ArtworkLike.query.filter_by(artwork_id=id).count()
        return jsonify({"message": "Artwork already liked", "likes": like_count}), 200

    # Create a new like
    new_like = ArtworkLike(artwork_id=id, user_id=current_user_id)
    db.session.add(new_like)
    db.session.commit()

    # Optionally, return updated like count
    like_count = ArtworkLike.query.filter_by(artwork_id=id).count()
    return jsonify({"message": "Artwork liked successfully", "likes": like_count}), 200

@app.route('/api/artworks/<int:id>/like', methods=['DELETE'])
@jwt_required()
def unlike_artwork(id):
    """
    Handle unliking an artwork by ID.
    """
    current_user_id = get_jwt_identity().get("id")  # Get the current user's ID
    print(f"Attempting to unlike artwork ID: {id}, User ID: {current_user_id}")

    # Check if the artwork exists
    artwork = Artwork.query.get(id)
    if not artwork:
        print(f"Artwork with ID {id} not found.")
        return jsonify({"message": "Artwork not found"}), 404

    # Check if the user has liked the artwork
    existing_like = ArtworkLike.query.filter_by(artwork_id=id, user_id=current_user_id).first()
    if not existing_like:
        print(f"No like record found for Artwork ID {id} and User ID {current_user_id}.")
        return jsonify({"message": "You have not liked this artwork"}), 400

    # Remove the like
    db.session.delete(existing_like)
    db.session.commit()
    print(f"Like removed for Artwork ID {id}, User ID {current_user_id}")

    # Optionally, return updated like count
    like_count = ArtworkLike.query.filter_by(artwork_id=id).count()
    return jsonify({"message": "Artwork unliked successfully", "likes": like_count}), 200


# CONTACT ROUTES
@app.route('/api/contact', methods=['POST'])
@jwt_required()
def create_contact():
    data = request.json
    new_contact = Contact(
        name=data['name'],
        email=data['email'],
        message=data['message']
    )
    db.session.add(new_contact)
    db.session.commit()
    return jsonify({"message": "Contact message submitted successfully"}), 201

@app.route('/api/contacts', methods=['GET'])
@jwt_required()
@admin_required
def get_contacts():
    contacts = Contact.query.all()
    return jsonify([contact.to_dict() for contact in contacts]), 200

@app.route('/api/contacts/email/<email>', methods=['GET'])
@jwt_required()
@admin_required
def get_contacts_by_email(email):
    contacts = Contact.query.filter_by(email=email).all()
    return jsonify([contact.to_dict() for contact in contacts]), 200

# GET a single contact by ID
@app.route('/api/contacts/<int:id>', methods=['GET'])
@jwt_required()
# @admin_required
def get_contact(id):
    contact = Contact.query.get(id)
    if not contact:
        return jsonify({"message": "Contact not found"}), 404
    return jsonify(contact.to_dict()), 200

# DELETE a single contact by ID
@app.route('/api/contacts/<int:id>', methods=['DELETE'])
# @jwt_required()
@admin_required
def delete_contact(id):
    contact = Contact.query.get(id)
    if not contact:
        return jsonify({"message": "Contact not found"}), 404
    db.session.delete(contact)
    db.session.commit()
    return jsonify({"message": "Contact deleted successfully"}), 200

@app.route('/api/users/me/contacts', methods=['GET'])
@jwt_required()
def get_user_contacts():
    # Get the current user ID from the JWT token
    current_user_id = get_jwt_identity().get("id")

    # Query the user based on the ID
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Query all contacts associated with the user
    contacts = Contact.query.filter_by(email=user.email).all()

    # If no contacts are found, return a message
    if not contacts:
        return jsonify({"message": "No contacts found"}), 404

    # Convert the contacts to dictionaries and return them
    return jsonify([contact.to_dict() for contact in contacts]), 200


# Admin routes
@app.route('/api/admin-register', methods=['POST'])
def admin_register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'admin')  # Default to 'admin' if no role is provided
    
    # Create a new admin object without the password hash
    new_admin = Admin(username=username, email=email, role=role)
    
    # Hash the password and set it on the admin object
    new_admin.set_password(password)
    
    # Example of checking the password (normally done during login)
    if new_admin.check_password(password):
        print("Password is correct") 
    else:
        print("Password is incorrect")

    try:
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({"message": "Admin registered successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Look up the admin by username
    admin = Admin.query.filter_by(username=username).first()
    
    if admin and admin.check_password(password):
        return jsonify({"message": "Login successful!"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401
    

if __name__ == '__main__':
    app.run(debug=True)


