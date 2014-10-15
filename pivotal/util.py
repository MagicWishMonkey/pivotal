import sys
import time
import urllib2
import base64 as __b64__
try:
    import simplejson as __json__
except ImportError:
    print "Unable to import the simplejson library. Degrading to the built in json module."
    import json as __json__
import cPickle
import uuid
import hashlib
from pivotal.fs import *



def uri_unquote(txt):
    return urllib2.unquote(txt)


def web_get(uri, *headers):
    header_table = {}
    if len(headers) > 0:
        for header in headers:
            key, val = None, None
            if isinstance(header, basestring) is True:
                parts = header.split(":") if header.find(":") > -1 else header.split("=")
                if len(parts) < 2:
                    raise Exception("The header format is not valid.")
                key = parts[0].strip()
                val = ":".join(parts[1:]).strip() if header.find(":") > -1 else "=".join(parts[1:]).strip()
            else:
                if isinstance(header, (tuple, list)) is False:
                    raise Exception("The header format is not valid.")
                key, val = header[0], header[1]
            header_table[key] = val
    header_table['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/530.33 (KHTML, like Gecko) Chrome/1.2.3.4 Safari/555.44'

    headers = []
    for key in header_table:
        val = header_table[key]
        headers.append((key, val))

    opener = urllib2.build_opener()
    opener.addheaders = headers
    response = opener.open(uri)
    data = response.read()
    return data


def web_post(uri, data, *headers):
    header_table = {}
    if len(headers) > 0:
        for header in headers:
            key, val = None, None
            if isinstance(header, basestring) is True:
                parts = header.split(":") if header.find(":") > -1 else header.split("=")
                if len(parts) < 2:
                    raise Exception("The header format is not valid.")
                key = parts[0].strip()
                val = ":".join(parts[1:]).strip() if header.find(":") > -1 else "=".join(parts[1:]).strip()
            else:
                if isinstance(header, (tuple, list)) is False:
                    raise Exception("The header format is not valid.")
                key, val = header[0], header[1]
            header_table[key] = val
    header_table['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/530.33 (KHTML, like Gecko) Chrome/1.2.3.4 Safari/555.44'

    if isinstance(data, (list, dict)) is True:
        data = json(data)
        header_table["Content-Type"] = "application/json"
    header_table["Content-Length"] = str(len(data))

    req = urllib2.Request(uri, data, headers=header_table)
    response = urllib2.urlopen(req)
    result = response.read()
    return result


def guid(*size):
    size = 32 if len(size) == 0 else size[0]
    txt = hashlib.md5(str(uuid.uuid4())).hexdigest()
    cnt = len(txt)

    while size > cnt:
        txt = "%s%s" % (txt, hashlib.md5(str(uuid.uuid4())).hexdigest())
        cnt = len(txt)

    if cnt > size:
        txt = txt[0:size]

    return txt


def dedupe(lst):
    tbl, filtered = {}, False
    for x, o in enumerate(lst):
        try:
            if tbl[o] is not None:
                filtered = True
                lst[x] = None
        except KeyError:
            tbl[o] = 1

    if filtered is True:
        lst = [o for o in lst if o is not None]
    return lst



def hash(data):
    return hashlib.md5(data).hexdigest()


def base64(data):
    data = __b64__.encodestring(data)
    while data.find("\n") > -1:
        data = data.replace("\n", "")
    #data = data.replace("\n", "")
    return data


def unbase64(data):
    data = __b64__.decodestring(data)
    return data



def json(obj, indent=None, sort_keys=True, pretty=False):
    """Convert the object instance into a json blob."""

    assert obj is not None, "The input parameter is null!"

    try:
        if indent:
            return __json__.dumps(obj, check_circular=False, sort_keys=sort_keys, indent=indent)
        else:
            if pretty is True:
                return __json__.dumps(obj, check_circular=False, sort_keys=sort_keys, indent=2)
            return __json__.dumps(obj, check_circular=False, sort_keys=sort_keys)
    except Exception, ex:
        message = "Unable to encode the object to json-> %s" % ex.message
        raise Exception(message)



def unjson(data):
    """Convert the json blob into an object instance."""
    assert data is not None, "The input parameter is null!"

    try:
        return __json__.loads(data, strict=False)
    except Exception, ex:
        message = "Unable to decode the json object-> %s" % ex.message
        raise Exception(message)


def pickle(obj, protocol=2):
    """Pickles the object instance"""
    assert obj is not None, "The obj parameter is null!"

    try:
        return cPickle.dumps(obj, protocol)
    except Exception, ex:
        message = "Unable to pickle the object instance-> %s" % ex.message
        raise Exception(message)


def unpickle(data):
    """Unpickles the object instance"""
    assert data is not None, "The data parameter is null!"

    try:
        return cPickle.loads(data)
    except Exception, ex:
        message = "Unable to unpickle the object instance-> %s" % ex.message
        raise Exception(message)


def file(uri):
    return File(uri)


def directory(uri):
    return Directory(uri)


def folder(uri):
    return Directory(uri)


def rcurry(f, *a, **kw):
    def curried(*more_a, **more_kw):
        return f(*(more_a + a), **dict(kw, **more_kw))
    return curried


def curry(f, *a, **kw):
    def curried(*more_a, **more_kw):
        return f(*(a + more_a), **dict(kw, **more_kw))
    return curried


def unroll(lst):
    if lst is None:
        return []
    def list_or_tuple(x):
        return isinstance(x, (list, tuple))

    def flatten(seq, to_expand=list_or_tuple):
        for i in seq:
            if to_expand(i):
                for sub in flatten(i, to_expand):
                    yield sub
            else:
                yield i

    if list_or_tuple(lst) is False:
        return [lst]

    unravelled = []
    for o in flatten(lst):
        unravelled.append(o)
    return unravelled


def ask(message):
    if message.endswith(" ") is False:
        message = "%s " % message

    sys.stdout.write(message)
    txt = sys.stdin.readline().replace("\n", "")
    if len(txt) == 0:
        return None
    if txt.lower() == "y" or txt.lower() == "yes" or txt == "1":
        return True
    if txt.lower() == "n" or txt.lower() == "no" or txt == "0":
        return False
    return txt