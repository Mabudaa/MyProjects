import base64
import numpy as np
import os
import cv2

from datetime import datetime
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, current_app, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
model = # input model here
app.config['SECRET_KEY'] = 'mabudaa292001'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = r'C:\\Users\\sibus\\Desktop\\dyslexia\\uploads'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    child_age = db.Column(db.Integer)
    gender = db.Column(db.String(80), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent = db.relationship('User', backref=db.backref('children', lazy=True))

class DyslexiaRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    child = db.relationship('Child', backref=db.backref('dyslexia_records', lazy=True))
    method = db.Column(db.String(20), nullable=False)
    result = db.Column(db.String(100), nullable=False)
    game_time_played = db.Column(db.Float, nullable=True)
    game_hits = db.Column(db.Integer, nullable=True)
    game_misses = db.Column(db.Integer, nullable=True)
    game_score = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128,255, cv2.THRESH_BINARY_INV)
    return binary

def segment_letters(binary_image):
    #finding individual letters
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    letters = []
    for contour in contours:
        x,y,w,h = cv2.boundingRect(contour)
        letter = binary_image[y:y+h, x:x+w]
        #resizing the iamge to the input shape of the model
        resized_letter = cv2.resize(letter, (255,255)) / 255.0
        letters .append((x, resized_letter))

    letters.sort(key=lambda l:l[0])
    return [l[1] for l in letters]

def classify_letters(letters):
    predictions = []
    for letter in letters:
        letter = letter.reshape(1,28,28,1)
        prediction = model.predict(letter)
        label = np.argmax(prediction)
        predictions.append(label)
    return predictions

@app.route('/')
def index():
    print("Current app context:", current_app)
    return render_template('index.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']  # Retrieve user type from form
        user = User.query.filter_by(username=username, password=password, user_type=user_type).first()
        if user:
            session['user_id'] = user.id
            if user_type == 'Parent':
                return redirect(url_for('parent_dashboard'))# Redirect to parent dashboard
            elif user_type == 'Teacher':
                return redirect(url_for('teacher_dashboard'))# Redirect to teacher dashboard
        else:
            error_message = "Invalid username or password. Please try again."
            return render_template('login.html', error_message=error_message)
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']# Retrieve user type from form
        new_user = User(username=username, email=email, password=password, user_type=user_type)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        return render_template('signup.html')

@app.route('/register_child', methods=['GET','POST'])
@app.route('/register_child', methods=['GET', 'POST'])
def register_child():
    if request.method == 'POST':
        child_name = request.form['child_name']
        child_age = request.form['child_age']
        gender = request.form['child_gender']
        parent_id = session.get('user_id')
        if parent_id:
            new_child = Child(name=child_name, child_age=child_age, gender=gender, parent_id=parent_id)
            db.session.add(new_child)
            db.session.commit()
            session['child_id'] = new_child.id  # Set child_id in session
            flash('Child registered successfully!', 'success')
            return redirect(url_for('parent_dashboard'))
        else:
            flash('User session expired. Please log in again.', 'error')
            return redirect(url_for('login'))
    return render_template('child_form.html')

@app.route('/parent-dashboard')
def parent_dashboard():
    # Retrieve the username of the logged-in user from the session or database
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            username = user.username
            # Render parent dashboard template and pass the username
            return render_template('parents.html', username=username)
    return redirect(url_for('login'))

@app.route('/teacher_dashboard')
def teacher_dashboard():
    # Retrieve the username of the logged-in user from the session or database
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            username = user.username
            # Render parent dashboard template and pass the username
            return render_template('teachers.html', username=username)
    return redirect(url_for('login'))

@app.route('/display_children')
def display_children():
    user_id = session.get('user_id')
    if user_id:
        parent = User.query.get(user_id)
        if parent:
            children = parent.children
            return render_template('display_child.html', children=children)
    
    flash('User session expired. Please log in again.', 'error')
    return redirect(url_for('login'))


