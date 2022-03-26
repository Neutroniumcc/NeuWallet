import sys
import pyqrcode
import png
from pyqrcode import QRCode
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
from PyQt5.QtGui import QPixmap
from web3 import Web3
from hashlib import sha256
from web3.middleware import geth_poa_middleware
import json
import webbrowser

#it will create account and store encrypted private and public keys

def create_account():
    global account
    account = w3.eth.account.create();
    with open('config.json', 'r+') as config:
        data = json.load(config)
        data["privatekey"] = account.privateKey.hex()
        data["address"] = account.address
        config.seek(0)
        config.write(json.dumps(data))
        config.truncate()


class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui",self)
        # check if there is no wallet , generate new one
        with open('config.json', 'r') as config:
	        json_load = json.load(config)
        if ( len(json_load['privatekey']) != 0 ):
            self.login.clicked.connect(self.gotologin)
        else:
            self.create.clicked.connect(self.gotocreate)

    def gotologin(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotocreate(self):
        create = CreateAccScreen()
        widget.addWidget(create)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login.ui",self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)

    def loginfunction(self):
        password = self.passwordfield.text()

        if ( len(password)==0 ):
            self.error.setText("Please input all fields.")          
        else:
            with open('config.json', 'r+') as config:
                data = json.load(config)
                if ( data["password"] == sha256((password).encode('utf-8')).hexdigest() ):
                    wallet = Mainwallet()
                    widget.addWidget(wallet)
                    widget.setCurrentIndex(widget.currentIndex()+1)
                else:
                    self.error.setText("Wrong password!")

class CreateAccScreen(QDialog):
    def __init__(self):
        super(CreateAccScreen, self).__init__()
        loadUi("createacc.ui",self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.signupfunction)

    def signupfunction(self):
        password = self.passwordfield.text()
        username = self.emailfield.text()

        if ( len(password) and len(username) != 0 ):
            with open('config.json', 'r+') as config:
                data = json.load(config)
                data["name"] = username
                data["password"] = sha256((password).encode('utf-8')).hexdigest()
                config.seek(0)
                config.write(json.dumps(data))
                config.truncate()
                create_account()

            wallet = Mainwallet()
            widget.addWidget(wallet)
            widget.setCurrentIndex(widget.currentIndex()+1)
         
        else:
            self.error.setText("Please input all fields!")


class Mainwallet(QDialog):
    def __init__(self):
        super(Mainwallet, self).__init__()
        loadUi("wallet.ui",self)
        self.setWindowTitle('Home - NeuWallet')
        self.btn_toggle_menu.clicked.connect(lambda: UIFunctions.toggleMenu(self, 220, True))
        self.send_button.clicked.connect(self.send)
        self.receive_button.clicked.connect(self.receive)
        self.setting_button.clicked.connect(self.setting)

    def send(self):
        send = Sending()
        widget.addWidget(send)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def receive(self):
        receive = Receiving()
        widget.addWidget(receive)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def setting(self):
        setting = Settings()
        widget.addWidget(setting)
        widget.setCurrentIndex(widget.currentIndex()+1)


class Sending(QDialog):
    def __init__(self):
        super(Sending, self).__init__()
        loadUi("send_transaction.ui",self)
        self.send_button.clicked.connect(self.send_transaction)
        

    def send_transaction(self):
        if (len(self.address.text()) and len(self.amount.text()) != 0):
            with open('config.json', 'r') as config:
                json_load = json.load(config)
            nonce = w3.eth.getTransactionCount(json_load['address'])

            tx = {
                'nonce': nonce,
                'to': self.address.text(),
                'value': w3.toWei( self.amount.text(),'ether'),
                'gas': 2000000,
                'gasPrice': w3.eth.gas_price
                }

            signed_tx = w3.eth.account.sign_transaction(tx,json_load['privatekey'])

            tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

            self.error.setText("Congratulation! your transaction was successful")

            webbrowser.open("https://testnet.coinex.net/tx/"+w3.toHex(tx_hash)) 
        else:
            self.error.setText("Please input all fields!")



class Receiving(QDialog):
    def __init__(self):
        super(Receiving, self).__init__()
        with open('config.json', 'r') as config:
            json_load = json.load(config)
        wallet_address = pyqrcode.create(json_load['address'])
        loadUi("receiving.ui",self)
        self.image.setPixmap(QPixmap(wallet_address.png('wallet_address.png',scale = 10)))
        self.Done.clicked.connect(self.done)

    def done(self):
        wallet = Mainwallet()
        widget.addWidget(wallet)
        widget.setCurrentIndex(widget.currentIndex()+1)



class Settings(QDialog):
    def __init__(self):
        super(Settings,self).__init__()
        with open('networks.json', 'r+') as config:
            json_load = json.load(config)     
        loadUi("setting.ui",self)



# Web3 provider configuration
with open('networks.json', 'r') as config:
	    json_load = json.load(config)
provider = Web3.HTTPProvider(json_load['rpc_node'])
w3 = Web3(provider)
w3.middleware_onion.inject(geth_poa_middleware, layer=0)



# it will make a transaction and sign it with private key    




def export():
    with open('config.json', 'r') as config:
	    json_load = json.load(config)
    print("Your privatekey is: "+json_load['privatekey'])
    print("Your address is: "+json_load['address'])
     

def get_balance():
    with open('config.json', 'r') as config:
	    json_load = json.load(config)
    balance = float(w3.eth.get_balance(json_load['address']))
    print(" \n Your balance is: " + str(w3.eth.get_balance(json_load['address'])) +" CET \n")

def networks():

    with open('networks.json', 'r+') as config:
        data = json.load(config)
        print("Current RPC node is: " + data["rpc_node"])
        data["rpc_node"] = input("Enter node RPC url: ")

def change_password():
    with open('config.json', 'r+') as config:
        data = json.load(config)
        password = sha256(input("Enter your new password: ").encode('utf-8')).hexdigest()
        data["password"] = password
        config.seek(0)
        config.write(json.dumps(data))
        config.truncate()
    print("\nYour password changed secessfully :) \n")




# main
app = QApplication(sys.argv)
welcome = WelcomeScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(800)
widget.setFixedWidth(1200)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Have Good Day :)")
