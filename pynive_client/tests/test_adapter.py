
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
        self.assert_(adp.token is None)
        self.assert_(adp.cookies is None)
        self.assert_(adp.responses is None)

    def test_responses(self):
        resp = adapter.StoredResponse(
                    name="users",
                    method="signup",
                    response= {
                        "status_code": 200,
                        "content": {"result": True},
                        "headers": []}
        )
        adp = adapter.MockAdapter(responses=(resp,))
        self.assert_(adp.token is None)
        self.assert_(adp.cookies is None)
        self.assert_(len(adp.responses)==1)


        resp = adapter.StoredResponse(
                    name="users",
                    method="signup",
                    response= {
                        "status_code": 403
                        }
        )
        adp = adapter.MockAdapter(responses=(resp,))
        self.assert_(adp.token is None)
        self.assert_(adp.cookies is None)
        self.assert_(len(adp.responses)==1)

    def test_session(self):
        adp = adapter.MockAdapter()
        self.assert_(adp.Session()==adp)

    def test_request(self):
        adp = adapter.MockAdapter()
        resp = adp.request("call", "url")
        self.assert_(resp)
        self.assert_(resp.url=="url")

    def test_request_responses(self):
        resp = {"name": "users",
                "method": "signup",
                "response": {
                    "status_code": 200,
                    "content": {"result": True},
                    "headers": {"Content-Type": "application/json"}
                }
        }
        adp = adapter.MockAdapter(responses=(resp,))
        resp = adp.request("POST", "users/api/signup")
        self.assert_(resp.status_code==200)
        self.assert_(resp.json()["result"])

        resp = {"name": "users",
                "method": "signup",
                "response": {
                    "status_code": 401
                }
        }
        adp = adapter.MockAdapter(responses=(resp,))
        resp = adp.request("POST", "users/api/signup")
        self.assert_(resp.status_code==401)
        self.assertFalse(resp.json())

    def test_match(self):
        resp = ({"name": "users",
                 "method": "signup",
                 "payload": {"name": "okok"},
                 "response": {
                     "status_code": 200,
                     "content": {"result": True},
                     "headers": {"Content-Type": "application/json"}
                 }
                },
                {"name": "users",
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
        resp = adp.request("POST", "users/api/signup")
        self.assert_(resp.status_code==404)

        resp = adp.request("POST", "users/api/signup", data={"name":"okok"})
        self.assert_(resp.status_code==200)
        self.assert_(resp.json()["result"])

        resp = adp.request("POST", "users/api/signup", data={"name":"not allowed"})
        self.assert_(resp.status_code==401)
        self.assertFalse(resp.json())

        resp = adp.request("GET", "users/api/signup", data={"name":"not allowed"})
        self.assert_(resp.status_code==404)




class storedRequestTest(unittest.TestCase):
    """
    """
    def setUp(self):
        logging.basicConfig()

    def test_init_dict(self):
        resp = adapter.StoredResponse(
              **{"name": "users",
                 "method": "signup",
                 "payload": {"name": "okok"},
                 "response": {
                     "status_code": 200,
                     "content": {"result": True},
                     "headers": {"Content-Type": "application/json"}
                 }
                })
        self.assert_(resp)
        self.assert_(resp.name=="users")
        self.assert_(resp.method=="signup")
        self.assert_(resp.payload["name"]=="okok")
        self.assert_(resp._urlreg)
        self.assertFalse(resp.httpmethod)
        self.assert_(isinstance(resp.response, adapter.MockResponse))
        self.assert_(resp.response.status_code==200)
        self.assert_(resp.response.headers["Content-Type"]=="application/json")
        self.assert_(resp.response.content["result"]==True)

        resp = adapter.StoredResponse(
              **{"name": "users",
                 "method": "signup",
                 "payload": {"name": "not allowed"},
                 "httpmethod": "POST",
                 "response": {
                     "status_code": 401,
                     "content": {},
                     "headers": {}
                 }
                })
        self.assert_(resp)
        self.assert_(resp.name=="users")
        self.assert_(resp.method=="signup")
        self.assert_(resp.payload["name"]=="not allowed")
        self.assert_(resp._urlreg)
        self.assert_(resp.httpmethod=="POST")
        self.assert_(isinstance(resp.response, adapter.MockResponse))
        self.assert_(resp.response.status_code==401)
        self.assertFalse(resp.response.headers)
        self.assertFalse(resp.response.content)

    def test_init_cls(self):
        resp = adapter.StoredResponse(
              name="users",
              method="signup",
              payload={"name": "okok"},
              response={
                     "status_code": 200,
                     "content": {"result": True},
                     "headers": {"Content-Type": "application/json"}
                 }
              )
        self.assert_(resp)
        self.assert_(resp.name=="users")
        self.assert_(resp.method=="signup")
        self.assert_(resp.payload["name"]=="okok")
        self.assert_(resp._urlreg)
        self.assertFalse(resp.httpmethod)
        self.assert_(isinstance(resp.response, adapter.MockResponse))
        self.assert_(resp.response.status_code==200)
        self.assert_(resp.response.headers["Content-Type"]=="application/json")
        self.assert_(resp.response.content["result"]==True)

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
        self.assert_(resp)
        self.assert_(resp.name=="users")
        self.assert_(resp.method=="signup")
        self.assert_(resp.payload["name"]=="not allowed")
        self.assert_(resp._urlreg)
        self.assert_(resp.httpmethod=="POST")
        self.assert_(isinstance(resp.response, adapter.MockResponse))
        self.assert_(resp.response.status_code==401)
        self.assertFalse(resp.response.headers)
        self.assertFalse(resp.response.content)

        resp = adapter.StoredResponse(
              name="users",
              method="signup"
        )
        self.assert_(resp)
        self.assert_(resp.name=="users")
        self.assert_(resp.method=="signup")
        self.assert_(resp._urlreg)
        self.assertFalse(resp.payload)
        self.assertFalse(resp.httpmethod)
        self.assertFalse(resp.response)

    def test_init_json(self):
        jsonstr = """{
               "name": "users",
               "method": "signup",
               "payload": {"name": "okok"},
               "response": {
                   "status_code": 200,
                   "content": {"result": true},
                   "headers": {"Content-Type": "application/json"}
               }
        }"""
        resp = adapter.StoredResponse.fromJson(jsonstr)
        self.assert_(resp)
        self.assert_(resp.name=="users")
        self.assert_(resp.method=="signup")
        self.assert_(resp.payload["name"]=="okok")
        self.assert_(resp._urlreg)
        self.assertFalse(resp.httpmethod)
        self.assert_(isinstance(resp.response, adapter.MockResponse))
        self.assert_(resp.response.status_code==200)
        self.assert_(resp.response.headers["Content-Type"]=="application/json")
        self.assert_(resp.response.content["result"]==True)

        jsonstr = """{
              "name": "users",
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
        self.assert_(resp)
        self.assert_(resp.name=="users")
        self.assert_(resp.method=="signup")
        self.assert_(resp.payload["name"]=="not allowed")
        self.assert_(resp._urlreg)
        self.assert_(resp.httpmethod=="POST")
        self.assert_(isinstance(resp.response, adapter.MockResponse))
        self.assert_(resp.response.status_code==401)
        self.assertFalse(resp.response.headers)
        self.assertFalse(resp.response.content)

    def test_response(self):
        resp = adapter.StoredResponse("user", "signup")
        resp.setResponse(adapter.MockResponse())
        self.assert_(isinstance(resp.response, adapter.MockResponse))
        self.assert_(resp.response.status_code==404)

        resp.setResponse({})
        self.assert_(isinstance(resp.response, adapter.MockResponse))
        self.assert_(resp.response.status_code==404)

    def test_init_match(self):
        resp = adapter.StoredResponse(
              name="users",
              method="signup",
              payload={"name": "okok"},
              response={
                     "status_code": 200,
                     "content": {"result": True},
                     "headers": {"Content-Type": "application/json"}
                 }
              )
        self.assert_(resp.match("POST", "http://domain.com/users/api/signup", {"name":"okok"}, {}))
        self.assert_(resp.match("POST", "http://domain.com/users/api/signup", {"name":"okok","password": "???"}, {}))
        self.assert_(resp.match("PUT", "http://domain.com/users/api/signup", {"name":"okok"}, {}))
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
        self.assert_(resp.match("POST", "http://domain.com/users/api/signup", {"name": "not allowed"}, {}))
        self.assertFalse(resp.match("PUT", "http://domain.com/users/api/signup", {"name": "not allowed"}, {}))
        self.assertFalse(resp.match("POST", "http://domain.com/users/api/signup", {}, {}))

        resp = adapter.StoredResponse(
              name="users",
              method="signup2",
              response={
                     "status_code": 200,
                     "content": {"result": True},
                     "headers": {"Content-Type": "application/json"}
                 }
        )
        self.assert_(resp.match("POST", "http://domain.com/users/api/signup2", {}, {}))
