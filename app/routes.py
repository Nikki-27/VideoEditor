from flask import Blueprint, app, jsonify, request, send_file, send_from_directory, render_template
from databases import db
from app.models import Subtitle
import os
import cv2

bp = Blueprint('routes', __name__)

@bp.route('/')
def view_subtitles():
    subtitles = Subtitle.query.all()
    return render_template('subtitles.html', subtitles=subtitles)

# ... (other route definitions)
@bp.route('/')
def view_subtitles():
    subtitles = Subtitle.query.all()  # Fetch all entries from the Subtitle model
    return render_template('subtitles.html', subtitles=subtitles)

@app.route('/save_subtitles', methods=['POST'])
def save_subtitles():
    try:
        data = request.json
        subtitle = data['subtitles']

        for subtitle in subtitle:
            new_subtitle = Subtitle(
                timestamp=subtitle['timestamp'],
                text=subtitle['text'],
                video_filename=subtitle['video_filename']
            )
            db.session.add(new_subtitle)

        db.session.commit()
        return jsonify({'message': 'Subtitles saved successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)})




@bp.route('/upload', methods=['POST'])
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

@app.route('/add_subtitles', methods=['POST'])
def add_subtitles():
    data = request.json
    video_filename = data['videoFilename']
    subtitles = data['subtitles']
    print(subtitles)
    
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'subtitled_' + video_filename)
    
    # Process video and add subtitles based on the provided timestamps and text
    add_subtitles_to_video(video_path, output_path, subtitles)
    
    return send_file(output_path, as_attachment=True)

def add_subtitles_to_video(input_video_path, output_video_path, subtitles):
    cap = cv2.VideoCapture(input_video_path)

    # Define the output codec and VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, cap.get(cv2.CAP_PROP_FPS), (int(cap.get(3)), int(cap.get(4))))

    # Loop through each frame in the video
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000

        # Add text overlay for captions
        for caption in subtitles:
            timestamp = caption['timestamp']
            text = caption['text']

            if current_time >= timestamp:
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5  # Font size
                font_color = (255, 255, 255)  # White color
                font_thickness = 1
                text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
                text_x = int((frame.shape[1] - text_size[0]) / 2)
                text_y = frame.shape[0] - 20
                background_color = (0, 0, 0)  # Black background
                cv2.rectangle(frame, (text_x, text_y - text_size[1]), (text_x + text_size[0], text_y), background_color, -1)
                cv2.putText(frame, text, (text_x, text_y), font, font_scale, font_color, font_thickness)

        # Write the frame to the output video
        out.write(frame)

    # Release the VideoCapture and VideoWriter objects
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    subtitle_entry = Subtitle.query.filter_by(video_filename=output_video_path).first()
    subtitle_entry.subtitled_video_path = output_video_path
    db.session.commit()

@bp.route('/get_subtitled_video/<video_filename>', methods=['GET'])
def get_subtitled_video(video_filename):
    subtitled_video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'subtitled_' + video_filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'subtitled_' + video_filename, as_attachment=True)


@bp.route('/get_output_video/<video_filename>', methods=['GET'])
def get_output_video(video_filename):
    output_video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output_' + video_filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'output_' + video_filename, as_attachment=True)

