from app.bdp import app

def allowed_file(filename):
    return "." in filename and\
        filename.rsplit(".",1)[1] in app.config["EXTENSIONS"]
