from subpython import Runner
import unittest

class TestRunner(unittest.TestCase):

    def test_getGlobal(self):
        runner = Runner()
        rep = runner.processCommand({
            "command": "getGlobal",
            "name": "dict",
        })
        self.assertEqual(rep["status"], "success")
        self.assertEqual(rep["value"]["isRef"], True)
        self.assertEqual(rep["value"]["class"], "type")
        self.assertEqual(isinstance(rep["value"]["refId"], int), True)
    
    def test_getattr(self):
        runner = Runner()
        rep = runner.processCommand({
            "command": "getGlobal",
            "name": "dict",
        })

        print(rep)

        dict_rep = runner.processCommand({
            "command": "call",
            "fromRef": rep["value"]["refId"],
        })


        update_rep = runner.processCommand({
            "command": "getattr",
            "name": "update",
            "fromRef": dict_rep["value"]["refId"],
        })

        self.assertEqual(update_rep["status"], "success")
        self.assertEqual(update_rep["value"]["isRef"], True)
        self.assertEqual(update_rep["value"]["class"], "builtin_function_or_method")
        self.assertEqual(isinstance(update_rep["value"]["refId"], int), True)


    
    def test_call(self):
        runner = Runner()
        rep = runner.processCommand({
            "command": "getGlobal",
            "name": "dict",
        })
        d_rep = runner.processCommand({
            "command": "call",
            "fromRef": rep["value"]["refId"],
        })
        self.assertEqual(d_rep["status"], "success")
        self.assertEqual(d_rep["value"]["isRef"], True)
        self.assertEqual(d_rep["value"]["class"], "dict")
        self.assertEqual(isinstance(d_rep["value"]["refId"], int), True)
    

    def test_import(self):
        runner = Runner()
        rep = runner.processCommand({
            "command": "importModule",
            "name": "os.path",
        })

        self.assertEqual(rep["status"], "success")

        rep = runner.processCommand({
            "command": "importModule",
            "name": "pprint",
            "fromlist": {"pretty": "pprint"},
        })

        self.assertEqual(rep["status"], "success")
