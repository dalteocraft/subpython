import zmq
import json
import time

class RemoteException(Exception):
    pass

class UnknownException(Exception):
    pass

class MappedRef(object):

    def __init__(self, client, refId, className):
        super(MappedRef, self).__init__()
        self._client = client
        self._refId = refId
        self._className = className
    
    def __getattr__(self, key):
        cmd = {
            "command": "getattr",
            "name": key,
            "fromRef": self._refId,
        }
        response = self._client.spSendCommand(cmd)
        if response["status"] != "success":
            print(response)
            if "exception" in response:
                if response["exception"]["class"] == "AttributeError":
                    raise AttributeError(*response["exception"]["args"])
                else:
                    raise RemoteException(response["exception"]["class"], *response["exception"]["args"])
            else:
                raise UnknownException(response["message"])
        return self._client.spGetMappedRef(response["value"])
    
    def __getitem__(self, key):
        response = self._client.spSendCommand({
            "command": "getitem",
            "fromRef": self._refId,
            "name": key,
        })
        value = response["value"]
        if isinstance(value, dict) and value.get("isRef", False):
            value = self._client.spGetMappedRef(value)
        return value
    
    def __setitem__(self, key, value):
        response = self._client.spSendCommand({
            "command": "setitem",
            "fromRef": self._refId,
            "name": key,
            "value": self._client.spSerializeValue(value)
        })
    
    def __call__(self, *args, **kwargs):
        cmd = {
            "command": "call",
            "fromRef": self._refId,
        }
        response = self._client.spSendCommand(cmd)
        print(response)
        value = response["value"]
        if isinstance(value, dict) and value.get("isRef", False):
            value = self._client.spGetMappedRef(value)
        return value


class Client(object):

    def __init__(self, endpoint):
        super(Client, self).__init__()
        self.endpoint = endpoint
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.endpoint)
    
    def spDisconnect(self):
        self.socket.close()
    
    def spSend(self, message):
        t1 = time.time()
        self.socket.send_string(message)
        while True:
            event = self.socket.poll(200)
            if event != 0:
                msg = self.socket.recv_multipart()
                return msg
            t2 = time.time()
            if t2 - t1 > 3:
                print("Timeout")
                break
    
    def spSendCommand(self, command):
        message = json.dumps(command)
        response = self.spSend(message)
        return json.loads(response[0])
    
    def spSerializeValue(self, value):
        if isinstance(value, MappedRef):
            return {"isRef": True, "refId": value._refId, "class": value._className}
        else:
            if isinstance(value, (bool, int, float, str)):
                return value
            else:
                return {"isJson": True, "data": json.dumps(value)}
    
    def __getattr__(self, key):
        cmd = {
            "command": "getGlobal",
            "name": key,
        }
        response = self.spSendCommand(cmd)
        if response["status"] != "success":
            if response["exception"]["class"] == "AttributeError":
                raise AttributeError(*response["exception"]["args"])
        return self.spGetMappedRef(response["value"])
    
    def spGetMappedRef(self, refDict):
        ref = MappedRef(self, refDict["refId"], refDict["class"])
        return ref
    
    def spImportModule(self, name, fromlist=None):
        if fromlist is None:
            fromlist = []
        cmd = {
            "command": "importModule",
            "name": name,
            "fromlist": fromlist,
        }
        response = self.spSendCommand(cmd)
        print(response)
    

