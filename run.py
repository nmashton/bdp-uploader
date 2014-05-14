from app.bdp import app
from flask import (render_template, request, redirect, url_for,
                   send_from_directory)
from werkzeug.utils import secure_filename
from urlparse import urljoin

from utils.csv import BudgetCSV, get_fields, currencies
from utils.files import allowed_file, slugify
from utils.metadata import create_json
from utils import s3

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

        budget = BudgetCSV(file)
        type_choice = request.form.get("type")
        deep = (request.form.get("deep") == "deep")

        try:
            budget.validate(type_choice, deep)
        except Exception as e:
            # Render the error
            return render_template("upload_error.html", errors=str(e)), 400

        filename = secure_filename(file.filename)
        name = os.path.splitext(filename)[0]

        if app.config['S3_BUCKET'] is not None:
            key = s3.generate_key(filename,
                                  prefix=app.config['S3_CSV_PREFIX'])
            s3.put_file(key, budget.file, content_type='application/json')
        else:
            filepath = os.path.join(app.config['UPLOADS'], filename)
            budget.file.save(filepath)

        (granularity, budget_type) = type_choice.rsplit("-",1)

        return render_template("csv.html",
                               filename=filename,
                               headers=budget.headers,
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

    package = slugify(secure_filename(request.form["name_package"]))
    metadata = create_json(request.form)

    if app.config['S3_BUCKET'] is not None:
        keypath = s3.generate_key(package, prefix=app.config['S3_BDP_PREFIX'])
        key= '/'.join([keypath, 'datapackage.json'])
        s3.put_content(key, metadata, content_type='application/csv')
        package_url = urljoin(app.config['S3_HTTP_URL'], key)
    else:
        packagedir = os.path.join(app.config['METADATA'], package)
        if not os.path.isdir(packagedir):
            os.mkdir(packagedir)

        jsonfile = open(os.path.join(packagedir, "datapackage.json"), "w")
        jsonfile.write(metadata)
        jsonfile.close()
        package_url = url_for('generate_package')

    return render_template("metadata.html", package_url=package_url)

@app.route("/bdp/<package>")
def generate_package(package):
    """
    Serves up the download link for the complete data package.

    For this to work, there must be an uploaded CSV and metadata
    descriptor with names corresponding to `package`.
    """
    packagename = slugify(secure_filename(package))
    packagedir = os.path.join(app.config['METADATA'], packagename)
    send_from_directory(packagedir, 'datapackage.json')

@app.route('/budget-data-package')
def specification_page():
    return render_template("content/specification.html")

@app.route('/standardized-data')
def standardized_data_page():
    return render_template("content/standardized-data.html")

@app.route('/howto')
def howto_page():
    return render_template("content/howto.html")

## Run the app.
if __name__ == '__main__':
    app.run()
