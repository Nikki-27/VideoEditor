from databases import db

class Subtitle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Float, nullable=False)
    text = db.Column(db.String(200), nullable=False)
    video_filename = db.Column(db.String(100), nullable=False)
    subtitled_video_path = db.Column(db.String(100))
