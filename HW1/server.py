#!/usr/bin/python3
import socket
import sqlite3
import sys
import traceback
from threading import Thread

#Return state 1: successfully 0: exist -1: fail
def register(inputString):
    splitCommand = inputString.split(' ')
    userName = splitCommand[1]
    email = splitCommand[2]
    password = splitCommand[3]
    dbConnection, dbCursor = connect_db()
    try:
        dbCursor.execute("INSERT INTO USERS (Username,Email,Password) VALUES(?,?,?)",(userName,email,password))
        close_db(dbConnection)
        return 1
    except:
        close_db(dbConnection)
        return 0

def login(inputString):
    splitCommand = inputString.split(' ')
    userName = splitCommand[1]
    password = splitCommand[-1]
    
    dbConnection, dbCursor = connect_db()
    dbCursor.execute("SELECT Username, Password FROM USERS WHERE Username = ? AND Password = ?",(userName, password))
    result = dbCursor.fetchall()
    close_db(dbConnection)
    if len(result) == 0:
        return 0
    else:
        return 1

def client_thread(connection, ip, port, buffer_size = 8192):
    dbConnection = sqlite3.connect("BBS.db")
    dbCursor = dbConnection.cursor()
    
    loginState = False
    loginName = ""

    welcomeString = "********************************\n** Welcome to the BBS server. **\n********************************\n% "
    sendString = welcomeString.encode("utf8")
    connection.sendall(sendString)
    sendMessage = ""
    while 1:
        receivedDataBinary = connection.recv(buffer_size)#, socket.MSG_WAITALL)
        receivedData = receivedDataBinary.decode("utf8").rstrip()
        command = receivedData.split(' ')
        #print(receivedData)
        if command[0] == "exit":
            if len(command) != 1:
                sendMessage = "Usage exit\n% "
            else:
                break
        elif command[0] == "register":
            if len(command) != 4:
                sendMessage = "Usage register <username> <email> <password>\n% "
            else:
                state = register(receivedData)
                if state == 0:
                    sendMessage = "Username is already used.\n% "
                else:
                    sendMessage = "Register successfully.\n% "
        elif command[0] == "login":
            if loginState == True:
                sendMessage = "Please logout first.\n% "
            elif len(command) != 3:
                sendMessage = "Usage login <username> <password>\n% "
            else:
                state = login(receivedData)
                if state == 0:
                    sendMessage = "Login failed.\n% "
                else:
                    loginState = True
                    loginName = str(command[1])
                    sendMessage = "Welcome, " + loginName + ".\n% " 
        elif command[0] == "logout":
            if len(command) != 1:
                sendMessage = "Usage logout\n% "
            elif loginState == False:
                sendMessage = "Please login first.\n% "
            else:
                sendMessage = "Bye, " + loginName + ".\n% "
                loginState = False
                loginName = ""
        elif command[0] == "whoami":
            if len(command) != 1:
                sendMessage = "Usage whoami\n% "
            elif loginState == False:
                sendMessage = "Please login first.\n% "
            else:
                sendMessage = loginName + "\n% "
        else:
            sendMessage = "No correponding command\n% "
        encodedString = sendMessage.encode("utf8")
        connection.sendall(encodedString)

    print("Child connection ends")
    connection.close()

def connect_db():
    dbConnection = sqlite3.connect("BBS.db")
    dbCursor = dbConnection.cursor()
    return dbConnection,dbCursor

def close_db(dbConnection):
    dbConnection.commit()
    dbConnection.close()
    
def main():
    if len(sys.argv) != 2:
        print("Usage ./server <port number>")
        exit()
    port = 7890
    try:
        port = int(sys.argv[1])
    except:
        print("port number needs to be integers")
        exit()
    dbConnection,dbCursor = connect_db()
    dbCursor.execute("CREATE TABLE IF NOT EXISTS USERS(UID INTEGER PRIMARY KEY AUTOINCREMENT, Username TEXT NOT NULL UNIQUE, Email TEXT NOT NULL, Password TEXT NOT NULL)")
    close_db(dbConnection)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("Server socket created")

    try:
        sock.bind(("127.0.0.1", port))
        print("Socket bind successfully")
    except:
        print("Bind Error: " + str(sys.exc_info()))
        sys.exit()

    sock.listen(20)
    print("Socket is listening")

    while 1:
        connection, address = sock.accept()
        ip = address[0]
        port = address[1]
        print("Accept conection from " + str(ip) + ": " + str(port))
        try:
            Thread(target = client_thread, args = (connection, ip, port)).start()
        except:
            print("Thread creation error")
            traceback.print_exc()

    sock.close()

if __name__ == "__main__":
    main()
