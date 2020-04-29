import json

END_CHARACTER = "\0"
TARGET_ENCODING = "utf-8"

class ClientMessage:

    def __init__(self, username="", hp=200, action=None, exit=False):
        self.username = username
        self.hp = hp
        self.action = action
        self.exit = exit

    def __str__(self):
        return "ClientMessage(username='{}', hp = '{}', action='{}', exit='{}')".format(self.username, self.hp, self.action, self.exit)

    def marshal(self):
        return (json.dumps(self.__dict__) + END_CHARACTER).encode(TARGET_ENCODING)

class ServerMessage:

    def __init__(self, hp, start=None, message=""):
        self.hp = hp
        self.start = start
        self.message = message

    def __str__(self):
        return "ServerMessage(hp='{}', start='{}', message='{}')".format(self.hp, self.start, self.message)

    def marshal(self):
        return (json.dumps(self.__dict__) + END_CHARACTER).encode(TARGET_ENCODING)