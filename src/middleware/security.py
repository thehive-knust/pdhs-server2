from werkzeug.security import safe_str_cmp
from pdhs_app.models.users.user import User
from flask_jwt_extended import JWTManager

jwt = JWTManager()
