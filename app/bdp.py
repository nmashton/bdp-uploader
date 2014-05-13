from flask import Flask

# Create the Flask application
app = Flask(__name__)

# Configure the Flask app based on configurations from the config file
app.config.from_object('app.config')

