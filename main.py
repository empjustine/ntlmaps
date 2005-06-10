#! /usr/bin/python

# This file is part of 'NTLM Authorization Proxy Server'
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
import __init__

import socket, thread, sys, getpass, string

import server, logger
import config, ntlm_procs, config_affairs


#--------------------------------------------------------------
# config affairs
# look for default config name in lib/config.py
conf = config.read_config(config.findConfigFileNameInArgv(sys.argv, __init__.ntlmaps_dir+'/'))

conf['GENERAL']['VERSION'] = '0.9.8.5'

config = config_affairs.arrange(conf)

#--------------------------------------------------------------
print 'NTLM authorization Proxy Server v%s' % conf['GENERAL']['VERSION'],
print 'at "%s:%s".' % (conf['GENERAL']['HOST'], conf['GENERAL']['LISTEN_PORT'])
print '2001-2004 (C) by Dmitry Rozmanov'
#print '\nAccepting connections'

#--------------------------------------------------------------
# password from console, if we don't have one in server.cfg
if not conf['NTLM_AUTH']['PASSWORD']:
    tries = 3
    print '------------------------'
    while tries and (not conf['NTLM_AUTH']['PASSWORD']):
        tries = tries - 1
        conf['NTLM_AUTH']['PASSWORD'] = getpass.getpass('Your NT password to be used:')

if not conf['NTLM_AUTH']['PASSWORD']:
    print 'Sorry. PASSWORD is required. Bye.'
    sys.exit(1)

#--------------------------------------------------------------
# hashed passwords calculation
conf['NTLM_AUTH']['LM_HASHED_PW'] = ntlm_procs.create_LM_hashed_password(conf['NTLM_AUTH']['PASSWORD'])
conf['NTLM_AUTH']['NT_HASHED_PW'] = ntlm_procs.create_NT_hashed_password(conf['NTLM_AUTH']['PASSWORD'])

#--------------------------------------------------------------
# let's run it
serv = server.AuthProxyServer(conf)
serv.run()
