# Date: 15/12/2025--dd/mm/yyyy. 
# Auther: Rashed Alothman.

# --- ROUTE STRUCTURE YOU PROVIDED ---
# '/' → landing/diagnostic page
# '/homepage' → main dashboard
# '/homepage/tasks/add_tasks' → add a task
# '/homepage/task/delete_task' → delete a task
# '/homepage/AddUsersToAccount' → placeholder
# '/homepage/User/about' → about‑me page
# '/login' → login page
from datetime import datetime 
from flask import Flask, request, render_template, redirect, url_for
import uuid
tasks = []
app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/homepage') 
def homepage():
    return render_template('homepage.html', tasks=tasks)

@app.route('/homepage/tasks', methods=['GET'])
def get_tasks():
    return {'Tasks': tasks}

@app.route('/homepage/tasks/add_Tasks',methods=['POST'])
def add_task_html():
    title = request.form.get('title') 
    
    if title:
        new_task = {
            'id': str(uuid.uuid4())[:8],
            'title': title
        }
        tasks.append(new_task)
    
    return redirect(url_for('home'))

@app.route('/homepage/api/tasks/add_Tasks',methods=['POST'])
def add_task_api():
    data = request.get_json()
    if not data or 'description' not in data:
        return {'error': 'Invalid or missing data'}, 400
    description = data.get('description')
    task ={
        'id':str(uuid.uuid4())[:8],
        'description':description,
        'Due date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'completed':False
    }
    tasks.append(task)
    return {'message':'task added','task':task},201

@app.route('/homepage/api/tasks/delete_task',methods=['DELETE'])
def deleteTask():
    data=request.get_json()
    if not data:
        return ({'error':' No data Provided'}), 400
    task_id=data.get('id')
    TaskHaveBeenDeleted = False
    if not task_id:
        return ({'error': 'Task ID is requried'}), 400
    else:
        for task in tasks:
            if task['id']==task_id:
                tasks.remove(task)
                TaskHaveBeenDeleted =True
                break
    if TaskHaveBeenDeleted:
        return ({'message':' Task deleted'}), 200
    else:
        return ({'message': 'Task not found, no found'}), 404

@app.route('/homepage/api/tasks/updatedtask',methods=["PATCH"])
def updatdTask():
    data=request.get_json()
    
    task_id=data.get('id')
    
    taskhavebeenupdated=False
    
    Newdescription = data.get('description')
    
    completed=data.get('completed')
    
    found_task = None
    if not data:
        return {'error': 'Invalid or missing data'}, 400
    if not task_id:
        return ({'error': 'Task ID is requried'}), 400
    else:
        for task in tasks:
            if task['id']==task_id:
                if Newdescription is not None:
                    task['description'] = Newdescription
                if completed is not None:
                    task['completed'] = completed
                found_task = task
                taskhavebeenupdated=True
                break
        if taskhavebeenupdated:
            return {'message': 'The Task have been updated', 'task': found_task}, 200
        else:
            return({'message ':'The Task fail to update'}),404 

@app.route('/homepage/AddUsersToAccout')
def addUsers(email):
    return 0

@app.route('/homepage/User/about me')
def aboutMe():
    return 0


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/homepage/login')
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'
    return render_template('login.html', error=error)
