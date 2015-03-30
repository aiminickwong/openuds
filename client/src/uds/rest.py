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

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import QObject, QUrl
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply, QSslCertificate
from PyQt4.QtGui import QMessageBox

import json
import six


class RestRequest(QObject):

    restApiUrl = ''  #
    done = pyqtSignal(QObject)

    def __init__(self, url, parentWindow, done):  # parent not used
        super(RestRequest, self).__init__()
        # private
        self._manager = QNetworkAccessManager()
        self.data = None
        self.url = QUrl(RestRequest.restApiUrl + url)

        # connect asynchronous result, when a request finishes
        self._manager.finished.connect(self._finished)
        self._manager.sslErrors.connect(self._sslError)
        self._parentWindow = parentWindow

        self.done.connect(done)

    # private slot, no need to declare as slot
    def _finished(self, reply):
        '''
        Handle signal 'finished'.  A network request has finished.
        '''
        try:
            if reply.error() != QNetworkReply.NoError:
                raise Exception(reply.errorString())

            data = six.text_type(reply.readAll())
            self.data = json.loads(data)
        except Exception as e:
            self.data = {
                'result': None,
                'error': six.text_type(e)
            }

        reply.deleteLater()  # schedule for delete from main event loop
        self.done.emit(self)

    def _sslError(self, reply, errors):

        print "SSL Error"
        print reply
        cert = errors[0].certificate()
        errorString = 'The certificate for "{}" has the following errors:\n'.format(cert.subjectInfo(QSslCertificate.CommonName))
        for err in errors:
            errorString += err.errorString() + '\n'

        if QMessageBox.warning(self._parentWindow, 'SSL Error', errorString, QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            reply.ignoreSslErrors()

    def get(self):
        print self.url
        request = QNetworkRequest(self.url)
        self._manager.get(request)