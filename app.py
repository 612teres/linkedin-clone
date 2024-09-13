from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId  # To work with MongoDB IDs
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/linkedin_clone"
mongo = PyMongo(app)

# Database collections
users = mongo.db.users

@app.route('/api/register', methods=['POST'])
def register():
    """Registers a new user."""
    data = request.get_json()
    email = data['email']
    password = data['password']

    # Check if user already exists
    if users.find_one({'email': email}):
        return jsonify({'error': 'Email already exists'}), 400

    # Hash the password before storing it
    hashed_password = generate_password_hash(password)

    # Create a new user document
    user_id = users.insert_one({
        'email': email,
        'password': hashed_password,
        'profile': {}  # Initialize an empty profile
    }).inserted_id

    return jsonify({'message': 'User registered successfully', 'user_id': str(user_id)}), 201

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticates a user."""
    data = request.get_json()
    email = data['email']
    password = data['password']

    user = users.find_one({'email': email})
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid email or password'}), 401

    return jsonify({'message': 'Login successful', 'user_id': str(user['_id'])}), 200

@app.route('/api/profile/<user_id>', methods=['GET', 'PUT'])
def profile(user_id):
    """Gets or updates a user's profile."""
    if request.method == 'GET':
        user = users.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user['profile']), 200

    if request.method == 'PUT':
        data = request.get_json()
        result = users.update_one({'_id': ObjectId(user_id)}, {'$set': {'profile': data}})
        if result.modified_count == 0:
            return jsonify({'error': 'Profile update failed'}), 500
        return jsonify({'message': 'Profile updated successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)