@app.route('/save_image', methods=['POST'])
def save_image():
    data = request.get_json()
    image_data = data.get('imageData', '')

    if not image_data:
        return 'No image data provided', 400

    try:
        image_data = image_data.split(",")[1]  # Remove 'data:image/png;base64,' part
        image_binary = base64.b64decode(image_data)
        
        file_name = 'captured_image.png'  # Generate a unique filename if needed
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        with open(file_path, 'wb') as f:
            f.write(image_binary)
        return 'Image saved successfully', 200
    except Exception as e:
        return f'Failed to save image: {str(e)}', 500

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process the image and save results
        image = cv2.imread(file_path)
        result = process_image()  # Define this function based on your image processing logic
        
        # Save the result in the database
        child_id = session.get('child_id')  # Ensure this is set when a child is selected
        if child_id:
            new_record = DyslexiaRecord(
                child_id=child_id,
                method='image_upload',
                result=str(result),
                game_time_played=None,
                game_hits=None,
                game_misses=None,
                game_score=None
            )
            db.session.add(new_record)
            db.session.commit()
        
        return jsonify({'success': 'Image uploaded and processed successfully'}), 200

    return jsonify({'error': 'Failed to upload image'}), 500


def process_images():
    results = []
    upload_folder = app.config['UPLOAD_FOLDER']
    for filename in os.listdir(upload_folder):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(upload_folder, filename)
            image = cv2.imread(image_path)
            
            # Check for handwriting in the image
            if is_handwriting_image(image):
                percentage = classify_letters(letters)
                results.append({
                    'filename': filename,
                    'result': f"Handwriting detected. Dyslexia probability: {percentage}%"
                })
            else:
                results.append({
                    'filename': filename,
                    'result': "Not a handwriting image."
                })

    if results:
        return {'success': True, 'results': results}
    else:
        return {'success': False, 'error': 'No handwriting detected in the uploaded images.'}

def is_handwriting_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 10:  
        return True
    return False

@app.route('/process-image', methods=['POST'])
def process_image():
    result = process_images()

    if result['success']:
        session['result'] = result  # Store the result in the session
        return jsonify({'redirect': url_for('results')})
    else:
        return jsonify(result)

@app.route('/results')
def results():
    result = session.get('result', None)

    if result is None:
        return redirect(url_for('upload_image'))  # Redirect to upload if no results found

    return render_template('results.html', results=result['results'])

@app.route('/capture-image')
def capture_image():

    return render_template('capture_image.html')

@app.route('/game_play')
def game_play():
    # Handle dyslexia detection through gameplay
    return render_template('game_play.html')

@app.route('/whac_a_mole')
def whac_a_mole():
    # Handle dyslexia detection through gameplay
    return render_template('whac_a_mole.html')

@app.route('/submit_game_data', methods=['POST'])
def submit_game_data():
    data = request.get_json()
    time_played = data.get('timePlayed')
    total_clicks = data.get('totalClicks')
    hits = data.get('hits')
    misses = data.get('misses')
    score = data.get('score')
    
    # Prepare the data for the model
    input_data = np.array([[time_played, total_clicks, hits, misses]])
    
    # Make prediction
    prediction = model.predict(input_data)
    is_dyslexic = np.argmax(prediction)
    
    # Save the result in the database
    child_id = session.get('child_id')  # Ensure this is set when a child is selected
    if child_id:
        new_record = DyslexiaRecord(
            child_id=child_id,
            method='whac_a_mole',
            result=str(is_dyslexic),
            game_time_played=time_played,
            game_hits=hits,
            game_misses=misses,
            game_score=score
        )
        db.session.add(new_record)
        db.session.commit()
    
    return jsonify({
        'timePlayed': time_played,
        'totalClicks': total_clicks,
        'hits': hits,
        'misses': misses,
        'score': score,
        'is_dyslexic': str(is_dyslexic)
    })

if __name__ == '__main__':
    # Set up the application context
    with app.app_context():
        # Create all database tables
        db.create_all()
    
    # Run the Flask app
    app.run(debug=True)