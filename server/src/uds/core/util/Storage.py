# -*- coding: utf-8 -*-

#
# Copyright (c) 2012 Virtual Cable S.L.
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

from django.db import transaction
from uds.models import Storage as dbStorage
import hashlib
import logging
import cPickle

logger = logging.getLogger(__name__)


class Storage(object):
    CODEC = 'base64'  # Can be zip, hez, bzip, base64, uuencoded

    def __init__(self, owner):
        self._owner = owner.encode('utf-8')

    def __getKey(self, key):
        h = hashlib.md5()
        h.update(self._owner)
        h.update(key.encode('utf-8'))
        return h.hexdigest()

    def saveData(self, skey, data, attr1=None):
        key = self.__getKey(skey)
        if isinstance(data, unicode):
            data = data.encode('utf-8')
        data = data.encode(Storage.CODEC)
        attr1 = '' if attr1 is None else attr1
        try:
            dbStorage.objects.create(owner=self._owner, key=key, data=data, attr1=attr1)  # @UndefinedVariable
        except Exception:
            dbStorage.objects.filter(key=key).update(owner=self._owner, data=data, attr1=attr1)  # @UndefinedVariable
        logger.debug('Key saved')

    def put(self, skey, data):
        return self.saveData(skey, data)

    def putPickle(self, skey, data, attr1=None):
        return self.saveData(skey, cPickle.dumps(data), attr1)

    def updateData(self, skey, data, attr1=None):
        self.saveData(skey, data, attr1)

    def readData(self, skey, fromPickle=False):
        try:
            key = self.__getKey(skey)
            logger.debug('Accesing to {0} {1}'.format(skey, key))
            c = dbStorage.objects.get(pk=key)  # @UndefinedVariable
            val = c.data.decode(Storage.CODEC)

            if fromPickle:
                return val

            try:
                return val.decode('utf-8')  # Tries to encode in utf-8
            except:
                return val
        except dbStorage.DoesNotExist:  # @UndefinedVariable
            logger.debug('key not found')
            return None

    def get(self, skey):
        return self.readData(skey)

    def getPickle(self, skey):
        v = self.readData(skey, True)
        if v is not None:
            v = cPickle.loads(v)
        return v

    def remove(self, skey):
        try:
            key = self.__getKey(skey)
            dbStorage.objects.filter(key=key).delete()  # @UndefinedVariable
        except Exception:
            pass

    def lock(self):
        '''
        Use with care. If locked, it must be unlocked before returning
        '''
        dbStorage.objects.lock()  # @UndefinedVariable

    def unlock(self):
        '''
        Must be used to unlock table
        '''
        dbStorage.objects.unlock()  # @UndefinedVariable

    def locateByAttr1(self, attr1):
        res = []
        for v in dbStorage.objects.filter(attr1=attr1):  # @UndefinedVariable
            res.append(v.data.decode(Storage.CODEC))
        return res

    @staticmethod
    def delete(owner=None):
        logger.info("Deleting storage items")
        if owner is None:
            objects = dbStorage.objects.all()  # @UndefinedVariable
        else:
            objects = dbStorage.objects.filter(owner=owner)  # @UndefinedVariable
        objects.delete()
