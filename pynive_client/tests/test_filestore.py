
import unittest
import logging

from pynive_client import adapter
from pynive_client import endpoint
from pynive_client import filestore


class filestoreTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def test_setup_empty(self):
        storage = filestore.FileStore(service="mystorage")
        self.assertFalse(storage.options["domain"])
        self.assertFalse(storage.session)
        self.assert_(storage.options["service"]=="mystorage")
        self.assert_(storage.options["version"]==storage.default_version)

    def test_setup(self):
        storage = filestore.FileStore(service="mystorage", domain="mydomain")
        self.assert_(storage.options["domain"]=="mydomain")
        self.assert_(storage.options["service"]=="mystorage")
        self.assert_(storage.options["version"]==storage.default_version)
        self.assertFalse(storage.session)

        storage = filestore.FileStore(service="mystorage", domain="mydomain", version="api23")
        self.assert_(storage.options["domain"]=="mydomain")
        self.assert_(storage.options["service"]=="mystorage")
        self.assert_(storage.options["version"]=="api23")
        self.assertFalse(storage.session)

    def test_setup_fails(self):
        storage = filestore.FileStore(service=None, domain="mydomain")
        self.assertRaises(endpoint.EndpointException, storage.call, "test", {}, {})

    def test_session(self):
        storage = filestore.FileStore(service="mystorage", domain="mydomain", session=adapter.MockAdapter())
        self.assert_(storage.options["domain"]=="mydomain")
        self.assert_(storage.options["service"]=="mystorage")
        self.assert_(storage.session)


class filestoreFunctionTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()
        session = adapter.MockAdapter()
        self.storage = filestore.FileStore(service="mystorage", domain="mydomain", session=session)

    def test_getItem(self):
        # getItem: name
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"name":"index.html", "type":"f", "size":2312,
                                                  "mime":"text/html", "header":"origin=local",
                                                  "mtime":"2014/03/01 12:15:10", "ctime":"2014/03/01 12:15:10"},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        item = self.storage.getItem(name="index.html")
        self.assertEqual(item["name"], "index.html")
        self.assertEqual(item["type"], "f")
        self.assertEqual(item["size"], 2312)
        self.assertEqual(item["header"], "origin=local")
        self.assertEqual(item["mime"], "text/html")
        self.assertEqual(item["mtime"], "2014/03/01 12:15:10")
        self.assertEqual(item["ctime"], "2014/03/01 12:15:10")

    def test_getItem_failure(self):
        # getItem not found
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        item = self.storage.getItem(name="image.jpg")
        self.assertFalse(item)

        # empty name
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.getItem, name="")

    def test_getItem_codes(self):
        # code 400
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.getItem, name="")

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.getItem, name="test")

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.getItem, name="test")

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.getItem, name="test")


    def test_newItem(self):
        # newItem: name, type=None, contents=None, mime=None, header=None
        r = adapter.StoredResponse(service="mystorage",
                                   method="@newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": 1},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result, m, i = self.storage.newItem(name="index.html")
        self.assertEqual(result, 1)

        result, m, i = self.storage.newItem(name="index.html", type="file", contents="Hello!", mime="text/html", header="origin=local")
        self.assertEqual(result, 1)

    def test_newItem_failure(self):
        # newItem not found
        r = adapter.StoredResponse(service="mystorage",
                                   method="@newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":0},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        r, m, i = self.storage.newItem(name="")
        self.assertFalse(r)

        # empty name
        r = adapter.StoredResponse(service="mystorage",
                                   method="@newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)

        self.assertRaises(endpoint.ClientFailure, self.storage.newItem, name="image.jpg", type="whatever", contents="Hello!", mime="text/html", header="origin=local")

    def test_newItem_codes(self):
        # code 400
        r = adapter.StoredResponse(service="mystorage",
                                   method="@newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.newItem, name="")

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="@newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.newItem, name="test")

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="@newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.newItem, name="test")

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="@newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.newItem, name="test")


    def test_setItem(self):
        # setItem: name, contents=None, mime=None, header=None
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": 1},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result, m, i = self.storage.setItem(name="index.html")
        self.assertEqual(result, 1)

        result, m, i = self.storage.setItem(name="index.html", contents="Hello!", mime="text/html", header="origin=local")
        self.assertEqual(result, 1)

    def test_setItem_failure(self):
        # setItem not found
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":0},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        r, m, i = self.storage.setItem(name="")
        self.assertFalse(r)

        # empty name
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)

        self.assertRaises(endpoint.ClientFailure, self.storage.setItem, name=None, contents="Hello!", mime="text/html", header="origin=local")

    def test_setItem_codes(self):
        # code 400
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.setItem, name="")

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.setItem, name="test")

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.setItem, name="test")

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.setItem, name="test")


    def test_removeItem(self):
        # removeItem: name, recursive=False
        r = adapter.StoredResponse(service="mystorage",
                                   method="@removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": 1},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result, m = self.storage.removeItem(name="index.html")
        self.assertEqual(result, 1)

        result, m = self.storage.removeItem(name="folder", recursive=True)
        self.assertEqual(result, 1)

    def test_removeItem_failure(self):
        # removeItem not found
        r = adapter.StoredResponse(service="mystorage",
                                   method="@removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":0},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        r, m = self.storage.removeItem(name="")
        self.assertFalse(r)

        # empty name
        r = adapter.StoredResponse(service="mystorage",
                                   method="@removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)

        self.assertRaises(endpoint.ClientFailure, self.storage.removeItem, name=None)

    def test_removeItem_codes(self):
        # code 400
        r = adapter.StoredResponse(service="mystorage",
                                   method="@removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.removeItem, name="")

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="@removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.removeItem, name="test")

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="@removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.removeItem, name="test")

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="@removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.removeItem, name="test")


    def test_read(self):
        # read: name
        r = adapter.StoredResponse(service="mystorage",
                                   method="@read",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": "Hello!",
                                      "headers": {"Content-Type":"text/html"}
                                   })
        self.storage.session.responses=(r,)

        item = self.storage.read(name="index.html")
        self.assertEqual(item, "Hello!")

    def test_read_failure(self):
        # not found
        r = adapter.StoredResponse(service="mystorage",
                                   method="@read",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.read, name="test")

        # empty name
        r = adapter.StoredResponse(service="mystorage",
                                   method="@read",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.read, name="")

    def test_read_codes(self):
        # code 400
        r = adapter.StoredResponse(service="mystorage",
                                   method="@read",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.read, name="")

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="@read",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.read, name="test")

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="@read",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.read, name="test")

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="@read",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.read, name="test")


    def test_write(self):
        # write: name, contents
        r = adapter.StoredResponse(service="mystorage",
                                   method="@write",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        r, i = self.storage.write(name="index.html", contents="Hello!")
        self.assertEqual(r, True)

    def test_write_failure(self):
        # empty contents
        r = adapter.StoredResponse(service="mystorage",
                                   method="@write",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.write, name="test", contents=None)

        # empty name
        r = adapter.StoredResponse(service="mystorage",
                                   method="@write",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.write, name="", contents="Hello!")

    def test_write_codes(self):
        # code 400
        r = adapter.StoredResponse(service="mystorage",
                                   method="@write",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.write, name="test", contents="test")

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="@write",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.write, name="test", contents="test")

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="@write",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.write, name="test", contents="test")

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="@write",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.write, name="test", contents="test")


    def test_move(self):
        # move: name, newpath
        r = adapter.StoredResponse(service="mystorage",
                                   method="@move",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        r, i = self.storage.move(name="index.html", newpath="another.html")
        self.assertEqual(r, True)

    def test_move_failure(self):
        # empty name
        r = adapter.StoredResponse(service="mystorage",
                                   method="@move",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.move, name="", newpath="another.html")

        # empty path
        r = adapter.StoredResponse(service="mystorage",
                                   method="@move",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.move, name="index.html", newpath=None)

    def test_move_codes(self):
        # code 400
        r = adapter.StoredResponse(service="mystorage",
                                   method="@move",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.move, name="test", newpath="another.html")

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="@move",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.move, name="test", newpath="another.html")

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="@move",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.move, name="test", newpath="another.html")

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="@move",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.move, name="test", newpath="another.html")


    def test_list(self):
        # list: name, type, sort, order, size, start
        r = adapter.StoredResponse(service="mystorage",
                                   method="@list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items":[
                                          {"name":"index.html", "type":"f", "size":2312, "mime":"text/html",
                                           "mtime":"2014/03/01 12:15:10", "ctime":"2014/03/01 12:15:10"},
                                          {"name":"image.jpg", "type":"f", "size":10234, "mime":"image/jpg",
                                           "mtime":"2014/03/01 14:18:21", "ctime":"2014/03/01 14:18:21"},
                                          {"name":"subfolder", "type":"d", "size":0, "mime":"",
                                           "mtime":"2014/03/03 12:00:00", "ctime":"2014/03/03 12:00:00"}
                                      ]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        items = self.storage.list()
        self.assert_(len(items)==3)
        self.assertEqual(items[0]["name"], "index.html")
        self.assertEqual(items[0]["type"], "f")
        self.assertEqual(items[0]["size"], 2312)
        self.assertEqual(items[0]["mime"], "text/html")
        self.assert_(items[0]["ctime"])
        self.assert_(items[0]["mtime"])
        self.assertEqual(items[2]["name"], "subfolder")
        self.assertEqual(items[2]["type"], "d")
        self.assertEqual(items[2]["size"], 0)
        self.assertEqual(items[2]["mime"], "")
        self.assert_(items[2]["ctime"])
        self.assert_(items[2]["mtime"])

        # list folder
        r = adapter.StoredResponse(service="mystorage",
                                   method="@list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items":[
                                          {"name":"index.html", "type":"f", "size":2312, "mime":"text/html",
                                           "mtime":"2014/03/01 12:15:10", "ctime":"2014/03/01 12:15:10"},
                                          {"name":"image.jpg", "type":"f", "size":10234, "mime":"image/jpg",
                                           "mtime":"2014/03/01 14:18:21", "ctime":"2014/03/01 14:18:21"},
                                          {"name":"subfolder", "type":"d", "size":0, "mime":"",
                                           "mtime":"2014/03/03 12:00:00", "ctime":"2014/03/03 12:00:00"}
                                      ]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        items = self.storage.list(name="/")
        self.assert_(len(items)==3)
        self.assertEqual(items[0]["name"], "index.html")
        self.assertEqual(items[0]["type"], "f")
        self.assertEqual(items[0]["size"], 2312)
        self.assertEqual(items[0]["mime"], "text/html")
        self.assert_(items[0]["ctime"])
        self.assert_(items[0]["mtime"])
        self.assertEqual(items[2]["name"], "subfolder")
        self.assertEqual(items[2]["type"], "d")
        self.assertEqual(items[2]["size"], 0)
        self.assertEqual(items[2]["mime"], "")
        self.assert_(items[2]["ctime"])
        self.assert_(items[2]["mtime"])

        # list folder
        r = adapter.StoredResponse(service="mystorage",
                                   method="@list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items":[
                                          {"name":"image2.jpg", "type":"f", "size":10234, "mime":"image/jpg",
                                           "mtime":"2014/03/01 14:18:21", "ctime":"2014/03/01 14:18:21"}
                                      ]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        items = self.storage.list(name="subfolder")
        self.assert_(items)
        self.assertEqual(items[0]["name"], "image2.jpg")

        # list types
        r = adapter.StoredResponse(service="mystorage",
                                   method="@list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items":[
                                          {"name":"subfolder", "type":"d", "size":0, "mime":"",
                                           "mtime":"2014/03/03 12:00:00", "ctime":"2014/03/03 12:00:00"}
                                      ]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        items = self.storage.list(name="/",filetype="d")
        self.assert_(len(items)==1)
        self.assertEqual(items[0]["name"], "subfolder")


    def test_list_failure(self):
        # if result empty
        r = adapter.StoredResponse(service="mystorage",
                                   method="@list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        items = self.storage.list()
        self.assertFalse(items)

        # if result none
        r = adapter.StoredResponse(service="mystorage",
                                   method="@list",
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
        r = adapter.StoredResponse(service="mystorage",
                                   method="@list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.list)

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="@list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.list)

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="@list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.list)

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="@list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.list)


    def test_allowed(self):
        # allowed: name, permission
        r = adapter.StoredResponse(service="mystorage",
                                   method="@allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"read": True, "write": False},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        p = self.storage.allowed(name="index.html", permission=("read","write"))
        self.assertEqual(p["read"], True)
        self.assertEqual(p["write"], False)

        r = adapter.StoredResponse(service="mystorage",
                                   method="@allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"read": True},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        p = self.storage.allowed(name="index.html", permission="read")
        self.assertEqual(p["read"], True)


    def test_allowed_failure(self):
        # empty name
        r = adapter.StoredResponse(service="mystorage",
                                   method="@allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.allowed, name="", permission="read")

        # empty permission
        r = adapter.StoredResponse(service="mystorage",
                                   method="@allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.allowed, name="index.html", permission=None)

    def test_allowed_codes(self):
        # code 400
        r = adapter.StoredResponse(service="mystorage",
                                   method="@allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.allowed, name="test", permission="read")

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="@allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.allowed, name="test", permission="read")

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="@allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.allowed, name="test", permission="read")

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="@allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.allowed, name="test", permission="read")


    def test_getPermissions(self):
        # getPermissions: name
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"read": ("sys:everyone",),
                                                  "write": ("mygroup","admins")},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        p = self.storage.getPermissions(name="index.html")
        self.assertEqual(len(p["read"]), 1)
        self.assertEqual(len(p["write"]), 2)

    def test_getPermissions_failure(self):
        # empty name
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.getPermissions, name="")

    def test_getPermissions_codes(self):
        # code 400
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.getPermissions, name="test")

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.getPermissions, name="test")

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.getPermissions, name="test")

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.getPermissions, name="test")


    def test_setPermissions(self):
        # setPermissions:  name, permission, group, action="allow"
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        r, i = self.storage.setPermissions(name="index.html",permissions=dict(permission="read",group="sys:everyone"))
        self.assertEqual(r, True)

        r, i = self.storage.setPermissions(name="index.html",permissions=[dict(permission="read",group="sys:everyone"),
                                                                          dict(permission="write",group="sys:everyone")])
        self.assertEqual(r, True)

        r, i = self.storage.setPermissions(name="index.html",permissions=dict(permission="write",group=("mygroup","admins")))
        self.assertEqual(r, True)

        r, i = self.storage.setPermissions(name="index.html",permissions=dict(permission="write",group=("mygroup","admins"),action="revoke"))
        self.assertEqual(r, True)

    def test_setPermissions_failure(self):
        # empty name
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.setPermissions, name="",permissions=dict(permission="write",group=("mygroup","admins")))

        # empty permission
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.setPermissions, name="index.html", permissions=dict(permission="",group=("mygroup","admins")))

        # empty group
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.setPermissions, name="index.html",permissions=dict(permission="write",group=None))


    def test_setPermissions_codes(self):
        # code 400
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.setPermissions, name="test",permissions=dict(permission="write",group=("mygroup","admins")))

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.setPermissions, name="test",permissions=dict(permission="write",group=("mygroup","admins")))

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.setPermissions, name="test",permissions=dict(permission="write",group=("mygroup","admins")))

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.setPermissions, name="test",permissions=dict(permission="write",group=("mygroup","admins")))


    def test_getOwner(self):
        # getOwner: name
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"owner": "user1"},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        o = self.storage.getOwner(name="index.html")
        self.assertEqual(o["owner"], "user1")

    def test_getOwner_failure(self):
        # empty name
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.getOwner, name="")

    def test_getOwner_codes(self):
        # code 400
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.getOwner, name="test")

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.getOwner, name="test")

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.getOwner, name="test")

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="@getOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.getOwner, name="test")


    def test_setOwner(self):
        # setOwner: name, owner
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        r, m = self.storage.setOwner(name="index.html", owner="user1")
        self.assertEqual(r, True)

    def test_setOwner_failure(self):
        # empty name
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.setOwner, name="", owner="user1")

        # empty owner
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.setOwner, name="index.html", owner=None)

    def test_setOwner_codes(self):
        # code 400
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.setOwner, name="test", owner="user1")

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.setOwner, name="test", owner="user1")

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.setOwner, name="test", owner="user1")

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="@setOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.setOwner, name="test", owner="user1")


    def test_ping(self):
        # ping:
        r = adapter.StoredResponse(service="mystorage",
                                   method="@ping",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": 1},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        r = self.storage.ping()
        self.assertEqual(r, 1)

