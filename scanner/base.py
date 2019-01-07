#encoding: utf-8

from abc import ABC, abstractmethod

class CommonVulnerability(ABC):

    @abstractmethod
    def check(self, request):
        pass