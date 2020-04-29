from PyQt5 import QtWidgets
import sys
from PyQt5.Qt import QMessageBox
from gui import Ui_MainWindow
from gameplay import ClientMessage, ServerMessage
import socket
import threading
import json
import gameplay

BUFFER_SIZE = 2**10

class MainPlayerWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainPlayerWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.port = 9096
        self.host = socket.gethostbyname(socket.gethostname())
        self.message = None
        self.inputMessage = None
        self.energy = 100
        try:
            self.ui.pushButton.clicked.connect(self.moveGame)
        except Exception:
            print("Что-то полшло не так")

    def getEnergy(self):
        return "Ваша энергия " + str(self.energy) + "\n"

    def getHP(self):
        return "Ваша доровье " + str(self.message.hp) + "\n"

    def getIndex(self):
        if self.ui.comboBox.currentIndex() == 0:
            return -50
        if self.ui.comboBox.currentIndex() == 1:
            return -25
        if self.ui.comboBox.currentIndex() == 2:
            return 100

    def moveGame(self):
        if self.message == None:
            if self.ui.lineEdit.text() == "":
                self.ui.labelResult.setText("Введите username")
                return
            self.connectServer()
            self.ui.pushButton.setText("OK")
            return
        if self.inputMessage == None:
            self.ui.labelResult.setText("Дождитесь хода")
            return
        if self.inputMessage.start == False:
            self.ui.labelResult.setText("Игра закончилась!!!\n" + self.inputMessage.message)
            return
        if self.energy + self.getIndex() < 0:
            self.ui.labelResult.setText("Выберете другое\n" + self.getEnergy())
            return
        self.message.action = self.ui.comboBox.currentIndex()
        self.energy += self.getIndex()
        self.sendMessage()


    def connectServer(self):
        try:
            self.message = ClientMessage(username=self.ui.lineEdit.text())
            self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.clientsocket.connect((self.host, self.port))
            self.clientsocket.sendall(self.message.marshal())
        except Exception:
            print("No connect")
        self.ui.comboBox.addItem("Удар en: 50")
        self.ui.comboBox.addItem("Защита en: 25")
        self.ui.comboBox.addItem("Востановить энергию en: 100")
        self.receive_worker = threading.Thread(target=self.receive)
        self.receive_worker.start()

    def receive(self):
        while True:
            try:
                self.inputMessage = ServerMessage(**json.loads(self.receive_message()))
                print(self.inputMessage)
                self.message.hp = self.inputMessage.hp
                if self.inputMessage.start == None:
                    self.ui.labelResult.clear()
                    self.ui.labelResult.setText("Игра не началсь дождитесь подключения!!!")
                else:
                    self.ui.labelResult.clear()
                    self.ui.labelResult.setText(self.inputMessage.message + self.getHP() + self.getEnergy())
                if self.inputMessage.start == False:
                    self.exit()
                    return
            except Exception:
                print("Error work")
                return

    def receive_message(self):
        buffer = ""
        while not buffer.endswith(gameplay.END_CHARACTER):
            buffer += self.clientsocket.recv(BUFFER_SIZE).decode(gameplay.TARGET_ENCODING)
        print(buffer)
        return buffer[:-1]

    def sendMessage(self):
        try:
            self.inputMessage = None
            self.clientsocket.sendall(self.message.marshal())
            self.ui.labelResult.clear()
            self.ui.labelResult.setText("Ход сделан")
        except Exception:
            print("disconnect")
            self.exit()

    def exit(self):
        self.clientsocket.close()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Выход", "Вы действительно хотите выйти?",
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.inputMessage.start == None or self.inputMessage.start == False:
                event.accept()
            else:
                self.message.exit = True
                self.sendMessage()
                event.accept()
                self.exit()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    application = MainPlayerWindow()
    application.show()
    sys.exit(app.exec())