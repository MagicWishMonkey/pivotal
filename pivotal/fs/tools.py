import os
import codecs
import shutil
from cStringIO import StringIO
from fnmatch import fnmatch

logger = lambda o: o



def is_file(uri):
    """Return True if the uri is a file uri, False otherwise."""
    return True if is_dir(uri) is False else False


def is_dir(uri):
    """Return True if the uri is a directory uri, False otherwise."""
    if uri.endswith("/") is True or os.path.isdir(uri) is True:
        return True
    return False


def exists(uri):
    """Return true if the file/folder exists."""
    return True if os.path.exists(uri) else False


def contents(uri, include_files=True, include_folders=True, recursive=False, pattern=None):
    """Iterate through the contents of the specified folder."""

    assert isinstance(uri, basestring) is True, \
        "The uri parameter is not a string value!"


    if os.path.isdir(uri) is False and uri.endswith(os.sep) is False:
        raise Exception("The folder uri is not valid-> %s" % uri)

    patterns = None
    if pattern is not None:
        if isinstance(pattern, list) is False:
            pattern = pattern.replace(";", " ")
            pattern = pattern.replace("  ", " ")
            pattern = pattern.split(" ")
        patterns = [p.strip().lower() for p in pattern]
        patterns = [p for p in patterns if len(p) > 1]

    try:
        for root, folders, files in os.walk(uri):
            if recursive is False:
                if root != uri:
                    break

            if include_files is True:
                for file_name in files:
                    if patterns is not None:
                        filtered = True
                        for pattern in patterns:
                            if fnmatch(file_name, pattern) is True:
                                filtered = False
                                continue
                        if filtered is True:
                            continue

                    path = os.path.join(root, file_name)
                    yield path

            if include_folders is True:
                for folder_name in folders:
                    path = os.path.join(root, folder_name)
                    yield path
    except Exception, ex:
        if exists(uri) is True:
            raise Exception("Error walking the directory-> %s" % uri, ex)



def clear(uri):
    """Clear the contents of the directory."""
    assert isinstance(uri, basestring) is True, \
        "The uri parameter is not a string value!"

    if os.path.isdir(uri) is False:
        raise Exception("The folder uri is not valid-> %s" % uri)

    for root, folders, files in os.walk(uri):
        for file_name in files:
            path = os.path.join(root, file_name)
            delete(path)

        for folder_name in folders:
            path = os.path.join(root, folder_name)
            delete(path)


def delete(uri):
    """Delete the specified file or folder."""

    def delete_folder(uri):
        """Delete the specified folder."""
        try:
            if exists(uri) is True:
                clear(uri)
                os.rmdir(uri)
                logger("Deleted folder-> %s" % uri)
        except Exception, ex:
            if exists(uri) is True:
                raise Exception("Error deleting directory-> %s" % uri, ex)



    def delete_file(uri):
        """Delete the specified file."""
        try:
            os.remove(uri)
            logger("Deleted file-> %s" % uri)
        except Exception, ex:
            if exists(uri) is True:
                raise Exception("Error deleting file-> %s" % uri, ex)

    if is_dir(uri) is True:#os.path.isdir(uri) is True:
        delete_folder(uri)
    else:
        delete_file(uri)


def create(uri):
    """Create the specified file or folder."""

    def create_folder(uri):
        """Create a folder at the specified uri."""

        try:
            if exists(uri) is True:
                return

            os.makedirs(uri)
            logger("Created folder-> %s" % uri)
        except Exception, ex:
            raise Exception("Error creating directory-> %s" % uri, ex)


    def create_file(uri):
        """Create an empty file entry at the specified uri."""

        try:
            if exists(uri) is True:
                return

            with open(uri, mode="w") as f:
                f.write("")

            logger("Created file-> %s" % uri)
        except Exception, ex:
            raise Exception("Error creating file-> %s" % uri, ex)

    if is_dir(uri) is True:#os.path.isdir(uri) is True:
        create_folder(uri)
    else:
        create_file(uri)


def relative(uri, path):
    newUri = os.path.join(uri, path)
    newUri = os.path.normpath(newUri)
    return newUri


def is_text_type(uri):
    raise NotImplementedError("This is not implemented!")

    # try:
    #     from fuze.toolkit import mime_type
    #     return mime_type.is_text_type(uri)
    # except:
    #     parts = uri.split(".")
    #     ext = parts[len(parts) - 1].strip().lower()
    #     if ext == "txt" or ext == "json" or ext == "css" or ext == "js":
    #         return True
    #     return False


def read(uri, *fn, **kwd):
    if is_text_type(uri) is True:
        return read_text(uri, *fn, **kwd)

    return read_data(uri, *fn, **kwd)


