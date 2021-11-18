#!python
#cython: language_level=3
########################################################################
########################################################################
# Portions Copyright (c) 2015-present MagicStack Inc.
# https://github.com/MagicStack/httptools
########################################################################
########################################################################
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from cpython cimport PyObject_GetBuffer, PyBuffer_Release, PyBUF_SIMPLE, Py_buffer
from aioclient.parsers.errors import  HttpParserInvalidURLError
cimport cython
from aioclient.parsers cimport cparser

__all__ = ('parse_url', 'URL')

@cython.freelist(250)
cdef class URL:
    cdef readonly bytes schema
    cdef readonly bytes host
    cdef readonly int port
    cdef readonly bytes path
    cdef readonly bytes query
    cdef readonly bytes fragment
    cdef readonly bytes userinfo
    cdef readonly bytes netloc

    def __cinit__(self, bytes schema, bytes host, object port, bytes path,
                  bytes query, bytes fragment, bytes userinfo):

        self.schema = schema if schema is not None else b"http"
        self.host = host if host is not None else b"127.0.0.1"
        if port and port != 0:
            self.port = port
        else:
            if schema == b'https':
                self.port = 443
            else:
                self.port = 80
        self.path = path if path is not None else b""
        self.query = query if query is not None else b""
        self.fragment = fragment if fragment is not None else b""
        self.userinfo = userinfo if userinfo is not None else b""
        self.netloc = b"%b://%b:%d" % (self.schema, self.host, self.port)

    @property
    def raw(self):
        return b"%b%b%b%b" % (self.netloc, self.path, self.query, self.fragment)

    def __repr__(self):
        return ('<URL schema: {!r}, host: {!r}, port: {!r}, path: {!r}, '
                'query: {!r}, fragment: {!r}, userinfo: {!r}>'
                .format(self.schema, self.host, self.port, self.path,
                        self.query, self.fragment, self.userinfo))

def parse_url(url):
    cdef:
        Py_buffer py_buf
        char*buf_data
        cparser.http_parser_url*parsed
        int res
        bytes schema = None
        bytes host = None
        object port = None
        bytes path = None
        bytes query = None
        bytes fragment = None
        bytes userinfo = None
        object result = None
        int off
        int ln

    parsed = <cparser.http_parser_url*> \
        PyMem_Malloc(sizeof(cparser.http_parser_url))
    cparser.http_parser_url_init(parsed)

    PyObject_GetBuffer(url, &py_buf, PyBUF_SIMPLE)
    try:
        buf_data = <char*> py_buf.buf
        res = cparser.http_parser_parse_url(buf_data, py_buf.len, 0, parsed)

        if res == 0:
            if parsed.field_set & (1 << cparser.UF_SCHEMA):
                off = parsed.field_data[<int> cparser.UF_SCHEMA].off
                ln = parsed.field_data[<int> cparser.UF_SCHEMA].len
                schema = buf_data[off:off + ln]

            if parsed.field_set & (1 << cparser.UF_HOST):
                off = parsed.field_data[<int> cparser.UF_HOST].off
                ln = parsed.field_data[<int> cparser.UF_HOST].len
                host = buf_data[off:off + ln]

            if parsed.field_set & (1 << cparser.UF_PORT):
                port = parsed.port

            if parsed.field_set & (1 << cparser.UF_PATH):
                off = parsed.field_data[<int> cparser.UF_PATH].off
                ln = parsed.field_data[<int> cparser.UF_PATH].len
                path = buf_data[off:off + ln]

            if parsed.field_set & (1 << cparser.UF_QUERY):
                off = parsed.field_data[<int> cparser.UF_QUERY].off
                ln = parsed.field_data[<int> cparser.UF_QUERY].len
                query = buf_data[off:off + ln]

            if parsed.field_set & (1 << cparser.UF_FRAGMENT):
                off = parsed.field_data[<int> cparser.UF_FRAGMENT].off
                ln = parsed.field_data[<int> cparser.UF_FRAGMENT].len
                fragment = buf_data[off:off + ln]

            if parsed.field_set & (1 << cparser.UF_USERINFO):
                off = parsed.field_data[<int> cparser.UF_USERINFO].off
                ln = parsed.field_data[<int> cparser.UF_USERINFO].len
                userinfo = buf_data[off:off + ln]
            return URL(schema, host, port, path, query, fragment, userinfo)
        else:
            raise HttpParserInvalidURLError("invalid url {!r}".format(url))
    finally:
        PyBuffer_Release(&py_buf)
        PyMem_Free(parsed)
