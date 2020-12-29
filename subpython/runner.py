import importlib

class RunnerRef(object):

    def __init__(self, obj):
        super(RunnerRef, self).__init__()
        self.obj = obj
        self.refcount = 0
    
    def incr(self):
        self.refcount += 1
    
    def decr(self):
        self.refcount -= 1

class Runner(object):

    def __init__(self):
        super(Runner, self).__init__()
        self.scope = {}
        self.runnerRefs = {}
    
    def execute(self, script):
        exec(script)
    
    def processCommand(self, command):
        try:
            return self._processCommand(command)
        except Exception as e:
            return {
                "status": "error",
                "message": "Runner Error",
                "exception": self.serializeValue(e),
            }
        finally:
            self.garbageCollect()
    
    def _processCommand(self, command):
        if command["command"] == "getGlobal":
            return self.processGetGlobal(command)
        elif command["command"] == "getattr":
            return self.processGetAttr(command)
        elif command["command"] == "getitem":
            return self.processGetItem(command)
        elif command["command"] == "setitem":
            return self.processSetItem(command)
        elif command["command"] == "call":
            return self.processCall(command)
        elif command["command"] == "importModule":
            return self.processImportModule(command)
        else:
            return {
                "status": "error",
                "message": "Invalid command %s" % repr(command["command"])
            }
    
    def processGetGlobal(self, command):
        name = command["name"]
        try:
            value = eval(name, globals(), self.scope)
            rep = {
                "status": "success",
                "value": self.serializeValue(value),
            }
        except NameError as e:
            rep = {
                "status": "error",
                "exception": self.serializeValue(e),
            }
        return rep
    
    def processGetAttr(self, command):
        name = command["name"]
        fromRef = command["fromRef"]
        ref = self.runnerRefs[fromRef]
        value = getattr(ref.obj, name)
        return {
            "status": "success",
            "value": self.serializeValue(value)
        }
    
    def processSetAttr(self, command):
        name = command["name"]
        fromRef = command["fromRef"]
        ref = self.runnerRefs[fromRef]
        value = self.deserializeValue(command["value"])
        setattr(ref.obj, name, value)
        return {
            "status": "success",
        }
    
    def processGetItem(self, command):
        name = command["name"]
        fromRef = command["fromRef"]
        ref = self.runnerRefs[fromRef]
        value = ref.obj[name]
        return {
            "status": "success",
            "value": self.serializeValue(value)
        }
    
    def processSetItem(self, command):
        name = command["name"]
        fromRef = command["fromRef"]
        ref = self.runnerRefs[fromRef]
        value = self.deserializeValue(command["value"])
        ref.obj[name] = value
        return {
            "status": "success",
        }
    
    def processCall(self, command):
        refId = command["fromRef"]
        ref = self.runnerRefs[refId]
        # TODO implement args and kwargs
        try:
            returnValue = ref.obj()
            return {
                "status": "success",
                "value": self.serializeValue(returnValue),
            }
        except Exception as e:
            return {
                "status": "error",
                "exception": self.serializeValue(e),
            }
    
    def processImportModule(self, command):
        fromlist = command.get("fromlist", [])
        if isinstance(fromlist, dict):
            mapping = dict(fromlist)
            fromlist = fromlist.values()
        else:
            mapping = dict((name, name) for name in fromlist)

        module = importlib.__import__(command["name"], fromlist=fromlist)
        if fromlist:
            for dest, source in mapping.items():
                self.scope[dest] = getattr(module, source)

        else:
            self.scope[module.__name__] = module
        if command["name"] == "pprint":
            print(module.pformat)
        return {
            "status": "success",
        }
    
    def deserializeValue(self, value):
        if isinstance(value, (bool, int, float, str)):
            return value
        else:
            raise NotImplementedError("")
    
    def serializeValue(self, value):
        if isinstance(value, (bool, int, float, str)):
            return value
        elif isinstance(value, Exception):
            return {"isException": True, "class": value.__class__.__name__, "args": value.args}
        else:
            refId = id(value)
            if refId not in self.runnerRefs:
                ref = RunnerRef(value)
                self.runnerRefs[refId] = ref
                ref.incr()
            else:
                ref = self.runnerRefs[refId]
            return {"isRef": True, "refId": refId, "class": ref.obj.__class__.__name__}
    
    def garbageCollect(self):
        to_delete = []
        for refId, ref in self.runnerRefs.items():
            if ref.refcount == 0:
                to_delete.append(refId)
        for refId in to_delete:
            del self.runnerRefs[refId]