def read_data(uri, *fn, **kwd):
    """Read the file data."""
    assert isinstance(uri, basestring) is True, \
        "The uri parameter is not a string value!"

    data = None
    try:
        with open(uri, "rb") as f:
            data = f.read()
    except Exception, ex:
        if exists(uri) is True:
            raise Exception("Error reading file-> %s" % uri, ex)
        return None

    fn = fn[0] if len(fn) > 0 else None
    if fn:
        try:
            return fn(data)
        except Exception, ex:
            raise Exception("Error applying function to data-> %s" % uri, ex)
    return data


def read_lines(uri, *fn, **kwd):
    """Read the file text data."""
    assert isinstance(uri, basestring) is True, \
        "The uri parameter is not a string value!"

    txt = read_text(uri, *fn, **kwd)
    chunks = txt.split("\n")
    cnt = len(chunks)
    lines = []
    for chunk in chunks:
        if len(chunk) == 0:
            continue
        line = chunk.strip()
        if len(line) == 0:
            continue
        lines.append(line)

    return lines



def read_text(uri, *fn, **kwd):
    """Read the file text data."""
    assert isinstance(uri, basestring) is True, \
        "The uri parameter is not a string value!"

    encoding = "utf-8"
    try:
        encoding = kwd["encoding"]
    except:
        pass

    data = None
    try:
        with codecs.open(uri, "r", encoding) as f:
            data = f.read()
    except Exception, ex:
        if exists(uri) is True:
            raise Exception("Error reading file-> %s" % uri, ex)
        return None

    fn = fn[0] if len(fn) > 0 else None
    if fn:
        try:
            return fn(data)
        except Exception, ex:
            raise Exception("Error applying function to data-> %s" % uri, ex)
    return data


def append(uri, data):
    """Append the data to the file."""
    return write(uri, data, overwrite=False, append=True)


def write(uri, data, overwrite=False, append=False):
    """Write the file data to disk."""
    if is_text_type(uri) is True:
        if append is True:
            return write_lines(uri, data)

        return write_text(uri, data, overwrite=overwrite, append=append)
    return write_data(uri, data, overwrite=overwrite, append=append)


def write_data(uri, data, overwrite=False, append=False):
    """Write the file data to disk."""
    assert isinstance(uri, basestring) is True, \
        "The uri parameter is not a string value!"
    assert isinstance(data, basestring) is True, \
        "The data parameter is not a string value!"
    try:
        if append is True:
            with open(uri, "a") as f:
                f.write(data)
            return

        if overwrite is False:
            if exists(uri) is True:
                raise Exception("The file already exists-> %s" % uri)

        with open(uri, "wb") as f:
            f.write(data)
    except Exception, ex:
        if isinstance(ex, IOError) is True:
            raise ex

        if exists(uri) is True:
            raise Exception("Error writing file-> %s" % uri, ex)


def write_text(uri, data, overwrite=False, append=False, encoding="utf-8"):
    """Write the file text to disk."""
    assert isinstance(uri, basestring) is True, \
        "The uri parameter is not a string value!"
    assert isinstance(data, basestring) is True, \
        "The data parameter is not a string value!"
    try:
        if append is True:
            with codecs.open(uri, "a", encoding) as f:
                f.write(data)
            return

        if overwrite is False:
            if exists(uri) is True:
                raise Exception("The file already exists-> %s" % uri)

        with codecs.open(uri, "w", encoding) as f:
            f.write(data)
    except Exception, ex:
        if exists(uri) is True:
            raise Exception("Error writing file-> %s" % uri, ex)
        return None


def write_lines(uri, lines):
    """Write a line to the specified file."""
    if exists(uri) is False:
        with open(uri, mode="w") as f:
            map(f.write, ["%s\n" % l for l in lines])
            #f.writelines(lines)
            #for txt in line:
            #    f.write(txt)
        return

    #newline = "\r\n"
    with open(uri, "a") as f:
        map(f.write, ["%s\n" % l for l in lines])
        #f.writelines(lines)


def copy(src, dst, overwrite=False):
    try:
        if overwrite is False:
            if exists(dst) is True:
                raise Exception("A file already exists in the destination path-> %s" % dst)
        shutil.copy2(src, dst)
        logger("Copied file from %s to %s" % (src, dst))
    except Exception, ex:
        if isinstance(ex, IOError) is True:
            raise ex


def move(src, dst, overwrite=False):
    try:
        if overwrite is False:
            if exists(dst) is True:
                raise Exception("A file already exists in the destination path-> %s" % dst)

        shutil.move(src, dst)
        logger("Moved file from %s to %s" % (src, dst))
    except Exception, ex:
        if isinstance(ex, IOError) is True:
            raise ex

        if is_file(src) is True:
            raise Exception("Error moving file-> %s to %s" % (src, dst), ex)
        raise Exception("Error moving directory-> %s to %s" % (src, dst), ex)



