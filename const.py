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

MPCHC_TAGS = 'https://api.github.com/repos/mpc-hc/mpc-hc/tags'
MPCHC_DOWNLADS = 'http://mpc-hc.org/downloads/'
MPCHC_LINK_INSTALLER = '<a href="([^\"]+)">installer</a>'
MPCHC_LINK_ARCHIVE = '<a href="([^\"]+)">zip</a>'
MPCHC_NIGHTLY_URL = 'https://nightly.mpc-hc.org/'
MPCHC_NIGHTLY_H5AI_QUERY = {'action': 'get', 'items': 'true', 'itemsHref': '/', 'itemsWhat': '1', 'X-Requested-With': 'XMLHttpRequest'}
MPCHC_NIGHTLY_URL_EXE = 'https://nightly.mpc-hc.org/MPC-HC.{0}.x86.exe'
MPCHC_NIGHTLY_URL_ARCHIVE = 'https://nightly.mpc-hc.org/MPC-HC.{0}.x86.7z'

LAVFILTERS_CLSID = '{171252A0-8820-4AFE-9DF8-5C92B2D66B04}'
LAVFILTERS_RELEASES = 'https://api.github.com/repos/Nevcairiel/LAVFilters/releases'
LAVFILTERS_URL_EXE = 'https://github.com/Nevcairiel/LAVFilters/releases/download/{0}/LAVFilters-{0}-Installer.exe'
LAVFILTERS_URL_ARCHIVE = 'https://github.com/Nevcairiel/LAVFilters/releases/download/{0}/LAVFilters-{0}-x86.zip'

MADVR_CLSID = '{E1A8B82A-32CE-4B0D-BE0D-AA68C772E423}'
MADVR_URL_VERSION = 'http://madshi.net/madVR/version.txt'
MADVR_URL_HASH = 'http://madshi.net/madVR/sha1.txt'
MADVR_URL_ARCHIVE = 'http://madshi.net/madVR.zip'

HEADERS_TRACKABLE = {'User-Agent': 'htpc-updater (https://github.com/nikola/htpc-updater)'}
HEADERS_SF = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'}
