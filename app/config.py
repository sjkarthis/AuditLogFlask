# app.py
from flask import Flask
import configparser
import os

app = Flask(__name__)

env = os.getenv('FLASK_ENV', 'development')
config_file = f'../config/{env}.properties'

config = configparser.ConfigParser()
config.read(config_file)