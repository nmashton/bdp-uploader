from app.bdp import app
import os.path

def allowed_file(filename):
    """
    See if the file extension is allowed by looking up in the app
    configured extensions.
    """
    return os.path.splitext(filename)[1] in app.config["EXTENSIONS"]
