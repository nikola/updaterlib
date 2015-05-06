# coding: iso-8859-1
"""
https://github.com/nikola/updaterlib
Copyright (c) 2014-2015 Nikola Klaric

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
__author__ = 'Nikola Klaric (nikola@generic.company)'
__copyright__ = 'Copyright (c) 2014-2015 Nikola Klaric'

import os
import re
import _winreg as registry
from tempfile import mkstemp
from ctypes import windll, create_string_buffer, c_uint, byref, string_at
from array import array
from zipfile import ZipFile
from cStringIO import StringIO


def getVersionTuple(version):
    version = re.sub(r'[a-z0-9]{7}', '', version)
    version = re.sub(r'[^0-9\._]', '', version)
    version = re.sub(r'^_|_$|__+', '', version)
    version = re.sub(r'_', '.', version).strip()
    return tuple(map(int, (version.split('.'))))


def writeTempFile(payload):
    fd, pathname = mkstemp(suffix='.exe')
    fp = os.fdopen(fd, 'wb')
    fp.write(payload)
    fp.close()

    return pathname


def getProductVersion(pathname):
    if os.path.exists(pathname) and os.path.isfile(pathname):
        filename = unicode(pathname)

        size = windll.version.GetFileVersionInfoSizeW(filename, None)
        if size:
            res = create_string_buffer(size)
            windll.version.GetFileVersionInfoW(filename, None, size, res)
            r = c_uint()
            l = c_uint()
            windll.version.VerQueryValueA(res, '\\VarFileInfo\\Translation', byref(r), byref(l))
            if l.value:
                windll.version.VerQueryValueA(
                    res,
                    '\\StringFileInfo\\%04x%04x\\FileVersion' % tuple(array('H', string_at(r.value, l.value))[:2].tolist()),
                    byref(r), byref(l),
                )
                return '.'.join(map(str, getVersionTuple(string_at(r.value, l.value))))
    raise ValueError


def getComLocationFromRegistry(clsid):
    connection = registry.ConnectRegistry(None, registry.HKEY_CLASSES_ROOT)
    key = registry.OpenKey(connection, r'CLSID\%s\InprocServer32' % clsid)
    pathname = registry.QueryValueEx(key, None)[0]
    key.Close()

    if os.path.exists(pathname):
        return pathname
    else:
        raise


def addAppLocationRegistryKey(software, location):
    connection = registry.ConnectRegistry(None, registry.HKEY_CURRENT_USER)
    key = registry.OpenKey(connection, r'Software\%s' % software, 0, registry.KEY_WRITE)
    registry.SetValueEx(key, 'ExePath', 0, registry.REG_SZ, location)
    registry.FlushKey(key)
    key.Close()


def getComVersionLocation(key):
    location = getComLocationFromRegistry(key)
    version = getProductVersion(location)
    return version, os.path.dirname(location)


def getAppLocationFromRegistry(software):
    connection = registry.ConnectRegistry(None, registry.HKEY_CURRENT_USER)
    key = registry.OpenKey(connection, r'Software\%s' % software)
    pathname = registry.QueryValueEx(key, 'ExePath')[0]
    key.Close()

    if os.path.exists(pathname):
        return pathname
    else:
        raise


def unzip(context, blob, pathname, compact=False, base=None, excludeExt=None, excludeList=None, compatText=False):
    if excludeList is None:
        excludeList = []

    zipFile = ZipFile(StringIO(blob))
    for member in zipFile.namelist():
        filename = zipFile.getinfo(member).filename
        if (excludeExt is not None and filename.lower().endswith(excludeExt)) or filename in excludeList:
            continue
        elif filename.find('/') != -1:
            if base is not None and filename[:filename.index('/')].lower().startswith(base):
                filename = filename[filename.index('/')+1:]
                if not filename or (compact and '/' in filename):
                    continue
            elif compact:
                continue
            elif filename.endswith('/'):
                os.makedirs(os.path.join(pathname, os.path.normpath(filename)))
                continue
            else:
                try:
                    os.makedirs(os.path.join(pathname, os.path.normpath(filename[:filename.rindex('/')])))
                except WindowsError:
                    pass
        if compact and compatText and (filename.endswith('.txt') or filename == 'COPYING'):
            filename = '[%s] %s' % (context, filename)
        with open(os.path.join(pathname, os.path.normpath(filename)), 'wb') as fp:
            fp.write(zipFile.open(member).read())
    zipFile.close()
