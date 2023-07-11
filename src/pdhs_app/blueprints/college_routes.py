from flask import Blueprint, request, jsonify, render_template
from pdhs_app.models.users.user import User  
from pdhs_app.models.colleges.college import College

bp = Blueprint('colleges', __name__, url_prefix='/colleges')


@bp.route('/test', methods=['GET', 'POST'])
def test():
    College(id=1, name="College of Engineering", provost_id=None).save_to_db()
    result = College.query.all()
    return jsonify(result)
    

@bp.route('/', methods=['GET'])
def get_all_colleges():
    """
    Get all the colleges in the college
    table.
    """
    if request.method == 'GET':
        colleges = []
        result = []
        error_msg = None
        try:
            result = College.query.all()
        except:
            error_msg = 'Error occured retrieving colleges'
        if len(result) == 0:
            error_msg = 'No colleges available'
        if error_msg is not None:
            return jsonify(msg=error_msg)
        else:
            for college in result:
                colleges.append(college.to_json())
            return jsonify(colleges=colleges)


@bp.route('/<string:college_id>', methods=['GET'])
def get_college_by_id(college_id):
    """
    Get a particular college by id
    """
    if request.method == 'GET':
        error_msg = None
        try:
            college = College.find_by_id(college_id)
        except:
            error_msg = 'Error occured finding college'
        if error_msg is not None:
            return jsonify(msg=error_msg), 404
        elif college is not None:
            return jsonify(college.to_json())


@bp.route('/new', methods=['GET', 'POST'])
def create_new_college():
    """
    Create a college
    """
    if request.method == 'POST':
        _id = request.form['id'] if request.form['id'] else request.json.get('id', None) 
        name = request.form['name'] if request.form['name'] else request.json.get('name', None)
        error_msg = None
        if not _id:
            error_msg = 'Id is required.'
        elif not name:
            error_msg = 'Name is required.'
        if error_msg is not None:
            return jsonify(msg=error_msg), 500
        else:
            new_college = College(id=_id, name=name)
            print("==========================================================", new_college.to_json())
            try:
                new_college.save_to_db() # = College(id=int(_id), name=name, provost_id=provost_id).
            except:
                return jsonify(msg='Error saving College to database'), 500
            return jsonify(new_college.to_json()), 201 
    return render_template("colleges/add_college.html")


@bp.route('/update/<string:college_id>', methods=['PUT'])
def update_college(college_id):
    """
    Update a College
    """
    if request.method == 'PUT':
        college_id = request.json.get('id', None)
        name = request.json.get('name', None)

        if not college_id:
            return jsonify(msg='Id is required.'), 500
        else:
            try:
                new_college = College.find_by_id(college_id)
                if new_college is not None:
                    if name is not None:
                        new_college.name = name
                    new_college.save_to_db()
            except:
                return jsonify(msg='Error updating College'), 500
            return jsonify(new_college.to_json()), 201


@bp.route('/delete/<string:college_id>', methods=['DELETE'])
def delete_college(college_id):
    if request.method == 'DELETE':
        error_msg = None
        try:
            college = College.find_by_id(college_id)
        except:
            error_msg = 'Error occured finding college'
        if college is not None:
            try:
                college.delete_from_db()
            except:
                error_msg = 'Error occured deleting College'
        if error_msg is not None:
            return jsonify(msg=error_msg), 404
        else:
            return jsonify(msg='College deleted successfully')
