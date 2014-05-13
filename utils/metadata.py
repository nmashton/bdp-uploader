from app.bdp import app
from utils.csv import get_fields
import json
import os

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

