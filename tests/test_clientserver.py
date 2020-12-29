from subpython import Client
import unittest
import subprocess
import time

class TestRunner(unittest.TestCase):

    def test_client(self):
        p = subprocess.Popen(["subpython", "run", "-E", "tcp://127.0.0.1:45555"], cwd="/", stderr=subprocess.STDOUT)
        time.sleep(2)
        try:
            client = Client("tcp://127.0.0.1:45555")
            client.spImportModule("os")
            cwd = client.os.getcwd()
            self.assertEqual(cwd, "/")
            data = client.dict()
            data["test"] = "Test"

            print(data)
            print(data["test"])

        finally:
            client.spDisconnect()
            p.kill()
        
        


