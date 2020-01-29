from manage import db, app

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    usertype = db.Column(db.String(120), nullable=False)

    def __init__(self, id=None, username=None, password=None):
        self.id=id
        self.username=username
        self.password=password
'''
class Entry(db.Model):
    __tablename__ = 'entry'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    action_plans = db.relationship('Action_Plan', secondary='junction_entry_action', lazy='subquery', backref=db.backref('entry', lazy=True))
    
    def __init__(self, id=None, parent_id=None, teacher_id=None, action_plans=None):
        self.id=id
        self.parent_id=parent_id
        self.teacher_id=teacher_id
        self.action_plans=action_plans

class Action_Plan(db.Model):
    __tablename__ = 'action_plan'
    id = db.Column(db.Integer, primary_key=True)

junction_entry_action = db.Table('junction_entry_action',
    db.Column('entry_id', db.Integer, db.ForeignKey('entry.id'), primary_key=True),
    db.Column('action_plan_id', db.Integer, db.ForeignKey('action_plan.id'), primary_key=True)
)
'''