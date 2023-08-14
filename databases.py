from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class Subtitle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Float, nullable=False)
    text = db.Column(db.String, nullable=False)
    video_filename = db.Column(db.String, nullable=False)
    subtitled_video_path = db.Column(db.String)  # Add this attribute for storing subtitled video path


    def __repr__(self):
        return f"<Subtitle {self.id}>"
