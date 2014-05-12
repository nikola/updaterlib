# coding: iso-8859-1
"""
"""
__author__ = 'Nikola Klaric (nikola@generic.company)'
__copyright__ = 'Copyright (c) 2014 Nikola Klaric'

import os
import re
import _winreg as registry
from tempfile import mkstemp
from subprocess import check_output
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
    if not (os.path.exists(pathname) and os.path.isfile(pathname)):
        raise ValueError
    else:
        result = check_output(
            " ".join([
                os.path.join(os.environ['SYSTEMROOT'], 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe'),
                "(Get-Item '%s').VersionInfo.ProductVersion" % pathname,
            ]),
        ).strip()
        return '.'.join(map(str, getVersionTuple(result)))


def getComLocationFromRegistry(clsid):
    connection = registry.ConnectRegistry(None, registry.HKEY_CLASSES_ROOT)
    key = registry.OpenKey(connection, r'CLSID\%s\InprocServer32' % clsid)
    pathname = registry.QueryValueEx(key, None)[0]
    key.Close()

    if os.path.exists(pathname):
        return pathname
    else:
        raise


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


def unzip(context, blob, pathname, compact=False, base=None, excludeExt=None, excludeList=[], compatText=False):
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
