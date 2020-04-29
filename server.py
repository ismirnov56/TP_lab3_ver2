import socket
import threading
import json
import gameplay
import sys
from gameplay import ClientMessage, ServerMessage


BUFFER_SIZE = 2**10

class Server:

    def __init__(self):
        self.clientMessages = []
        self.players = []
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 9096
        self.damage = 100

    def recv(self, player):
        buffer = ""
        while not buffer.endswith(gameplay.END_CHARACTER):
            buffer += player.recv(BUFFER_SIZE).decode(gameplay.TARGET_ENCODING)
        print(buffer)
        return buffer[:-1]

    def run(self):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((self.host, self.port))
        self.serversocket.listen(1)
        while True:
            try:
                player, addr = self.serversocket.accept()
            except Exception:
                print("No connect")
                return
            print(addr, " Подключился")
            if len(self.players) == 2:
                mess = ServerMessage(message="Два игрока уже в игре")
                player.sendall(mess)
                player.close()
                return
            self.players.append(player)
            threading.Thread(target=self.connect, args=(player, )).start()

    def connect(self, player):
        while True:
            try:
                message = ClientMessage(**json.loads(self.recv(player)))
                self.clientMessages.append(message)
            except Exception:
                print("Error")
                return
            if message.exit:
                player.close()
                self.players.remove(player)
                if len(self.players) == 1:
                    str = "Player: " + message.username + " disconnect, You WINNER"
                    messageServ = ServerMessage(hp=self.clientMessages[-2].hp, start=False, message=str)
                    message.true = True
                    self.players[0].sendall(messageServ.marshal())
                    self.serverClose()
                    return
                return
            self.broadcast(player)

    def broadcast(self, player):
        if len(self.players) == 1:
            mess = ServerMessage(hp=self.clientMessages[0].hp)
            print(mess.marshal())
            player.sendall(mess.marshal())
            return
        if len(self.clientMessages) % 2 != 0:
            return
        for pl in self.players:
            if pl != player:
                self.play(player, pl)

    def send(self, player1, player2, message1, message2):
        message1.message += "HP противника " + str(message2.hp) + "\n"
        message2.message += "HP противника " + str(message1.hp) + "\n"
        player1.sendall(message1.marshal())
        player2.sendall(message2.marshal())

    def move(self, message1, message2):
        if self.clientMessages[-1].action == 0 and self.clientMessages[-2].action == 0:
            message1.hp = message1.hp - self.damage
            message2.hp = message2.hp - self.damage
            return
        if self.clientMessages[-1].action == 0 and self.clientMessages[-2].action == 2:
            message2.hp = message2.hp - self.damage
            return
        if self.clientMessages[-1].action == 2 and self.clientMessages[-2].action == 0:
            message1.hp = message1.hp - self.damage
            return

    def play(self, player1, player2):
        str1 = "Player: " + self.clientMessages[-2].username + "\n"
        str2 = "Player: " + self.clientMessages[-1].username + "\n"
        message1 = ServerMessage(hp=self.clientMessages[-1].hp, start=True)
        message2 = ServerMessage(hp=self.clientMessages[-2].hp, start=True)
        if len(self.clientMessages) == 2:
            str1 += "Игра началась делайте ход\n"
            str2 += "Игра началась делайте ход\n"
            message1.message = str1
            message2.message = str2
            self.send(player1, player2, message1, message2)
            return
        self.move(message1, message2)
        if message1.hp <= 0 and message2.hp <= 0:
            str1 += "Ничья\n"
            str2 += "Ничья\n"
            message1.message = str1
            message2.message = str2
            message1.start = False
            message2.start = False
            self.send(player1, player2, message1, message2)
            self.serverClose()
            return
        if message1.hp <= 0:
            str1 += "Вы проиграли\n"
            str2 += "Вы победили\n"
            message1.message = str1
            message2.message = str2
            message1.start = False
            message1.start = False
            self.send(player1, player2, message1, message2)
            self.serverClose()
            return
        if message2.hp <= 0:
            str1 += "Вы победили\n"
            str2 += "Вы проиграли\n"
            message1.message = str1
            message2.message = str2
            message1.start = False
            message1.start = False
            self.send(player1, player2, message1, message2)
            self.serverClose()
            return
        message1.message = str1
        message2.message = str2
        self.send(player1, player2, message1, message2)

    def serverClose(self):
        for pl in self.players:
            pl.close()
        self.serversocket.close()
        sys.exit()

if __name__ == '__main__':
    Server().run()