from app.bdp import app
from boto import connect_s3


def get_bucket():    
    """
    Connect to s3 with credentials provided by the flask application
    and return the bucket as configured by the app
    """
    bucket_name = app.config['S3_BUCKET']
    if bucket_name is None:
        raise EnvironmentError('Flask application is improperly configured')

    connection = connect_s3()
    return connection.get_bucket(bucket_name)


def put_file(key_name, file, content_type=None):
    """
    Put a file onto s3 at the given key name
    The bucket comes from the flask app configuration
    """

    bucket = get_bucket()
    key = bucket.new_key(key_name)
    if content_type:
        key.set_metadata('Content-Type', content_type)
    key.set_contents_from_file(file)
    key.set_acl('public-read')

def put_content(key_name, content, content_type=None):
    """
    Put a string onto s3 at the given key name
    The bucket comes from the flask app configuration
    """

    bucket = get_bucket()
    key = bucket.new_key(key_name)
    if content_type:
        key.set_metadata('Content-Type', content_type)
    key.set_contents_from_string(content)
    key.set_acl('public-read')

def generate_key(filename, prefix=''):
    """
    Generate a key name for the filename and a prefix
    """
    return '{prefix}{filename}'.format(prefix=prefix, filename=filename)
