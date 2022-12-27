from database import db
from sqlalchemy import  ForeignKey

class User(db.Model):
    user_id = db.Column("user_id", db.Integer, primary_key = True)
    username = db.Column("username", db.String(16))
    fname = db.Column("fname", db.String(32))
    lname = db.Column("lname", db.String(32))
    email = db.Column("email", db.String(64))
    password = db.Column("password", db.String(16))
    

    def __init__(self,username,fname,lname,email,password):
        self.username = username
        self.fname = fname
        self.lname = lname
        self.email = email
        self.password = password


class Projects(db.Model):
    project_id = db.Column("project_id", db.Integer, primary_key = True)
    name = db.Column("name", db.String(32))
    description = db.Column("description", db.String(32))
    imagefile = db.Column("imagefile", db.String(128))
    due_date = db.Column("due_date", db.Date)
    start_date = db.Column("start_date", db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    creator = db.relationship("User", backref="projects", lazy=True)
    notes = db.relationship("Notes", backref="projects", lazy=True)
    tasks = db.relationship("Tasks", backref="projects", lazy=True)

    def __init__(self,name,description,due_date, start_date,user_id,imagefile):
        self.name = name
        self.description = description
        self.due_date = due_date
        self.start_date = start_date
        self.user_id = user_id
        self.imagefile = imagefile

class Tasks(db.Model):
    task_id = db.Column("task_id", db.Integer, primary_key = True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.project_id"), nullable=False)
    assigned_id =  db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    name = db.Column("name", db.String(32))
    description = db.Column("description", db.String(32))
    due_date = db.Column("due_date", db.Date)
    assigned = db.relationship("User", backref="tasks", lazy=True)

    def __init__(self,project_id,assigned_id,name,description,due_date):
        self.project_id = project_id
        self.assigned_id = assigned_id
        self.name = name
        self.description = description
        self.due_date = due_date 

class Notes(db.Model):
    note_id = db.Column("note_id", db.Integer, primary_key = True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.task_id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.project_id"), nullable=True)
    note = db.Column("note", db.String(32))
    flag = db.Column("flag", db.Integer, default=0)
    create_date = db.Column("due_date", db.Date)  
    creator = db.relationship("User", backref="notes", lazy=True)

    def __init__(self,project_id,task_id,user_id,note,create_date,flag):
        self.project_id = project_id
        self.task_id = task_id
        self.user_id = user_id
        self.note = note
        self.create_date = create_date
        self.flag = flag         
        



