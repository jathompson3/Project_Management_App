from database import db
import os                 # os is used to get environment variables IP & PORT
from flask import Flask , render_template ,request,redirect, url_for,session
import datetime
from datetime import date
from werkzeug.utils import secure_filename


#model imports
from models import User, Projects ,Tasks, Notes
from database import db
from forms import RegisterForm, LoginForm, noteModal

from flask_bcrypt import bcrypt

app = Flask(__name__)     # create an app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_project_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
app.config['SECRET_KEY'] = 'SE3155'

#  Bind SQLAlchemy db object to this Flask app
db.init_app(app)

# Setup models
with app.app_context():
    db.create_all()   # run under the app context

userid = 1

#make sure only valid dates get put in the db
def toDateFromForm(datestring): 
    try:
        due_date = datetime.datetime.strptime(datestring, '%Y-%m-%d') 
    except ValueError:
        due_date =  datetime.datetime.now() 
    return due_date  



@app.route('/')        
@app.route('/index')
def index():
    login_form = LoginForm()
    if session.get('user'):
        projects = db.session.query(Projects).all()
        edituser = db.session.query(User).filter_by(user_id=session['user_id']).first()

        for p in projects:
            if (p.due_date - p.start_date) != 0:
                p.percent = 100-round(((p.due_date - date.today())/(p.due_date - p.start_date)*100),0)
        else:
            p.percent = 0        
        return render_template('index.html', user = ['user'], projects = projects)
    else:
        return render_template("login.html", form=login_form)

@app.route('/login', methods=['POST', 'GET'])

def login():
    login_form = LoginForm()
    # validate_on_submit only validates using POST
    if login_form.validate_on_submit():
        # we know user exists. We can use one()
        the_user = db.session.query(User).filter_by(username=request.form['username']).first()
        
        if the_user == None:
            login_form.password.errors = ["Incorrect username and password."]
            return render_template("login.html", form=login_form)

        # user exists check password entered matches stored password
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), the_user.password):
            # password match add user info to session
            session['user'] = the_user.fname
            session['user_id'] = the_user.user_id
            session['username'] = the_user.username
            # render view
            return redirect(url_for('projects'))

        # password check failed
        # set error message to alert user
        login_form.password.errors = ["Incorrect username or password."]
        return render_template("login.html", form=login_form)
    else:
        # form did not validate or GET request
        return render_template("login.html", form=login_form)

