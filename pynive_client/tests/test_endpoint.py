
import unittest
import requests
import json
import logging

from pynive_client import endpoint
from pynive_client import adapter

class urlTest(unittest.TestCase):

    """
    tested parameters:

    method: required. empty, test-method, getItem
    service: required. empty, test-svc, myservice
    domain: required. empty, test-domain, mydomain, mydomain.com
    version: optional. empty, api, widgets, api-1.1, widgets-1
    secure: optional. empty, None, True, False, No
    path: optional. empty, path, /path/1, path/1, path/1/, /path/1/, ./path/1, ../path/1
    """
    method="test-method"
    service="test-svc"
    domain="test-domain"
    protocol="https://"  # current default
    api="api"            # current default
    widget="widgets"     # current default
    basedomain=".nive.io"

    # defaults
    def setUp(self):
        logging.basicConfig()

    def test_make(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               version=self.api,
                               domain=self.domain)
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/"+self.api+"/"+self.method)

    def test_make_noapi(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               domain=self.domain)
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/"+self.method)


    # method -------------------------------------------------------------------------

    def test_method(self):
        url = endpoint.makeUrl(method="getItem",
                               service=self.service,
                               version=self.api,
                               domain=self.domain)
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/"+self.api+"/getItem")

    def test_method_empty(self):
        url = endpoint.makeUrl(method="",
                               service=self.service,
                               version=self.api,
                               domain=self.domain)
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/"+self.api)

    def test_method_failure(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               version=self.api,
                               domain=self.domain)
        self.assertNotEqual(url,
                            self.protocol+self.domain+self.basedomain+"/"+self.service+"/"+self.api+"/not expected")


    # service -------------------------------------------------------------------------

    def test_service(self):
        url = endpoint.makeUrl(method=self.method,
                               service="myservice",
                               version=self.api,
                               domain=self.domain)
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/myservice/"+self.api+"/"+self.method)

    def test_service_empty(self):
        self.assertRaises(endpoint.EndpointException, endpoint.makeUrl,
                          method=self.method,
                          domain=self.domain,
                          version=self.api)

    def test_service_failure(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               version=self.api,
                               domain=self.domain)
        self.assertNotEqual(url,
                            self.protocol+self.domain+self.basedomain+"/not expected/"+self.api+"/"+self.method)


    # domain -------------------------------------------------------------------------

    def test_domain(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               version=self.api,
                               domain="mydomain")
        self.assertEqual(url,
                         self.protocol+"mydomain"+self.basedomain+"/"+self.service+"/"+self.api+"/"+self.method)

    def test_domain2(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               version=self.api,
                               domain="mydomain.com")
        self.assertEqual(url,
                         self.protocol+"mydomain.com"+"/"+self.service+"/"+self.api+"/"+self.method)

    def test_domain_empty(self):
        self.assertRaises(endpoint.EndpointException, endpoint.makeUrl,
                          method=self.method,
                          service=self.service,
                          version=self.api)

    def test_domain_failure(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               version=self.api,
                               domain=self.domain)
        self.assertNotEqual(url,
                            self.protocol+"not expected"+self.basedomain+"/"+self.service+"/"+self.api+"/"+self.method)


    # version -------------------------------------------------------------------------

    def test_version(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               version="api-1.1",
                               domain=self.domain)
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/api-1.1/"+self.method)

    def test_version_empty(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               version="",
                               domain=self.domain)
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/"+self.method)

    def test_version_empty2(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               version=None,
                               domain=self.domain)
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/"+self.method)

    def test_version_failure(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               version=self.api,
                               domain=self.domain)
        self.assertNotEqual(url,
                            self.protocol+self.domain+self.basedomain+"/"+self.service+"/not expected/"+self.method)


    # secure -------------------------------------------------------------------------

    def test_secure(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               version=self.api,
                               domain=self.domain,
                               secure=True)
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/"+self.api+"/"+self.method)

    def test_secure2(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               version=self.api,
                               domain=self.domain,
                               secure=None)
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/"+self.api+"/"+self.method)

    def test_secure3(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               version=self.api,
                               domain=self.domain,
                               secure="No")
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/"+self.api+"/"+self.method)

    def test_secure_false(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               version=self.api,
                               domain=self.domain,
                               secure=False)
        self.assertEqual(url,
                         "http://"+self.domain+self.basedomain+"/"+self.service+"/"+self.api+"/"+self.method)


    # path -------------------------------------------------------------------------

    def test_path(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               domain=self.domain,
                               path="/path/1")
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/path/1/"+self.method)

    def test_path2(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               domain=self.domain,
                               path="path/1")
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/path/1/"+self.method)

    def test_path3(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               domain=self.domain,
                               path="path/1/")
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/path/1/"+self.method)

    def test_path4(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               domain=self.domain,
                               path="/path/1/")
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/path/1/"+self.method)

    def test_path5(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               domain=self.domain,
                               path="path")
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/path/"+self.method)

    # extended path -------------------------------------------------------------------------

    def test_epath(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               domain=self.domain,
                               extendedPath="/path/1")
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/path/1/"+self.method)

    def test_epath2(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               domain=self.domain,
                               extendedPath="path/1")
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/path/1/"+self.method)

    def test_epath3(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               domain=self.domain,
                               extendedPath="path/1/")
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/path/1/"+self.method)

    def test_epath4(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               domain=self.domain,
                               extendedPath="/path/1/")
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/path/1/"+self.method)

    def test_epath5(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               domain=self.domain,
                               extendedPath="path")
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/path/"+self.method)


   # path and extended path -------------------------------------------------------------------------

    def test_mpath(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               domain=self.domain,
                               path="/path/1",
                               extendedPath="subfolder")
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/path/1/subfolder/"+self.method)

    def test_mpath2(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               domain=self.domain,
                               path="path/1",
                               extendedPath="subfolder")
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/path/1/subfolder/"+self.method)

    def test_mpath3(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               domain=self.domain,
                               path="path/1/",
                               extendedPath="subfolder/2")
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/path/1/subfolder/2/"+self.method)

    def test_mpath4(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               domain=self.domain,
                               path="/path/1/",
                               extendedPath="subfolder/")
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/path/1/subfolder/"+self.method)

    def test_mpath5(self):
        url = endpoint.makeUrl(method=self.method,
                               service=self.service,
                               domain=self.domain,
                               path="path",
                               extendedPath="/folder")
        self.assertEqual(url,
                         self.protocol+self.domain+self.basedomain+"/"+self.service+"/folder/"+self.method)



