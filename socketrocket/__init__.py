import socket

class SocketLauncher:

    def __init__(self, host, port):
        self._conn = socket.socket()
        self._conn.connect((host,port))

    def home(self):
        self._conn.send("home\r\n")
        if self._conn.recv(1024)[0:2] != "OK":
            print "ERROR!!!! ERROR!!!!! Unable to home launcher!!!!"
            return False
        return True

    def left(self, ms):
        self._conn.send("left %d\r\n" % ms)
        if self._conn.recv(1024)[0:2] != "OK":
            print "ERROR!!!! ERROR!!!!! Unable to aim!!!!"
            return False
        return True

    def right(self, ms):
        self._conn.send("right %d\r\n" % ms)
        if self._conn.recv(1024)[0:2] != "OK":
            print "ERROR!!!! ERROR!!!!! Unable to aim!!!!"
            return False
        return True

    def up(self, ms):
        self._conn.send("up %d\r\n" % ms)
        if self._conn.recv(1024)[0:2] != "OK":
            print "ERROR!!!! ERROR!!!!! Unable to aim!!!!"
            return False
        return True

    def down(self, ms):
        self._conn.send("down %d\r\n" % ms)
        if self._conn.recv(1024)[0:2] != "OK":
            print "ERROR!!!! ERROR!!!!! Unable to aim!!!!"
            return False
        return True

    def fire(self, nrounds):
        self._conn.send("fire %d\r\n" % nrounds)
        if self._conn.recv(1024)[0:2] != "OK":
            print "ERROR!!!! ERROR!!!!! Unable to fire!!!!"
            return False
        return True
