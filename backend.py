import json
from flask import Flask, Response, request, jsonify, send_file
from flask_cors import CORS
import os
import cv2
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'uploads'
SUBTITLES_FOLDER = 'subtitles'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(SUBTITLES_FOLDER):
    os.makedirs(SUBTITLES_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SUBTITLES_FOLDER'] = SUBTITLES_FOLDER

# Define the Subtitle model
class Subtitle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Float, nullable=False)
    text = db.Column(db.String, nullable=False)
    video_filename = db.Column(db.String, nullable=False)
    subtitled_video_path = db.Column(db.String)

# Create the database tables within the application context
with app.app_context():
    db.create_all()

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video part'})

    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        return jsonify({'message': 'Video uploaded successfully'})

""" @app.route('/add_subtitles', methods=['POST'])
def add_subtitles():
    data = request.json
    video_filename = data['videoFilename']
    subtitles = data['subtitles']
    
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'subtitled_' + video_filename)
    
    add_subtitles_to_video(video_path, output_path, subtitles)
    
    try:
        with open(output_path, 'rb') as output_video:
            response_data = {
                'message': 'Subtitles added successfully',
                'videoBlob': output_video.read()
            }

        return Response(response=json.dumps(response_data), status=200, mimetype='video/mp4')
    except Exception as e:
        return jsonify({'error': str(e)}) """

@app.route('/add_subtitles', methods=['POST'])
def add_subtitles():
    data = request.json
    video_filename = data['videoFilename']
    subtitles = data['subtitles']
    
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'subtitled_' + video_filename)
    
    add_subtitles_to_video(video_path, output_path, subtitles)
    
    try:
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)})

def add_subtitles_to_video(input_video_path, output_video_path, subtitles):
    cap = cv2.VideoCapture(input_video_path)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, cap.get(cv2.CAP_PROP_FPS), (int(cap.get(3)), int(cap.get(4))))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000

        for caption in subtitles:
            timestamp = time_to_seconds(caption['timestamp'])
            text = caption['text']

            if current_time >= timestamp:
                # Add text overlay for captions
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                font_color = (255, 255, 255)
                font_thickness = 1
                text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
                text_x = int((frame.shape[1] - text_size[0]) / 2)
                text_y = frame.shape[0] - 20
                background_color = (0, 0, 0)
                cv2.rectangle(frame, (text_x, text_y - text_size[1]), (text_x + text_size[0], text_y), background_color, -1)
                cv2.putText(frame, text, (text_x, text_y), font, font_scale, font_color, font_thickness)

        out.write(frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

def time_to_seconds(timestamp):
    parts = timestamp.split(':')
    if len(parts) == 3:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    else:
        try:
            return int(timestamp)
        except ValueError:
            raise ValueError("Invalid timestamp format. Expected hh:mm:ss or seconds")



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
