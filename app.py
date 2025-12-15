# Date: 15/12/2025--dd/mm/yyyy. 
# Auther: Rashed Alothman.

# --- ROUTE STRUCTURE YOU PROVIDED ---
# '/' → landing/diagnostic page
# '/home' → main dashboard
# '/home/tasks/add_tasks' → add a task
# '/home/task/delete_task' → delete a task
# '/home/AddUsersToAccount' → placeholder
# '/home/User/about' → about‑me page
# '/login' → login page
from flask import Flask, request, render_template, redirect, url_for
tasks = []
app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/home') 
def home():
    return render_template('homepage.html', tasks=tasks)

@app.route('/homepage/tasks', methods=['GET'])
def get_tasks():
    return {'tasks': tasks}

@app.route('/homepage/tasks/add_Tasks',methods=['POST'])
def add_task():
    # 'title' matches the input name="title" in homepage.html
    title = request.form.get('title') 
    
    if title:
        new_task = {
            'id': len(tasks) + 1,
            'title': title
        }
        tasks.append(new_task)
    
    # Reload the homepage to show the new task
    return redirect(url_for('home'))

def addtasks():
    data = request.get_json()
    description = data.get('description')
    task ={
        'id':len(tasks)+1,
        'description':description
    }
    tasks.append(task)
    return {'message':'task addad','task':task},201

@app.route('/homepage/tasks/delete_task',methods=['DELETE'])
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
