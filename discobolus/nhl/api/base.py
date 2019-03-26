from collections import UserList, UserDict
from abc import abstractmethod
import requests


class AbstractArray(UserList):

    def __init__(self, data=[]):
        UserList.__init__(self, data=data)


class AbstractMap(UserDict):

    def __init__(self, data={}):
        UserDict.__init__(self, data=data)



class BaseEndpoint(object):

    def __init__(self, url_ext):
        self.baseurl = "https://statsapi.web.nhl.com"
        self.url = "/".join([self.baseurl, "api", "v1", url_ext])
        self.params = {}
        self.headers = {}

    def _request(self, url):
        try:
            resp = requests.get(url, params=self.params, headers=self.headers)
        except requests.RequestException or requests.HTTPError as err:
            raise Exception(err)
        else:
            js = resp.json()
            if 'messageNumber' in js.keys():
                return js['message']
            else:
                return js

    def _check_response(self, data):
        if type(data) is str:
            print("Failed to create player", data)
            return None
        else:
            return data

    @abstractmethod
    def get(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def get_multi(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def get_all(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def lookup_name(self, name, *args, **kwargs):
        raise NotImplementedError()
