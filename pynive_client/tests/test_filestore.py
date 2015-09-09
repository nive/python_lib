
import unittest
import json
import logging

from pynive_client import adapter
from pynive_client import endpoint
from pynive_client import filestore


class filestoreTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def test_setup_empty(self):
        storage = filestore.FileStore(name="mystorage")
        self.assertFalse(storage.options["domain"])
        self.assertFalse(storage.session)
        self.assert_(storage.options["name"]=="mystorage")
        self.assert_(storage.options["version"]==storage.default_version)

    def test_setup(self):
        storage = filestore.FileStore(name="mystorage",domain="mydomain")
        self.assert_(storage.options["domain"]=="mydomain")
        self.assert_(storage.options["name"]=="mystorage")
        self.assert_(storage.options["version"]==storage.default_version)
        self.assertFalse(storage.session)

        storage = filestore.FileStore(name="mystorage", domain="mydomain", version="api23")
        self.assert_(storage.options["domain"]=="mydomain")
        self.assert_(storage.options["name"]=="mystorage")
        self.assert_(storage.options["version"]=="api23")
        self.assertFalse(storage.session)

    def test_setup_fails(self):
        storage = filestore.FileStore(name=None,domain="mydomain")
        self.assertRaises(endpoint.EndpointException, storage.call, "test", {}, {})

    def test_session(self):
        storage = filestore.FileStore(name="mystorage", domain="mydomain", session=adapter.MockAdapter())
        self.assert_(storage.options["domain"]=="mydomain")
        self.assert_(storage.options["name"]=="mystorage")
        self.assert_(storage.session)


class filestoreFunctionTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()
        session = adapter.MockAdapter()
        self.storage = filestore.FileStore(name="mystorage", domain="mydomain", session=session)

    def test_getItem(self):
        # getItem
        r = adapter.StoredResponse(name="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"name":"index.html", "type":"f", "size":2312,
                                                  "mime":"text/html", "mtime":"2014/03/01 12:15:10"},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        item = self.storage.getItem(path="/index.html")
        self.assertEqual(item["name"], "index.html")
        self.assertEqual(item["type"], "f")
        self.assertEqual(item["size"], 2312)
        self.assertEqual(item["mime"], "text/html")
        self.assertEqual(item["mtime"], "2014/03/01 12:15:10")

    def test_getItem_failure(self):
        # getItem not found
        r = adapter.StoredResponse(name="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        item = self.storage.getItem(path="image.jpg")
        self.assertFalse(item)

        # empty path
        r = adapter.StoredResponse(name="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.InvalidParameter, self.storage.getItem, path="")

    def test_getItem_codes(self):
        # code 400
        r = adapter.StoredResponse(name="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.InvalidParameter, self.storage.getItem, path="")

        # code 403
        r = adapter.StoredResponse(name="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.getItem, path="test")

        # code 404
        r = adapter.StoredResponse(name="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.getItem, path="test")

        # code 500
        r = adapter.StoredResponse(name="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.getItem, path="test")


    def test_list(self):
        # list
        r = adapter.StoredResponse(name="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items":[
                                          {"name":"index.html", "type":"f", "size":2312,
                                           "mime":"text/html", "mtime":"2014/03/01 12:15:10"},
                                          {"name":"image.jpg", "type":"f", "size":10234,
                                           "mime":"image/jpg", "mtime":"2014/03/01 14:18:21"},
                                          {"name":"subfolder", "type":"d", "size":0,
                                           "mime":"", "mtime":"2014/03/03 12:00:00"}
                                      ]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result = self.storage.list()
        self.assert_(len(result["items"])==3)
        self.assertEqual(result["items"][0]["name"], "index.html")

        # list root
        r = adapter.StoredResponse(name="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items":[
                                          {"name":"index.html", "type":"f", "size":2312,
                                           "mime":"text/html", "mtime":"2014/03/01 12:15:10"},
                                          {"name":"image.jpg", "type":"f", "size":10234,
                                           "mime":"image/jpg", "mtime":"2014/03/01 14:18:21"},
                                          {"name":"subfolder", "type":"d", "size":0,
                                           "mime":"", "mtime":"2014/03/03 12:00:00"}
                                      ]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result = self.storage.list(path="/")
        self.assert_(len(result["items"])==3)
        self.assertEqual(result["items"][0]["name"], "index.html")

        # list folder
        r = adapter.StoredResponse(name="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items":[
                                          {"name":"image2.jpg", "type":"f", "size":10234,
                                           "mime":"image/jpg", "mtime":"2014/03/01 14:18:21"}
                                      ]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result = self.storage.list(path="/subfolder")
        self.assert_(result["items"])
        self.assertEqual(result["items"][0]["name"], "image2.jpg")

        # list types
        r = adapter.StoredResponse(name="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items":[
                                          {"name":"subfolder", "type":"d", "size":0,
                                           "mime":"", "mtime":"2014/03/03 12:00:00"}
                                      ]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result = self.storage.list(path="/",filetype="d")
        self.assert_(len(result["items"])==1)
        self.assertEqual(result["items"][0]["name"], "subfolder")


    def test_list_failure(self):
        # if result empty
        r = adapter.StoredResponse(name="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result = self.storage.list()
        self.assertFalse(result["items"])

        # if result none
        r = adapter.StoredResponse(name="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result = self.storage.list()

    def test_list_codes(self):
        # code 400
        r = adapter.StoredResponse(name="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.InvalidParameter, self.storage.list)

        # code 403
        r = adapter.StoredResponse(name="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.list)

        # code 404
        r = adapter.StoredResponse(name="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.list)

        # code 500
        r = adapter.StoredResponse(name="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.list)

