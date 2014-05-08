import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from csv_utils import validate_csv, get_fields
import json
import zipfile

UPLOADS = "./csv-uploads/"
METADATA = "./metadata/"
ZIPS = "./bdp/"
EXTENSIONS = ["csv"]

app = Flask(__name__)
app.config["UPLOADS"] = UPLOADS
app.config["METADATA"] = METADATA
app.config["ZIPS"] = ZIPS
app.debug = True

## Utility functions.
def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1] in EXTENSIONS

def create_json(form):
    """
    Turns form data submitted at /metdata into a JSON object.

    (To be written to disk elsewhere.)
    """
    j = {
        "name": form["name_package"],
        "datapackage_version": "1.0-beta.7",
        "resources": [
            {
            "path": "./" + form["filename"],
            "name": form["name_resource"],

            "currency": form["currency"],
            "dateLastUpdated": form["dateLastUpdated"],
            "datePublished": form["datePublished"],
            "fiscalYear": form["fiscalYear"],
            "granularity": form["granularity"],
            "standard": "prerelease-MayDay",
            "status": form["status"],
            "type": form["type"],

            "schema": {
                "primaryKey": "id",
                "fields": get_fields(os.path.join(app.config["UPLOADS"], form["filename"]))
            }
            }
        ]
    }

    return json.dumps(j)

def handle_csv(filename, type, deep):
    """
    Check the CSV and return the metadata form.

    Takes a filename, a joined-up type (e.g. 'aggregated-expenditure'),
    and a boolean indicating whether or not deep validation is to be done.
    """
    f = os.path.join(app.config["UPLOADS"], filename)
    try:
        validate_csv(f,type,deep)
    except Exception as e:
        return render_template("upload_error.html", errors=str(e))

    name = filename.rsplit(".",1)[0]
    type_split = type.rsplit("-",1)

    return render_template("csv.html",
        filename=filename,
        name=name,
        granularity=type_split[0],
        type=type_split[1])

## Routes.
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/csv", methods=["POST"])
def upload_csv():
    """
    Saves an uploaded CSV to disk and serves up its metadata editor.

    POST request includes both the uploaded file and a few form
    parameters (deep, type).
    """
    file = request.files["csv"]

    if request.form.get("deep") == "deep":
        deep = True
    else:
        deep = False

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOADS"], filename))
        return handle_csv(filename=filename, type=request.form["type"], deep=deep)

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

@app.route("/bdp/<package>", methods=["GET"])
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