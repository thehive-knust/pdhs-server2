from flask import Blueprint, request, jsonify, render_template
from pdhs_app.models.users.user import User  # 
from pdhs_app.models.departments.department import Department
from pdhs_app.models.portfolios.portfolio import Portfolio
from pdhs_app.models.colleges.college import College
from pdhs_app.models.faculties.faculty import Faculty

from sqlalchemy import null
from database.db import db

bp = Blueprint('departments', __name__, url_prefix='/departments')


@bp.route('/get/<string:college_id>', methods=['GET'])
def get_college_departments(college_id):
    if request.method == 'GET':
        faculty_obj_lst = Faculty.query.filter_by(college_id=college_id) 
        faculty_json_lst = [faculty_obj.to_json() for faculty_obj in faculty_obj_lst]
        department_obj_lsts = [Department.query.filter_by(faculty_id=faculty['id']) for faculty in faculty_json_lst]
        
        departments = []
        
        for lst in department_obj_lsts:
            for lst_obj in lst:
                departments.append(lst_obj.to_json())
        return jsonify(departments=departments)

    
@bp.route('/faculty/<int:faculty_id>', methods=['GET'])
def get_faculty_departments(faculty_id):
    result = Department.query.filter_by(faculty_id=faculty_id)
    department_json_lst = [department.to_json() for department in result]
    return jsonify(departments=department_json_lst)
    
    
@bp.route('/', methods=['GET'])
def get_all_departments():
    """
    Get all the departments in the department
    table.
    """
    if request.method == 'GET':
        departments = []
        result = []
        error_msg = None
        try:
            result = Department.query.all()
        except:
            error_msg = 'Error occured retrieving departments'
        if len(result) == 0:
            error_msg = 'No departments available'
        if error_msg is not None:
            return jsonify(msg=error_msg)
        else:
            for department in result:
                departments.append(department.to_json())
            return jsonify(departments=departments)


@bp.route('/<string:department_id>', methods=['GET'])
def get_department_by_id(department_id):
    """
    Get a particular department by id
    """
    if request.method == 'GET':
        error_msg = None
        department = None
        if department_id == "others":
            try:
                department = Department.find_by_id(department_id)
            except:
                error_msg = "No department not found"
        else:
            try:
                department = Department.find_by_id(department_id)
            except:
                error_msg = f'No department with ID {department_id} found'
                
        if error_msg is not None:
            return jsonify(msg=error_msg), 404
        elif department is not None:
            return jsonify(department.to_json())


@bp.route('/new', methods=['POST', 'GET'])
def create_department():
    """
    Create a department
    """
    if request.method == 'POST':
        _id = request.form['id'] if request.form['id'] else request.json.get('id', None) 
        name = request.form['name'] if request.form['name'] else request.json.get('name', None)
        faculty_id = request.form['faculty_id'] if request.form['faculty_id'] else request.json.get('faculty_id', None)
        
        error_msg = None
        if not id:
            error_msg = 'Id is required.'
        elif not name:
            error_msg = 'Name is required.'
        elif not faculty_id:
            faculty_id = 0
        if error_msg is not None:
            return jsonify(msg=error_msg), 500
        else:
            new_dept = Department(
                id=_id,
                name=name,
                faculty_id=int(faculty_id)
            )
            try:
                new_dept.save_to_db()
            except:
                return jsonify(msg='Error saving Department to database'), 500
            return jsonify(new_dept.to_json()), 201
    return render_template("departments/add_department.html")


@bp.route('/update/<string:department_id>', methods=['GET','POST'])
def update_department(department_id):
    """
    Update a Department
    """
    if request.method == 'POST':
        department_id = request.form['id'] if request.form['id'] else request.json.get('id', None)
        name = request.form['name'] if request.form['name'] else request.json.get('name', None)
        faculty_id = request.form['faculty_id'] if request.form['faculty_id'] else request.json.get('faculty_id', None)

        if not department_id:
            return jsonify(msg='Id is required.'), 500
        else:
            try:
                new_dept = Department.find_by_id(department_id)
                if new_dept is not None:
                    if department_id is not None:
                        new_dept.department_id = department_id
                    if name is not None:
                        new_dept.name = name
                    if faculty_id is not None:
                        new_dept.faculty_id = faculty_id
                    new_dept.save_to_db()
            except:
                return jsonify(msg='Error updating Department'), 500
            return jsonify(new_dept.to_json()), 201
    return render_template("departments/add_department.html")

@bp.route('/delete/<string:department_id>', methods=['DELETE'])
def delete_department(department_id):
    if request.method == 'DELETE':
        error_msg = None
        try:
            department = Department.find_by_id(department_id)
        except:
            error_msg = 'Error occured finding department'
        if department is not None:
            try:
                department.delete_from_db()
            except:
                error_msg = 'Error occured deleting Department'
        if error_msg is not None:
            return jsonify(msg=error_msg), 404
        else:
            return jsonify(msg='Department deleted successfully')


@bp.route('get_portfolio/<string:department_id>', methods=['GET'])
def get_department_portfolios(department_id):
    users = User.query.filter_by(department_id=department_id)
    portfolio_ids = list(set([ user.portfolio_id for user in users ].sort()))
    portfolios = []
    for id in portfolio_ids:
        portfolios.append(Portfolio.find_by_id(id).to_json())
    return jsonify(portfolios)


@bp.route('users/<string:department_id>', methods=['GET'])
def get_department_users(department_id):
    users = []
    
    if department_id == "others":
        others_list = User.query.filter(User.department_id.is_(None))
        for other in others_list:
            new = other.to_json()
            new['department_id'] = "others"
            users.append(new)
    else:
        user_obj_lst = User.query.filter_by(department_id=department_id)
        for user in user_obj_lst:
            users.append(user.to_json())

    return jsonify(department_users=users)
