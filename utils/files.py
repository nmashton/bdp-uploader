from app.bdp import app
from unicodedata import normalize
import os.path
import re


def allowed_file(filename):
    """
    See if the file extension is allowed by looking up in the app
    configured extensions.
    """
    extension = os.path.splitext(filename)[1].lstrip('.')
    return extension in app.config["EXTENSIONS"]


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'-'):
    """
    Generate an ASCII slug with built-in tools
    Thanks to Armin Ronacher:
    http://flask.pocoo.org/snippets/5/
    """

    # text must be unicode so we cast it to unicode if it isn't
    if not isinstance(text, unicode):
        text = unicode(text)

    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))
