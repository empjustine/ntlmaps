#! /usr/bin/python

# This file is Copyright 2005 Mario Zoppetti, and was added by
# Darryl A. Dixon <esrever_otua@pythonhacker.is-a-geek.net> to 
# 'NTLM Authorization Proxy Server',
# Copyright 2001 Dmitry A. Rozmanov <dima@xenon.spb.ru>
#
# NTLM APS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# NTLM APS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the sofware; see the file COPYING. If not, write to the
# Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# setup.py
from distutils.core import setup
import py2exe, sys, re, string
sys.argv.append("py2exe")

# Hmmmmmm.
repline = re.compile("(?P<before>^conf.*?)__init__.*?(?P<after>\)\)$)", re.M|re.S)
fileh = open('main.py', 'r')
code = fileh.read()
fileh.close()
newcode = re.sub(repline, re.search(repline, code).group('before')+"'./'"+re.search(repline, code).group('after'), code)
fileh = open('main.py', 'w')
fileh.write(newcode)
fileh.close()

_ver = string.replace(string.split(sys.version)[0], '.', '')[:2]
_thisdir = 'py%s' % _ver
sys.path.append('lib/%s' % _thisdir)

try:
    import _win32console
except ImportError:
    win32console_mod = ''
else:
    win32console_mod = 'lib/%s/_win32console' % _thisdir

setup(name='ntlmaps',
    version='0.9.9.7',
    console=["main.py"],
    options = {"py2exe": {"packages": ["encodings"],
                          "optimize": 2}},
    py_modules = ['lib/basic_auth',
        'lib/config',
        'lib/config_affairs',
        'lib/des',
        'lib/des_c',
        'lib/des_data',
        'lib/http_header',
        'lib/logger',
        'lib/md4',
        'lib/monitor_upstream',
        'lib/ntlm_auth',
        'lib/ntlm_messages',
        'lib/ntlm_procs',
        'lib/proxy_client',
        'lib/server',
        'lib/U32',
        'lib/utils',
        'win32console',
        win32console_mod],
    data_files=[("",["server.cfg"]),],
    description='NTLM Authorization Proxy Server',
    author='Dmitry A. Rozmanov',
    author_email='<dima@xenon.spb.ru',
    url='http://ntlmaps.sourceforge.net/',
    )
