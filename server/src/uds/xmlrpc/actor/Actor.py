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

from uds.models import UserService
from uds.core.util.State import State
from uds.core.util import log

import logging

logger = logging.getLogger(__name__)


def test():
    '''
    Simple test function called by actors to test communication.
    '''
    logger.debug("Test called")
    return True


def message_fnc(id_, message, data):
    '''
    Process a message from the actor.
    @param _id: Ids used by actors to identify themself and locate services to witch they belongs
    @param message: Mesagge received from actor
    @param data: Extra data
    '''
    ids = id_.split(",")[:5]  # Limit ids received to five...
    logger.debug("Called message for id_ {0}, message \"{1}\" and data \"{2}\"".format(ids, message, data))

    # Fix: Log used to send "INFO", "DEBUG", .. as level instead of numeric
    # Now, we use levels, so for "legacy" actors we can do logs correctly
    if message == 'log':
        try:
            msg, level = data.split('\t')
            logger.debug('Msg: {}, level: "{}"'.format(msg, level))
            level = "{}".format(log.logLevelFromStr(level))
            logger.debug('Level: "{}"'.format(level))
            data = '\t'.join([msg, level])
        except Exception:
            logger.exception("Exception at log")
            data = data.replace('\t', ' ') + '\t10000'  # Other

    res = ""
    try:
        services = UserService.objects.filter(unique_id__in=ids, state__in=[State.USABLE, State.PREPARING])
        if services.count() == 0:
            res = ""
        else:
            res = services[0].getInstance().osmanager().process(services[0], message, data, None)
    except Exception as e:
        logger.error("Exception at message (client): {0}".format(e))
        res = ""
    logger.debug("Returning {0}".format(res))
    return res


def registerActorFunctions(dispatcher):
    '''
    Utility function to register methods at xmlrpc server for actor
    '''
    dispatcher.register_function(test, 'test')
    dispatcher.register_function(message_fnc, 'message')
