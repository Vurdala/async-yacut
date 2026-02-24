from datetime import datetime

from yacut import db


class URLMap(db.Model):
<<<<<<< HEAD
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(255), nullable=False)
    short = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
=======
    ...
>>>>>>> 49d2e9456624819a7595eae1ed67115cd43bd364
