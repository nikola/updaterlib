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
    result = check_output(
        " ".join([
            os.path.join(os.environ['SYSTEMROOT'], 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe'),
            "(Get-Item '%s').VersionInfo.ProductVersion" % pathname,
        ]),
    ).rstrip()
    return result


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
    try:
        location = getComLocationFromRegistry(key)
        version = getProductVersion(location)
    except:
        return None, None
    else:
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
