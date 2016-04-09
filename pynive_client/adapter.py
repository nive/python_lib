# (c) 2013-2015 Nive GmbH - nive.io
# This file is released under the BSD-License.
#
# Helper class to mock server requests in tests
# ---------------------------------------------
#

import re
import json



class MockAdapter(object):
    """
    request adapter for testing and mocking services

    Supports stored responses. See ``StoredResponse``.

    ::

        adapter = MockAdapter(responses=[...])

    """
    token = None
    cookies = None
    responses = None

    def __init__(self, responses=None):
        if responses is not None:
            resp = []
            for r in responses:
                if isinstance(r, basestring):
                    resp.append(StoredResponse.fromJson(r))
                elif isinstance(r, dict):
                    resp.append(StoredResponse(**r))
                else:
                    resp.append(r)
            self.responses = resp

    def request(self, method, url, **settings):
        if self.responses:
            data = settings.get("data")
            if isinstance(data, basestring):
                data = json.loads(data)
            for resp in self.responses:
                if resp.match(method, url, data, settings):
                    resp.response.url = url
                    return resp.response
        return MockResponse(url=url)

    def Session(self):
        return self


class Elapsed(object):
    tt = 0.1
    def total_seconds(self):
        return self.tt

class MockResponse(object):
    status_code=404
    reason=''
    content=''
    headers=None
    url=''
    elapsed=Elapsed()
    def __init__(self, **values):
        self.headers={}
        self.__dict__.update(values)

    def iter_content(self, size=1000):
        return self
    def next(self):
        return self.content

    def json(self):
        if self.content and isinstance(self.content, basestring):
            return json.loads(self.content)
        return self.content


class StoredResponse(object):
    """
    match conditions:

      <service>,<function>,<payload match|*>,<method|*>)

    response values as dict or `MockResponse` instance:

      {status_code, content, reason, headers}


    e.g. ::

        response = StoredResponse(service="users",
                                  method="signup",
                                  payload={"name": "tester"},
                                  httpmethod="POST",
                                  response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                  })

    or  ::

        response = StoredResponse(service="users",
                                  method="signup",
                                  response={
                                      "status_code": 403
                                  })

    or from json string ::

        jsonstr = '''{
            "service": "users",
            "method": "signup",
            "payload": {"name": "tester"},
            "httpmethod": "POST",
            "response": {
                "status_code": 200,
                "content": {"result": True},
                "headers": {"Content-Type": "application/json"}
            }
        }'''

        response = StoredResponse.fromJson(jsonstr)

    or same contents as above stored in file ::

        response = StoredResponse.fromFile(filename)

    """
    service= None
    method = None
    response = None
    _urlreg = None

    def __init__(self,
                 service,
                 method,
                 payload=None,
                 httpmethod=None,
                 response=None):
        self.setNameMethod(service, method)
        self.payload = payload
        self.httpmethod = httpmethod
        if response is not None:
            self.setResponse(response)

    @staticmethod
    def fromJson(jsonstr):
        values = json.loads(jsonstr)
        response = StoredResponse(**values)
        return response

    @staticmethod
    def fromFile(filename):
        with open(filename) as fp:
            jsonstr = fp.read()
        return StoredResponse.fromJson(jsonstr)

    def setNameMethod(self, service, method):
        self.service = service
        self.method = method
        self._urlreg = re.compile("/%s/.*/%s$" % (service, method))

    def setResponse(self, response):
        if isinstance(response, MockResponse):
            self.response = response
        else:
            self.response = MockResponse(**response)

    def match(self, httpmethod, url, data, settings):
        # http method
        if self.httpmethod is not None and self.httpmethod!=httpmethod:
            return False
        # url match
        if self._urlreg.search(url) is None:
            return False
        # payload match
        if self.payload is None:
            return True
        if data is None:
            return False
        for k,v in self.payload.items():
            if data.get(k) != v:
                return False
        return True


def AssertResult(result, request, testcase):
    response = request.response
    testdata = response.content

    # compare result format
    if isinstance(testdata, dict):
        if response.validate:
            for key in response.validate:
                testcase.assertEqual(testdata.get(key), result.get(key), key)
            else:
                for key, value in testdata.items():
                    testcase.assertEqual(value, result.get(key), key)

    elif isinstance(testdata, (list, tuple)):
        match = filter(lambda v: v not in result, testdata)
        testcase.assertFalse(match, match)