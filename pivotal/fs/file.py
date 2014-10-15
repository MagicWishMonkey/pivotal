import os
import codecs
from os.path import expanduser
from . import tools
from .abstract import IOError
from .abstract import FSEntry



class File(FSEntry):
    __slots__ = ["uri", "type", "name", "ext"]#, "name_sans_ext"]

    def __init__(self, uri):
        if uri.startswith("~"):
            path = expanduser("~")
            if len(uri) > 1:
                uri = uri[1:]
            else:
                uri = os.sep
            if uri[0] != os.sep:
                uri = "{sep}{uri}".format(sep=os.sep, uri=uri)

            uri = "{pfx}{sfx}".format(pfx=path, sfx=uri)

        if os.path.isabs(uri) is False:
            try:
                #is this a relative path? try and resolve the real path
                retry = os.path.realpath(uri)
                if os.path.isabs(retry):
                    uri = retry
            except Exception, ex:
                raise IOError("Invalid uri-> %s" % uri, ex)

            if os.path.isabs(uri) is False:
                raise IOError("Invalid uri-> %s" % uri)

        self.uri = uri
        if uri.endswith(os.sep) is True:
            self.uri = uri[0:len(uri) - 1]

        if tools.is_file(self.uri) is False:
            raise IOError("Invalid uri-> %s" % uri)


        parts = os.path.normpath(self.uri).split(os.path.sep)
        self.name = parts[len(parts) - 1]


        ext = os.path.splitext(self.name)[1]
        self.ext = ext.lower()
        self.name = os.path.splitext(self.name)[0]
        #self.name_sans_ext = self.name
        if len(self.ext) > 0:
            self.name = "%s%s" % (self.name, self.ext)


    def stream(self, append=False, text_mode=True, encoding="utf-8"):
        return FileStream(self, append=append, text_mode=text_mode, encoding=encoding)

    #     if text_mode is False:
    #         if append is False:
    #             return open(self.uri, "wb")
    #         return open(self.uri, "a")
    #
    #
    #     if append is False:
    #         return codecs.open(self.uri, "w", encoding)
    #     return codecs.open(self.uri, "a", encoding)



    @property
    def siblings(self):
        return self.parent.siblings

    def reverse_search(self, name):
        return self.parent.reverse_search(name)

    def search(self, name, reverse_search=False):
        return self.parent.search(name, reverse_search=reverse_search)

    def read(self, *fn, **kwd):
        """Open the file handle and return the contents back out."""
        return tools.read(self.uri, *fn, **kwd)

    def read_data(self, *fn):
        return tools.read_data(self.uri, *fn)

    def read_text(self, *fn, **kwd):
        return tools.read_text(self.uri, *fn, **kwd)

    def read_lines(self, *fn, **kwd):
        return tools.read_lines(self.uri, *fn, **kwd)

    def append(self, data, overwrite=False, append=False):
        return tools.append(self.uri, data, overwrite=overwrite, append=append)

    def write(self, data, overwrite=False, append=False):
        return tools.write(self.uri, data, overwrite=overwrite, append=append)

    def write_data(self, data, overwrite=True, append=False):
        if append is True:
            if self.exists is False:
                append = False

        return tools.write_data(self.uri, data, overwrite=overwrite, append=append)

    def write_text(self, data, overwrite=True, append=False):
        if append is True:
            if self.exists is False:
                append = False
        return tools.write_text(self.uri, data, overwrite=overwrite, append=append)

    def write_lines(self, *lines):
        if len(lines) == 1 and isinstance(lines[0], list) is True:
            lines = lines[0]

        tools.write_lines(self.uri, lines)

    def relative(self, path, cls=None):
        if path.find(os.sep) == -1:
            return self.parent.relative(path, cls=cls)
        return FSEntry.relative(self, path, cls=cls)


    def move(self, path, overwrite=False):
        uri = path.uri if isinstance(path, File) is True else self.relative(path)
        tools.move(self.uri, uri, overwrite=overwrite)
        self.uri = uri
        return self

    def copy(self, path, overwrite=False):
        uri = path.uri if isinstance(path, File) is True else self.relative(path)
        tools.copy(self.uri, uri, overwrite=overwrite)
        self.uri = uri
        return self


    def rename(self, name):
        uri = self.parent.relative(name)
        tools.move(self.uri, uri)
        self.uri = uri
        return self

    @property
    def name_sans_ext(self):
        name = self.name
        if len(self.ext) > 0:
            parts = name.split(".")
            if len(parts) == 2:
                name = parts[0]
                return name

            parts.pop()
            name = ".".join(parts)

        return name

    # @property
    # def fullname(self):
    #     ext = self.ext
    #     if not ext:
    #         return self.name
    #     return "%s%s" % (self.name, ext)

    @property
    def length(self):
        if self.exists is False:
            return 0
        st = os.stat(self.uri)
        bytes = st.st_size
        return bytes

    @property
    def kb(self):
        bytes = self.length
        if bytes < 1024:
            return 0
        elif bytes == 1024:
            return 1

        kb = round((float(bytes) / float(1024)), 2)
        return kb

    @property
    def mb(self):
        kb = self.kb
        if kb < 1024:
            return 0
        elif kb == 1024:
            return 1

        mb = round((kb / float(1024)), 2)
        return mb

        # @property
        # def bytes(self):
        #     if self.exists is False:
        #         return 0
        #
        #     st = os.stat(self.uri)
        #     bytes = st.st_size
        #     return bytes
        #
        # @property
        # def size(self):
        #     bytes = self.bytes
        #     if bytes > 1024:
        #         return (bytes / 1024)
        #     return bytes
        #
        # @property
        # def kb(self):
        #     if self.exists is False:
        #         return 0
        #
        #     st = os.stat(self.uri)
        #     bytes = st.st_size
        #     if bytes > 1024:
        #         kb = round((float(bytes) / float(1024)), 2)
        #         return kb
        #     elif bytes == 1024:
        #         return 1
        #     return 0
        #
        # @property
        # def mb(self):
        #     kb = self.kb
        #     if kb > 1024:
        #         mb = round((kb / float(1024)), 2)
        #         return mb
        #     elif kb == 1024:
        #         return 1
        #     return 0
        #
        # #@property
        # #def age(self):
        # #    date = self.date_created()
        # #    if date is None:
        # #        return 0
        # #    return chronos.age(date)



class FileStream(object):
    def __init__(self, file, append=False, text_mode=True, encoding="utf-8"):
        self.file = file
        self.uri = file.uri
        self.append = append
        self.text_mode = text_mode
        self.encoding = encoding
        self.stream = None


    def __enter__(self):
        if self.text_mode is False:
            if self.append is False:
                self.stream = open(self.uri, "wb")
                return self
            self.stream = open(self.uri, "a")
        else:
            if self.append is False:
                self.stream = codecs.open(self.uri, "w", self.encoding)
                return self
            self.stream = codecs.open(self.uri, "a", self.encoding)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.stream is not None:
            self.stream.flush()
            self.stream.close()
            self.stream = None

        return self

    def flush(self):
        if self.stream is not None:
            self.stream.flush()


    def write(self, data):
        self.stream.write(data)


    def stream(self, append=False, text_mode=True, encoding="utf-8"):
        if text_mode is False:
            if append is False:
                return open(self.uri, "wb")
            return open(self.uri, "a")


        if append is False:
            return codecs.open(self.uri, "w", encoding)
        return codecs.open(self.uri, "a", encoding)
