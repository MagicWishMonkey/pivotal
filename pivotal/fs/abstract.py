import os
import time
import datetime
from . import tools


class IOError(Exception):
    def __init__(self, message, inner, frame, **kwd):
        Exception.__init__(message, inner)




class FSEntry(object):
    __slots__ = ["uri", "name"]

    def verify(self):
        """Verify that this folder exists. If it doesn't exist, create it."""
        if self.exists is False:
            self.create()
        return self

    def create(self):
        """Create the filesystem entry."""
        tools.create(self.uri)
        return self

    def delete(self):
        """Delete the filesystem entry."""
        if self.exists is True:
            tools.delete(self.uri)
        return self

    def relative(self, path, cls=None):
        if cls is None:
            return tools.relative(self.uri, path)
        return cls(tools.relative(self.uri, path))

    @property
    def is_file(self):
        return True if self.is_folder is False else False

    @property
    def is_folder(self):
        from .directory import Directory
        if isinstance(self, Directory) is True:
            return True
        return False


    @property
    def parent(self):
        from .directory import Directory
        if isinstance(self, Directory) is False:
            uri = tools.relative(self.uri, "..")
            return Directory(uri)

        uri = self.relative("..")
        if uri == self.uri:
            #This is the root folder.
            return None

        return Directory(uri)

    @property
    def type(self):
        return self.__class__.__name__.lower()

    @property
    def exists(self):
        return tools.exists(self.uri)

    @property
    def created(self):
        if self.exists is False:
            return None

        st = os.stat(self.uri)
        return datetime.parse(time.ctime(st.st_ctime))

    @property
    def modified(self):
        if self.exists is False:
            return None

        st = os.stat(self.uri)
        return datetime.parse(time.ctime(st.st_mtime))

    @property
    def accessed(self):
        if self.exists is False:
            return None

        st = os.stat(self.uri)
        return datetime.parse(time.ctime(st.st_atime))

    def size(self):
        if self.exists is False:
            return 0

        st = os.stat(self.uri)
        if self.is_file is True:
            bytes = st.st_size
            return bytes

        files = self.files(recursive=True)
        if len(files) == 0:
            return 0

        sizes = [f.size() for f in files]
        bytes = sum(sizes)
        return bytes

        # mb = st.st_blocks * st.st_blksize
        # bytes = (mb * 1024)
        # return bytes

    @property
    def bytes(self):
        bytes = self.size()
        return bytes

    @property
    def kb(self):
        bytes = self.size()
        if bytes == 0:
            return 0# if bytes == 0 else round((float(bytes) / float(1024)), 2)
        return round((float(bytes) / float(1024)), 2)

    @property
    def mb(self):
        kb = self.kb
        if kb > 1024:
            mb = round((kb / float(1024)), 2)
            return mb
        elif kb == 1024:
            return 1
        return 0

    @property
    def gb(self):
        mb = self.mb
        if mb > 1024:
            gb = round((mb / float(1024)), 2)
            return gb
        elif mb == 1024:
            return 1
        return 0

    @classmethod
    def get(cls, uri):
        return cls(uri)

    def __str__(self):
        return self.uri

    def __repr__(self):
        return self.__str__()