@app.route('/logout')
def logout():
    if session.get('user'):
        session.clear()
    return redirect(url_for('login'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():
        # salt and hash password
        h_password = bcrypt.hashpw(
            request.form['password'].encode('utf-8'), bcrypt.gensalt())
        # get entered user data
        username = request.form['username']
        fname = request.form['firstname']
        lname = request.form['lastname']
        email = request.form['email']

        # create user model
        new_user = User(username, fname, lname, email, h_password)
        # add user to database and commit
        db.session.add(new_user)
        db.session.commit()
        # save the user's name to the session
        session['user'] = fname
        session['user_id'] = new_user.user_id  # access id value from user model of this newly added user
        # show user dashboard view
        return redirect(url_for('projects'))

    # something went wrong - display register view
    return render_template('register.html', form=form)

# show all projects
@app.route('/Projects')
def projects():
    
    if session.get('user'):
        #my_projects = db.session.query(Projects).filter_by(user_id=session['user_id']).all()
        my_projects = db.session.query(Projects).all()
        edituser = db.session.query(User).filter_by(user_id=session['user_id']).first()

        return render_template('ProjectGridView.html', projects=my_projects, user= edituser)
    else:
        return redirect(url_for('login'))


# get a project
@app.route('/Projects/<project_id>')
def get_project(project_id):

    if session.get('user'):
        edituser = db.session.query(User).filter_by(user_id=session['user_id']).first()

        noteform = noteModal()
        pj = db.session.query(Projects).filter_by(project_id=project_id).one()

        return render_template('projectdetail.html', project = pj, noteform = noteform, user = edituser)   
    else:
        return redirect(url_for('login'))


# create a project
@app.route('/NewProject')
def create_project():
    if session.get('user'):
        edituser = db.session.query(User).filter_by(user_id=session['user_id']).first()

        return render_template('editProject.html', user = edituser) 
    else:
        return redirect(url_for('login'))  

# comments for a project
@app.route('/comments/<project_id>')
def comments(project_id):
    if session.get('user'):
        edituser = db.session.query(User).filter_by(user_id=session['user_id']).first()

        return render_template('comments.html', user=edituser)  
    else:
        return redirect(url_for('login'))

# EDIT PROJECT
@app.route('/editProject/<project_id>', methods=['GET','POST'])
def editProject(project_id):

    if session.get('user'):

        if request.method == 'POST':

                saveloc = ""
                if request.files['file']:
                    f = request.files['file']
                    saveloc = "./static/images/uploads/" + secure_filename(f.filename)
                    f.save(saveloc)

                name = request.form['name']
                description = request.form['description']
                
                due_date = toDateFromForm(request.form['due_date'])  
                start_date = toDateFromForm(request.form['start_date'])  
        
                if int(project_id) != 0:
                    project = db.session.query(Projects).filter_by(project_id = project_id).one()
                    project.name = name
                    project.description = description
                    project.due_date = due_date
                    project.start_date = start_date
                    if saveloc:
                        project.imagefile = saveloc
                else:
                    project = Projects(name,description,due_date,start_date, session['user_id'],saveloc)
            

                db.session.add(project)
                db.session.commit()


                

                return redirect(url_for('get_project',project_id = project.project_id))
        else :
            if project_id:
                project = db.session.query(Projects).filter_by(project_id = project_id).one()
                return render_template('editProject.html',project = project)      
    else:
        return redirect(url_for('login'))

@app.route('/editTask/<task_id>', methods=['GET','POST'])
def editTask(task_id):
    if session.get('user'):
        if request.method == 'POST':
                name = request.form['name']
                description = request.form['description']

                due_date = toDateFromForm(request.form['due_date'])
                
                task = db.session.query(Tasks).filter_by(task_id = task_id).one()
                task.name = name
                task.description = description
                task.due_date = due_date

                db.session.add(task)
                db.session.commit()
        
                return redirect(url_for('get_project',project_id = task.project_id))
        else:
            if task_id:
                task = db.session.query(Tasks).filter_by(task_id = task_id).one()
                return render_template('editTask.html', task = task)
    else:
        return redirect(url_for('login')) 

@app.route('/newTask/<project_id>', methods=['GET','POST'])
def newTask(project_id):
    if session.get('user'):
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            
            due_date = toDateFromForm(request.form['due_date'])

            assigned_id = session['user_id']
        
            task = Tasks(project_id,assigned_id,name,description,due_date)
            db.session.add(task)
            db.session.commit()

            return redirect(url_for('get_project',project_id = task.project_id))    

        else:
            project = db.session.query(Projects).filter_by(project_id = project_id).one()

            return render_template('editTask.html', project_id = project.project_id)   
    else:
        return redirect(url_for('login'))

@app.route('/deleteTask/<task_id>', methods=['GET'])
def deleteTask(task_id):
    if session.get('user'):
        task = db.session.query(Tasks).filter_by(task_id = task_id).one()
        project_id = task.project_id  
        db.session.delete(task)
        db.session.commit()  
        return redirect(url_for('get_project',project_id = project_id))
    else:
        return redirect(url_for('login'))

@app.route('/deleteProject/<project_id>', methods=['GET'])
def deleteProject(project_id):
    if session.get('user'):
        pj = db.session.query(Projects).filter_by(project_id=project_id).one() 
        db.session.delete(pj)
        db.session.commit()  
        return redirect(url_for('index')) 
    else:
        return redirect(url_for('login'))  

@app.route('/addNote/<project_id>', methods=['POST'])
def addNote(project_id):
    if session.get('user'):
        form = request.form
        
        task_id = 0
        user_id = session['user_id']
        note = form['note']
        create_date = datetime.datetime.now() 
        flag = 0
        note = Notes(project_id,task_id,user_id,note,create_date,flag) 
        db.session.add(note)
        db.session.commit()  
        return redirect(url_for('get_project', project_id = project_id)) 
    else:
        return redirect(url_for('login')) 
        
@app.route('/deleteNote/<note_id>', methods=['GET'])
def deleteNote(note_id):
    if session.get('user'):
        note = db.session.query(Notes).filter_by(note_id=note_id).one()
        project_id = note.project_id
        db.session.delete(note)
        db.session.commit()  
        return redirect(url_for('get_project', project_id = project_id)) 
    else:
        return redirect(url_for('login'))  

@app.route('/flagNote/<note_id>', methods=['GET'])
def flagNote(note_id):
    if session.get('user'):
        note = db.session.query(Notes).filter_by(note_id=note_id).one()
        if note.flag >= 4:
             db.session.delete(note)
        else:
            note.flag = note.flag + 1
            db.session.add(note)

        project_id = note.project_id
        db.session.commit()  
        return redirect(url_for('get_project', project_id = project_id)) 
    else:
        return redirect(url_for('login'))  

@app.route('/about')
def about():
    login_form = LoginForm()
    if session.get('user'):
        edituser = db.session.query(User).filter_by(user_id=session['user_id']).first()

        return render_template('profileAbout.html', user = edituser)
    else:
        return render_template("login.html", form=login_form)       

@app.route('/profileEdit' , methods=['GET','POST'])
def profileEdit():
    login_form = LoginForm()
    if request.method == 'GET':
        if session.get('user'):
            edituser = db.session.query(User).filter_by(user_id=session['user_id']).first()
            return render_template('profileAboutEdit.html', user = edituser)
        else:
            return render_template("login.html", form=login_form)    


    elif request.method == 'POST':

        username = request.form['username']
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        h_password = request.form['password']

        h_password = bcrypt.hashpw(
            request.form['password'].encode('utf-8'), bcrypt.gensalt())


        edituser = db.session.query(User).filter_by(user_id=session['user_id']).first()
        edituser.username = username
        edituser.fname = fname
        edituser.lname = lname
        edituser.email = email
        edituser.password = h_password
        db.session.add(edituser)
        db.session.commit()
        # save the user's name to the session
        session['user'] = fname
        session['user_id'] = edituser.user_id  # access id value from user model of this newly added user
        # show user dashboard view
        return redirect(url_for('profileEdit'))






app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 5000)),debug=True)

# source venv/Scripts/activate
# To see the web page in your web browser, go to the url,
#   http://127.0.0.1:5000

  
