from datetime import datetime, timezone
from flask import (Blueprint, request, jsonify, render_template)
from flask_jwt_extended import (create_access_token, create_refresh_token, get_jwt_identity, get_jwt, jwt_required, current_user)
from middleware.security import jwt
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from middleware.cloud_upload import upload_file
# from storage.cloud_storage import delete_blob, upload_blob
from database import db
from pdhs_app.models.users.user import User
from pdhs_app.models.faculties.faculty import Faculty
from pdhs_app.models.departments.department import Department
from .tokens import TokenBlocklist

bp = Blueprint('auth', __name__, url_prefix='/auth')


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def _allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/', methods=['GET'])
def all():
    if request.method == 'GET':
        result = User.query.all()
        users = [user.to_json() for user in result]
        return jsonify(users=users)


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    user = User.find_by_id(identity)
    return user if user else None


@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = current_user
    access_token = create_access_token(identity=identity, fresh=False)
    return jsonify(access_token=access_token)

@jwt.token_verification_loader
def verify_token(jwt_header, jwt_data):
    print('verify_token', jwt_header)
    return True


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None


@bp.route('/signup', methods=['POST', 'GET'])
def register_user():
    if request.method == 'POST':
        request_data = request.form.to_dict()
        _id = request_data.get('id', None)                              # request.form['id'] if request.form['id'] else 
        first_name = request_data.get('first_name', None)               # request.form['first_name'] if request.form['first_name'] else 
        last_name = request_data.get('last_name', None)                 # request.form['last_name'] if request.form['last_name'] else 
        email = request_data.get('email', None)                         # request.form['email'] if request.form['email'] else 
        contact = request_data.get('contact', None)                     # request.form['contact'] if request.form['contact'] else 
        password = request_data.get('password', None)                   # request.form['password'] if request.form['password'] else 
        user_img = request.files.get('user_img', None)                  # request.files['user_img'] if request.files['user_img'] else 
        portfolio_id = request_data.get('portfolio_id', None)           # request.form['portfolio_id'] if request.form['portfolio_id'] else 
        department_id = request_data.get('department_id', None)         # request.form['department_id'] if request.form['department_id'] else 
        faculty_id = request_data.get('faculty_id', None)               # request.form['faculty_id'] if request.form['faculty_id'] else 
        college_id = "COE" # request_data.get('college_id', None)               # request.form['college_id'] if request.form['college_id']  else 

        error = None
        
        print("ALL DATA RECIEVED" + _id + "<<<>>>" + first_name + "<<<>>>" + department_id + "<<<>>>" + faculty_id + "<<<>>>" + college_id + "<<<>>>")

        if not email:
            error = 'Email is required.'
        elif not first_name:
            error = 'First name is required.'
        elif not _id:
            error = 'ID is required.'
        elif not last_name:
            error = 'Last name is required.'
        elif not portfolio_id:
            error = 'Portfolio is required.'
        elif not contact:
            error = 'Contact is required.'
        elif not password:
            error = 'Password is required.'
            
        if department_id == "None":
            department_id = None
            
        if faculty_id == "None":
            faculty_id = None
        
        if college_id == "None":
            college_id = None
            
        if department_id and not (faculty_id and college_id):
            error = 'Faculty and College IDs are required if Dept is provided.'
        
        if faculty_id and not college_id:
            error = 'College ID is required if faculty is provided.'
            
        if User.find_by_id(_id) is not None:
            error = f"The ID {_id} is already registered."
            
        if User.find_by_email(email) is not None:
            error = f"The email address {email} is already registered."
           
#         try:
#             registrar = User.find_by_id(registrars_id) 
#         except:
#             error = f"Unathorized Access."
            
#         if registrar:
#             if registrar.portfolio_id == portfolio_id:
#                 registrar.portfolio_id = None
#                 registrar.save_to_db()
        
        user_img_url = None
        
        if user_img:
            if _allowed_file(user_img.filename):
                filename = secure_filename(user_img.filename)
                try:
                    user_img_url = upload_file(user_img)            # upload_blob(user_img.stream, filename)
                    print('IMAGE URL..............', user_img_url)
                except Exception as e:
                    print('Error uploading file: %s' % e)
        
        
        if error is not None:
            return jsonify({"msg": error}), 500
        else:
            password = generate_password_hash(password)
            new_user = User(
                id=int(_id),
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                contact=contact,
                img_url=user_img_url if user_img_url else None,
                portfolio_id=int(portfolio_id)
            )
            if department_id is not None:
                new_user.department_id=department_id
                
            if faculty_id is not None:
                new_user.faculty_id=int(faculty_id )
                
            if college_id is not None:
                new_user.college_id=college_id 
                
            try:
                new_user.save_to_db()
                print(" YOU HAVE TO SAVE THE USER!!! ")
            except Exception as e:
                print("Error saving user to database: ..............................\n", e)
                return jsonify(msg="Could not save new user to database"), 500
            return jsonify({'msg': 'User created successfully'})
    return render_template("users/signup.html")


@bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        _id = request.json.get('id', None) #request.form['id'] if request.form['id'] else 
        password = request.json.get('password', None) # request.form['password'] if request.form['password'] else 
        try:
            user = User.find_by_id(int(_id))
        except:
            return jsonify(message="User Don't Exist")
        correct_password = password #check_password_hash(user.password, password)
        if _id is not None and correct_password:
            user.last_login = datetime.utcnow()
            user.login_count = user.login_count + 1 if user.login_count else 1
            user.save_to_db()
            
            logged_in_user = user.to_json()
            if user.department_id is None:
                logged_in_user['department_id'] = "others"
                
            access_token = create_access_token(identity=user)
            refresh_token = create_refresh_token(identity=user)
            return jsonify(access_token=access_token, refresh_token=refresh_token, user=logged_in_user), 200
        else:
            return jsonify(msg='Invalid ID or password'), 401
    else:
        return render_template("users/login.html") #404


@bp.route('/logout', methods=["DELETE"])
@jwt_required()
def modify_token():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    token_block = TokenBlocklist(
        jti=jti, created_at=now, created_by=current_user.id)
    db.session.add(token_block)
    db.session.commit()
    return jsonify(msg="JWT revoked")


@bp.route('/test_login', methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@bp.route("/who_am_i", methods=["GET"])
@jwt_required()
def who_am_i():
    # We can now access our sqlalchemy User object via `current_user`.
    return jsonify(
        id=current_user.id,
        first_name=current_user.first_name.title(),
        last_name=current_user.last_name.title()
    )


# @bp.before_app_request
# def load_logged_in_user():
#     user_id = session.get('user_id')

#     if user_id is None:
#         g.user = None
#     else:
#         g.user = User.query.filter_by(id=user_id).first()


# @bp.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('index'))


# def login_required(view):
#     @functools.wraps(view)
#     def wrapped_view(**kwargs):
#         if g.user is None:
#             return redirect(url_for('auth.login'))

#         return view(**kwargs)

#     return wrapped_view
