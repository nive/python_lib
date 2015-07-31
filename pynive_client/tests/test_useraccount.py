
import unittest
import json
import logging

from pynive_client import adapter
from pynive_client import endpoint
from pynive_client import useraccount


class userTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def test_setup_empty(self):
        user = useraccount.User()
        self.assertFalse(user.options["domain"])
        self.assertFalse(user.session)
        self.assert_(user.options["name"]==user.service_name)
        self.assert_(user.options["version"]==user.default_version)

    def test_setup(self):
        user = useraccount.User(domain="mydomain")
        self.assert_(user.options["domain"]=="mydomain")
        self.assert_(user.options["name"]==user.service_name)
        self.assert_(user.options["version"]==user.default_version)
        self.assertFalse(user.session)

        user = useraccount.User(domain="mydomain", version="api23")
        self.assert_(user.options["domain"]=="mydomain")
        self.assert_(user.options["name"]==user.service_name)
        self.assert_(user.options["version"]=="api23")
        self.assertFalse(user.session)

    def test_setup_fails(self):
        self.assertRaises(TypeError, useraccount.User, domain="mydomain", name="myservice")

    def test_session(self):
        user = useraccount.User(domain="mydomain", session=adapter.MockAdapter())
        self.assert_(user.options["domain"]=="mydomain")
        self.assert_(user.session)


class userFunctionTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()
        session = adapter.MockAdapter()
        self.user = useraccount.User(domain="mydomain", session=session)

    def test_token(self):
        # valid token
        r = adapter.StoredResponse(name="users",
                                   method="token",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"token": "1234567890"},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)

        token = self.user.token(identity="tester", password="aaaaa", storeInSession=False)
        self.assertEqual(token, "1234567890")
        self.assertNotEqual(self.user.session.token, "1234567890")

        # valid token, stored in session
        token = self.user.token(identity="tester", password="aaaaa", storeInSession=True)
        self.assertEqual(token, "1234567890")
        self.assertEqual(self.user.session.token, "1234567890")

    def test_token_failure(self):
        # empty token, custom message
        r = adapter.StoredResponse(name="users",
                                   method="token",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"token": "", "messages": ("Server message",)},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.AuthorizationFailure, self.user.token, identity="tester", password="aaaaa", storeInSession=False)

        # empty content, no json
        r = adapter.StoredResponse(name="users",
                                   method="token",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": "",
                                      "headers": {}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.AuthorizationFailure, self.user.token, identity="tester", password="aaaaa", storeInSession=False)

        # no token, custom messages, json
        r = adapter.StoredResponse(name="users",
                                   method="token",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"messages": ("Server message","Another Message")},
                                      "headers": {}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.AuthorizationFailure, self.user.token, identity="tester", password="aaaaa", storeInSession=False)

    def test_token_codes(self):
        # code 401
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
                                   method="token",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.user.token, identity="tester", password="bbbbb", storeInSession=False)

        # code 500
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
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
        self.assertFalse(self.user.session.token)

    def test_signin_failure(self):
        # result false, custom message
        r = adapter.StoredResponse(name="users",
                                   method="signin",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False, "messages": ("Server message",)},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.AuthorizationFailure, self.user.signin, identity="tester", password="aaaaa")

        # empty content, no json
        r = adapter.StoredResponse(name="users",
                                   method="signin",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": "",
                                      "headers": {}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.AuthorizationFailure, self.user.signin, identity="tester", password="aaaaa")

        # no result, custom messages, json
        r = adapter.StoredResponse(name="users",
                                   method="signin",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"messages": ("Server message","Another Message")},
                                      "headers": {}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.AuthorizationFailure, self.user.signin, identity="tester", password="aaaaa")

    def test_signin_codes(self):
        # code 401
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
                                   method="signin",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.user.signin, identity="tester", password="bbbbb")

        # code 500
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
                                   method="signout",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Set-Cookie": "auth=1234567890;", "Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.user.session.token = "1234567890"
        self.user.signout()
        self.assertFalse(self.user.session.token)

    def test_signout_codes(self):
        # code 403
        r = adapter.StoredResponse(name="users",
                                   method="signout",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.signout, identity="tester", password="bbbbb")

        # code 404
        r = adapter.StoredResponse(name="users",
                                   method="signout",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.user.signout, identity="tester", password="bbbbb")

        # code 500
        r = adapter.StoredResponse(name="users",
                                   method="signout",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.signout, identity="tester", password="bbbbb")


    def test_identity(self):
        # identity
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
                                   method="identity",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.identity)

        # code 404
        r = adapter.StoredResponse(name="users",
                                   method="identity",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.user.identity)

        # code 500
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
                                   method="name",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.name)

        # code 404
        r = adapter.StoredResponse(name="users",
                                   method="name",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.user.name)

        # code 500
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
                                   method="profile",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.profile)

        # code 404
        r = adapter.StoredResponse(name="users",
                                   method="profile",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.user.profile)

        # code 500
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
                                   method="authenticated",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.authenticated)

        # code 404
        r = adapter.StoredResponse(name="users",
                                   method="authenticated",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.user.authenticated)

        # code 500
        r = adapter.StoredResponse(name="users",
                                   method="authenticated",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.authenticated)



    def test_signup(self):
        # signup
        r = adapter.StoredResponse(name="users",
                                   method="signup",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.signup(name="tester",
                             email="tester@email.com",
                             password="aaaaa",
                             realname="tester",
                             notify=True,
                             data="custom")
        self.assert_(result)

        # minimum values
        r = adapter.StoredResponse(name="users",
                                   method="signup",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.signup(name="tester",
                               email="tester@email.com",
                               password="aaaaa")
        self.assert_(result)

        # minimum values, messages
        r = adapter.StoredResponse(name="users",
                                   method="signup",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "invalid": [], "messages": ["OK"]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.signup(name="tester",
                               email="tester@email.com",
                               password="aaaaa")
        self.assert_(result)
        self.assert_(m)

    def test_signup_failure(self):
        # no name
        r = adapter.StoredResponse(name="users",
                                   method="signup",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "invalid": [["name", "empty"]],
                                                  "messages": ["Validation failed."]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.signup(name="",
                               email="tester@email.com",
                               password="aaaaa")
        self.assertFalse(result)
        self.assert_(i)
        self.assert_(m)

        # no result
        r = adapter.StoredResponse(name="users",
                                   method="signup",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.signup(name="tester",
                               email="tester@email.com",
                               password="aaaaa")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(name="users",
                                   method="signup",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.signup(name="tester",
                               email="tester@email.com",
                               password="aaaaa")
        self.assertFalse(result)

    def test_signup_codes(self):
        # code 403
        r = adapter.StoredResponse(name="users",
                                   method="signup",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.signup)

        # code 404
        r = adapter.StoredResponse(name="users",
                                   method="signup",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.user.signup)

        # code 500
        r = adapter.StoredResponse(name="users",
                                   method="signup",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.signup)


    def test_signup2(self):
        # signup2
        r = adapter.StoredResponse(name="users",
                                   method="signup2",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m=self.user.signup2(token="0000000000")
        self.assert_(result)

        # signup2, messages
        r = adapter.StoredResponse(name="users",
                                   method="signup2",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "messages": ["OK"]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m=self.user.signup2(token="0000000000")
        self.assert_(result)
        self.assert_(m)

    def test_signup2_failure(self):
        # no token
        r = adapter.StoredResponse(name="users",
                                   method="signup2",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "messages": ["Empty token."]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m=self.user.signup2(token="")
        self.assertFalse(result)
        self.assert_(m)

        # no result
        r = adapter.StoredResponse(name="users",
                                   method="signup2",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result,m=self.user.signup2(token="000000000")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(name="users",
                                   method="signup2",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m=self.user.signup2(token="000000000")
        self.assertFalse(result)

    def test_signup2_codes(self):
        # code 403
        r = adapter.StoredResponse(name="users",
                                   method="signup2",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.signup2, token="000000")

        # code 404
        r = adapter.StoredResponse(name="users",
                                   method="signup2",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.user.signup2, token="000000")

        # code 500
        r = adapter.StoredResponse(name="users",
                                   method="signup2",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.signup2, token="000000")


    def test_update(self):
        # update
        r = adapter.StoredResponse(name="users",
                                   method="update",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.update(data="custom", realname="tester", notify=False)
        self.assert_(result)

        # update, messages
        r = adapter.StoredResponse(name="users",
                                   method="update",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "messages": ["OK"]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.update(data="custom", realname=None, notify=None)
        self.assert_(result)
        self.assert_(m)

    def test_update_failure(self):
        # no values
        r = adapter.StoredResponse(name="users",
                                   method="update",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "invalid": [["data","too long"]],
                                                  "messages": ["Invalid data."]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.update(data="custom"*1000)
        self.assertFalse(result)
        self.assert_(i)
        self.assert_(m)

        # no result
        r = adapter.StoredResponse(name="users",
                                   method="update",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.update(data="custom", realname="tester", notify=False)
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(name="users",
                                   method="update",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.update(data="custom", realname="tester", notify=False)
        self.assertFalse(result)

    def test_update_codes(self):
        # code 403
        r = adapter.StoredResponse(name="users",
                                   method="update",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.update, data="custom", realname="tester", notify=False)

        # code 404
        r = adapter.StoredResponse(name="users",
                                   method="update",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.user.update, data="custom", realname="tester", notify=False)

        # code 500
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
                                   method="updatePassword",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.updatePassword(password="aaaaa", newpassword="bbbbb")
        self.assert_(result)

        # updatePassword, messages
        r = adapter.StoredResponse(name="users",
                                   method="updatePassword",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "messages": ["OK"]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.updatePassword(password="aaaaa", newpassword="bbbbb")
        self.assert_(result)
        self.assert_(m)

    def test_updatePassword_failure(self):
        # no values
        r = adapter.StoredResponse(name="users",
                                   method="updatePassword",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "invalid": [["password","empty"]],
                                                  "messages": ["Invalid password."]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.updatePassword(password="", newpassword="bbbbb")
        self.assertFalse(result)
        self.assert_(i)
        self.assert_(m)

        # no result
        r = adapter.StoredResponse(name="users",
                                   method="updatePassword",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.updatePassword(password="aaaaa", newpassword="bbbbb")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(name="users",
                                   method="updatePassword",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.updatePassword(password="aaaaa", newpassword="bbbbb")
        self.assertFalse(result)

    def test_updatePassword_codes(self):
        # code 403
        r = adapter.StoredResponse(name="users",
                                   method="updatePassword",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.updatePassword, password="aaaaa", newpassword="bbbbb")

        # code 404
        r = adapter.StoredResponse(name="users",
                                   method="updatePassword",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.user.updatePassword, password="aaaaa", newpassword="bbbbb")

        # code 500
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
                                   method="updateEmail",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.updateEmail(email="tester@email.com")
        self.assert_(result)

        # updateEmail, messages
        r = adapter.StoredResponse(name="users",
                                   method="updateEmail",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "messages": ["OK"]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.updateEmail(email="tester@email.com")
        self.assert_(result)
        self.assert_(m)

    def test_updateEmail_failure(self):
        # no values
        r = adapter.StoredResponse(name="users",
                                   method="updateEmail",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "invalid": [["email","empty"]],
                                                  "messages": ["Invalid email."]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.updateEmail(email="")
        self.assertFalse(result)
        self.assert_(i)
        self.assert_(m)

        # no result
        r = adapter.StoredResponse(name="users",
                                   method="updateEmail",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.updateEmail(email="tester@email.com")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(name="users",
                                   method="updateEmail",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.updateEmail(email="tester@email.com")
        self.assertFalse(result)

    def test_updateEmail_codes(self):
        # code 403
        r = adapter.StoredResponse(name="users",
                                   method="updateEmail",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.updateEmail, email="tester@email.com")

        # code 404
        r = adapter.StoredResponse(name="users",
                                   method="updateEmail",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.user.updateEmail, email="tester@email.com")

        # code 500
        r = adapter.StoredResponse(name="users",
                                   method="updateEmail",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.updateEmail, email="tester@email.com")


    def test_updateEmail2(self):
        # updateEmail2
        r = adapter.StoredResponse(name="users",
                                   method="updateEmail2",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m=self.user.updateEmail2(token="0000000000")
        self.assert_(result)

        # updateEmail2, messages
        r = adapter.StoredResponse(name="users",
                                   method="updateEmail2",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "messages": ["OK"]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m=self.user.updateEmail2(token="0000000000")
        self.assert_(result)
        self.assert_(m)

    def test_updateEmail2_failure(self):
        # no values
        r = adapter.StoredResponse(name="users",
                                   method="updateEmail2",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "messages": ["Invalid token."]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m=self.user.updateEmail2(token="")
        self.assertFalse(result)
        self.assert_(m)

        # no result
        r = adapter.StoredResponse(name="users",
                                   method="updateEmail2",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result,m=self.user.updateEmail2(token="0000000000")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(name="users",
                                   method="updateEmail2",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m=self.user.updateEmail2(token="0000000000")
        self.assertFalse(result)

    def test_updateEmail2_codes(self):
        # code 403
        r = adapter.StoredResponse(name="users",
                                   method="updateEmail2",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.updateEmail2, token="0000000000")

        # code 404
        r = adapter.StoredResponse(name="users",
                                   method="updateEmail2",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.user.updateEmail2, token="0000000000")

        # code 500
        r = adapter.StoredResponse(name="users",
                                   method="updateEmail2",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.updateEmail2, token="0000000000")


    def test_resetPassword(self):
        # resetPassword
        r = adapter.StoredResponse(name="users",
                                   method="resetPassword",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m=self.user.resetPassword(identity="tester@email.com")
        self.assert_(result)

        # resetPassword, messages
        r = adapter.StoredResponse(name="users",
                                   method="resetPassword",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "messages": ["OK"]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m=self.user.resetPassword(identity="tester@email.com")
        self.assert_(result)
        self.assert_(m)

    def test_resetPassword_failure(self):
        # no values
        r = adapter.StoredResponse(name="users",
                                   method="resetPassword",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "messages": ["Unknown identity."]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m=self.user.resetPassword(identity="")
        self.assertFalse(result)
        self.assert_(m)

        # no result
        r = adapter.StoredResponse(name="users",
                                   method="resetPassword",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result,m=self.user.resetPassword(identity="tester@email.com")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(name="users",
                                   method="resetPassword",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m=self.user.resetPassword(identity="tester@email.com")
        self.assertFalse(result)

    def test_resetPassword_codes(self):
        # code 403
        r = adapter.StoredResponse(name="users",
                                   method="resetPassword",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.resetPassword, identity="tester@email.com")

        # code 404
        r = adapter.StoredResponse(name="users",
                                   method="resetPassword",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.user.resetPassword, identity="tester@email.com")

        # code 500
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
                                   method="resetPassword2",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.resetPassword2(token="0000000000", newpassword="bbbbb")
        self.assert_(result)

        # resetPassword2, messages
        r = adapter.StoredResponse(name="users",
                                   method="resetPassword2",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "messages": ["OK"]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.resetPassword2(token="0000000000", newpassword="bbbbb")
        self.assert_(result)
        self.assert_(m)

    def test_resetPassword2_failure(self):
        # no token
        r = adapter.StoredResponse(name="users",
                                   method="resetPassword2",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "invalid": [["token","invalid"]],
                                                  "messages": ["Empty token."]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.resetPassword2(token="", newpassword="bbbbb")
        self.assertFalse(result)
        self.assert_(i)
        self.assert_(m)

        # no password
        r = adapter.StoredResponse(name="users",
                                   method="resetPassword2",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False,
                                                  "invalid": [["newpassword","invalid"]],
                                                  "messages": ["Empty password."]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.resetPassword2(token="0000000000", newpassword="")
        self.assertFalse(result)
        self.assert_(i)
        self.assert_(m)

        # no result
        r = adapter.StoredResponse(name="users",
                                   method="resetPassword2",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.resetPassword2(token="0000000000", newpassword="bbbbb")
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(name="users",
                                   method="resetPassword2",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,i,m=self.user.resetPassword2(token="0000000000", newpassword="bbbbb")
        self.assertFalse(result)

    def test_resetPassword2_codes(self):
        # code 403
        r = adapter.StoredResponse(name="users",
                                   method="resetPassword2",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.resetPassword2, token="0000000000", newpassword="bbbbb")

        # code 404
        r = adapter.StoredResponse(name="users",
                                   method="resetPassword2",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.user.resetPassword2, token="0000000000", newpassword="bbbbb")

        # code 500
        r = adapter.StoredResponse(name="users",
                                   method="resetPassword2",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.resetPassword2, token="0000000000", newpassword="bbbbb")


    def test_disable(self):
        # disable
        r = adapter.StoredResponse(name="users",
                                   method="disable",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m = self.user.disable()
        self.assert_(result)

        # disable messages
        r = adapter.StoredResponse(name="users",
                                   method="disable",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "messages": ["OK"]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m = self.user.disable()
        self.assert_(result)
        self.assert_(m)

    def test_disable_failure(self):
        # disable false
        r = adapter.StoredResponse(name="users",
                                   method="disable",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False, "messages": ["Failed"]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m = self.user.disable()
        self.assertFalse(result)
        self.assert_(m)

        # no result
        r = adapter.StoredResponse(name="users",
                                   method="disable",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m = self.user.disable()
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(name="users",
                                   method="disable",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m = self.user.disable()
        self.assertFalse(result)

    def test_disable_codes(self):
        # code 403
        r = adapter.StoredResponse(name="users",
                                   method="disable",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.disable)

        # code 404
        r = adapter.StoredResponse(name="users",
                                   method="disable",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.user.disable)

        # code 500
        r = adapter.StoredResponse(name="users",
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
        r = adapter.StoredResponse(name="users",
                                   method="delete",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m = self.user.delete()
        self.assert_(result)

        # disable messages
        r = adapter.StoredResponse(name="users",
                                   method="delete",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True, "messages": ["OK"]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m = self.user.delete()
        self.assert_(result)
        self.assert_(m)

    def test_delete_failure(self):
        # delete false
        r = adapter.StoredResponse(name="users",
                                   method="delete",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": False, "messages": ["Failed"]},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m = self.user.delete()
        self.assertFalse(result)
        self.assert_(m)

        # no result
        r = adapter.StoredResponse(name="users",
                                   method="delete",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m = self.user.delete()
        self.assertFalse(result)

        # empty result
        r = adapter.StoredResponse(name="users",
                                   method="delete",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })


        self.user.session.responses=(r,)
        result,m = self.user.delete()
        self.assertFalse(result)

    def test_delete_codes(self):
        # code 403
        r = adapter.StoredResponse(name="users",
                                   method="delete",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.user.delete)

        # code 404
        r = adapter.StoredResponse(name="users",
                                   method="delete",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.user.delete)

        # code 500
        r = adapter.StoredResponse(name="users",
                                   method="delete",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })

        self.user.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.user.delete)

