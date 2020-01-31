from manage import db, app

class User(db.Model):
    __tablename__ = 'User'
    #uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    firstName = db.Column(db.String(80), nullable=False)
    lastName = db.Column(db.String(80), nullable=False)
    childFirstName = db.Column(db.String(80), nullable=False)
    childLastName = db.Column(db.String(80), nullable=False)
    userRole = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    entries = db.relationship('Entry', backref='User', lazy=True)

    def __init__(self, firstName=None, lastName=None, childFirstName=None, childLastName=None, userRole=None, email=None, password=None):
        self.firstName=firstName
        self.lastName=lastName
        self.childFirstName=childFirstName
        self.childLastName=childLastName
        self.userRole=userRole
        self.email=email
        self.password=password
    
    def __repr__(self):
        # TODO: might want to get rid of password in repr
        return "<User(userid={}, firstName={}, lastName={}, childFirstName={}, childLastName={}, userRole={}, email={}, password={})>".format(self.userid, self.firstName, self.lastName,
                self.childFirstName, self.childLastName, self.userRole, self.email, self.password)

class Entry(db.Model):
    entryid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.userid'))
    target_behavior = db.Column(db.String(255), nullable=False)
    home_school_goal = db.Column(db.String(255), nullable=False)
    action_plan_one = db.Column(db.String(255), nullable=False)
    action_plan_two = db.Column(db.String(255))
    action_plan_three = db.Column(db.String(255))
    action_plan_four = db.Column(db.String(255))
    action_plan_five = db.Column(db.String(255))
    goal_rating = db.Column(db.Integer(), nullable=False)
    date = db.Column(db.Date())

    def serialize(self):
        action_plans = [self.action_plan_one]
        if self.action_plan_two != None:
            action_plans.append(self.action_plan_two)
        if self.action_plan_three != None:
            action_plans.append(self.action_plan_three)
        if self.action_plan_four != None:
            action_plans.append(self.action_plan_four)
        if self.action_plan_five != None:
            action_plans.append(self.action_plan_five)
        return {
            'date':self.date.isoformat(),
            'target_behavior':self.target_behavior,
            'home_school_goal':self.home_school_goal,
            'action_plans':action_plans,
            'goal_rating':self.goal_rating,
            'user_id':self.user_id
        }
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