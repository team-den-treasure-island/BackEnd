import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

SECRET_KEY = os.environ.get("SECRET_KEY")
# DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")






# HEROKU STUFF
# https://github.com/heroku/django-heroku
# Configure Django App for Heroku.
import django_heroku
django_heroku.settings(locals())
