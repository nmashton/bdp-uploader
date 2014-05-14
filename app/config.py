import os.path
from os import environ as env

# Configure directories to hold files, default are directories which are
# one above the directory where the config file is
here = lambda x: os.path.abspath(os.path.join(os.path.dirname(__file__), x))
UPLOADS = env.get('BDP_CSV_UPLOAD_DIR', here('../csv-uploads/'))
METADATA = env.get('BDP_METADATA_DIR', here('../bdp/'))
DATA = env.get('BDP_DATA_DIR', here('../data/'))

# Allowed upload extensions
EXTENSIONS = env.get('BDP_ALLOWED_EXTENSIONS', 'csv').split(',')

# Amazon S3 configurations
S3_BUCKET = env.get('BDP_S3_BUCKET', None)
S3_HTTP_URL = env.get('BDP_S3_HTTP', None)
S3_CSV_PREFIX = env.get('BDP_S3_CSV_PREFIX', 'csv/')
S3_BDP_PREFIX = env.get('BDP_S3_BDP_PREFIX', 'bdp/')

# Run in debug mode or not
DEBUG = env.get('BDP_DEBUG', 'false').lower() == 'true'
