#encoding: utf-8

import logging
import random
import copy
from itertools import product
from urllib.parse import urljoin

from crawler import Curl

from . import register
from .base import CommonVulnerability
from .vul import Vulnerability
from .serverity import Serverity


logger = logging.getLogger(__name__)


@register('codemgr')
class CodeMgr(CommonVulnerability):

    NAME = '代码管理'
    RANK = Serverity.HIGH

    def __init__(self):
        self.__file_names = ['.svn/wc.db', '.svn/entries', '.git/index']
        self.__content_types = ['application/octet-stream']
        self.__checked_sites = {}

    def check(self, request):
        rt_list = []

        site = request.url.site

        if self.__checked_sites.get(site):
            return rt_list

        self.__checked_sites[site] = True

        file_names = self.__file_names
        content_types = self.__content_types

        curl = Curl()

        for name in file_names:
            url = urljoin(site, name)

            response = curl.head(url)
            logger.debug('check result: %s, %s', url, response)
            print(response)
            content_type = response.headers.get('content-type', '').lower()
            if content_type in content_types:
                vul = Vulnerability(self.NAME, self.RANK, url, 'HEAD')
                logger.info(vul)
                rt_list.append(vul)

        return rt_list
