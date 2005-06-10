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

import signal, httplib, time, socket, thread, os

#--------------------------------------------------------------
class monitorThread:

    #--------------------------------------------------------------
    def __init__(self, config):
        self.alive = 1
        self.config = config
        self.threadsToKill = []
            
    #--------------------------------------------------------------
    def run(self):
        if self.config['GENERAL']['PARENT_PROXY']:
            while self.alive:
                self.alarmThread = timerThread(3, self)
                thread.start_new_thread(self.alarmThread.run, ())
                # We poll the current proxy for responsiveness...           
                try:
                    conn = httplib.HTTPConnection(self.config['GENERAL']['PARENT_PROXY'], self.config['GENERAL']['PARENT_PROXY_PORT'])
                    try:
                        conn.request("GET", "/")
                        try:
                            data = conn.getresponse()
                            if not data.read():    # Got a b0rked response?
                                self.die()
                            conn.close()
                        except AttributeError:    # Didn't somehow connect?
                            self.die()
                    except socket.error:    # Service not running/listening on specified port?
                        self.die()
                except socket.gaierror:    # Name resolution error for this proxy?
                    self.die()
                self.alarmThread.alive = 0
                time.sleep(2)
                # Maximum timeout before hitting bottom of this loop is therefore
                # at most ~5 seconds and at least >2 seconds.
                # Hopefully this is a reasonable timeout to tradeoff between noticeable
                # service outage for user and creaming the proxy with stacks of
                # our spurious requests... :)
        else:
            while self.alive:
                pass #'Gracefully' spin without returning from function
        thread.exit()

    def die(self, die_sig=signal.SIGINT):
        self.alive = 0
        self.alarmThread.alive = 0
        os.kill(os.getpid(), die_sig)
        thread.exit()
            
#--------------------------------------------------------------
class timerThread:
    """
    Used in place of SIGALRM as Windows doesn't support it.
    """

    #--------------------------------------------------------------
    def __init__(self, seconds, caller):
        self.alive = 1
        self.timed_out = 0
        self.seconds = seconds
        self.caller = caller

    #--------------------------------------------------------------
    def run(self):
        time.sleep(self.seconds)
        if self.alive and self.caller.alive:
            self.timed_out = 1
            #print "Timer expired"
            os.kill(os.getpid(), signal.SIGINT)
        thread.exit()
