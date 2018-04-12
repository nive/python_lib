
import unittest
import json
import logging

from pynive_client import adapter




class mockRequestTest(unittest.TestCase):
    """
    """
    def setUp(self):
        logging.basicConfig()

    def test_adapter(self):
        adp = adapter.MockAdapter()
        self.assertTrue(adp.authtoken is None)
        self.assertTrue(adp.cookies is None)
        self.assertTrue(adp.responses is None)

    def test_responses(self):
        resp = adapter.StoredResponse(
                    service="users",
                    method="signup",
                    response= {
                        "status_code": 200,
                        "content": {"result": True},
                        "headers": []}
        )
        adp = adapter.MockAdapter(responses=(resp,))
        self.assertTrue(adp.authtoken is None)
        self.assertTrue(adp.cookies is None)
        self.assertTrue(len(adp.responses)==1)


        resp = adapter.StoredResponse(
                    service="users",
                    method="signup",
                    response= {
                        "status_code": 403
                        }
        )
        adp = adapter.MockAdapter(responses=(resp,))
        self.assertTrue(adp.authtoken is None)
        self.assertTrue(adp.cookies is None)
        self.assertTrue(len(adp.responses)==1)

    def test_session(self):
        adp = adapter.MockAdapter()
        self.assertTrue(adp.Session()==adp)

    def test_request(self):
        adp = adapter.MockAdapter()
        resp = adp.request("call", "url")
        self.assertTrue(resp)
        self.assertTrue(resp.url=="url")

    def test_request_responses(self):
        resp = {"service": "users",
                "method": "signup",
                "response": {
                    "status_code": 200,
                    "content": {"result": True},
                    "headers": {"Content-Type": "application/json"}
                }
        }
        adp = adapter.MockAdapter(responses=(resp,))
        resp = adp.request("POST", "/users/api/signup")
        self.assertTrue(resp.status_code==200)
        self.assertTrue(resp.json()["result"])

        resp = {"service": "users",
                "method": "signup",
                "response": {
                    "status_code": 401
                }
        }
        adp = adapter.MockAdapter(responses=(resp,))
        resp = adp.request("POST", "/users/api/signup")
        self.assertTrue(resp.status_code==401)
        self.assertFalse(resp.json())

    def test_match(self):
        resp = ({"service": "users",
                 "method": "signup",
                 "payload": {"name": "okok"},
                 "response": {
                     "status_code": 200,
                     "content": {"result": True},
                     "headers": {"Content-Type": "application/json"}
                 }
                },
                {"service": "users",
                 "method": "signup",
                 "payload": {"name": "not allowed"},
                 "httpmethod": "POST",
                 "response": {
                     "status_code": 401,
                     "content": {},
                     "headers": {}
                 }
                })
        adp = adapter.MockAdapter(responses=resp)
        resp = adp.request("POST", "/users/api/signup")
        self.assertTrue(resp.status_code==404)

        resp = adp.request("POST", "/users/api/signup", data={"name":"okok"})
        self.assertTrue(resp.status_code==200)
        self.assertTrue(resp.json()["result"])

        resp = adp.request("POST", "/users/api/signup", data={"name":"not allowed"})
        self.assertTrue(resp.status_code==401)
        self.assertFalse(resp.json())

        resp = adp.request("GET", "/users/api/signup", data={"name":"not allowed"})
        self.assertTrue(resp.status_code==404)