class sessionTest(unittest.TestCase):
    """
    """
    def setUp(self):
        logging.basicConfig()

    def test_new(self):
        session = endpoint.Client().newSession()
        self.assertTrue(session)

        session = endpoint.Client().newSession(max_retries=5)
        self.assertTrue(session)

        session = endpoint.Client().newSession(pool_connections=7)
        self.assertTrue(session)

        session = endpoint.Client().newSession(pool_maxsize=10)
        self.assertTrue(session)

    def test_token(self):
        session = endpoint.Client().newSession(auth="12345")
        self.assertTrue(session)
        self.assertTrue(session.authtoken=="12345")

    def test_adapter(self):
        client = endpoint.Client()
        client.adapter = adapter.MockAdapter()
        session = client.newSession(auth="12345")
        self.assertTrue(session)
        self.assertTrue(session.authtoken=="12345")
        self.assertTrue(isinstance(session, adapter.MockAdapter))




class clientTest(unittest.TestCase):
    """
    """
    def setUp(self):
        logging.basicConfig()

    def test_client(self):
        client = endpoint.Client()
        self.assertTrue(client)

        client = endpoint.Client(service="myservice", domain="mydomain")
        self.assertTrue(client.options["service"]=="myservice")
        self.assertTrue(client.options["domain"]=="mydomain")

        url = client.url(method="mymethod")
        self.assertEqual(url,
                         endpoint.makeUrl(method="mymethod",service="myservice", domain="mydomain"))

        client = endpoint.Client(session=None, version="another")
        self.assertTrue(client.options["version"] == "another")


    def test_session(self):
        client = endpoint.Client(session=None)
        self.assertTrue(client.session is None)

        client = endpoint.Client(session="a session")
        self.assertTrue(client.session == "a session")

        client = endpoint.Client(session=adapter.MockAdapter())
        self.assertTrue(isinstance(client.session, adapter.MockAdapter))


    def test_url(self):
        client = endpoint.Client(service="myservice", domain="mydomain")
        self.assertEqual(client.url("call"), endpoint.makeUrl("call", service="myservice", domain="mydomain"))


    def test_adapter(self):
        client = endpoint.Client()
        adp = adapter.MockAdapter()
        client.adapter = adp
        self.assertTrue(isinstance(client.adapter, adapter.MockAdapter))


    def test_call(self):
        #adp = adapter.MockAdapter()
        client = endpoint.Client(service="myservice", domain="mydomain")
        #client.adapter = adp
        self.assertRaises(requests.ConnectionError, client.call, "call", {}, {})


    def test_callmock(self):
        adp = adapter.MockAdapter()
        client = endpoint.Client(service="myservice", domain="mydomain")
        client.adapter = adp
        self.assertRaises(endpoint.NotFound, client.call, "not found", {}, {})
        self.assertRaises(endpoint.NotFound, client.call, "not found", {"key1": 123, "key2": "ooo"}, {})


    def test_send(self):
        #adp = adapter.MockAdapter()
        client = endpoint.Client(service="myservice", domain="mydomain")
        #client.adapter = adp
        self.assertRaises(requests.ConnectionError, client._send, client.url("call"), "call", {})


    def test_sendmock(self):
        adp = adapter.MockAdapter()
        client = endpoint.Client(service="myservice", domain="mydomain")
        client.adapter = adp
        response = client._send(client.url("not found"), "not found", {})
        self.assertTrue(response.status_code==404)

        response = client._send(client.url("not found"), "not found", {"key1": 123, "key2": "ooo"})
        self.assertTrue(response.status_code==404)


    def test_sendmock_token(self):
        adp = adapter.MockAdapter()
        client = endpoint.Client(service="myservice", domain="mydomain")
        client.adapter = adp

        #token
        response = client._send(client.url("not found"), "not found", {}, **{"token": "1234567890"})
        self.assertTrue(response.status_code==404)

        client.session = adapter.MockAdapter().Session()
        client.session.authtoken = "1234567890"
        response = client._send(client.url("not found"), "not found", {})
        self.assertTrue(response.status_code==404)


    def test_sendmock_opts(self):
        adp = adapter.MockAdapter()
        client = endpoint.Client(service="myservice", domain="mydomain")
        client.adapter = adp

        # header
        response = client._send(client.url("not found"), "not found", {}, **{"headers": {"x-custom": "custom"}})
        self.assertTrue(response.status_code==404)

        # type
        response = client._send(client.url("not found"), "not found", {}, **{"type": "DELETE"})
        self.assertTrue(response.status_code==404)

        response = client._send(client.url("not found"), "not found", {})
        self.assertTrue(response.status_code==404)

        response = client._send(client.url("not found"), "not found", {"key": "value"})
        self.assertTrue(response.status_code==404)

        # timeout
        response = client._send(client.url("not found"), "not found", {}, **{"timeout": 20})
        self.assertTrue(response.status_code==404)

        # cookies
        client.session = adapter.MockAdapter().Session()
        response = client._send(client.url("not found"), "not found", {})
        self.assertTrue(response.status_code==404)

        client.session.cookies = "cookie!"
        response = client._send(client.url("not found"), "not found", {})
        self.assertTrue(response.status_code==404)


    def test_response_status(self):
        client = endpoint.Client(service="myservice", domain="mydomain")
        resp = adapter.MockResponse()

        resp.status_code = 200
        c,r = client._handleResponse(resp, "call", {}, {})
        self.assertFalse(c)
        self.assertTrue(r.status_code==200)

        resp.status_code = 401
        self.assertRaises(endpoint.AuthorizationFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 403
        self.assertRaises(endpoint.Forbidden, client._handleResponse, resp, "call", {}, {})

        resp = adapter.MockResponse()
        resp.reason = "HTTP status message"

        resp.status_code = 400
        self.assertRaises(endpoint.ClientFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 401
        self.assertRaises(endpoint.AuthorizationFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 403
        self.assertRaises(endpoint.Forbidden, client._handleResponse, resp, "call", {}, {})

        resp.status_code = 404
        self.assertRaises(endpoint.NotFound, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 405
        self.assertRaises(endpoint.ClientFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 406
        self.assertRaises(endpoint.ClientFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 407
        self.assertRaises(endpoint.ClientFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 408
        self.assertRaises(endpoint.ClientFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 409
        self.assertRaises(endpoint.ClientFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 410
        self.assertRaises(endpoint.ClientFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 411
        self.assertRaises(endpoint.ClientFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 412
        self.assertRaises(endpoint.ClientFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 413
        self.assertRaises(endpoint.ServiceLimits, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 414
        self.assertRaises(endpoint.ClientFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 415
        self.assertRaises(endpoint.ClientFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 416
        self.assertRaises(endpoint.ClientFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 417
        self.assertRaises(endpoint.ClientFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 422
        self.assertRaises(endpoint.InvalidParameter, client._handleResponse, resp, "call", {}, {})

        resp.status_code = 500
        self.assertRaises(endpoint.ServiceFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 501
        self.assertRaises(endpoint.ServiceFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 502
        self.assertRaises(endpoint.ServiceFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 503
        self.assertRaises(endpoint.ServiceFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 504
        self.assertRaises(endpoint.ServiceFailure, client._handleResponse, resp, "call", {}, {})
        resp.status_code = 505
        self.assertRaises(endpoint.ServiceFailure, client._handleResponse, resp, "call", {}, {})


    def test_response_json(self):
        client = endpoint.Client(service="myservice", domain="mydomain")
        resp = adapter.MockResponse()

        resp.status_code = 200
        resp.content = json.dumps({})
        resp.headers["Content-Type"] = "application/json"
        c,r = client._handleResponse(resp, "call", {}, {})
        self.assertFalse(c)
        self.assertTrue(r.status_code==200)
        self.assertTrue(isinstance(r.json(), dict))
        self.assertTrue(r.json()=={})


    def test_response_body(self):
        client = endpoint.Client(service="myservice", domain="mydomain")
        resp = adapter.MockResponse()

        resp.status_code = 200
        resp.content = "Hello!"
        c,r = client._handleResponse(resp, "call", {}, {})
        self.assertTrue(c=="Hello!")
        self.assertTrue(r.status_code==200)


    def test_response_content(self):
        client = endpoint.Client(service="myservice", domain="mydomain")

        resp = adapter.MockResponse()
        resp.status_code = 200
        resp.content = json.dumps({"key1": 123, "key2": "ooo"})
        resp.headers["Content-Type"] = "application/json"
        c,r = client._handleResponse(resp, "call", {}, {})
        self.assertTrue(r.status_code==200)
        self.assertTrue(c["key1"]==123)
        self.assertTrue(c["key2"]=="ooo")

        resp = adapter.MockResponse()
        resp.status_code = 200
        resp.headers["Content-Type"] = "application/json; codepage=utf-8"
        resp.content = json.dumps({"key1": 123, "key2": "ooo"})
        c,r = client._handleResponse(resp, "call", {}, {})
        self.assertTrue(r.status_code==200)
        self.assertTrue(c["key1"]==123)
        self.assertTrue(c["key2"]=="ooo")

        resp = adapter.MockResponse()
        resp.status_code = 200
        resp.headers["Content-Type"] = "application/json; codepage=utf-8"
        client._handleResponse(resp, "call", {}, {})


    def test_msgs(self):
        client = endpoint.Client(service="myservice", domain="mydomain")
        self.assertTrue(client._fmtMsgs(('msg1','msg2'), 'default', seperator=' ; '))
        self.assertTrue(client._fmtMsgs(('msg1',), 'default', seperator=' ; '))
        self.assertTrue(client._fmtMsgs('msg1', 'default', seperator=' ; '))
        self.assertTrue(client._fmtMsgs({'messages': ('msg1','msg2')}, 'default', seperator=' ; '))
        self.assertTrue(client._fmtMsgs({'messages': 'msg1'}, 'default', seperator=' ; '))
        self.assertTrue(client._fmtMsgs({'messages': ('msg1','msg2')}, 'default', seperator=' ; '))
        self.assertTrue(client._fmtMsgs({'something': ('msg1','msg2')}, 'default', seperator=' ; '))
        self.assertTrue(client._fmtMsgs(None, 'default', seperator=' ; '))
        self.assertTrue(client._fmtMsgs({'messages': ('msg1','msg2')}, 'default', seperator=' <br> '))


class excpTest(unittest.TestCase):
    def setUp(self):
        logging.basicConfig()

    def test_excp_endpoint(self):
        try:
            raise endpoint.EndpointException("test")
        except endpoint.EndpointException:
            pass

    def test_excp_auth1(self):
        try:
            raise endpoint.Forbidden("test")
        except endpoint.Forbidden:
            pass

    def test_excp_auth2(self):
        try:
            raise endpoint.AuthorizationFailure("test")
        except endpoint.AuthorizationFailure:
            pass

    def test_excp_notfound(self):
        try:
            raise endpoint.ClientFailure("test")
        except endpoint.ClientFailure:
            pass

    def test_excp_servicefailed(self):
        try:
            raise endpoint.ServiceFailure("test")
        except endpoint.ServiceFailure:
            pass

    def test_excpurl(self):
        self.assertRaises(endpoint.EndpointException, endpoint.makeUrl)



