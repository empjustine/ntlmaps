# This file is Copyright 2004 Darryl A. Dixon <esrever_otua@pythonhacker.is-a-geek.net>
# and is part of 'NTLM Authorization Proxy Server',
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

import signal, httplib, time, sys, socket

#--------------------------------------------------------------
class monitorThread:

    #--------------------------------------------------------------
    def __init__(self, config):
        self.config = config
        signal.signal(signal.SIGINT, self.sigHandler)
        signal.signal(signal.SIGALRM, self.sigHandler)
        self.threadsToKill = []
            
    #--------------------------------------------------------------
    def run(self):
        if self.config['GENERAL']['PARENT_PROXY']:
            while 1:
                signal.alarm(3)
                # We poll the current proxy for responsiveness...           
                try:
                    conn = httplib.HTTPConnection(self.config['GENERAL']['PARENT_PROXY'], self.config['GENERAL']['PARENT_PROXY_PORT'])
                    try:
                        conn.request("GET", "/")
                        try:
                            data = conn.getresponse()
                            if not data.read():    # Got a b0rked response?
                                self.sigHandler(signal.SIGINT)
                            conn.close()
                        except AttributeError:    # Didn't somehow connect?
                            self.sigHandler(signal.SIGINT)
                    except socket.error:    # Service not running/listening on specified port?
                        self.sigHandler(signal.SIGINT)
                except socket.gaierror:    # Name resolution error for this proxy?
                    self.sigHandler(signal.SIGINT)
                signal.alarm(0)
                time.sleep(2)
                # Maximum timeout before hitting bottom of this loop is therefore
                # at most ~5 seconds and at least >2 seconds.
                # Hopefully this is a reasonable timeout to tradeoff between noticeable
                # service outage for user and creaming the proxy with stacks of
                # our spurious requests... :)
        else:
            while 1:
                pass #'Gracefully' spin without returning from function
            
    #--------------------------------------------------------------
    def sigHandler(self, signum=None, frame=None):
        if signum == signal.SIGINT:
            if self.config['GENERAL']['PARENT_PROXY']:
                #print "Got SIGINT, changing server now..."
                self.config['GENERAL']['AVAILABLE_PROXY_LIST'].insert(0, self.config['GENERAL']['PARENT_PROXY'])
                self.config['GENERAL']['PARENT_PROXY'] = self.config['GENERAL']['AVAILABLE_PROXY_LIST'].pop()
                print "Moving to proxy server: "+self.config['GENERAL']['PARENT_PROXY']
                # Done this way to avoid races without having to resort to
                # locking, as new connections are coming in all the time...
                for i in range(len(self.threadsToKill)):
                    self.threadsToKill[0].exit()
                    self.threadsToKill.remove(self.threadsToKill[0])
            else:
                # SIGINT is only special if we are in upstream mode:
                print 'Got '+signum+', exiting now...'
                sys.exit(1)
        elif signum == signal.SIGALRM:
            # Timeout on proxy responses
            #print "Timed out with ALRM"
            self.sigHandler(signal.SIGINT)
        else:
            print 'Got '+signum+', exiting now...'
            sys.exit(1)
        return
