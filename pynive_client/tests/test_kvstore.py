
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
        storage = kvstore.KvStore(service="mystorage", domain="mydomain")
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
        storage = kvstore.KvStore(service=None, domain="mydomain")
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
        self.service = kvstore.KvStore(service="mystorage", domain="mydomain", session=session)


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
                    "content": {"items":[{"key":"key1", "value":"value1", "timestamp":1438351642.6136}]},
                    "validate": ["items"]
                }}""")
        self.service.session.responses=(r,)

        result = self.service.getItem(key="key1")
        adapter.AssertResult(result, r, self)

    def test_getItemv2(self):
        # getItem
        r = adapter.StoredResponse.fromJson("""{
                "service": "mystorage",
                "method": "getItem",
                "httpmethod": "POST",
                "payload": {"key": ["key1","key2"], "owner": "me"},
                "response": {
                    "status_code": 200,
                    "headers": {"Content-Type":"application/json"},
                    "content": {"items":[{"key":"key1", "value":"value1", "timestamp":1438351642.6136},
                                         {"key":"key2", "value":"value2", "timestamp":1438351642.6136}]},
                    "validate": ["items"]
                }}""")
        self.service.session.responses=(r,)

        result = self.service.getItem(key=["key1","key2"], owner="me")
        adapter.AssertResult(result, r, self)

    def test_getItemv3(self):
        # getItem
        r = adapter.StoredResponse(service="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items": [{"key":"key1", "value":"value1", "timestamp":1438351642.6136}]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.getItem(id=123)
        item = result.items[0]
        self.assertEqual(item["key"], "key1")
        self.assertEqual(item["value"], "value1")

    def test_getItemv4(self):
        # getItem
        r = adapter.StoredResponse(service="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items": [{"key":"key1", "value":"value1", "timestamp":1438351642.6136},
                                                            {"key":"key2", "value":"value2", "timestamp":1438351642.6136}]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.getItem(id=[123,124])
        item = result.items[0]
        self.assertEqual(item["key"], "key1")
        self.assertEqual(item["value"], "value1")



    def test_newItemv1(self):
        # single item
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success": (("key1",123,1438351642.6136,1),)},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.newItem(key="key1", value="value1")
        self.assert_(result)
        self.assert_(len(result.success)==1)
        self.assert_(result.success[0][0]=="key1")

    def test_newItemv2(self):
        # single item
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success": (("key1",123,1438351642.6136,1),)},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.newItem(key="key1", value="value1", owner="you")
        self.assert_(result)
        self.assert_(len(result.success)==1)
        self.assert_(result.success[0][0]=="key1")

    def test_newItemv3(self):
        # single item
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success": (("key1",123,1438351642.6136,1),)},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.newItem(items={"key":"key1", "value":"value1"})
        self.assert_(result)
        self.assert_(len(result.success)==1)
        self.assert_(result.success[0][0]=="key1")

    def test_newItemv4(self):
        # multiple items
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":2, "success": (("key1",123,1438351642.6136,1),
                                                                          ("key2",124,1438351642.6136,1))},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.newItem(items=({"key":"key1", "value":"value1", "owner": "you"},
                                             {"key":"key2", "value":"value2", "owner": "you"}))
        self.assert_(result==2)
        self.assert_(len(result.success)==2)

        # multiple items partial write
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success": ("key1",)},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.newItem(({"key":"key1", "value":"value1"},{"key":"key2", "value":"value2"}))
        self.assert_(result==1)
        self.assert_(len(result.success)==1)



    def test_setItemv1(self):
        # single item
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success": [("key1",1438351642.6136,1)]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.setItem(key="key1", value="value1")
        self.assert_(result)
        self.assert_(len(result.success)==1)
        self.assert_(result.success[0][0]=="key1")

    def test_setItemv2(self):
        # multiple items
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success": [("key1",1438351642.6136,1)]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.setItem(key="key1", value="value1", owner="you")
        self.assert_(result)
        self.assert_(len(result.success)==1)

    def test_setItemv3(self):
        # multiple items
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success": [(123,1438351642.6136,1)]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.setItem(key="key1", value="value1", id=123)
        self.assert_(result)
        self.assert_(len(result.success)==1)

    def test_setItemv4(self):
        # single item
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success": [("key1",1438351642.6136,1)]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.setItem(items={"key":"key1", "value":"value1", "owner": "you"})
        self.assert_(result)
        self.assert_(len(result.success)==1)

    def test_setItemv5(self):
        # multiple items
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":2, "success": [("key1",1438351642.6136,1),
                                                                          ("key2",1438351642.6136,2)]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.setItem(items=({"key":"key1", "value":"value1"},{"key":"key2", "value":"value2"}))
        self.assert_(result)
        self.assert_(len(result.success)==2)

    def test_setItemv6(self):
        # single item
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success": [(123,1438351642.6136,1)]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.setItem(items={"key":"key1", "value":"value1", "id": 123})
        self.assert_(result)
        self.assert_(len(result.success)==1)



    def test_removeItemv1(self):
        # single item
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success":("key1",)},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.removeItem(key="key1")
        self.assert_(result)
        self.assertEqual(len(result.success), 1)

    def test_removeItemv2(self):
        # single item
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success":("key1",)},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.removeItem(key="key1", owner="you")
        self.assert_(result)
        self.assertEqual(len(result.success), 1)

    def test_removeItemv3(self):
        # multiple items
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success":[123]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.removeItem(id=123)
        self.assert_(result)
        self.assertEqual(len(result.success), 1)

    def test_removeItemv4(self):
        # multiple items partial delete
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":1, "success":("key1",)},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.removeItem(items={"key": "key1", "owner": "you"})
        self.assert_(result)
        self.assertEqual(len(result.success), 1)

    def test_removeItemv5(self):
        # multiple items partial delete
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":2, "success":("key1","key2")},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.removeItem(items=[{"key": "key1", "owner": "you"}, {"key": "key2", "owner": "me"}])
        self.assert_(result)
        self.assertEqual(len(result.success), 2)

    def test_removeItemv6(self):
        # multiple items partial delete
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":2, "success":(123, 124)},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.removeItem(items=[{"id": 123}, {"id": 124}])
        self.assert_(result)
        self.assertEqual(len(result.success), 2)



    def test_listv1(self):
        # list all
        r = adapter.StoredResponse(service="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items":[
                                          {"key":"key1", "value":"value1", "owner": "me", "timestamp": 1438351642.6136},
                                          {"key":"key2", "value":"value2", "owner": "me", "timestamp": 1438351643.6136},
                                          {"key":"key3", "value":"value3", "owner": "me", "timestamp": 1438351644.6136},
                                      ], "start":1, "size":3},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.list()
        self.assert_(result["items"])
        self.assertEqual(result["size"], 3)
        self.assertEqual(result["start"], 1)

    def test_listv2(self):
        # list key
        r = adapter.StoredResponse(service="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items":[
                                          {"key":"key1", "value":"value1", "owner": "me", "timestamp": 1438351642.6136}
                                      ], "start":1, "size":1},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.list(key="key1")
        self.assert_(result["items"])
        self.assertEqual(result["size"], 1)
        self.assertEqual(result["start"], 1)

    def test_listv3(self):
        # list keys
        r = adapter.StoredResponse(service="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items":[
                                          {"key":"key1", "value":"value1", "owner": "me", "timestamp": 1438351642.6136},
                                          {"key":"key2", "value":"value2", "owner": "me", "timestamp": 1438351643.6136},
                                          {"key":"key3", "value":"value3", "owner": "me", "timestamp": 1438351644.6136},
                                      ], "start":1, "size":3},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.list(key=("key1","key2","key3"))
        self.assert_(result["items"])
        self.assertEqual(result["size"], 3)
        self.assertEqual(result["start"], 1)

    def test_listv4(self):
        # batch
        r = adapter.StoredResponse(service="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items":[
                                          {"key":"key1", "value":"value1", "owner": "me", "timestamp": 1438351642.6136},
                                          {"key":"key2", "value":"value2", "owner": "me", "timestamp": 1438351643.6136}
                                      ], "start":1, "size":2},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.list(size=2,start=1,order="<",sort="value",owner="me")
        self.assert_(result["items"])
        self.assertEqual(result["size"], 2)
        self.assertEqual(result["start"], 1)

    def test_listv5(self):
        # owner
        r = adapter.StoredResponse(service="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items":[
                                          {"key":"key1", "value":"value1", "owner": "you", "timestamp": 1438351642.6136},
                                          {"key":"key2", "value":"value2", "owner": "you", "timestamp": 1438351643.6136}
                                      ], "start":1, "size":2},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.list(owner="you")
        self.assert_(result["items"])
        self.assertEqual(result["size"], 2)
        self.assertEqual(result["start"], 1)



    def test_keysv1(self):
        # all
        r = adapter.StoredResponse(service="mystorage",
                                   method="keys",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"keys":["key1","key2"], "start":1, "size":2},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.keys()
        self.assert_(result["keys"])
        self.assertEqual(result["size"], 2)
        self.assertEqual(result["start"], 1)

    def test_keysv2(self):
        # options
        r = adapter.StoredResponse(service="mystorage",
                                   method="keys",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"keys":["key1","key2"], "start":1, "size":2},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.keys(size=2,start=1,order="<",owner="me")
        self.assert_(result["keys"])
        self.assertEqual(result["size"], 2)
        self.assertEqual(result["start"], 1)

    def test_keysv3(self):
        # owner
        r = adapter.StoredResponse(service="mystorage",
                                   method="keys",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"keys":["key1","key2"], "start":1, "size":2},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.keys(owner="you")
        self.assert_(result["keys"])
        self.assertEqual(result["size"], 2)
        self.assertEqual(result["start"], 1)



    def test_allowedv1(self):
        # allowed: name, permission
        r = adapter.StoredResponse(service="mystorage",
                                   method="allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"getItem": True, "setItem": False},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        p = self.service.allowed(permissions=("getItem","setItem"))
        self.assertEqual(p.get("getItem"), True)
        self.assertEqual(p.setItem, False)

    def test_allowedv2(self):
        r = adapter.StoredResponse(service="mystorage",
                                   method="allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"newItem": True},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        p = self.service.allowed(permissions="newItem")
        self.assertEqual(p.newItem, True)



    def test_getPermissionsv1(self):
        # getPermissions: name
        r = adapter.StoredResponse(service="mystorage",
                                   method="getPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"getItem": ("sys:everyone",),
                                                  "setItem": ("mygroup","admins")},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        p = self.service.getPermissions()
        self.assertEqual(len(p["getItem"]), 1)
        self.assertEqual(len(p["setItem"]), 2)



    def test_setPermissions(self):
        # setPermissions:  name, permission, group, action="allow"
        r = adapter.StoredResponse(service="mystorage",
                                   method="setPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": True},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        r = self.service.setPermissions(permissions=dict(permission="getItem",group="sys:everyone"))
        self.assertEqual(r, True)

        r = self.service.setPermissions(permissions=[dict(permission="getItem",group="sys:everyone"),
                                                     dict(permission="setItem",group="sys:everyone")])
        self.assertEqual(r, True)

        r = self.service.setPermissions(permissions=dict(permission="setItem",group=("mygroup","admins")))
        self.assertEqual(r, True)

        r = self.service.setPermissions(permissions=dict(permission="setItem",group=("mygroup","admins"),action="revoke"))
        self.assertEqual(r, True)



    def test_getOwnerv1(self):
        # getOwner: key
        r = adapter.StoredResponse(service="mystorage",
                                   method="getOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items": [{"key": "key1", "owner": "user1"}]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.getOwner(key="key1")
        self.assertEqual(result.items[0]["owner"], "user1")
        self.assertEqual(result.items[0]["key"], "key1")

    def test_getOwnerv2(self):
        # getOwner: multiple keys
        r = adapter.StoredResponse(service="mystorage",
                                   method="getOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items": [{"key": "key1", "owner": "user1"},
                                                            {"key": "key2", "owner": "user2"}]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.getOwner(key=("key1","key2"))
        self.assertEqual(result.items[0]["owner"], "user1")
        self.assertEqual(result.items[0]["key"], "key1")
        self.assertEqual(result.items[1]["owner"], "user2")
        self.assertEqual(result.items[1]["key"], "key2")

    def test_getOwnerv3(self):
        # getOwner: id
        r = adapter.StoredResponse(service="mystorage",
                                   method="getOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items": [{"id": 12, "key": "key1", "owner": "user1"}]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.getOwner(id=12)
        self.assertEqual(result.items[0]["owner"], "user1")
        self.assertEqual(result.items[0]["key"], "key1")
        self.assertEqual(result.items[0]["id"], 12)

    def test_getOwnerv4(self):
        # getOwner: multiple ids
        r = adapter.StoredResponse(service="mystorage",
                                   method="getOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"items": [{"id": 12, "key": "key1", "owner": "user1"},
                                                            {"id": 16, "key": "key2", "owner": "user2"}]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.getOwner(id=(12,16))
        self.assertEqual(result.items[0]["owner"], "user1")
        self.assertEqual(result.items[0]["key"], "key1")
        self.assertEqual(result.items[0]["id"], 12)
        self.assertEqual(result.items[1]["owner"], "user2")
        self.assertEqual(result.items[1]["key"], "key2")
        self.assertEqual(result.items[1]["id"], 16)



    def test_setOwnerv1(self):
        # setOwner: key, owner
        r = adapter.StoredResponse(service="mystorage",
                                   method="setOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": 1, "success":[("key1",1438351643.6136,1)]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        r = self.service.setOwner(newOwner="me", key="key1")
        self.assert_(r)
        self.assert_(r.result)
        self.assert_(len(r.success)==1)
        self.assert_(r.success[0][0]=="key1")

    def test_setOwnerv2(self):
        # setOwner: multiple key, owner
        r = adapter.StoredResponse(service="mystorage",
                                   method="setOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": 2, "success":[("key1",1438351643.6136,1),
                                                                          ("key2",1438351643.6136,2)]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        r = self.service.setOwner(newOwner="me", items=(dict(key="key1", owner="user1"),
                                                        dict(key="key2", owner="user2")))
        self.assert_(r)
        self.assert_(r.result)
        self.assert_(len(r.success)==2)
        self.assert_(r.success[0][0]=="key1")
        self.assert_(r.success[1][0]=="key2")

    def test_setOwnerv3(self):
        # setOwner: id, owner
        r = adapter.StoredResponse(service="mystorage",
                                   method="setOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": 1, "success":[(123,1438351643.6136,1)]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        r = self.service.setOwner(newOwner="me", id=123)
        self.assert_(r)
        self.assert_(r.result)
        self.assert_(len(r.success)==1)
        self.assert_(r.success[0][0]==123)

    def test_setOwnerv4(self):
        # setOwner: multiple id, owner
        r = adapter.StoredResponse(service="mystorage",
                                   method="setOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": 2, "success":[(123,1438351643.6136,1),
                                                                          (124,1438351643.6136,2)]},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        r = self.service.setOwner(newOwner="me", items=(dict(id=123, owner="user1"),
                                                        dict(id=124, owner="user2")))
        self.assert_(r)
        self.assert_(r.result)
        self.assert_(len(r.success)==2)
        self.assert_(r.success[0][0]==123)
        self.assert_(r.success[1][0]==124)



    def test_ping(self):
        # ping:
        r = adapter.StoredResponse(service="mystorage",
                                   method="ping",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result": 1},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        r = self.service.ping()
        self.assertEqual(r, 1)




class kvstoreFailureTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()
        session = adapter.MockAdapter()
        self.service = kvstore.KvStore(service="mystorage", domain="mydomain", session=session)

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
        self.service.session.responses=(r,)

        result = self.service.getItem(key="key1")
        self.assertFalse(result.items)

        # empty key
        r = adapter.StoredResponse(service="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 422,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.InvalidParameter, self.service.getItem, key="")

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
        self.service.session.responses=(r,)

        self.assertRaises(endpoint.InvalidParameter, self.service.newItem, {})

        # invalid item
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 422,
                                      "content": {"result":0, "success": ()},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        self.assertRaises(endpoint.InvalidParameter, self.service.newItem, {"value":"value3"})

        # too many items
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 413,
                                      "content": {"result":0, "success": ()},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        self.assertRaises(endpoint.ServiceLimits, self.service.newItem, [{"key":"key1","value":"value3"}]*1000)

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
        self.service.session.responses=(r,)

        self.assertRaises(endpoint.InvalidParameter, self.service.setItem, {})

        # invalid item
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 422,
                                      "content": {"result":0, "success": ()},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        self.assertRaises(endpoint.InvalidParameter, self.service.setItem, {"value":"value3"})

        # too many items
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 413,
                                      "content": {"result":0, "success": ()},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        self.assertRaises(endpoint.ServiceLimits, self.service.setItem, [{"key":"key1","value":"value3"}]*1000)

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
        self.service.session.responses=(r,)

        result = self.service.removeItem(key="")
        self.assertFalse(result)
        self.assertEqual(len(result.success), 0)

        # none
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": {"result":0, "success":()},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.removeItem()
        self.assertFalse(result)
        self.assertEqual(len(result.success), 0)

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
        self.service.session.responses=(r,)

        result = self.service.list()
        self.assertFalse(result["items"])
        self.assertEqual(result["size"], 0)

        # if result none
        r = adapter.StoredResponse(service="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.list()
        self.assertFalse(result["items"])
        self.assertEqual(result["size"], 0)

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
        self.service.session.responses=(r,)

        result = self.service.keys()
        self.assertFalse(result["keys"])
        self.assertEqual(result["size"], 0)

        # if result none
        r = adapter.StoredResponse(service="mystorage",
                                   method="keys",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 200,
                                      "content": None,
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)

        result = self.service.keys()
        self.assertFalse(result["keys"])
        self.assertEqual(result["size"], 0)

    def test_allowed_failure(self):
        # empty name
        r = adapter.StoredResponse(service="mystorage",
                                   method="allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.service.allowed, permissions="getItem")

        # empty permission
        r = adapter.StoredResponse(service="mystorage",
                                   method="allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.service.allowed, permissions=None)

    def test_getPermissions_failure(self):
        # empty name
        r = adapter.StoredResponse(service="mystorage",
                                   method="getPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.service.getPermissions)

    def test_setPermissions_failure(self):
        # empty name
        r = adapter.StoredResponse(service="mystorage",
                                   method="setPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.service.setPermissions, permissions=dict(permission="setItem",group=("mygroup","admins")))

        # empty permission
        r = adapter.StoredResponse(service="mystorage",
                                   method="setPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.service.setPermissions, permissions=dict(permission="",group=("mygroup","admins")))

        # empty group
        r = adapter.StoredResponse(service="mystorage",
                                   method="setPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.service.setPermissions, permissions=dict(permission="setItem",group=None))

    def test_getOwner_failure(self):
        # empty name
        r = adapter.StoredResponse(service="mystorage",
                                   method="getOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.service.getOwner, key="key1")

    def test_setOwner_failure(self):
        # empty name
        r = adapter.StoredResponse(service="mystorage",
                                   method="setOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.service.setOwner, "me", items=dict(key="key1", owner="user1"))

        # empty owner
        r = adapter.StoredResponse(service="mystorage",
                                   method="setOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type":"application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.service.setOwner, "me", items=dict(key="test", owner=None))




class kvstoreCodesTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()
        session = adapter.MockAdapter()
        self.service = kvstore.KvStore(service="mystorage", domain="mydomain", session=session)

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
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.InvalidParameter, self.service.getItem, key="")

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.service.getItem, key="test")

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.service.getItem, key="test")

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="getItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.service.getItem, key="test")

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
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.InvalidParameter, self.service.newItem, ("key1","value1"))

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.service.newItem, ("key1","value1"))

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.service.newItem, ("key1","value1"))

        # code 413
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 413,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ServiceLimits, self.service.newItem, ("key1","value1"))

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="newItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.service.newItem, ("key1","value1"))

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
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.InvalidParameter, self.service.setItem, ("key1","value1"))

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.service.setItem, ("key1","value1"))

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.service.setItem, ("key1","value1"))

        # code 413
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 413,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ServiceLimits, self.service.setItem, ("key1","value1"))

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="setItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.service.setItem, ("key1","value1"))

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
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.InvalidParameter, self.service.removeItem, "key1")

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.service.removeItem, "key1")

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.service.removeItem, "key1")

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="removeItem",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.service.removeItem, "key1")


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
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.InvalidParameter, self.service.list)

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.service.list)

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.service.list)

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="list",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.service.list)

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
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.InvalidParameter, self.service.keys)

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="keys",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.service.keys)

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="keys",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.service.keys)

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="keys",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.service.keys)

    def test_allowed_codes(self):
        # code 400
        r = adapter.StoredResponse(service="mystorage",
                                   method="allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.service.allowed, permissions="getItem")

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.service.allowed, permissions="getItem")

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.service.allowed, permissions="getItem")

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="allowed",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.service.allowed, permissions="getItem")

    def test_getPermissions_codes(self):
        # code 400
        r = adapter.StoredResponse(service="mystorage",
                                   method="getPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.service.getPermissions)

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="getPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.service.getPermissions)

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="getPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.service.getPermissions)

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="getPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.service.getPermissions)

    def test_setPermissions_codes(self):
        # code 400
        r = adapter.StoredResponse(service="mystorage",
                                   method="setPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.service.setPermissions, permissions=dict(permission="setItem",group=("mygroup","admins")))

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="setPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.service.setPermissions, permissions=dict(permission="setItem",group=("mygroup","admins")))

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="setPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.service.setPermissions, permissions=dict(permission="setItem",group=("mygroup","admins")))

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="setPermissions",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.service.setPermissions, permissions=dict(permission="setItem",group=("mygroup","admins")))

    def test_getOwner_codes(self):
        # code 400
        r = adapter.StoredResponse(service="mystorage",
                                   method="getOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.service.getOwner, key="test")

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="getOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.service.getOwner, key="test")

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="getOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.service.getOwner, key="test")

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="getOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.service.getOwner, key="test")

    def test_setOwner_codes(self):
        # code 400
        r = adapter.StoredResponse(service="mystorage",
                                   method="setOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 400,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ClientFailure, self.service.setOwner, "me", items=dict(key="test", owner="user1"))

        # code 403
        r = adapter.StoredResponse(service="mystorage",
                                   method="setOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 403,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.Forbidden, self.service.setOwner, "me", items=dict(key="test", owner="user1"))

        # code 404
        r = adapter.StoredResponse(service="mystorage",
                                   method="setOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 404,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.NotFound, self.service.setOwner, "me", items=dict(key="test", owner="user1"))

        # code 500
        r = adapter.StoredResponse(service="mystorage",
                                   method="setOwner",
                                   httpmethod="POST",
                                   response={
                                      "status_code": 500,
                                      "content": {},
                                      "headers": {"Content-Type": "application/json"}
                                   })
        self.service.session.responses=(r,)
        self.assertRaises(endpoint.ServiceFailure, self.service.setOwner, "me", items=dict(key="test", owner="user1"))

