from database.db import db


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    content = db.Column(db.String(1000), nullable=True)

    def __repr__(self):
        return '<Comment on %r>' % self.document_id

    @classmethod
    def find_by_id(cls, id):
        return cls.query.get(id)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def to_json(self):
        comment = {
            'id': self.id,
            'sender_id': self.sender_id,
            'document_id': self.document_id,
            'content': self.content
        }
        return comment
