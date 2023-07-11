from database.db import db


class College(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    faculties = db.relationship("Faculty", lazy='select', backref=db.backref('college', lazy='joined'))
    users = db.relationship("User", lazy='select', backref=db.backref('college', lazy='joined'))

    def __repr__(self):
        return '<College %r>' % self.name

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

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
        college = {
            'id': self.id,
            'name': self.name
        }
        return college
