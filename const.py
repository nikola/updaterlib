# coding: iso-8859-1
"""
"""
__author__ = 'Nikola Klaric (nikola@generic.company)'
__copyright__ = 'Copyright (c) 2014 Nikola Klaric'

MPCHC_TAGS = 'https://api.github.com/repos/mpc-hc/mpc-hc/tags'
MPCHC_DOWNLADS = 'http://mpc-hc.org/downloads/'
MPCHC_LINK_INSTALLER = '<a href="([^\"]+)">installer</a>'
MPCHC_LINK_ARCHIVE = '<a href="([^\"]+)">zip</a>'
MPCHC_NIGHTLY_URL = 'http://nightly.mpc-hc.org/'
MPCHC_NIGHTLY_H5AI_QUERY = {'action':'get', 'items': 'true', 'itemsHref':'/', 'itemsWhat': '1'}
MPCHC_NIGHTLY_URL_EXE = 'http://nightly.mpc-hc.org/MPC-HC.{0}.x86.exe'
MPCHC_NIGHTLY_URL_ARCHIVE = 'http://nightly.mpc-hc.org/MPC-HC.{0}.x86.7z'

LAVFILTERS_CLSID = '{171252A0-8820-4AFE-9DF8-5C92B2D66B04}'
LAVFILTERS_RELEASES = 'https://api.github.com/repos/Nevcairiel/LAVFilters/releases'
LAVFILTERS_URL_EXE = 'https://github.com/Nevcairiel/LAVFilters/releases/download/{0}/LAVFilters-{0}-Installer.exe'
LAVFILTERS_URL_ARCHIVE = 'https://github.com/Nevcairiel/LAVFilters/releases/download/{0}/LAVFilters-{0}-x86.zip'

MADVR_CLSID = '{E1A8B82A-32CE-4B0D-BE0D-AA68C772E423}'
MADVR_URL_VERSION = 'http://madshi.net/madVR/version.txt'
MADVR_URL_HASH = 'http://madshi.net/madVR/sha1.txt'
MADVR_URL_ARCHIVE = 'http://madshi.net/madVR.zip'

HEADERS_TRACKABLE = {'User-agent': 'htpc-updater (https://github.com/nikola/htpc-updater)'}
HEADERS_SF = {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'}
