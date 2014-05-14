from app.bdp import app
from utils.s3 import generate_key
from utils.csv import get_fields
from urlparse import urljoin
import json
import os

def resource_path(filename):
    if app.config['S3_BUCKET'] and app.config['S3_HTTP_URL']:
        key = generate_key(filename, prefix=app.config['S3_CSV_PREFIX'])
        return urljoin(app.config['S3_HTTP_URL'], key)
    else:
        package = os.path.join(app.config['METADATA'], filename)
        filepath = os.path.join(app.config['UPLOADS'], filename)
        return os.path.relpath(filepath, package)
    

def create_json(form):
    """
    Turns data submitted at /metadata into a JSON object.

    (To be written to disk elsewhere.)
    """
    j = {
        "name": form["name_package"],
        "datapackage_version": "1.0-beta.7",
        "resources": [
            {
            "path": resource_path(form["filename"]),
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
                "fields": get_fields(form.getlist('headers'))
                }
            }
        ]
    }

    return json.dumps(j)

