from manage import db, app

# 1: move the field
# 2: change the database
# 3: debug
# 4: notifications
# 5: something quick for the new landing page
# 6: profit

class User(db.Model):
    __tablename__ = "User"
    #uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.String(255), primary_key=True, autoincrement=False, unique=True)
    userRole = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(1023), nullable=False)
    targetBehavior = db.Column(db.String(1023), nullable=False)
    homeSchoolGoal = db.Column(db.String(1023), nullable=False)
    email = db.Column(db.String(1023), nullable=False)
    phoneNumber = db.Column(db.String(80), nullable=True)

    entries = db.relationship('Entry', backref='User', lazy=True)
    actionplans = db.relationship('ActionPlan', cascade="all, delete-orphan", backref='User', lazy=True)

    def __init__(self, id=None, userRole=None, password=None, targetBehavior=None, homeSchoolGoal=None, email=None, phoneNumber=None):
        # TODO: if idNum is None, throw an exception so it can be handled with appropriately.
        self.id=id
        self.userRole=userRole
        self.password=password
        self.targetBehavior=targetBehavior
        self.homeSchoolGoal=homeSchoolGoal
        self.email=email
        self.phoneNumber=phoneNumber
    
    def serialize(self):
        return {
            'userID' : self.idNum,
            'role' : self.userRole,
            'targetBehavior' : self.targetBehavior,
            'homeSchoolGoal' : self.homeSchoolGoal,
            'email' : self.email
        }

    def __repr__(self):
        # TODO: might want to get rid of password in repr
        #return "<User(userid={}, firstName={}, lastName={}, childFirstName={}, childLastName={}, userRole={}, email={}, password={})>".format(self.userid, self.firstName, self.lastName,
        #        self.childFirstName, self.childLastName, self.userRole, self.email, self.password)
        return "<User(id={}, userRole={})>".format(self.id, self.userRole)

class ActionPlan(db.Model):
    __tablename__ = "ActionPlan"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    userId = db.Column(db.String(255), db.ForeignKey('User.id'))
    stepName = db.Column(db.String(1023))
    order = db.Column(db.Integer)

    def serialize(self):
        return {
            'actionPlanId' : self.actionPlanId,
            'userId' : self.userId,
            'stepName' : self.stepName,
            'order' : self.order
        }

class Entry(db.Model):
    __tablename__ = "Entry"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    userId = db.Column(db.String(255), db.ForeignKey('User.id'))
    actionPlanOne = db.Column(db.String(1023), nullable=False)
    actionPlanTwo = db.Column(db.String(1023))
    actionPlanThree = db.Column(db.String(1023))
    actionPlanFour = db.Column(db.String(1023))
    actionPlanFive = db.Column(db.String(1023))
    actionPlanSix = db.Column(db.String(1023))
    actionPlanSeven = db.Column(db.String(1023))
    actionPlanEight = db.Column(db.String(1023))
    actionPlanNine = db.Column(db.String(1023))
    actionPlanTen = db.Column(db.String(1023))
    targetBehavior = db.Column(db.String(1023), nullable=False)
    homeSchoolGoal = db.Column(db.String(1023), nullable=False)
    goalRating = db.Column(db.Integer(), nullable=False)
    # TODO: Date uniqueness fix.
    date = db.Column(db.Date())
    signature = db.Column(db.String(50000), nullable=False)

    def serialize(self):
        all_action_plans = [self.actionPlanOne, self.actionPlanTwo, self.actionPlanThree, self.actionPlanFour, self.actionPlanFive,
                            self.actionPlanSix, self.actionPlanSeven, self.actionPlanEight, self.actionPlanNine, self.actionPlanTen]
        action_plans = [self.actionPlanOne]
        for ap in all_action_plans[1:]:
            if ap != None:
                action_plans.append(ap)
        return {
            'date':self.date.isoformat(),
            'action_plans':action_plans,
            'goal_rating':self.goalRating,
            'user_id':self.userId
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
