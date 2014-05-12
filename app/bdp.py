from flask import Flask
from .config import UPLOADS, METADATA, DATA, ZIPS, EXTENSIONS, DEBUG

# Create the Flask application
app = Flask(__name__)

# Configure the Flask app based on configurations from the config file
app.config["UPLOADS"] = UPLOADS
app.config["METADATA"] = METADATA
app.config["DATA"] = DATA
app.config["ZIPS"] = ZIPS
app.config["EXTENSIONS"] = EXTENSIONS
app.debug = DEBUG
