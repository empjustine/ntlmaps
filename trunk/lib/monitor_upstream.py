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
    def __init__(self, config, die_sig=signal.SIGINT):
        self.alive = 1
        self.config = config
        self.die_sig = die_sig
        self.threadsToKill = []
        self.timeoutSeconds = self.config['GENERAL']['PARENT_PROXY_TIMEOUT']
            
    #--------------------------------------------------------------
    def run(self):
        while self.alive:
            self.alarmThread = timerThread(self.timeoutSeconds, self.alive, self.die_sig)
            thread.start_new_thread(self.alarmThread.run, ())
            # We poll the current proxy for responsiveness...           
            # TODO: add logger entries for all these exceptions
            try:
                conn = httplib.HTTPConnection(self.config['GENERAL']['PARENT_PROXY'], self.config['GENERAL']['PARENT_PROXY_PORT'])
                try:
                    conn.request("GET", "/")
                    try:
                        data = conn.getresponse()
                        try:
                            if not data.read():    # Got a b0rked response?
                                self.die()
                        except AssertionError: # Yup, got a wacky response
                            self.die()
                        conn.close()
                    except (AttributeError, httplib.BadStatusLine):    # Didn't somehow connect?
                        self.die()
                except socket.error:    # Service not running/listening on specified port?
                    self.die()
            except socket.gaierror:    # Name resolution error for this proxy?
                self.die()
            self.alarmThread.alive = 0
            time.sleep(self.timeoutSeconds+1)
            # Maximum timeout before hitting bottom of this loop is therefore
            # at most self.timeoutSeconds*2+1 and at least self.timeoutSeconds+1.
            # Hopefully this is a reasonable tradeoff between noticeable
            # service outage for user and creaming the proxy with stacks of
            # our spurious requests... :)

    def die(self):
        try:
            self.alarmThread.alive = 0
        except AttributeError:
            pass # self.alarmThread is already dead
        self.alive = 0
        die_func = signal.getsignal(self.die_sig)
        die_func(self.die_sig)
            
#--------------------------------------------------------------
class timerThread:
    """
    Used in place of SIGALRM as Windows doesn't support it.
    """

    #--------------------------------------------------------------
    def __init__(self, seconds, parentAlive, die_sig=signal.SIGINT):
        self.seconds = seconds
        self.parentAlive = parentAlive
        self.die_sig = die_sig
        self.alive = 1

    #--------------------------------------------------------------
    def run(self):
        time.sleep(self.seconds)
        if self.alive and self.parentAlive:
            die_func = signal.getsignal(self.die_sig)
            die_func(self.die_sig)
