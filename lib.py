# coding: iso-8859-1
"""
"""
__author__ = 'Nikola Klaric (nikola@generic.company)'
__copyright__ = 'Copyright (c) 2014 Nikola Klaric'

import time
from hashlib import sha1 as SHA1
from inspect import getmembers, ismethod
from types import MethodType
from operator import itemgetter

import requests
from lxml.html.clean import clean_html

from const import *
from utils import *


BLACK, GREEN, RED = 15, 10, 12

MPC_HC_LOG = '%s_MPC-HC.log' % time.strftime('%Y-%m-%d')


def _getDefaultInstallationPath(component):
    pathname = os.path.join(os.environ['PROGRAMFILES'], component)
    if not os.path.exists(pathname):
        os.makedirs(pathname)

    return pathname


class Component(object):

    def __init__(self, *args, **kwargs):
        self._identifier = args[0]
        for method in map(itemgetter(0), getmembers(self, predicate=ismethod)):
            if method in kwargs: setattr(self, method, MethodType(kwargs.get(method), self))

    def getLatestReleaseVersion(self, *args, **kwargs): pass
    def getLatestPreReleaseVersion(self, *args, **kwargs): pass
    def getInstalledVersion(self, *args, **kwargs): pass
    def getPostInstallVersion(self, *args, **kwargs): return self.getInstalledVersion(*args, **kwargs)
    def installLatestReleaseVersion(self, *args, **kwargs): pass
    def installLatestPreReleaseVersion(self, *args, **kwargs): pass


log = lambda x, *y: None
def setLogger(func):
    global log
    log = func


def getLatestGitHubReleaseVersion(url):
    return requests.get(url, headers=HEADERS_TRACKABLE).json()[0].get('tag_name')


def mpcHc_getLatestReleaseVersion(self):
    return '.'.join(map(str, max([getVersionTuple(tag.get('name'))
        for tag in requests.get(MPCHC_TAGS, headers=HEADERS_TRACKABLE).json()])))


def mpcHc_getLatestPreReleaseVersion(self):
    items = requests.post(MPCHC_NIGHTLY_URL, MPCHC_NIGHTLY_H5AI_QUERY, headers=HEADERS_TRACKABLE).json().get('items')
    return re.match(r'^/MPC-HC\.((\d+\.?)+)\.x86\.exe$',
        filter(lambda i: i.get('absHref').endswith('.x86.exe'), items)[0].get('absHref')).group(1)


def mpcHc_getInstalledVersion(self, location=None, *args, **kwargs):
    try:
        if location is None:
            location = getAppLocationFromRegistry(self._identifier)
        version = getProductVersion(location)
    except:
        return None, None
    else:
        return version, os.path.dirname(location)


def mpcHc_getPostInstallVersion(self, cwd, *args, **kwargs):
    logPathname = os.path.join(cwd, MPC_HC_LOG)
    if os.path.exists(logPathname):
        with open(logPathname, 'rU') as fd:
            protocol = fd.read()
        if protocol.find('Installation process succeeded.') != -1:
            installationSearch = re.search('Directory for uninstall files:\s+(.*?)$', protocol, re.M)
            if installationSearch is not None:
                location = installationSearch.group(1)
                mpcHcexecutable = os.path.join(location, 'mpc-hc.exe')
                version = getProductVersion(mpcHcexecutable)

                # Manually set the installation directory in the Windows registry
                # in case the user did not launch MPC-HC at the last step in InnoSetup.
                addAppLocationRegistryKey(r'MPC-HC\MPC-HC', mpcHcexecutable)

                return version, location

    return None, None


def mpcHc_install(payload, version, pathname, silent, archive, compact=False, compatText=False):
    log('Installing MPC-HC %s ...' % version)
    if not archive:
        pathname = writeTempFile(payload)
        verySilent = '/VERYSILENT ' if silent else ''
        os.system('""%s" /NORESTART %s/NOCLOSEAPPLICATIONS /LOG=%s""' % (pathname, verySilent, MPC_HC_LOG))
        os.remove(pathname)
    else:
        unzip('MPC-HC', payload, pathname, compact, base='mpc-hc', compatText=compatText)


def mpcHc_installLatestReleaseVersion(self, version, pathname, silent=False, archive=False, compact=False, compatText=False):
    log('Identifying filename of MPC-HC download ...')
    html = clean_html(requests.get(MPCHC_DOWNLADS, headers=HEADERS_TRACKABLE).text)
    url = MPCHC_LINK_ARCHIVE if archive else MPCHC_LINK_INSTALLER
    initialUrl = re.search(url, html).group(1)
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

    mpcHc_install(response, version, pathname, silent, archive, compact, compatText)


def mpcHc_installLatestPreReleaseVersion(self, version, pathname, silent=False, archive=False, compact=False, compatText=False):
    url = MPCHC_NIGHTLY_URL_EXE.format(version)
    log('Downloading %s ...' % url)
    response = requests.get(url, headers=HEADERS_TRACKABLE).content
    log(' done.\n')

    mpcHc_install(response, version, pathname, silent, archive, compact, compatText)


def lavFilters_getLatestReleaseVersion(self):
    return getLatestGitHubReleaseVersion(LAVFILTERS_RELEASES)


def lavFilters_getInstalledVersion(self, location=None, *args, **kwargs):
    try:
        if location is None:
            version, location = getComVersionLocation(self._identifier)
            if location.endswith('x86') or location.endswith('x64'):
                location = os.path.abspath(os.path.join(location, os.pardir))
        else:
            version = getProductVersion(location)
    except:
        return None, None
    else:
        return version, os.path.dirname(location)


def lavFilters_installLatestReleaseVersion(self, version, pathname, silent=False, archive=False, compact=False, compatText=False):
    url = (LAVFILTERS_URL_ARCHIVE if archive else LAVFILTERS_URL_EXE).format(version)
    log('Downloading %s ...' % url)
    blob = requests.get(url, headers=HEADERS_TRACKABLE).content
    log(' done.\n')

    log('Installing LAV Filters %s ...' % version)
    if archive:
        unzip('LAV Filters', blob, pathname, compact, excludeExt='.bat', compatText=compatText)
    else:
        pathname = writeTempFile(blob)
        os.system('""%s" /NORESTART /NOCLOSEAPPLICATIONS""' % pathname)
        os.remove(pathname)


def madVr_getLatestReleaseVersion(self):
    return requests.get(MADVR_URL_VERSION, headers=HEADERS_TRACKABLE).text


def madVr_getInstalledVersion(self, location=None, *args, **kwargs):
    try:
        if location is None:
            version, location = getComVersionLocation(self._identifier)
        else:
            version = getProductVersion(location)
    except:
        return None, None
    else:
        return version, os.path.dirname(location)


def madVr_installLatestReleaseVersion(self, version, pathname, silent=False, compact=False, compatText=False, *args, **kwargs):
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
    madVrInstallationPath = pathname or _getDefaultInstallationPath('madVR')

    excludeList = ['InstallFilter.exe', 'madVR [debug].ax'] if compact else []
    excludeExt = '.bat' if compact else None
    unzip('madVR', madVrZipFile, madVrInstallationPath, compact=compact, excludeExt=excludeExt, excludeList=excludeList, compatText=compatText)

    os.system('""%s" /s "%s""'
        % (os.path.join(os.environ['SYSTEMROOT'], 'System32', 'regsvr32'), os.path.join(madVrInstallationPath, 'madVR.ax')))
