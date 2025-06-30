
try:
    from urllib import urlencode, urlopen, urlretrieve
except ImportError:
    from urllib.parse import urlencode
    from urllib.request import urlopen, urlretrieve
