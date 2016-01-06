
import unittest
import json
import logging

from pynive_client import adapter
from pynive_client import endpoint
from pynive_client import kvstore


class kvstoreTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()

    def test_setup_empty(self):
        storage = kvstore.KvStore(service="mystorage")
        self.assertFalse(storage.options["domain"])
        self.assertFalse(storage.session)
        self.assert_(storage.options["service"]=="mystorage")
        self.assert_(storage.options["version"]==storage.default_version)

    def test_setup(self):
        storage = kvstore.KvStore(service="mystorage",domain="mydomain")
        self.assert_(storage.options["domain"]=="mydomain")
        self.assert_(storage.options["service"]=="mystorage")
        self.assert_(storage.options["version"]==storage.default_version)
        self.assertFalse(storage.session)

        storage = kvstore.KvStore(service="mystorage", domain="mydomain", version="api23")
        self.assert_(storage.options["domain"]=="mydomain")
        self.assert_(storage.options["service"]=="mystorage")
        self.assert_(storage.options["version"]=="api23")
        self.assertFalse(storage.session)

    def test_setup_fails(self):
        storage = kvstore.KvStore(service=None,domain="mydomain")
        self.assertRaises(endpoint.EndpointException, storage.call, "test", {}, {})

    def test_session(self):
        storage = kvstore.KvStore(service="mystorage", domain="mydomain", session=adapter.MockAdapter())
        self.assert_(storage.options["domain"]=="mydomain")
        self.assert_(storage.options["service"]=="mystorage")
        self.assert_(storage.session)


class kvstoreFunctionTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()
        session = adapter.MockAdapter()
        self.storage = kvstore.KvStore(service="mystorage", domain="mydomain", session=session)


    def test_getItemv1(self):
        # getItem
        r = adapter.StoredResponse.fromJson("""{
                "service": "mystorage",
                "method": "getItem",
                "httpmethod": "POST",
                "payload": {"key": "key1"},
                "response": {
                    "status_code": 200,
                    "headers": {"Content-Type":"application/json"},
                    "content": {"key":"key1", "value":"value1", "timestamp":1438351642.6136},
                    "validate": ["key", "value"]
                }}""")
        self.storage.session.responses=(r,)

        item = self.storage.getItem(**r.payload)
        adapter.AssertResult(item, r, self)


    def test_getItemv2(self):
        # getItem
        r = adapter.StoredResponse.fromJson("""{
                "service": "mystorage",
                "method": "getItem",
                "httpmethod": "POST",
                "payload": {"key": "key1"},
                "response": {
                    "status_code": 200,
                    "headers": {"Content-Type":"application/json"},
                    "content": ["key1", "value1", 1438351642.6136]
                }}""")
        self.storage.session.responses=(r,)

        item = self.storage.getItem(**r.payload)
        adapter.AssertResult(item, r, self)

    def test_getItem(self):
        # getItem
        r = adapter.StoredResponse(service="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"key":"key1", "value":"value1", "timestamp":1438351642.6136},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        item = self.storage.getItem(key="key1")
        self.assertEqual(item["key"], "key1")
        self.assertEqual(item["value"], "value1")

    def test_getItem_failure(self):
        # getItem not found
        r = adapter.StoredResponse(service="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        item = self.storage.getItem(key="key1")
        self.assertFalse(item)

        # empty key
        r = adapter.StoredResponse(service="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 422,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.InvalidParameter, self.storage.getItem, key="")

    def test_getItem_codes(self):
        # code 422
        r = adapter.StoredResponse(service="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 422,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.InvalidParameter, self.storage.getItem, key="")

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.getItem, key="test")

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.getItem, key="test")

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.getItem, key="test")


    def test_list(self):
        # list key
        r = adapter.StoredResponse(service="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items":[
                                          {"key":"key1", "value":"value1", "timestamp": 1438351642.6136}
                                      ], "start":1, "size":1, "total":1},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result = self.storage.list(key="key1")
        self.assert_(result["items"])
        self.assertEqual(result["size"], 1)
        self.assertEqual(result["start"], 1)
        self.assertEqual(result["total"], 1)

        # list all
        r = adapter.StoredResponse(service="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items":[
                                          {"key":"key1", "value":"value1", "timestamp": 1438351642.6136},
                                          {"key":"key2", "value":"value2", "timestamp": 1438351643.6136},
                                          {"key":"key3", "value":"value3", "timestamp": 1438351644.6136},
                                      ], "start":1, "size":3, "total":3},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result = self.storage.list()
        self.assert_(result["items"])
        self.assertEqual(result["size"], 3)
        self.assertEqual(result["start"], 1)
        self.assertEqual(result["total"], 3)

        # list keys
        r = adapter.StoredResponse(service="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items":[
                                          {"key":"key1", "value":"value1", "timestamp": 1438351642.6136},
                                          {"key":"key2", "value":"value2", "timestamp": 1438351643.6136},
                                          {"key":"key3", "value":"value3", "timestamp": 1438351644.6136},
                                      ], "start":1, "size":3, "total":3},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result = self.storage.list(key=("key1","key2","key3"))
        self.assert_(result["items"])
        self.assertEqual(result["size"], 3)
        self.assertEqual(result["start"], 1)
        self.assertEqual(result["total"], 3)

        # batch
        r = adapter.StoredResponse(service="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items":[
                                          {"key":"key1", "value":"value1", "timestamp": 1438351642.6136},
                                          {"key":"key2", "value":"value2", "timestamp": 1438351643.6136}
                                      ], "start":1, "size":2, "total":3},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result = self.storage.list(size=2,start=1,order="<",sort="value",owner=False)
        self.assert_(result["items"])
        self.assertEqual(result["size"], 2)
        self.assertEqual(result["start"], 1)
        self.assertEqual(result["total"], 3)

        # owner
        r = adapter.StoredResponse(service="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items":[
                                          {"key":"key1", "value":"value1", "timestamp": 1438351642.6136},
                                          {"key":"key2", "value":"value2", "timestamp": 1438351643.6136}
                                      ], "start":1, "size":2, "total":2},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result = self.storage.list(owner=True)
        self.assert_(result["items"])
        self.assertEqual(result["size"], 2)
        self.assertEqual(result["start"], 1)
        self.assertEqual(result["total"], 2)

    def test_list_failure(self):
        # if result empty
        r = adapter.StoredResponse(service="mystorage",
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
        self.assertEqual(result["size"], 0)
        self.assertEqual(result["total"], 0)

        # if result none
        r = adapter.StoredResponse(service="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result = self.storage.list()
        self.assertFalse(result["items"])
        self.assertEqual(result["size"], 0)
        self.assertEqual(result["total"], 0)

    def test_list_codes(self):
        # code 422
        r = adapter.StoredResponse(service="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 422,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.InvalidParameter, self.storage.list)

        # code 403
        r = adapter.StoredResponse(service="mystorage",
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
        r = adapter.StoredResponse(service="mystorage",
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
        r = adapter.StoredResponse(service="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.list)



    def test_keys(self):
        # all
        r = adapter.StoredResponse(service="mystorage",
                                   method="keys",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"keys":["key1","key2"], "start":1, "size":2, "total":2},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result = self.storage.keys()
        self.assert_(result["keys"])
        self.assertEqual(result["size"], 2)
        self.assertEqual(result["start"], 1)
        self.assertEqual(result["total"], 2)

        # options
        r = adapter.StoredResponse(service="mystorage",
                                   method="keys",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"keys":["key1","key2"], "start":1, "size":2, "total":3},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result = self.storage.keys(size=2,start=1,order="<",owner=False)
        self.assert_(result["keys"])
        self.assertEqual(result["size"], 2)
        self.assertEqual(result["start"], 1)
        self.assertEqual(result["total"], 3)

        # owner
        r = adapter.StoredResponse(service="mystorage",
                                   method="keys",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"keys":["key1","key2"], "start":1, "size":2, "total":2},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result = self.storage.keys(owner=True)
        self.assert_(result["keys"])
        self.assertEqual(result["size"], 2)
        self.assertEqual(result["start"], 1)
        self.assertEqual(result["total"], 2)

    def test_keys_failure(self):
        # if result empty
        r = adapter.StoredResponse(service="mystorage",
                                   method="keys",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result = self.storage.keys()
        self.assertFalse(result["keys"])
        self.assertEqual(result["size"], 0)
        self.assertEqual(result["total"], 0)

        # if result none
        r = adapter.StoredResponse(service="mystorage",
                                   method="keys",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result = self.storage.keys()
        self.assertFalse(result["keys"])
        self.assertEqual(result["size"], 0)
        self.assertEqual(result["total"], 0)

    def test_keys_codes(self):
        # code 422
        r = adapter.StoredResponse(service="mystorage",
                                   method="keys",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 422,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.InvalidParameter, self.storage.keys)

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="keys",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.keys)

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="keys",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.keys)

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="keys",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.keys)



    def test_newItem(self):
        # single item
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success": ("key1",)},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result, keys = self.storage.newItem({"key":"key1", "value":"value1"})
        self.assert_(result==1)
        self.assert_(len(keys)==1)
        self.assert_(keys[0]=="key1")

        # multiple items
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":2, "success": ("key1","key2")},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result, keys = self.storage.newItem(({"key":"key1", "value":"value1"},{"key":"key2", "value":"value2"}))
        self.assert_(result==2)
        self.assert_(len(keys)==2)

        # multiple items partial write
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success": ("key1",)},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result, keys = self.storage.newItem(({"key":"key1", "value":"value1"},{"key":"key2", "value":"value2"}))
        self.assert_(result==1)
        self.assert_(len(keys)==1)

    def test_newItem_failure(self):
       # empty item
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 422,
                                      "content": {"result":0, "success": ()},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        self.assertRaises(endpoint.InvalidParameter, self.storage.newItem, {})

        # invalid item
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 422,
                                      "content": {"result":0, "success": ()},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        self.assertRaises(endpoint.InvalidParameter, self.storage.newItem, {"value":"value3"})

        # too many items
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 413,
                                      "content": {"result":0, "success": ()},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        self.assertRaises(endpoint.ClientFailure, self.storage.newItem, [{"key":"key1","value":"value3"}]*1000)

    def test_newItem_codes(self):
        # code 422
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 422,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.InvalidParameter, self.storage.newItem, ("key1","value1"))

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.newItem, ("key1","value1"))

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.newItem, ("key1","value1"))

        # code 413
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 413,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.newItem, ("key1","value1"))

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.newItem, ("key1","value1"))



    def test_setItem(self):
        # single item
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success": ("key1",)},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result, keys = self.storage.setItem({"key":"key1", "value":"value1"})
        self.assert_(result==1)
        self.assert_(len(keys)==1)
        self.assert_(keys[0]=="key1")

        # multiple items
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":2, "success": ("key1","key2")},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result, keys = self.storage.setItem(({"key":"key1", "value":"value1"},{"key":"key2", "value":"value2"}))
        self.assert_(result==2)
        self.assert_(len(keys)==2)

        # multiple items partial write
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success": ("key1",)},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result, keys = self.storage.setItem(({"key":"key1", "value":"value1"},{"key":"key2", "value":"value2"}))
        self.assert_(result==1)
        self.assert_(len(keys)==1)

    def test_setItem_failure(self):
       # empty item
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 422,
                                      "content": {"result":0, "success": ()},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        self.assertRaises(endpoint.InvalidParameter, self.storage.setItem, {})

        # invalid item
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 422,
                                      "content": {"result":0, "success": ()},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        self.assertRaises(endpoint.InvalidParameter, self.storage.setItem, {"value":"value3"})

        # too many items
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 413,
                                      "content": {"result":0, "success": ()},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        self.assertRaises(endpoint.ClientFailure, self.storage.setItem, [{"key":"key1","value":"value3"}]*1000)

    def test_setItem_codes(self):
        # code 422
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 422,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.InvalidParameter, self.storage.setItem, ("key1","value1"))

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.setItem, ("key1","value1"))

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.setItem, ("key1","value1"))

        # code 413
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 413,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.setItem, ("key1","value1"))

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.setItem, ("key1","value1"))



    def test_removeItem(self):
        # single item
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success":("key1",)},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result, success = self.storage.removeItem(key="key1")
        self.assertEqual(result, 1)
        self.assertEqual(len(success), 1)

        # multiple items
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":2, "success":("key1","key2")},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result, success = self.storage.removeItem(key=("key1","key2"))
        self.assertEqual(result, 2)
        self.assertEqual(len(success), 2)

        # multiple items partial delete
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success":("key1",)},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result, success = self.storage.removeItem(key=("key1","key2"))
        self.assertEqual(result, 1)
        self.assertEqual(len(success), 1)

    def test_removeItem_failure(self):
        # empty key
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":0, "success":()},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result, success = self.storage.removeItem(key="")
        self.assertEqual(result, 0)
        self.assertEqual(len(success), 0)

        # none
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":0, "success":()},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.storage.session.responses=(r,)

        result, success = self.storage.removeItem()
        self.assertEqual(result, 0)
        self.assertEqual(len(success), 0)

    def test_removeItem_codes(self):
        # code 422
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 422,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.InvalidParameter, self.storage.removeItem, "key1")

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.storage.removeItem, "key1")

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.storage.removeItem, "key1")

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.storage.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.storage.removeItem, "key1")
