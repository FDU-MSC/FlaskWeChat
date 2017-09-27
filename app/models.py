from app import db


class Talk(db.Model):
    __tablename__ = 'talk'
    id = db.Column(db.Integer, primary_key=True)
    come = db.Column(db.Boolean, default=False)
    wcid = db.Column(db.String(50), unique=True)
    context = db.Column(db.String(255))


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    wcid = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    state = db.Column(db.Integer, default=1)
    sid = db.Column(db.String(12))
    ans1 = db.Column(db.String(255))
    ans2 = db.Column(db.String(255))
    ans3 = db.Column(db.String(255))
    ans4 = db.Column(db.String(255))


class Record(db.Model):
    __tablename__ = 'record'
    id = db.Column(db.Integer, primary_key=True)
    wcid = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    state = db.Column(db.Integer, default=1)
