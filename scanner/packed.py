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


@register('packed')
class Packed(CommonVulnerability):

    NAME = '压缩文件'
    RANK = Serverity.HIGH

    def __init__(self):
        self.__file_names = ['bak', 'backfile', 'www', 'root', 'wwwroot']
        self.__file_exts = [
            '.zip',
            '.rar',
            '.tar', '.tar.gz', '.tgz', '.tar.gz2', '.tbz2', '.tbz',
            '.bz2',
            '.gzip',
            '.7z'
        ]
        self.__content_types = [
            'application/zip', 'application/x-zip-compressed',
            'application/x-rar-compressed',
            'application/x-gtar',
            'application/x-bzip2',
            'application/gzip',
            'application/x-7z-compressed'
        ]
        self.__checked_sites = {}

    def check(self, request):
        rt_list = []

        site = request.url.site

        if self.__checked_sites.get(site):
            return rt_list

        self.__checked_sites[site] = True

        file_names = self.__file_names
        file_exts = self.__file_exts
        content_types = self.__content_types

        curl = Curl()

        for name, ext in product(file_names, file_exts):
            filename = '{0}{1}'.format(name, ext)
            url = urljoin(site, filename)

            response = curl.head(url)
            logger.debug('check result: %s, %s', url, response)

            content_type = response.headers.get('content-type', '').lower()
            if content_type in content_types:
                vul = Vulnerability(self.NAME, self.RANK, url, 'HEAD')
                logger.info(vul)
                rt_list.append(vul)

        return rt_list
