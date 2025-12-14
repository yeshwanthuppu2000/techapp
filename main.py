from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import pandas as pd
import docx
import json
import os
from dotenv import load_dotenv, set_key
from helper import roles_required

load_dotenv()

app = Flask(__name__, template_folder='src', static_folder='src')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

DATABASE = 'database.db'
DOTENV_PATH = '.env'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Main Routes ---
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/home')
@roles_required('admin', 'user')
def home():
    return render_template('home.html')

@app.route('/admin')
@roles_required('admin', 'user')
def admin_dashboard():
    return render_template('admin.html')

@app.route('/upload', methods=['GET', 'POST'])
@roles_required('admin', 'user')
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400
        
        return redirect(url_for('tracking'))
    
    return render_template('upload.html')

@app.route('/tracking')
@roles_required('admin', 'user')
def tracking():
    return render_template('tracking.html')

@app.route('/chatpage')
@roles_required('admin', 'user')
def chatpage():
    return render_template('chat.html')

# --- API Routes ---
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['role'] = user['role']
        
        return jsonify({'success': True, 'redirect_url': url_for('home')})
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/chat', methods=['POST'])
@roles_required('admin', 'user')
def chat():
    data = request.get_json()
    message = data.get('message')
    model = data.get('model')

    # Simulate a response from the selected LLM
    response = f"This is a simulated response for '{message}' using {model}."
    
    return jsonify({'response': response})

@app.route('/profile')
@roles_required('admin', 'user')
def profile():
    user = get_user_by_id(session['user_id'])
    if user:
        return jsonify({
            'username': user['username'],
            'email': user['email'],
            'full_name': user['full_name'],
            'role': user['role']
        })
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/dashboard_data')
@roles_required('admin')
def dashboard_data():
    conn = get_db()
    total_users = conn.execute('SELECT COUNT(id) FROM users').fetchone()[0]
    admin_count = conn.execute('SELECT COUNT(id) FROM users WHERE role = ?', ('admin',)).fetchone()[0]
    user_count = total_users - admin_count
    conn.close()

    # Dummy data for docs
    docs_processed = 250
    doc_types = {
        'docx': 120,
        'xlsx': 80,
        'csv': 50
    }

    return jsonify({
        'total_users': total_users,
        'admin_count': admin_count,
        'user_count': user_count,
        'docs_processed': docs_processed,
        'user_roles': {
            'Admins': admin_count,
            'Users': user_count
        },
        'doc_types': doc_types
    })

@app.route('/users', methods=['GET', 'POST'])
@roles_required('admin')
def manage_users():
    conn = get_db()
    if request.method == 'POST':
        data = request.get_json()
        if not all(k in data for k in ['username', 'password', 'email', 'full_name', 'role']):
             conn.close()
             return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        hashed_password = generate_password_hash(data['password'])
        try:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password, email, role, full_name) VALUES (?, ?, ?, ?, ?)',
                         (data['username'], hashed_password, data['email'], data['role'], data['full_name']))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            new_user = get_user_by_id(user_id)
            return jsonify({'success': True, 'user': dict(new_user)}), 201
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'success': False, 'error': 'Username or email already exists'}), 409

    users = conn.execute('SELECT id, username, email, role, full_name FROM users').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in users])

@app.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@roles_required('admin')
def manage_single_user(user_id):
    conn = get_db()
    
    if request.method == 'GET':
        user = conn.execute('SELECT id, username, email, role, full_name FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if user:
            return jsonify(dict(user))
        return jsonify({'error': 'User not found'}), 404

    if request.method == 'PUT':
        data = request.get_json()
        password = data.get('password')

        try:
            if password:
                hashed_password = generate_password_hash(password)
                conn.execute('UPDATE users SET username=?, email=?, role=?, full_name=?, password=? WHERE id=?',
                             (data['username'], data['email'], data['role'], data['full_name'], hashed_password, user_id))
            else:
                conn.execute('UPDATE users SET username=?, email=?, role=?, full_name=? WHERE id=?',
                             (data['username'], data['email'], data['role'], data['full_name'], user_id))
            
            conn.commit()
            conn.close()
            updated_user = get_user_by_id(user_id)
            return jsonify({'success': True, 'user': dict(updated_user)})
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'success': False, 'error': 'Username or email already exists'}), 409

    if request.method == 'DELETE':
        if user_id == session.get('user_id'):
            conn.close()
            return jsonify({'success': False, 'error': 'Cannot delete currently logged-in user'}), 400
            
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

@app.route('/llm/settings', methods=['GET', 'POST'])
@roles_required('admin')
def llm_settings():
    if request.method == 'POST':
        data = request.get_json()
        selected_models = data.get('selected_models', [])
        
        set_key(DOTENV_PATH, 'SELECTED_MODELS', ",".join(selected_models))
        
        return jsonify({'success': True})

    all_models = os.getenv('AVAILABLE_MODELS', '').split(',')
    selected_models = os.getenv('SELECTED_MODELS', '').split(',')
    
    return jsonify({
        'all_models': all_models,
        'selected_models': selected_models
    })

@app.route('/llm/models')
@roles_required('admin', 'user')
def get_llm_models():
    selected_models = os.getenv('SELECTED_MODELS', '').split(',')
    return jsonify({'models': selected_models})

def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085, debug=True)