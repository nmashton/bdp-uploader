import os.path
from os import environ as env

# Configure directories to hold files, default are directories which are
# one above the directory where the config file is
here = lambda x: os.path.abspath(os.path.join(os.path.dirname(__file__), x))
UPLOADS = env.get('BDP_CSV_UPLOAD_DIR', here('../csv-uploads/'))
METADATA = env.get('BDP_METADATA_DIR', here('../metadata/'))
DATA = env.get('BDP_DATA_DIR', here('../data/'))
ZIPS = env.get('BDP_ZIPFILE_DIR', here('../bdp/'))

# Allowed upload extensions
EXTENSIONS = env.get('BDP_ALLOWED_EXTENSIONS', 'csv').split(',')

# Run in debug mode or not
DEBUG = env.get('BDP_DEBUG', 'false').lower() == 'true'
