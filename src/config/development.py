"""Development configuration."""

import os #import os
from datetime import timedelta

from dotenv import load_dotenv
project_folder = os.path.expanduser('~/pdhs-server')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

# defaults
SECRET_KEY = os.getenv('SECRET_KEY')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(
    hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES')))
JWT_REFRESH_TOKEN_EXPIRES = timedelta(
    days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES')))

# Others
FLASK_ENV = 'development'
DEBUG = True
JWT_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Database
DATABASE_URI = "sqlite:///{instance_path}/{path}".format(
    instance_path=os.getenv('INSTANCE_PATH'),
    path=os.getenv('SQL_LITE_PATH')
)

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username=os.getenv('DB_USERNAME'),
    password=os.getenv('DB_PASSWORD'),
    hostname=os.getenv('DB_HOSTNAME'),
    databasename=os.getenv('DB_NAME'),
)
