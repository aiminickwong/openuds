# -*- coding: utf-8 -*-

#
# Copyright (c) 2015 Virtual Cable S.L.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#    * Neither the name of Virtual Cable S.L. nor the names of its contributors
#      may be used to endorse or promote products derived from this software
#      without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''
@author: Adolfo Gómez, dkmaster at dkmon dot com
'''
from __future__ import unicode_literals

import tempfile
import string
import random
import os
import sys
import stat

_unlinkFiles = []
_tasksToWait = []
_execBeforeExit = []


def saveTempFile(content, filename=None):
    if filename is None:
        filename = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
        filename = filename + '.uds'
    filename = os.path.join(tempfile.gettempdir(), filename)
    with open(filename, 'w') as f:
        f.write(content)

    return filename


def findApp(appName, extraPath=None):
    searchPath = os.environ['PATH'].split(os.pathsep)
    if extraPath is not None:
        searchPath += extraPath

    for path in searchPath:
        fileName = os.path.join(path, appName)
        if os.path.isfile(fileName) and (os.stat(fileName).st_mode & stat.S_IXUSR) != 0:
            return fileName
    return None


# Queing operations (to be executed before exit)

def addFileToUnlink(filename):
    '''
    Adds a file to the wait-and-unlink list
    '''
    _unlinkFiles.append(filename)


def unlinkFiles():
    '''
    Removes all wait-and-unlink files
    '''
    for f in _unlinkFiles:
        try:
            os.unlink(f)
        except Exception:
            pass


def addTaskToWait(taks):
    _tasksToWait.append(taks)


def waitForTasks():
    for t in _tasksToWait:
        t.wait()


def addExecBeforeExit(fnc):
    _execBeforeExit.append(fnc)


def execBeforeExit():
    for fnc in _execBeforeExit:
        fnc.__call__()
