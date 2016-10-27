
import unittest
import json
import logging

from pynive_client import adapter
from pynive_client import endpoint
from pynive_client import userstore


class userTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def test_setup_empty(self):
        user = userstore.User()
        self.assertFalse(user.options["domain"])
        self.assertFalse(user.session)
        self.assert_(user.options["service"]==user.service_name)
        self.assert_(user.options["version"]==user.default_version)

    def test_setup(self):
        user = userstore.User(domain="mydomain")
        self.assert_(user.options["domain"]=="mydomain")
        self.assert_(user.options["service"]==user.service_name)
        self.assert_(user.options["version"]==user.default_version)
        self.assertFalse(user.session)

        user = userstore.User(domain="mydomain", version="api23")
        self.assert_(user.options["domain"]=="mydomain")
        self.assert_(user.options["service"]==user.service_name)
        self.assert_(user.options["version"]=="api23")
        self.assertFalse(user.session)

    def test_setup_fails(self):
        self.assertRaises(TypeError, userstore.User, domain="mydomain", service="myservice")

    def test_session(self):
        user = userstore.User(domain="mydomain", session=adapter.MockAdapter())
        self.assert_(user.options["domain"]=="mydomain")
        self.assert_(user.session)



class signupFunctionTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()
        session = adapter.MockAdapter()
        self.user = userstore.User(domain="mydomain", session=session)


    def test_signupDirect(self):
        # signup
        r = adapter.StoredResponse(service="users",
                                   method="signupDirect",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupDirect(name="tester",
                             email="tester@email.com",
                             password="aaaaa",
                             data="custom")
        self.assert_(result)

        # minimum values
        r = adapter.StoredResponse(service="users",
                                   method="signupDirect",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupDirect(name="tester",
                               email="tester@email.com",
                               password="aaaaa")
        self.assert_(result)

        # minimum values, message
        r = adapter.StoredResponse(service="users",
                                   method="signupDirect",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "invalid": [], "message": "OK"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupDirect(name="tester",
                               email="tester@email.com",
                               password="aaaaa")
        self.assert_(result)
        self.assert_(result.message)

    def test_signupDirect_failure(self):
        # no name
        r = adapter.StoredResponse(service="users",
                                   method="signupDirect",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "invalid": [["name", "empty"]],
                                                  "message": "validation_failure"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupDirect(name="",
                               email="tester@email.com",
                               password="aaaaa")
        self.assertFalse(result)
        self.assert_(result.invalid)
        self.assert_(result.message)

        # no result
        r = adapter.StoredResponse(service="users",
                                   method="signupDirect",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupDirect(name="tester",
                               email="tester@email.com",
                               password="aaaaa")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="signupDirect",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupDirect(name="tester",
                               email="tester@email.com",
                               password="aaaaa")
        self.assertFalse(result)

    def test_signupDirect_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="signupDirect",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.signupDirect)

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="signupDirect",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.signupDirect)

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="signupDirect",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.signupDirect)


    def test_signupOptin(self):
        # signup
        r = adapter.StoredResponse(service="users",
                                   method="signupOptin",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupOptin(name="tester",
                             email="tester@email.com",
                             password="aaaaa",
                             data="custom")
        self.assert_(result)

        # minimum values
        r = adapter.StoredResponse(service="users",
                                   method="signupOptin",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupOptin(name="tester",
                               email="tester@email.com",
                               password="aaaaa")
        self.assert_(result)

        # minimum values, message
        r = adapter.StoredResponse(service="users",
                                   method="signupOptin",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "invalid": [], "message": "OK"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupOptin(name="tester",
                               email="tester@email.com",
                               password="aaaaa")
        self.assert_(result)
        self.assert_(result.message)

    def test_signupOptin_failure(self):
        # no name
        r = adapter.StoredResponse(service="users",
                                   method="signupOptin",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "invalid": [["name", "empty"]],
                                                  "message": "validation_failure"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupOptin(name="",
                               email="tester@email.com",
                               password="aaaaa")
        self.assertFalse(result)
        self.assert_(result.invalid)
        self.assert_(result.message)

        # no result
        r = adapter.StoredResponse(service="users",
                                   method="signupOptin",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupOptin(name="tester",
                               email="tester@email.com",
                               password="aaaaa")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="signupOptin",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupOptin(name="tester",
                               email="tester@email.com",
                               password="aaaaa")
        self.assertFalse(result)

    def test_signupOptin_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="signupOptin",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.signupOptin)

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="signupOptin",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.signupOptin)

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="signupOptin",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.signupOptin)


    def test_signupReview(self):
        # signup
        r = adapter.StoredResponse(service="users",
                                   method="signupReview",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupReview(name="tester",
                             email="tester@email.com",
                             password="aaaaa",
                             data="custom")
        self.assert_(result)

        # minimum values
        r = adapter.StoredResponse(service="users",
                                   method="signupReview",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupReview(name="tester",
                               email="tester@email.com",
                               password="aaaaa")
        self.assert_(result)

        # minimum values, message
        r = adapter.StoredResponse(service="users",
                                   method="signupReview",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "invalid": [], "message": "OK"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupReview(name="tester",
                               email="tester@email.com",
                               password="aaaaa")
        self.assert_(result)
        self.assert_(result.message)

    def test_signupReview_failure(self):
        # no name
        r = adapter.StoredResponse(service="users",
                                   method="signupReview",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "invalid": [["name", "empty"]],
                                                  "message": "validation_failure"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupReview(name="",
                               email="tester@email.com",
                               password="aaaaa")
        self.assertFalse(result)
        self.assert_(result.invalid)
        self.assert_(result.message)

        # no result
        r = adapter.StoredResponse(service="users",
                                   method="signupReview",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupReview(name="tester",
                               email="tester@email.com",
                               password="aaaaa")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="signupReview",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupReview(name="tester",
                               email="tester@email.com",
                               password="aaaaa")
        self.assertFalse(result)

    def test_signupReview_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="signupReview",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.signupReview)

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="signupReview",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.signupReview)

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="signupReview",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.signupReview)


    def test_signupSendpw(self):
        # signup
        r = adapter.StoredResponse(service="users",
                                   method="signupSendpw",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupSendpw(name="tester",
                             email="tester@email.com",
                             data="custom")
        self.assert_(result)

        # minimum values
        r = adapter.StoredResponse(service="users",
                                   method="signupSendpw",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupSendpw(name="tester",
                               email="tester@email.com")
        self.assert_(result)

        # minimum values, message
        r = adapter.StoredResponse(service="users",
                                   method="signupSendpw",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "invalid": [], "message": "OK"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupSendpw(name="tester",
                               email="tester@email.com")
        self.assert_(result)
        self.assert_(result.message)

    def test_signupSendpw_failure(self):
        # no name
        r = adapter.StoredResponse(service="users",
                                   method="signupSendpw",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "invalid": [["name", "empty"]],
                                                  "message": "validation_failure"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupSendpw(name="",
                               email="tester@email.com")
        self.assertFalse(result)
        self.assert_(result.invalid)
        self.assert_(result.message)

        # no result
        r = adapter.StoredResponse(service="users",
                                   method="signupSendpw",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupSendpw(name="tester",
                               email="tester@email.com")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="signupSendpw",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupSendpw(name="tester",
                               email="tester@email.com")
        self.assertFalse(result)

    def test_signupSendpw_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="signupSendpw",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.signupSendpw)

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="signupSendpw",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.signupSendpw)

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="signupSendpw",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.signupSendpw)


    def test_signupUid(self):
        # signup
        r = adapter.StoredResponse(service="users",
                                   method="signupUid",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupUid(
                             email="tester@email.com",
                             password="aaaaa",
                             data="custom")
        self.assert_(result)

        # minimum values
        r = adapter.StoredResponse(service="users",
                                   method="signupUid",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupUid(
                               email="tester@email.com",
                               password="aaaaa")
        self.assert_(result)

        # minimum values, message
        r = adapter.StoredResponse(service="users",
                                   method="signupUid",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "invalid": [], "message": "OK"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupUid(
                               email="tester@email.com",
                               password="aaaaa")
        self.assert_(result)
        self.assert_(result.message)

    def test_signupUid_failure(self):
        # no name
        r = adapter.StoredResponse(service="users",
                                   method="signupUid",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "invalid": [["name", "empty"]],
                                                  "message": "validation_failure"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupUid(
                               email="tester@email.com",
                               password="aaaaa")
        self.assertFalse(result)
        self.assert_(result.invalid)
        self.assert_(result.message)

        # no result
        r = adapter.StoredResponse(service="users",
                                   method="signupUid",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupUid(
                               email="tester@email.com",
                               password="aaaaa")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="signupUid",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.signupUid(
                               email="tester@email.com",
                               password="aaaaa")
        self.assertFalse(result)

    def test_signupUid_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="signupUid",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.signupUid)

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="signupUid",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.signupUid)

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="signupUid",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.signupUid)


    def test_activate(self):
        # activate
        r = adapter.StoredResponse(service="users",
                                   method="activate",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.activate(token="0000000000")
        self.assert_(result)

        # activate, message
        r = adapter.StoredResponse(service="users",
                                   method="activate",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "message": "OK"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.activate(token="0000000000")
        self.assert_(result)

    def test_activate_failure(self):
        # no token
        r = adapter.StoredResponse(service="users",
                                   method="activate",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "message": "empty_token"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.activate(token="")
        self.assertFalse(result)
        self.assert_(result.message)

        # no result
        r = adapter.StoredResponse(service="users",
                                   method="activate",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result = self.user.activate(token="000000000")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="activate",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.activate(token="000000000")
        self.assertFalse(result)

    def test_activate_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="activate",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.activate, token="000000")

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="activate",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.activate, token="000000")

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="activate",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.activate, token="000000")


    def test_review(self):
        # review
        r = adapter.StoredResponse(service="users",
                                   method="review",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.review(identity="tester",action="accept")
        self.assert_(result.result)

        # review
        r = adapter.StoredResponse(service="users",
                                   method="review",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.review(identity="tester",action="optin")
        self.assert_(result.result)

        # review, message
        r = adapter.StoredResponse(service="users",
                                   method="review",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "message": "OK"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.review(identity="tester",action="reject")
        self.assert_(result)
        self.assert_(result.result)

        # review, message
        r = adapter.StoredResponse(service="users",
                                   method="review",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "message": "OK"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.review(identity="tester",action="activate")
        self.assert_(result)
        self.assert_(result.result)

        # review, message
        r = adapter.StoredResponse(service="users",
                                   method="review",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "message": "OK"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.review(identity="tester",action="disable")
        self.assert_(result)
        self.assert_(result.result)

    def test_review_failure(self):
        # no token
        r = adapter.StoredResponse(service="users",
                                   method="review",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "message": "empty_identity"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.review(identity="",action="accept")
        self.assertFalse(result)

        # no result
        r = adapter.StoredResponse(service="users",
                                   method="review",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result = self.user.review(identity="000000000",action="")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="review",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.review(identity="000000000",action="")
        self.assertFalse(result)

    def test_review_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="review",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.review, identity="tester",action="accept")

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="review",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.review, identity="tester",action="accept")

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="review",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.review, identity="tester",action="accept")




class userFunctionTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()
        session = adapter.MockAdapter()
        self.user = userstore.User(domain="mydomain", session=session)

    def test_token(self):
        # valid token
        r = adapter.StoredResponse(service="users",
                                   method="token",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"token": "1234567890"},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)

        result = self.user.token(identity="tester", password="aaaaa", storeInSession=False)
        self.assertEqual(result.token, "1234567890")
        self.assertNotEqual(self.user.session.authtoken, "1234567890")

        # valid token, stored in session
        result = self.user.token(identity="tester", password="aaaaa", storeInSession=True)
        self.assertEqual(result.token, "1234567890")
        self.assertEqual(self.user.session.authtoken, "1234567890")

    def test_token_failure(self):
        # empty token, custom message
        r = adapter.StoredResponse(service="users",
                                   method="token",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"token": "", "message": ("Server message",)},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.AuthorizationFailure, self.user.token, identity="tester", password="aaaaa", storeInSession=False)

        # empty content, no json
        r = adapter.StoredResponse(service="users",
                                   method="token",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": "",
                                      "headers": {}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.AuthorizationFailure, self.user.token, identity="tester", password="aaaaa", storeInSession=False)

        # no token, custom message, json
        r = adapter.StoredResponse(service="users",
                                   method="token",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"message": ("Server message","Another Message")},
                                      "headers": {}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.AuthorizationFailure, self.user.token, identity="tester", password="aaaaa", storeInSession=False)

    def test_token_codes(self):
        # code 401
        r = adapter.StoredResponse(service="users",
                                   method="token",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 401,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.AuthorizationFailure, self.user.token, identity="tester", password="bbbbb", storeInSession=False)

        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="token",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.token, identity="tester", password="bbbbb", storeInSession=False)

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="token",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.token, identity="tester", password="bbbbb", storeInSession=False)

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="token",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.token, identity="tester", password="bbbbb", storeInSession=False)



    def test_signin(self):
        # valid signin
        r = adapter.StoredResponse(service="users",
                                   method="signin",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Set-Cookie": "auth=1234567890;", "Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.signin(identity="tester", password="aaaaa")
        self.assert_(result)
        self.assertFalse(self.user.session.authtoken)

    def test_signin_failure(self):
        # result false, custom message
        r = adapter.StoredResponse(service="users",
                                   method="signin",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False, "message": ("Server message",)},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.AuthorizationFailure, self.user.signin, identity="tester", password="aaaaa")

        # empty content, no json
        r = adapter.StoredResponse(service="users",
                                   method="signin",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": "",
                                      "headers": {}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.AuthorizationFailure, self.user.signin, identity="tester", password="aaaaa")

        # no result, custom message, json
        r = adapter.StoredResponse(service="users",
                                   method="signin",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"message": ("Server message","Another Message")},
                                      "headers": {}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.AuthorizationFailure, self.user.signin, identity="tester", password="aaaaa")

    def test_signin_codes(self):
        # code 401
        r = adapter.StoredResponse(service="users",
                                   method="signin",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 401,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.AuthorizationFailure, self.user.signin, identity="tester", password="bbbbb")

        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="signin",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.signin, identity="tester", password="bbbbb")

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="signin",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.signin, identity="tester", password="bbbbb")

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="signin",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.signin, identity="tester", password="bbbbb")



    def test_signout(self):
        # signout
        r = adapter.StoredResponse(service="users",
                                   method="signout",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Set-Cookie": "auth=1234567890;", "Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.user.session.authtoken = "1234567890"
        self.user.signout()
        self.assertFalse(self.user.session.authtoken)

    def test_signout_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="signout",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.signout)

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="signout",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.signout)

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="signout",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.signout)


    def test_identity(self):
        # identity
        r = adapter.StoredResponse(service="users",
                                   method="identity",
                                   response={
                                      "status_code": 200,
                                      "content": {"name": "tester", "email": "tester@email.com", "realname": "tester", "reference": "00000"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        values = self.user.identity()
        self.assertEqual(values["name"], "tester")
        self.assertEqual(values["email"], "tester@email.com")
        self.assertEqual(values["realname"], "tester")
        self.assertEqual(values["reference"], "00000")

    def test_identity_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="identity",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.identity)

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="identity",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.identity)

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="identity",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.identity)


    def test_name(self):
        # name
        r = adapter.StoredResponse(service="users",
                                   method="name",
                                   response={
                                      "status_code": 200,
                                      "content": {"name": "tester", "realname": "tester"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        values = self.user.name()
        self.assertEqual(values["name"], "tester")
        self.assertEqual(values["realname"], "tester")

    def test_name_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="name",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.name)

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="name",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.name)

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="name",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.name)


    def test_profile(self):
        # identity
        r = adapter.StoredResponse(service="users",
                                   method="profile",
                                   response={
                                      "status_code": 200,
                                      "content": {"data": "custom", "notify": True,
                                                  "email": "tester@email.com", "lastlogin": "2014-10-21T16:54:21+00:00",
                                                  "name": "tester", "realname": "tester"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        values = self.user.profile()
        self.assertEqual(values["data"], "custom")
        self.assertEqual(values["notify"], True)
        self.assertEqual(values["email"], "tester@email.com")
        self.assertEqual(values["lastlogin"], "2014-10-21T16:54:21+00:00")
        self.assertEqual(values["name"], "tester")
        self.assertEqual(values["realname"], "tester")

    def test_profile_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="profile",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.profile)

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="profile",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.profile)

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="profile",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.profile)


    def test_authenticated(self):
        # authenticated
        r = adapter.StoredResponse(service="users",
                                   method="authenticated",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.authenticated()
        self.assert_(result)

        # single group
        r = adapter.StoredResponse(service="users",
                                   method="authenticated",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.authenticated(groups="mygroup")
        self.assert_(result)

        # multiple groups
        r = adapter.StoredResponse(service="users",
                                   method="authenticated",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.authenticated(groups=("mygroup","yourgroup"))
        self.assert_(result)

    def test_authenticated_failure(self):
        # authenticated
        r = adapter.StoredResponse(service="users",
                                   method="authenticated",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.authenticated()
        self.assertFalse(result)

        # single group
        r = adapter.StoredResponse(service="users",
                                   method="authenticated",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.authenticated(groups="mygroup")
        self.assertFalse(result)

        # multiple groups
        r = adapter.StoredResponse(service="users",
                                   method="authenticated",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.authenticated(groups=("mygroup","yourgroup"))
        self.assertFalse(result)

        # no result
        r = adapter.StoredResponse(service="users",
                                   method="authenticated",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result = self.user.authenticated()
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="authenticated",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.authenticated()
        self.assertFalse(result)

    def test_authenticated_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="authenticated",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.authenticated)

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="authenticated",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.authenticated)

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="authenticated",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.authenticated)



    def test_update(self):
        # update
        r = adapter.StoredResponse(service="users",
                                   method="update",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.update(data="custom", realname="tester", notify=False)
        self.assert_(result)

        # update, message
        r = adapter.StoredResponse(service="users",
                                   method="update",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "message": "OK"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.update(data="custom", realname=None, notify=None)
        self.assert_(result)
        self.assert_(result.message)

    def test_update_failure(self):
        # no values
        r = adapter.StoredResponse(service="users",
                                   method="update",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "invalid": [["data","too long"]],
                                                  "message": "invalid_data"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.update(data="custom"*1000)
        self.assertFalse(result)
        self.assert_(result.invalid)
        self.assert_(result.message)

        # no result
        r = adapter.StoredResponse(service="users",
                                   method="update",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result = self.user.update(data="custom", realname="tester", notify=False)
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="update",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.update(data="custom", realname="tester", notify=False)
        self.assertFalse(result)

    def test_update_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="update",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.update, data="custom", realname="tester", notify=False)

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="update",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.update, data="custom", realname="tester", notify=False)

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="update",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.update, data="custom", realname="tester", notify=False)


    def test_updatePassword(self):
        # updatePassword
        r = adapter.StoredResponse(service="users",
                                   method="updatePassword",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.updatePassword(password="aaaaa", newpassword="bbbbb")
        self.assert_(result)

        # updatePassword, message
        r = adapter.StoredResponse(service="users",
                                   method="updatePassword",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "message": "OK"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.updatePassword(password="aaaaa", newpassword="bbbbb")
        self.assert_(result)
        self.assert_(result.message)

    def test_updatePassword_failure(self):
        # no values
        r = adapter.StoredResponse(service="users",
                                   method="updatePassword",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "invalid": [["password","empty"]],
                                                  "message": "invalild_data"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.updatePassword(password="", newpassword="bbbbb")
        self.assertFalse(result)
        self.assert_(result.invalid)
        self.assert_(result.message)

        # no result
        r = adapter.StoredResponse(service="users",
                                   method="updatePassword",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result = self.user.updatePassword(password="aaaaa", newpassword="bbbbb")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="updatePassword",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.updatePassword(password="aaaaa", newpassword="bbbbb")
        self.assertFalse(result)

    def test_updatePassword_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="updatePassword",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.updatePassword, password="aaaaa", newpassword="bbbbb")

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="updatePassword",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.updatePassword, password="aaaaa", newpassword="bbbbb")

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="updatePassword",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.updatePassword, password="aaaaa", newpassword="bbbbb")


    def test_updateEmail(self):
        # updateEmail
        r = adapter.StoredResponse(service="users",
                                   method="updateEmail",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.updateEmail(email="tester@email.com")
        self.assert_(result)

        # updateEmail, message
        r = adapter.StoredResponse(service="users",
                                   method="updateEmail",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "message": "OK"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.updateEmail(email="tester@email.com")
        self.assert_(result)
        self.assert_(result.message)

    def test_updateEmail_failure(self):
        # no values
        r = adapter.StoredResponse(service="users",
                                   method="updateEmail",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "invalid": [["email","empty"]],
                                                  "message": "validation_failure"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.updateEmail(email="")
        self.assertFalse(result)
        self.assert_(result.invalid)
        self.assert_(result.message)

        # no result
        r = adapter.StoredResponse(service="users",
                                   method="updateEmail",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result = self.user.updateEmail(email="tester@email.com")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="updateEmail",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.updateEmail(email="tester@email.com")
        self.assertFalse(result)

    def test_updateEmail_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="updateEmail",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.updateEmail, email="tester@email.com")

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="updateEmail",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.updateEmail, email="tester@email.com")

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="updateEmail",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.updateEmail, email="tester@email.com")


    def test_verifyEmail2(self):
        # verifyEmail2
        r = adapter.StoredResponse(service="users",
                                   method="verifyEmail2",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.verifyEmail2(token="0000000000")
        self.assert_(result)

        # verifyEmail2, message
        r = adapter.StoredResponse(service="users",
                                   method="verifyEmail2",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "message": "OK"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.verifyEmail2(token="0000000000")
        self.assert_(result)
        self.assert_(result.message)

    def test_verifyEmail2_failure(self):
        # no values
        r = adapter.StoredResponse(service="users",
                                   method="verifyEmail2",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "message": "invalid_token"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.verifyEmail2(token="")
        self.assertFalse(result)
        self.assert_(result.message)

        # no result
        r = adapter.StoredResponse(service="users",
                                   method="verifyEmail2",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result = self.user.verifyEmail2(token="0000000000")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="verifyEmail2",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.verifyEmail2(token="0000000000")
        self.assertFalse(result)

    def test_verifyEmail2_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="verifyEmail2",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.verifyEmail2, token="0000000000")

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="verifyEmail2",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.verifyEmail2, token="0000000000")

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="verifyEmail2",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.verifyEmail2, token="0000000000")


    def test_resetPassword(self):
        # resetPassword
        r = adapter.StoredResponse(service="users",
                                   method="resetPassword",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.resetPassword(identity="tester@email.com")
        self.assert_(result)

        # resetPassword, message
        r = adapter.StoredResponse(service="users",
                                   method="resetPassword",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "message": "OK"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.resetPassword(identity="tester@email.com")
        self.assert_(result)
        self.assert_(result.message)

    def test_resetPassword_failure(self):
        # no values
        r = adapter.StoredResponse(service="users",
                                   method="resetPassword",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "message": "unknown_user"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.resetPassword(identity="")
        self.assertFalse(result)
        self.assert_(result.message)

        # no result
        r = adapter.StoredResponse(service="users",
                                   method="resetPassword",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result = self.user.resetPassword(identity="tester@email.com")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="resetPassword",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.resetPassword(identity="tester@email.com")
        self.assertFalse(result)

    def test_resetPassword_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="resetPassword",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.resetPassword, identity="tester@email.com")

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="resetPassword",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.resetPassword, identity="tester@email.com")

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="resetPassword",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.resetPassword, identity="tester@email.com")


    def test_resetPassword2(self):
        # resetPassword2
        r = adapter.StoredResponse(service="users",
                                   method="resetPassword2",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.resetPassword2(token="0000000000", newpassword="bbbbb")
        self.assert_(result)

        # resetPassword2, message
        r = adapter.StoredResponse(service="users",
                                   method="resetPassword2",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "message": "OK"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.resetPassword2(token="0000000000", newpassword="bbbbb")
        self.assert_(result)
        self.assert_(result.message)

    def test_resetPassword2_failure(self):
        # no token
        r = adapter.StoredResponse(service="users",
                                   method="resetPassword2",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "invalid": [["token","invalid"]],
                                                  "message": "empty_token"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.resetPassword2(token="", newpassword="bbbbb")
        self.assertFalse(result)
        self.assert_(result.invalid)
        self.assert_(result.message)

        # no password
        r = adapter.StoredResponse(service="users",
                                   method="resetPassword2",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "invalid": [["newpassword","invalid"]],
                                                  "message": "validation_failure"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.resetPassword2(token="0000000000", newpassword="")
        self.assertFalse(result)
        self.assert_(result.invalid)
        self.assert_(result.message)

        # no result
        r = adapter.StoredResponse(service="users",
                                   method="resetPassword2",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result = self.user.resetPassword2(token="0000000000", newpassword="bbbbb")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="resetPassword2",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.resetPassword2(token="0000000000", newpassword="bbbbb")
        self.assertFalse(result)

    def test_resetPassword2_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="resetPassword2",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.resetPassword2, token="0000000000", newpassword="bbbbb")

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="resetPassword2",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.resetPassword2, token="0000000000", newpassword="bbbbb")

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="resetPassword2",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.resetPassword2, token="0000000000", newpassword="bbbbb")


    def test_message(self):
        # disable
        r = adapter.StoredResponse(service="users",
                                   method="message",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.message("Hello!")
        self.assert_(result)

    def test_message_failure(self):
        # false
        r = adapter.StoredResponse(service="users",
                                   method="message",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False, "message": "validation_failure"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.message("")
        self.assertFalse(result)
        self.assert_(result.message)

        # no result
        r = adapter.StoredResponse(service="users",
                                   method="message",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.message("")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="message",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.message(None)
        self.assertFalse(result)

    def test_message_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="message",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.message, "Hello!")

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="message",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.message, "Hello!")

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="message",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.message, "Hello!")


    def test_disable(self):
        # disable
        r = adapter.StoredResponse(service="users",
                                   method="disable",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.disable()
        self.assert_(result)

        # disable message
        r = adapter.StoredResponse(service="users",
                                   method="disable",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "message": "OK"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.disable()
        self.assert_(result)
        self.assert_(result.message)

    def test_disable_failure(self):
        # disable false
        r = adapter.StoredResponse(service="users",
                                   method="disable",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False, "message": "failed"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.disable()
        self.assertFalse(result)
        self.assert_(result.message)

        # no result
        r = adapter.StoredResponse(service="users",
                                   method="disable",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.disable()
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="disable",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.disable()
        self.assertFalse(result)

    def test_disable_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="disable",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.disable)

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="disable",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.disable)

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="disable",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.disable)


    def test_delete(self):
        # disable
        r = adapter.StoredResponse(service="users",
                                   method="delete",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.delete()
        self.assert_(result)

        # disable message
        r = adapter.StoredResponse(service="users",
                                   method="delete",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "message": "OK"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.delete()
        self.assert_(result)
        self.assert_(result.message)

    def test_delete_failure(self):
        # delete false
        r = adapter.StoredResponse(service="users",
                                   method="delete",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False, "message": "failed"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.delete()
        self.assertFalse(result)
        self.assert_(result.message)

        # no result
        r = adapter.StoredResponse(service="users",
                                   method="delete",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.delete()
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="delete",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.delete()
        self.assertFalse(result)

    def test_delete_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="delete",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.delete)

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="delete",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.delete)

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="delete",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.delete)




class adminFunctionTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()
        session = adapter.MockAdapter()
        self.user = userstore.User(domain="mydomain", session=session)

    def test_getUser(self):
        # getUser
        r = adapter.StoredResponse(service="users",
                                   method="getUser",
                                   response={
                                      "status_code": 200,
                                      "content": {"reference": "1234567890"},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.getUser(identity="tester")
        self.assert_(result["reference"]=="1234567890")

    def test_getUser_failure(self):
        # no result
        r = adapter.StoredResponse(service="users",
                                   method="getUser",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.getUser(identity="tester")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="getUser",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.getUser(identity="tester")
        self.assertFalse(result)

    def test_getUser_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="getUser",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.getUser, identity="tester")

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="getUser",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.getUser, identity="tester")

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="getUser",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.getUser, identity="tester")


    def test_setUser(self):
        # setUser
        r = adapter.StoredResponse(service="users",
                                   method="setUser",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.setUser(identity="tester",values={"realname":"new"})
        self.assert_(result.result)

    def test_setUser_failure(self):
        # no result
        r = adapter.StoredResponse(service="users",
                                   method="setUser",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.setUser(identity="tester",values={"realname":"new"})
        self.assertFalse(result.result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="setUser",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.setUser(identity="tester",values={"realname":"new"})
        self.assertFalse(result.result)

    def test_setUser_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="setUser",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.setUser, identity="tester",values={"realname":"new"})

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="setUser",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.setUser, identity="tester",values={"realname":"new"})

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="setUser",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.setUser, identity="tester",values={"realname":"new"})


    def test_removeUser(self):
        # getUser
        r = adapter.StoredResponse(service="users",
                                   method="removeUser",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result = self.user.removeUser(identity="tester")
        self.assert_(result)

    def test_removeUser_failure(self):
        # no result
        r = adapter.StoredResponse(service="users",
                                   method="removeUser",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.removeUser(identity="tester")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="removeUser",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.removeUser(identity="tester")
        self.assertFalse(result)

    def test_removeUser_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="removeUser",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.removeUser, identity="tester")

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="removeUser",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.removeUser, identity="tester")

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="removeUser",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.removeUser, identity="tester")


    def test_list(self):
        resultusers = [{u'realname': u'surname', u'reference': u'8d54c2528b4f46918fb2117d8d251dcb', u'activity': None,
                        u'active': 1, u'email': u'admin@aaa.ccc', u'pending': False, u'name': u'admin'},
                       {u'realname': u'surname', u'reference': u'7e4ce2615602401ab0abaf5face300be', u'activity': None,
                        u'active': 0, u'email': u'user1@aaa.ccc', u'pending': True, u'name': u'user1'}]
        # list
        r = adapter.StoredResponse(service="users",
                                   method="list",
                                   response={
                                      "status_code": 200,
                                      "content": {"users": resultusers, "size": 2, "start": 1},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.list()
        self.assert_(len(result.users)==2)

        r = adapter.StoredResponse(service="users",
                                   method="list",
                                   response={
                                      "status_code": 200,
                                      "content": {"users": resultusers[1:], "size": 1, "start": 2},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.list(start=2, sort="name", order="<", size=5)
        self.assert_(len(result.users)==1)

        r = adapter.StoredResponse(service="users",
                                   method="list",
                                   response={
                                      "status_code": 200,
                                      "content": {"users": resultusers[:1], "size": 1, "start": 1},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.list(active=True)
        self.assert_(len(result.users)==1)

        r = adapter.StoredResponse(service="users",
                                   method="list",
                                   response={
                                      "status_code": 200,
                                      "content": {"users": resultusers[1:], "size": 1, "start": 1},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.list(pending=True)
        self.assert_(len(result.users)==1)

    def test_list_failure(self):
        # no result
        r = adapter.StoredResponse(service="users",
                                   method="list",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.list()
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="list",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.list()
        self.assertFalse(result)

    def test_list_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="list",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.list)

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="list",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.list)

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="list",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.list)


    def test_identities(self):
        resultusers = [{u'reference': u'8d54c2528b4f46918fb2117d8d251dcb', u'name': u'admin'},
                       {u'reference': u'7e4ce2615602401ab0abaf5face300be', u'name': u'user1'}]
        # list
        r = adapter.StoredResponse(service="users",
                                   method="identities",
                                   response={
                                      "status_code": 200,
                                      "content": {"users": resultusers, "size": 2, "start": 1},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.identities()
        self.assert_(len(result.users)==2)

        r = adapter.StoredResponse(service="users",
                                   method="identities",
                                   response={
                                      "status_code": 200,
                                      "content": {"users": resultusers[1:], "size": 1, "start": 2},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.identities(start=2, order="<", size=5)
        self.assert_(len(result.users)==1)

        r = adapter.StoredResponse(service="users",
                                   method="identities",
                                   response={
                                      "status_code": 200,
                                      "content": {"users": resultusers[:1], "size": 1, "start": 1},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.identities(active=True)
        self.assert_(len(result.users)==1)

        r = adapter.StoredResponse(service="users",
                                   method="identities",
                                   response={
                                      "status_code": 200,
                                      "content": {"users": resultusers[1:], "size": 1, "start": 1},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.identities(pending=True)
        self.assert_(len(result.users)==1)

    def test_identities_failure(self):
        # no result
        r = adapter.StoredResponse(service="users",
                                   method="identities",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.identities()
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(service="users",
                                   method="identities",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        result = self.user.identities()
        self.assertFalse(result)

    def test_identities_codes(self):
        # code 403
        r = adapter.StoredResponse(service="users",
                                   method="identities",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.identities)

        # code 404
        r = adapter.StoredResponse(service="users",
                                   method="identities",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.user.identities)

        # code 500
        r = adapter.StoredResponse(service="users",
                                   method="identities",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.identities)


    def test_allowedv1(self):
        # allowed: name, permission
        r = adapter.StoredResponse(service="users",
                                   method="allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"profile": True, "update": False},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.user.session.responses=(r,)

        p = self.user.allowed(permissions=("profile","update"))
        self.assertEqual(p.get("profile"), True)
        self.assertEqual(p.update, False)

    def test_allowedv2(self):
        r = adapter.StoredResponse(service="users",
                                   method="allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"signupDirect": True},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.user.session.responses=(r,)

        p = self.user.allowed(permissions="signupDirect")
        self.assertEqual(p.signupDirect, True)



    def test_getPermissionsv1(self):
        # getPermissions: name
        r = adapter.StoredResponse(service="users",
                                   method="getPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"profile": ("sys:everyone",),
                                                  "update": ("mygroup","admins")},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.user.session.responses=(r,)

        p = self.user.getPermissions()
        self.assertEqual(len(p["profile"]), 1)
        self.assertEqual(len(p["update"]), 2)



    def test_setPermissions(self):
        # setPermissions:  name, permission, group, action="allow"
        r = adapter.StoredResponse(service="users",
                                   method="setPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.user.session.responses=(r,)

        r = self.user.setPermissions(permissions=dict(permission="profile",group="sys:everyone"))
        self.assertEqual(r, True)

        r = self.user.setPermissions(permissions=[dict(permission="profile",group="sys:everyone"),
                                                     dict(permission="update",group="sys:everyone")])
        self.assertEqual(r, True)

        r = self.user.setPermissions(permissions=dict(permission="update",group=("mygroup","admins")))
        self.assertEqual(r, True)

        r = self.user.setPermissions(permissions=dict(permission="update",group=("mygroup","admins"),action="revoke"))
        self.assertEqual(r, True)


    def test_ping(self):
        # ping:
        r = adapter.StoredResponse(service="users",
                                   method="ping",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": 1},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.user.session.responses=(r,)

        r = self.user.ping()
        self.assertEqual(r, 1)

