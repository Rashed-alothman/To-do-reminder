# Date: 20/12/2025--dd/mm/yyyy. 
# Auther: Rashed Alothman.

# Description: This is a simple Task Management System (TMS) web application built using Flask and SQLAlchemy.
# The application allows users to add, delete, and view tasks through both HTML pages and RESTful API endpoints.

# Routes:
# '/' → landing/diagnostic page
# '/homepage' → main dashboard
# '/homepage/tasks/add_tasks' → add a task
# '/homepage/task/delete_task' → delete a task
# '/homepage/AddUsersToAccount' → placeholder
# '/homepage/User/about' → about‑me page
# '/login' → login page


from datetime import datetime 
from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from uuid import uuid4
from typing import Optional
import uuid

tasks = []
# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tms.db"
# if you tracks changes to objects and sends signals before and after modifications just change the value to True; it may have a performance impact
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the base model
class Task(db.Model):
    __tablename__ = 'tasks'
    id: Mapped[str] = mapped_column(String(8), primary_key=True, default=lambda: str(uuid4())[:8])
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    due_date: Mapped[Optional[datetime]] = mapped_column(db.DateTime, nullable=True)
    completed: Mapped[bool] = mapped_column(db.Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)
    
    # Representation method for debugging
    def __repr__(self) -> str:
        due_date_str = self.due_date.strftime('%Y-%m-%d %H:%M:%S') if self.due_date else 'None'
        return f"Task(id={self.id}, description={self.description}, due_date={due_date_str}, completed={self.completed})"
    
    # Convert to dictionary
    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'due_date': self.due_date.strftime('%Y-%m-%d %H:%M:%S') if self.due_date else None,
            'completed': self.completed,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/homepage') 
def homepage():
    return render_template('homepage.html', tasks=tasks)


@app.route('/homepage/tasks/add_Tasks',methods=['POST'])
def add_task_html():
    title = request.form.get('title') 
    
    if title:
        new_task = {
            'id': str(uuid.uuid4())[:8],
            'title': title
        }
        tasks.append(new_task)
    
    return redirect(url_for('homepage'))

@app.route('/homepage/task/delete',methods=['POST'])
def delete_task_html():
    task_id =request.form.get('task_id')
    
    if not task_id:
        return({'erorr':'No data Provided'}),404
    
    for task in tasks:
        if task['id'] == task_id:
            tasks.remove(task)
            break
    return redirect(url_for('homepage'))

@app.route('/homepage/api/tasks', methods=['GET'])
def get_tasks():
    return {'Tasks': tasks}

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
def delete_task():
    data=request.get_json()
    if not data:
        return ({'error':' No data Provided'}), 400
    task_id=data.get('id')
    task_have_been_deleted = False
    if not task_id:
        return ({'error': 'Task ID is requried'}), 400
    else:
        for task in tasks:
            if task['id']==task_id:
                tasks.remove(task)
                task_have_been_deleted =True
                break
    if task_have_been_deleted:
        return ({'message':' Task deleted'}), 200
    else:
        return ({'message': 'Task not found, no found'}), 404

@app.route('/homepage/api/tasks/updatedtask',methods=["PATCH"])
def updatd_task():
    data = request.get_json()
    if not data:
        return {'error': 'Invalid or missing data'}, 400

    task_id = data.get('id')
    if not task_id:
        return {'error': 'Task ID is required'}, 400

    new_description = data.get('description')
    completed = data.get('completed')

    for task in tasks:
        if task.get('id') != task_id:
            continue
        if new_description is not None:
            task['description'] = new_description
        if completed is not None:
            task['completed'] = completed
        return {'message': 'The Task has been updated', 'task': task}, 200

    return {'message': 'Task not found'}, 404

@app.route('/homepage/AddUsersToAccout')
def add_users(email):
    return 0

@app.route('/homepage/User/about me')
def about_me():
    return 0

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)