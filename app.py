# Date: 21/12/2025--dd/mm/yyyy. 
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

import logging
from datetime import datetime 
from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.exc import SQLAlchemyError
from uuid import uuid4
from typing import Optional
import os


answer_for_data_not_found = 'Invalid or missing data'
error_massage_for_try_except_Exception_in_jsonify_fromat='An unexpected error occurred'
error_massage_for_database = 'Database error occurred'
# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tms.db"
# if you tracks changes to objects and sends signals before and after modifications just change the value to True; it may have a performance impact
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the base model
class Task(db.Model):
    __tablename__ = 'tasks'
    id: Mapped[str] = mapped_column(String(8), primary_key=True, default=lambda: str(uuid4())[:8])
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    due_date: Mapped[Optional[datetime]] = mapped_column(db.DateTime, nullable=True)
    completed: Mapped[bool] = mapped_column(db.Boolean, default=False)
    priority: Mapped[str] = mapped_column(String(10),default="low")
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
            'Due Date': self.due_date.strftime('%Y-%m-%d %H:%M:%S') if self.due_date else None,
            'completed': self.completed,
            'priority': self.priority,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')}

@app.route('/')
def landing():
    """Landing page."""
    return render_template('landing.html')

@app.route('/homepage')
def homepage():
    """Dashboard - displays all tasks."""
    return render_template('homepage.html')
    
@app.route('/login')
def login():
    """Login page."""
    return render_template('login.html')

@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')

@app.route('/homepage/api/tasks', methods=['GET'])
def get_tasks():
    try:
        completed_param = request.args.get('completed')

        priority_param = request.args.get('priority')

        sort_by =   request.args.get('sort','created_at')

        query = Task.query

        if completed_param is not None:
            completed_bool = completed_param.lower() == 'true'
            query = query.filter_by(completed=completed_bool)


        if priority_param :
            query = query.filter_by(priority=priority_param)

        if sort_by == 'created_at':
            query = query.order_by(Task.created_at.desc())
        elif sort_by == 'due_date':
            query = query.order_by(Task.due_date.asc().nullslast())
        elif sort_by == 'priority':
            priority_order = ['urgent', 'high', 'medium', 'low']
            query = query.order_by(db.case({p: i for i, p in enumerate(priority_order)}, value=Task.priority))

        tasks = query.all()
        return jsonify({'Tasks': [task.to_dict() for task in tasks]})
    except SQLAlchemyError as e:
        logger.error(f"Database error while Looking and sorting the tasks: {str(e)}")
        return jsonify({'error': error_massage_for_database}), 500
    except Exception as e:
        logger.error(f'there was error in showing Tasks: {str(e)}')
        return jsonify({'error': error_massage_for_try_except_Exception_in_jsonify_fromat}), 500

@app.route('/homepage/api/tasks/add_Tasks',methods=['POST'])
def add_task_api():
    try:
        data = request.get_json()

        if not data or 'description' not in data:
            return jsonify({'error': answer_for_data_not_found}), 400

        description = data.get('description')
        
        priority = data.get('priority', 'low').lower()
        
        valid_priorities = ['low', 'medium', 'high', 'urgent']
  
        if priority not in valid_priorities:
            return jsonify({'error': f'Priority must be one of: {valid_priorities}'}), 400
        
        new_task = Task(
            description = description,
            due_date = datetime.now(),
            priority = priority
            )
        db.session.add(new_task)
        db.session.commit()
        return jsonify({'message':'task added','task':new_task.to_dict()}),201
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error while adding task: {str(e)}")
        return jsonify({'error': error_massage_for_database}), 500
    except Exception as e:
        logger.error(f"Unexpected error while adding task: {str(e)}")
        return jsonify({'error': error_massage_for_try_except_Exception_in_jsonify_fromat}), 500

@app.route('/homepage/api/tasks/delete_task',methods=['DELETE'])
def delete_task():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': answer_for_data_not_found}), 400

        task_id = data.get('id')
        
        if not task_id:
            return jsonify({'error': 'Task ID is required'}), 400

        task = Task.query.filter_by(id=task_id).first()
        
        if not task:
            return jsonify({'message': 'Task not found'}), 404
        
        db.session.delete(task)
        db.session.commit()
        logger.info(f"Task deleted: {task_id}")
        return jsonify({'message': 'Task deleted successfully'}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error while deleting task: {str(e)}")
        return jsonify({'error': error_massage_for_database}), 500
    except Exception as e:
        logger.error(f"Unexpected error while deleting task: {str(e)}")
        return jsonify({'error': error_massage_for_try_except_Exception_in_jsonify_fromat}), 500


@app.route('/homepage/api/tasks/updated_task',methods=["PATCH"])
def updated_task():
    
    data = request.get_json()
    if not data:
        return jsonify({'error': answer_for_data_not_found}), 400

    task_id = data.get('id')
    if not task_id:
        return jsonify({'error': 'Task ID is required'}), 400

    task = Task.query.filter_by(id=task_id).first()
    
    if not task:
        return jsonify({'message': 'Task not found'}), 404

    new_description = data.get('description')
    completed = data.get('completed')

    if new_description is not None:
        task.description = new_description
    if completed is not None:
        task.completed = completed

    db.session.commit()

    return jsonify({'message': 'The Task has been updated', 'task':  task.to_dict()}), 200

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)