# coding: iso-8859-1
"""
"""
__author__ = 'Nikola Klaric (nikola@generic.company)'
__copyright__ = 'Copyright (c) 2014 Nikola Klaric'

import time
from hashlib import sha1 as SHA1
from zipfile import ZipFile
from cStringIO import StringIO
from inspect import getmembers, ismethod
from types import MethodType
from operator import itemgetter

import requests

from const import *
from utils import *


BLACK, GREEN, RED = 15, 10, 12


def _getDefaultInstallationPath(component):
    pathname = os.path.join(os.environ['PROGRAMFILES'], component)
    if not os.path.exists(pathname):
        os.makedirs(pathname)

    return pathname


def _getLatestGitHubReleaseVersion(url):
    try:
        response = requests.get(url, headers=HEADERS_TRACKABLE).json()
        latestVersion = response[0].get('tag_name')
    except:
        latestVersion = None

    return latestVersion


log = lambda x, *y: None
def setLogger(func):
    global log
    log = func


class Component(object):

    def __init__(self, *args, **kwargs):
        self._identifier = args[0]
        for method in map(itemgetter(0), getmembers(self, predicate=ismethod)):
            if method in kwargs: setattr(self, method, MethodType(kwargs.get(method), self))

    def getLatestReleaseVersion(self, *args, **kwargs): pass
    def getLatestPreReleaseVersion(self, *args, **kwargs): pass
    def getInstalledVersion(self, *args, **kwargs): pass
    def installLatestReleaseVersion(self, *args, **kwargs): pass
    def installLatestPreReleaseVersion(self, *args, **kwargs): pass


def mpcHc_getLatestReleaseVersion(self):
    try:
        latestReleaseVersion = '.'.join(map(str, max([getVersionTuple(tag.get('name'))
            for tag in requests.get(MPCHC_TAGS, headers=HEADERS_TRACKABLE).json()])))
    except:
        latestReleaseVersion = None

    return latestReleaseVersion


def mpcHc_getLatestPreReleaseVersion(self):
    try:
        items = requests.post(MPCHC_NIGHTLY_URL, MPCHC_NIGHTLY_H5AI_QUERY, headers=HEADERS_TRACKABLE).json().get('items')
        latestPreReleaseVersion = re.match(r'^/MPC-HC\.((\d+\.?)+)\.x86\.exe$',
            filter(lambda i: i.get('absHref').endswith('.x86.exe'), items)[0].get('absHref')).group(1)
    except:
        latestPreReleaseVersion = None

    return latestPreReleaseVersion


def mpcHc_getInstalledVersion(self):
    try:
        location = getAppLocationFromRegistry(self._identifier)
        version = getProductVersion(location)
    except:
        return None, None
    else:
        return version, os.path.dirname(location)


def mpcHc_install(exe, version, silent):
    log('Installing MPC-HC %s ...' % version)
    pathname = writeTempFile(exe)
    verySilent = '/VERYSILENT ' if silent else ''
    os.system('""%s" /NORESTART %s/NOCLOSEAPPLICATIONS""' % (pathname, verySilent))
    os.remove(pathname)


def mpcHc_installLatestReleaseVersion(self, version, path, silent=False):
    log('Identifying filename of MPC-HC download ...')
    response = requests.get(MPCHC_DOWNLADS, headers=HEADERS_TRACKABLE).text
    initialUrl = re.search(MPCHC_LINK_INSTALLER, response).group(1)
    log(' done.\n')

    retries = 0
    while True:
        log('Selecting filehost for MPC-HC download ...')
        response = requests.get(initialUrl, headers=HEADERS_SF).text
        filehostResolver = re.search('<meta[^>]*?url=(.*?)["\']', response, re.I).group(1)
        filehostName = re.search('use_mirror=([a-z\-]+)', filehostResolver).group(1)
        filehostUrl = filehostResolver[:filehostResolver.index('?')].replace('downloads', filehostName + '.dl')
        log(' done: %s.\n' % filehostName)

        time.sleep(1)

        log('Downloading %s ...' % filehostUrl)
        response = requests.get(filehostUrl, headers=HEADERS_SF).content
        log(' done.\n')

        if response.strip().endswith('</html>') or len(response) < 1e6:
            retries += 1

            if retries < 10:
                log('Selected filehost is not serving MPC-HC %s, trying another filehost.\n' % version, RED)
                time.sleep(2)
            else:
                log('It appears no filehost can be found serving MPC-HC %s, aborting for now.\n' % version, RED)
                return
        else:
            break

    mpcHc_install(response, version, silent)


def mpcHc_installLatestPreReleaseVersion(self, version, path, silent=False):
    url = MPCHC_NIGHTLY_URL_EXE.format(version)
    log('Downloading %s ...' % url)
    response = requests.get(url, headers=HEADERS_TRACKABLE).content
    log(' done.\n')

    mpcHc_install(response, version, silent)


def lavFilters_getLatestReleaseVersion(self):
    return _getLatestGitHubReleaseVersion(LAVFILTERS_RELEASES)


def lavFilters_getInstalledVersion(self):
    version, location = getComVersionLocation(self._identifier)
    if location.endswith('x86') or location.endswith('x64'):
         location = os.path.abspath(os.path.join(location, os.pardir))
    return version, location


def lavFilters_installLatestReleaseVersion(self, version, path, silent=False):
    url = LAVFILTERS_URL_EXE.format(version)
    log('Downloading %s ...' % url)
    response = requests.get(url, headers=HEADERS_TRACKABLE).content
    log(' done.\n')

    log('Installing LAV Filters %s ...' % version)
    pathname = writeTempFile(response)
    os.system('""%s" /NORESTART /NOCLOSEAPPLICATIONS""' % pathname)
    os.remove(pathname)


def madVr_getLatestReleaseVersion(self):
    try:
        latestVersion = requests.get(MADVR_URL_VERSION, headers=HEADERS_TRACKABLE).text
    except:
        latestVersion = None

    return latestVersion


def madVr_getInstalledVersion(self):
    return getComVersionLocation(self._identifier)


def madVr_installLatestReleaseVersion(self, version, path, silent=False):
    log('Downloading %s ...' % MADVR_URL_ARCHIVE)
    madVrZipFile = requests.get(MADVR_URL_ARCHIVE, headers=HEADERS_TRACKABLE).content
    log(' done.\n')

    log('Verifying SHA1 of downloaded ZIP file ...')
    madVrZipHashShould = requests.get(MADVR_URL_HASH, headers=HEADERS_TRACKABLE).content
    sha1 = SHA1()
    sha1.update(madVrZipFile)
    madVrZipHashIs = sha1.hexdigest()
    if madVrZipHashIs == madVrZipHashShould:
        log(' OK!\n')
    else:
        log(' ERROR: SHA1 is %s but should be %s!\n' % (madVrZipHashIs, madVrZipHashShould), RED)
        log('Aborting installation of madVR %s.\n' % version, RED)
        return

    log('Installing madVR %s ...' % version)
    madVrInstallationPath = path or _getDefaultInstallationPath('madVR')

    ZipFile(StringIO(madVrZipFile)).extractall(madVrInstallationPath)

    os.system('""%s" /s "%s""'
        % (os.path.join(os.environ['SYSTEMROOT'], 'System32', 'regsvr32'), os.path.join(madVrInstallationPath, 'madVR.ax')))
