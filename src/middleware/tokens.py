from database.db import db


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
