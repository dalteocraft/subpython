import zmq
import json
from zmq.eventloop.zmqstream import ZMQStream
from tornado.ioloop import IOLoop

from .runner import Runner

class Server(object):

    def __init__(self, listen):
        super(Server, self).__init__()
        self.listen = listen
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.stream = ZMQStream(self.socket)
        self.runner = Runner()
    
    def start(self):
        print("Server starting")
        self.socket.bind(self.listen)
        self.stream.on_recv(self.on_recv)
        IOLoop.instance().start()
    
    def on_recv(self, msg):
        print("received !")
        command = json.loads(msg[0].decode("utf8"))
        reply = self.runner.processCommand(command)
        self.socket.send_string(json.dumps(reply))

    
    
        