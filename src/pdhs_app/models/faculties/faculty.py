from database.db import db


class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    college_id = db.Column(db.String(10), db.ForeignKey('college.id', use_alter=True), nullable=False)
    departments = db.relationship('Department', lazy='select', backref=db.backref('faculty', lazy='joined'))
    users = db.relationship("User", lazy='select', backref=db.backref('faculty', lazy='joined'))

    def __repr__(self):
        return '<Faculty %r>' % self.name

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
        faculty = {
            'id': self.id,
            'name': self.name,
            'college_id': self.college_id
        }
        return faculty
