# Budget Data Package uploader

Upload a CSV, get back a Budget Data Package.

(This is a very, very early first draft.)

## Install the webapp

We recommend you install it using virtualenv:

    virtualenv venv

Then install the requirements:

    pip install -r requirements.txt

Celebrate, because you've installed everything!

## Configure the webapp

The webapp is configured via environment variables:

* ``BDP_CSV_UPLOAD_DIR`` sets the path to the directory where uploaded csv files will be placed. Default is ``csv-uploads`` in the code base's root.
* ``BDP_METADATA_DIR`` sets the path to the diretory where the generated metadata files wil be placed. Default is ``metadata`` in the code base's root.
* ``BDP_DATA_DIR`` sets the path for a data directory with configuration files like currencies used by the software. Default is ``data`` in the code base's root and it should probably be left that way unless you know what you're doing.
* ``BDP_ZIPFILE_DIR`` sets the path to the directory where the zipfile of the budget data packages will be stored. Default is ``bdp`` in the code base's root.
* ``BDP_ALLOWED_EXTENSIONS`` is a comma separated list of extensions for the CSV files that can be uploaded. Default is only one file extension: *csv*.
* ``BDP_DEBUG`` sets a boolean *true* or *false* to indicate if server should be run in debug mode. Default is *false* (not run in debug mode).

To configure S3 support further environment variables are needed:

* ``AWS_ACCESS_KEY_ID`` sets the access key id for S3
* ``AWS_SECRET_ACCESS_KEY`` sets the secret access key (sshh... don't tell anyone)
* ``BDP_S3_BUCKET`` sets the bucket name where all the csv files and buckets will be stored
* ``BDP_S3_HTTP`` sets the URL for the HTTP fron of the S3 bucket. This is needed to serve the budget data packages from the web interface
* ``BDP_S3_CSV_PREFIX`` sets the prefix used in the keys for the csv files on S3. Default is *csv/* (note: if you skip trailing slash it will be a general prefix)
* ``BDP_S3_BDP_PREFIX`` sets the prefix used in the keys for the budget data packages themselves. The metadata files will stored at {THIS PREFIX}{PACKAGE NAME}/datapackage.json. Default is *bdp/* (note: if you skip the thrailing slash it will be a general prefix

## Run the webapp

To run the server, after setting all environment variables as you need them to be, just run (with your virtualenv activated, if you're using one):

    python run.py
