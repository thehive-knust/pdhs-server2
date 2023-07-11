from database.db import db
from pdhs_app.models.approvals import errors as ApprovalErrors

class Approval(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default="pending")

    def __repr__(self):
        return '<Approval %r>' % self.id

    @classmethod
    def find_by_id(cls, id):
        try:
            result = cls.query.filter_by(id=id).first()
        except:
            raise ApprovalErrors.ApprovalDontExistError(f"Approval with {id} does not exist")
        return result

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def to_json(self):
        approval = {
            'id': self.id,
            'document_id': self.document_id,
            'recipient_id': self.recipient_id,
            'status': self.status
        }
        return approval
