#encoding: utf-8

import logging
import random
import copy

from simhash import Simhash

from crawler import Curl

from .base import CommonVulnerability
from .vul import Vulnerability
from .serverity import Serverity


logger = logging.getLogger(__name__)

class SQL(CommonVulnerability):

    NAME = 'SQL注入'
    RANK = Serverity.HIGH

    NIL = lambda *args, **kwargs: None

    def __init__(self):
        self.__distance = 3

    def check(self, request):
        curl = Curl()

        key = ''
        callback = None
        params = {}
        if request.method == 'GET':
            key = 'data'
            callback = curl.post
            params = request.params
        else:
            key = 'params'
            callback = curl.get
            params = request.post

        playloads = self.__get_playloads(params)
        rt_list = []
        for name, poc_true, poc_false in playloads:
            response = callback(request.url, **{key : params})
            response_true = callback(request.url, **{key : poc_true})
            response_false = callback(request.url, **{key : poc_false})

            if response_true.body == response_false.body:
                continue

            if Simhash(response_true.body).\
                distance(Simhash(response_false.body)) < self.__distance:
                continue

            if Simhash(response.body).\
                distance(Simhash(response_true.body)) < self.__distance:
                continue
            vul = Vulnerability(self.NAME, self.RANK, request.url.url,
                                    request.method, name, poc_true)
            logger.info(vul)
            rt_list.append(vul)

        return rt_list

    def __get_playloads(self, params):
        playloads = []
        for name, value in params.items():
            pls = []
            value = "".join(value) if isinstance(value, (list, )) else value

            rint = random.randint(0, 100)
            pt = '{0} or {1}={1}'.format(value, rint)
            pf = '{0} and {1}={2}'.format(value, rint, rint + 1)
            pls.append((pt, pf))

            pt = '{0}" or "{1}"="{1}'.format(value, rint)
            pf = '{0}" and "{1}"="{2}'.format(value, rint, rint + 1)
            pls.append((pt, pf))

            pt = "{0}' or '{1}'='{1}".format(value, rint)
            pf = "{0}' and '{1}'='{2}".format(value, rint, rint + 1)
            pls.append((pt, pf))

            for pl in pls:
                poc_ture = copy.deepcopy(params)
                poc_false = copy.deepcopy(params)
                poc_ture[name] = pt
                poc_false[name] = pf
                playloads.append((name, poc_ture, poc_false))

        return playloads