
import unittest
import logging
from StringIO import StringIO

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

        item = self.storage.getItem(path="index.html")
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

        item = self.storage.getItem(path="image.jpg")
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
        self.assertRaises(endpoint.ClientFailure, self.storage.getItem, path="")

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
        self.assertRaises(endpoint.ClientFailure, self.storage.getItem, path="")

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
        self.assertRaises(endpoint.Forbidden, self.storage.getItem, path="test")

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
        self.assertRaises(endpoint.NotFound, self.storage.getItem, path="test")

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
        self.assertRaises(endpoint.ServiceFailure, self.storage.getItem, path="test")


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

        result = self.storage.newItem(path="/", name="index.html")
        self.assertEqual(result, 1)

        result = self.storage.newItem(path="/", name="index.html", type="file", contents="Hello!", mime="text/html", header="origin=local")
        self.assertEqual(result, 1)

        result = self.storage.newItem("index.html", type="file", contents="Hello!", mime="text/html", header="origin=local")
        self.assertEqual(result, 1)

        result = self.storage.newItem("/index.html", type="file", contents="Hello!", mime="text/html", header="origin=local")
        self.assertEqual(result, 1)

        result = self.storage.newItem("/folder/index.html", type="file", contents="Hello!", mime="text/html", header="origin=local")
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

        r = self.storage.newItem(path="", name="")
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

        self.assertRaises(endpoint.ClientFailure, self.storage.newItem, path="/", name="image.jpg", type="whatever", contents="Hello!", mime="text/html", header="origin=local")

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
        self.assertRaises(endpoint.ClientFailure, self.storage.newItem, path="", name="")

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
        self.assertRaises(endpoint.Forbidden, self.storage.newItem, path="/", name="test")

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
        self.assertRaises(endpoint.NotFound, self.storage.newItem, path="/", name="test")

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
        self.assertRaises(endpoint.ServiceFailure, self.storage.newItem, path="/", name="test")


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

        result = self.storage.setItem(path="index.html")
        self.assertEqual(result, 1)

        result = self.storage.setItem(path="index.html", contents="Hello!", mime="text/html", header="origin=local")
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

        r = self.storage.setItem(path="")
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

        self.assertRaises(endpoint.ClientFailure, self.storage.setItem, path=None, contents="Hello!", mime="text/html", header="origin=local")

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
        self.assertRaises(endpoint.ClientFailure, self.storage.setItem, path="")

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
        self.assertRaises(endpoint.Forbidden, self.storage.setItem, path="test")

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
        self.assertRaises(endpoint.NotFound, self.storage.setItem, path="test")

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
        self.assertRaises(endpoint.ServiceFailure, self.storage.setItem, path="test")


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

        result = self.storage.removeItem(path="index.html")
        self.assertEqual(result, 1)

        result = self.storage.removeItem(path="folder", recursive=True)
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

        r = self.storage.removeItem(path="")
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

        self.assertRaises(endpoint.ClientFailure, self.storage.removeItem, path=None)

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
        self.assertRaises(endpoint.ClientFailure, self.storage.removeItem, path="")

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
        self.assertRaises(endpoint.Forbidden, self.storage.removeItem, path="test")

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
        self.assertRaises(endpoint.NotFound, self.storage.removeItem, path="test")

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
        self.assertRaises(endpoint.ServiceFailure, self.storage.removeItem, path="test")


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

        item = self.storage.read(path="index.html")
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
        self.assertRaises(endpoint.NotFound, self.storage.read, path="test")

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
        self.assertRaises(endpoint.ClientFailure, self.storage.read, path="")

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
        self.assertRaises(endpoint.ClientFailure, self.storage.read, path="")

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
        self.assertRaises(endpoint.Forbidden, self.storage.read, path="test")

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
        self.assertRaises(endpoint.NotFound, self.storage.read, path="test")

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
        self.assertRaises(endpoint.ServiceFailure, self.storage.read, path="test")


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

        r = self.storage.write(path="index.html", file=StringIO("Hello!"))
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
        self.assertRaises(endpoint.NotFound, self.storage.write, path="test", file=None)

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
        self.assertRaises(endpoint.ClientFailure, self.storage.write, path="", file=StringIO("Hello!"))

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
        self.assertRaises(endpoint.ClientFailure, self.storage.write, path="test", file=StringIO("test"))

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
        self.assertRaises(endpoint.Forbidden, self.storage.write, path="test", file="test")

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
        self.assertRaises(endpoint.NotFound, self.storage.write, path="test", file="test")

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
        self.assertRaises(endpoint.ServiceFailure, self.storage.write, path="test", file="test")


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

        r = self.storage.move(path="index.html", newpath="another.html")
        self.assert_(r)

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
        self.assertRaises(endpoint.NotFound, self.storage.move, path="", newpath="another.html")

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
        self.assertRaises(endpoint.ClientFailure, self.storage.move, path="index.html", newpath=None)

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
        self.assertRaises(endpoint.ClientFailure, self.storage.move, path="test", newpath="another.html")

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
        self.assertRaises(endpoint.Forbidden, self.storage.move, path="test", newpath="another.html")

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
        self.assertRaises(endpoint.NotFound, self.storage.move, path="test", newpath="another.html")

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
        self.assertRaises(endpoint.ServiceFailure, self.storage.move, path="test", newpath="another.html")


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

        items = self.storage.list(path="")
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

        items = self.storage.list(path="/")
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

        items = self.storage.list(path="subfolder")
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

        items = self.storage.list(path="/",type="d")
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

        items = self.storage.list(path="")
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

        result = self.storage.list(path="root")

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
        self.assertRaises(endpoint.ClientFailure, self.storage.list, "")

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
        self.assertRaises(endpoint.Forbidden, self.storage.list, "")

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
        self.assertRaises(endpoint.NotFound, self.storage.list, "")

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
        self.assertRaises(endpoint.ServiceFailure, self.storage.list, "")


    def test_allowed(self):
        # allowed: name, permission
        r = adapter.StoredResponse(service="mystorage",
                                   method="@allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":False, "permission": {"read": True, "write": False}},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        p = self.storage.allowed(path="index.html", permission=("read","write"))
        self.assertEqual(p.permission["read"], True)
        self.assertEqual(p.permission["write"], False)

        r = adapter.StoredResponse(service="mystorage",
                                   method="@allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":True, "permission": {"read": True}},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        p = self.storage.allowed(path="index.html", permission="read")
        self.assertEqual(p.permission["read"], True)


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
        self.assertRaises(endpoint.NotFound, self.storage.allowed, path="", permission="read")

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
        self.assertRaises(endpoint.ClientFailure, self.storage.allowed, path="index.html", permission=None)

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
        self.assertRaises(endpoint.ClientFailure, self.storage.allowed, path="test", permission="read")

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
        self.assertRaises(endpoint.Forbidden, self.storage.allowed, path="test", permission="read")

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
        self.assertRaises(endpoint.NotFound, self.storage.allowed, path="test", permission="read")

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
        self.assertRaises(endpoint.ServiceFailure, self.storage.allowed, path="test", permission="read")


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

        p = self.storage.getPermissions(path="index.html")
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
        self.assertRaises(endpoint.NotFound, self.storage.getPermissions, path="")

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
        self.assertRaises(endpoint.ClientFailure, self.storage.getPermissions, path="test")

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
        self.assertRaises(endpoint.Forbidden, self.storage.getPermissions, path="test")

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
        self.assertRaises(endpoint.NotFound, self.storage.getPermissions, path="test")

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
        self.assertRaises(endpoint.ServiceFailure, self.storage.getPermissions, path="test")


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

        r = self.storage.setPermissions(path="index.html",permissions=dict(permission="read",group="sys:everyone"))
        self.assertEqual(r, True)

        r = self.storage.setPermissions(path="index.html",permissions=[dict(permission="read",group="sys:everyone"),
                                                                          dict(permission="write",group="sys:everyone")])
        self.assertEqual(r, True)

        r = self.storage.setPermissions(path="index.html",permissions=dict(permission="write",group=("mygroup","admins")))
        self.assertEqual(r, True)

        r = self.storage.setPermissions(path="index.html",permissions=dict(permission="write",group=("mygroup","admins"),action="revoke"))
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
        self.assertRaises(endpoint.NotFound, self.storage.setPermissions, path="",permissions=dict(permission="write",group=("mygroup","admins")))

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
        self.assertRaises(endpoint.ClientFailure, self.storage.setPermissions, path="index.html", permissions=dict(permission="",group=("mygroup","admins")))

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
        self.assertRaises(endpoint.ClientFailure, self.storage.setPermissions, path="index.html",permissions=dict(permission="write",group=None))


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
        self.assertRaises(endpoint.ClientFailure, self.storage.setPermissions, path="test",permissions=dict(permission="write",group=("mygroup","admins")))

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
        self.assertRaises(endpoint.Forbidden, self.storage.setPermissions, path="test",permissions=dict(permission="write",group=("mygroup","admins")))

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
        self.assertRaises(endpoint.NotFound, self.storage.setPermissions, path="test",permissions=dict(permission="write",group=("mygroup","admins")))

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
        self.assertRaises(endpoint.ServiceFailure, self.storage.setPermissions, path="test",permissions=dict(permission="write",group=("mygroup","admins")))


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

        o = self.storage.getOwner(path="index.html")
        self.assertEqual(o, "user1")

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
        self.assertRaises(endpoint.NotFound, self.storage.getOwner, path="")

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
        self.assertRaises(endpoint.ClientFailure, self.storage.getOwner, path="test")

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
        self.assertRaises(endpoint.Forbidden, self.storage.getOwner, path="test")

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
        self.assertRaises(endpoint.NotFound, self.storage.getOwner, path="test")

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
        self.assertRaises(endpoint.ServiceFailure, self.storage.getOwner, path="test")


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

        r = self.storage.setOwner(path="index.html", owner="user1")
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
        self.assertRaises(endpoint.NotFound, self.storage.setOwner, path="", owner="user1")

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
        self.assertRaises(endpoint.ClientFailure, self.storage.setOwner, path="index.html", owner=None)

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
        self.assertRaises(endpoint.ClientFailure, self.storage.setOwner, path="test", owner="user1")

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
        self.assertRaises(endpoint.Forbidden, self.storage.setOwner, path="test", owner="user1")

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
        self.assertRaises(endpoint.NotFound, self.storage.setOwner, path="test", owner="user1")

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
        self.assertRaises(endpoint.ServiceFailure, self.storage.setOwner, path="test", owner="user1")


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

