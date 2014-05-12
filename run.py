from app.bdp import app
from flask import (render_template, request, redirect, url_for,
                   send_from_directory)
from werkzeug.utils import secure_filename

from utils.csv import validate_csv, get_fields, currencies
from utils.files import allowed_file
from utils.metadata import create_json

import zipfile
import os


## Routes.
@app.route("/")
def index():
    return render_template("index.html")

@app.errorhandler(400)
@app.route("/csv", methods=["POST"])
def upload_csv():
    """
    Saves an uploaded CSV to disk and serves up its metadata editor.

    POST request includes both the uploaded file and a few form
    parameters (deep, type).
    """
    if request.method == "POST":
        file = request.files["csv"]
        if not (file and allowed_file(file.filename)):
            return redirect('/')

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOADS'], filename)
        file.save(filepath)

        type_choice = request.form.get("type")
        deep = (request.form.get("deep") == "deep")

        try:
            validate_csv(filepath,type_choice,deep)
        except Exception as e:
            # Remove the csv file if it didn't validate
            os.remove(filepath)
            # Render the error
            return render_template("upload_error.html", errors=str(e)), 400

        name = os.path.splitext(filename)[0]
        (granularity, budget_type) = type_choice.rsplit("-",1)

        return render_template("csv.html",
                               filename=filename,
                               name=name,
                               granularity=granularity,
                               type=budget_type,
                               currencies=currencies)


@app.route("/metadata", methods=["POST"])
def create_metadata():
    """
    Saves a metadata descriptor to disk and serves up a link
    to the complete data package.

    POST request includes user-entered metadata fields as well
    as a few hidden fields generated when the CSV was uploaded.
    """

    fn = secure_filename(request.form["filename"].rsplit(".",1)[0])
    f = open(os.path.join(app.config["METADATA"], fn + ".json"),"w")
    f.write(create_json(request.form))
    f.close()

    return render_template("metadata.html", name=fn)

@app.route("/bdp/<package>")
def generate_package(package):
    """
    Serves up the download link for the complete data package.

    For this to work, there must be an uploaded CSV and metadata
    descriptor with names corresponding to `package`.
    """
    safe_p = secure_filename(package)

    f = zipfile.ZipFile(os.path.join(app.config["ZIPS"], safe_p + ".zip"), "w")
    f.write(os.path.join(app.config["UPLOADS"], safe_p + ".csv"), safe_p + ".csv")
    f.write(os.path.join(app.config["METADATA"], safe_p + ".json"), "datapackage.json")
    f.close()

    return send_from_directory(app.config["ZIPS"], safe_p + ".zip")

## Run the app.
if __name__ == '__main__':
    app.run()