class storedRequestTest(unittest.TestCase):
    """
    """
    def setUp(self):
        logging.basicConfig()

    def test_init_dict(self):
        resp = adapter.StoredResponse(
              **{"service": "users",
                 "method": "signup",
                 "payload": {"name": "okok"},
                 "response": {
                     "status_code": 200,
                     "content": {"result": True},
                     "headers": {"Content-Type": "application/json"}
                 }
                })
        self.assertTrue(resp)
        self.assertTrue(resp.service=="users")
        self.assertTrue(resp.method=="signup")
        self.assertTrue(resp.payload["name"]=="okok")
        self.assertTrue(resp._urlreg)
        self.assertFalse(resp.httpmethod)
        self.assertTrue(isinstance(resp.response, adapter.MockResponse))
        self.assertTrue(resp.response.status_code==200)
        self.assertTrue(resp.response.headers["Content-Type"]=="application/json")
        self.assertTrue(resp.response.content["result"]==True)

        resp = adapter.StoredResponse(
              **{"service": "users",
                 "method": "signup",
                 "payload": {"name": "not allowed"},
                 "httpmethod": "POST",
                 "response": {
                     "status_code": 401,
                     "content": {},
                     "headers": {}
                 }
                })
        self.assertTrue(resp)
        self.assertTrue(resp.service=="users")
        self.assertTrue(resp.method=="signup")
        self.assertTrue(resp.payload["name"]=="not allowed")
        self.assertTrue(resp._urlreg)
        self.assertTrue(resp.httpmethod=="POST")
        self.assertTrue(isinstance(resp.response, adapter.MockResponse))
        self.assertTrue(resp.response.status_code==401)
        self.assertFalse(resp.response.headers)
        self.assertFalse(resp.response.content)

    def test_init_cls(self):
        resp = adapter.StoredResponse(
              service="users",
              method="signup",
              payload={"name": "okok"},
              response={
                     "status_code": 200,
                     "content": {"result": True},
                     "headers": {"Content-Type": "application/json"}
                 }
              )
        self.assertTrue(resp)
        self.assertTrue(resp.service=="users")
        self.assertTrue(resp.method=="signup")
        self.assertTrue(resp.payload["name"]=="okok")
        self.assertTrue(resp._urlreg)
        self.assertFalse(resp.httpmethod)
        self.assertTrue(isinstance(resp.response, adapter.MockResponse))
        self.assertTrue(resp.response.status_code==200)
        self.assertTrue(resp.response.headers["Content-Type"]=="application/json")
        self.assertTrue(resp.response.content["result"]==True)

        resp = adapter.StoredResponse(
              "users",
              "signup",
              payload={"name": "not allowed"},
              httpmethod="POST",
              response={
                     "status_code": 401,
                     "content": {},
                     "headers": {}
                 }
              )
        self.assertTrue(resp)
        self.assertTrue(resp.service=="users")
        self.assertTrue(resp.method=="signup")
        self.assertTrue(resp.payload["name"]=="not allowed")
        self.assertTrue(resp._urlreg)
        self.assertTrue(resp.httpmethod=="POST")
        self.assertTrue(isinstance(resp.response, adapter.MockResponse))
        self.assertTrue(resp.response.status_code==401)
        self.assertFalse(resp.response.headers)
        self.assertFalse(resp.response.content)

        resp = adapter.StoredResponse(
              service="users",
              method="signup"
        )
        self.assertTrue(resp)
        self.assertTrue(resp.service=="users")
        self.assertTrue(resp.method=="signup")
        self.assertTrue(resp._urlreg)
        self.assertFalse(resp.payload)
        self.assertFalse(resp.httpmethod)
        self.assertFalse(resp.response)

    def test_init_json(self):
        jsonstr = """{
               "service": "users",
               "method": "signup",
               "payload": {"name": "okok"},
               "response": {
                   "status_code": 200,
                   "content": {"result": true},
                   "headers": {"Content-Type": "application/json"}
               }
        }"""
        resp = adapter.StoredResponse.fromJson(jsonstr)
        self.assertTrue(resp)
        self.assertTrue(resp.service=="users")
        self.assertTrue(resp.method=="signup")
        self.assertTrue(resp.payload["name"]=="okok")
        self.assertTrue(resp._urlreg)
        self.assertFalse(resp.httpmethod)
        self.assertTrue(isinstance(resp.response, adapter.MockResponse))
        self.assertTrue(resp.response.status_code==200)
        self.assertTrue(resp.response.headers["Content-Type"]=="application/json")
        self.assertTrue(resp.response.content["result"]==True)

        jsonstr = """{
              "service": "users",
              "method": "signup",
              "payload": {"name": "not allowed"},
              "httpmethod": "POST",
              "response": {
                  "status_code": 401,
                  "content": {},
                  "headers": {}
              }
        }"""
        resp = adapter.StoredResponse.fromJson(jsonstr)
        self.assertTrue(resp)
        self.assertTrue(resp.service=="users")
        self.assertTrue(resp.method=="signup")
        self.assertTrue(resp.payload["name"]=="not allowed")
        self.assertTrue(resp._urlreg)
        self.assertTrue(resp.httpmethod=="POST")
        self.assertTrue(isinstance(resp.response, adapter.MockResponse))
        self.assertTrue(resp.response.status_code==401)
        self.assertFalse(resp.response.headers)
        self.assertFalse(resp.response.content)

    def test_response(self):
        resp = adapter.StoredResponse("user", "signup")
        resp.setResponse(adapter.MockResponse())
        self.assertTrue(isinstance(resp.response, adapter.MockResponse))
        self.assertTrue(resp.response.status_code==404)

        resp.setResponse({})
        self.assertTrue(isinstance(resp.response, adapter.MockResponse))
        self.assertTrue(resp.response.status_code==404)

    def test_init_match(self):
        resp = adapter.StoredResponse(
              service="users",
              method="signup",
              payload={"name": "okok"},
              response={
                     "status_code": 200,
                     "content": {"result": True},
                     "headers": {"Content-Type": "application/json"}
                 }
              )
        self.assertTrue(resp.match("POST", "http://domain.com/users/api/signup", {"name":"okok"}, {}))
        self.assertTrue(resp.match("POST", "http://domain.com/users/api/signup", {"name":"okok","password": "???"}, {}))
        self.assertTrue(resp.match("PUT", "http://domain.com/users/api/signup", {"name":"okok"}, {}))
        self.assertFalse(resp.match("POST", "http://domain.com/users/api/signup2", {"name":"okok"}, {}))
        self.assertFalse(resp.match("POST", "http://domain.com/users/api/signup", {"name":"not ok"}, {}))
        self.assertFalse(resp.match("POST", "http://domain.com/user/api/signup", {"name":"okok"}, {}))
        self.assertFalse(resp.match("POST", "http://domain.com/users/api/signup", {}, {}))

        resp = adapter.StoredResponse(
              "users",
              "signup",
              payload={"name": "not allowed"},
              httpmethod="POST",
              response={
                     "status_code": 401,
                     "content": {},
                     "headers": {}
                 }
              )
        self.assertTrue(resp.match("POST", "http://domain.com/users/api/signup", {"name": "not allowed"}, {}))
        self.assertFalse(resp.match("PUT", "http://domain.com/users/api/signup", {"name": "not allowed"}, {}))
        self.assertFalse(resp.match("POST", "http://domain.com/users/api/signup", {}, {}))

        resp = adapter.StoredResponse(
              service="users",
              method="signup2",
              response={
                     "status_code": 200,
                     "content": {"result": True},
                     "headers": {"Content-Type": "application/json"}
                 }
        )
        self.assertTrue(resp.match("POST", "http://domain.com/users/api/signup2", {}, {}))
