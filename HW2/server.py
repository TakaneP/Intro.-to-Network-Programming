#!/usr/bin/python3
import socket
import sqlite3
import sys
import traceback
import time
from threading import Thread

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

def create_board(inputString, currentUser):
    splitCommand = inputString.split(' ')
    boardName = splitCommand[-1]

    dbConnection, dbCursor = connect_db()
    try:
        dbCursor.execute("INSERT INTO BOARDS (Boardname,Moderator) VALUES(?,?)",(boardName,currentUser))
        close_db(dbConnection)
        return 1
    except:
        close_db(dbConnection)
        return 0

def create_post(inputString, currentUser):
    splitCommand = inputString.split(' ')
    date = time.strftime("%Y-%m-%d", time.localtime())
    boardName = splitCommand[1]
    titleBeg = inputString.find("--title")
    contentBeg = inputString.find("--content")
    title = inputString[titleBeg + 8:contentBeg]
    content = inputString[contentBeg + 10:]

    dbConnection, dbCursor = connect_db()
    dbCursor.execute("SELECT Boardname FROM BOARDS WHERE Boardname = ?",(boardName,))
    result = dbCursor.fetchall()
    if len(result) == 0:
        close_db(dbConnection)
        return 0
    dbCursor.execute("INSERT INTO POSTS (Title, Board, Content, Author, Date) VALUES(?,?,?,?,?)",(title, boardName, content, currentUser, date))
    close_db(dbConnection)
    return 1

def get_max_board(result):
    maxL = 0
    for t in result:
        for i in range(1,len(t)):
            maxL = max(maxL,len(t[i]))
    return maxL

def get_max_post(result):
    maxL = 0
    for t in result:
        for i in range(1,len(t)):
            if i == 1 or i == 4:
                maxL = max(maxL,len(t[i]))
    return maxL

def list_board():
    dbConnection, dbCursor = connect_db()
    dbCursor.execute("SELECT * FROM BOARDS")
    result = dbCursor.fetchall()
    close_db(dbConnection)
    return result

def list_post(boardName):
    dbConnection, dbCursor = connect_db()
    dbCursor.execute("SELECT Boardname FROM BOARDS WHERE Boardname = ?",(boardName,))
    result = dbCursor.fetchall()
    if len(result) == 0:
        close_db(dbConnection)
        return 0,result

    dbCursor.execute("SELECT * FROM POSTS WHERE Board = ?",(boardName,))
    result = dbCursor.fetchall()
    close_db(dbConnection)
    return 1,result

def read(postId):
    try:
        test = int(postId)
    except:
        return 2,[]
    ID = int(postId)
    dbConnection, dbCursor = connect_db()
    dbCursor.execute("SELECT * FROM POSTS WHERE PID = ?",(ID,))
    result = dbCursor.fetchall()
    if len(result) == 0:
        close_db(dbConnection)
        return 0,result
    close_db(dbConnection)
    return 1,result

def get_comment(postId):
    dbConnection, dbCursor = connect_db()
    dbCursor.execute("SELECT * FROM COMMENTS WHERE Postid = ?",(postId,))
    result = dbCursor.fetchall()
    close_db(dbConnection)
    return result

def delete_post(postId, currentUser):
    try:
        test = int(postId)
    except:
        return -1
    ID = int(postId)
    dbConnection, dbCursor = connect_db()
    dbCursor.execute("SELECT * FROM POSTS WHERE PID = ?",(ID,))
    result = dbCursor.fetchall()
    if len(result) == 0: 
        close_db(dbConnection)
        return 0
    if result[0][-2] != currentUser: 
        close_db(dbConnection)
        return 1
    dbCursor.execute("DELETE FROM POSTS WHERE PID = ?",(ID,))
    close_db(dbConnection)
    return 2

def update_post(inputString, currentUser):
    splitCommand = inputString.split(" ")
    try:
        test = int(splitCommand[1])
    except:
        return -1
    ID = int(splitCommand[1])
    dbConnection, dbCursor = connect_db()
    dbCursor.execute("SELECT * FROM POSTS WHERE PID = ?",(ID,))
    result = dbCursor.fetchall()
    if len(result) == 0:
        close_db(dbConnection)
        return 0
    if result[0][-2] != currentUser:
        close_db(dbConnection)
        return 1
    if splitCommand[2] == "--title":
        newTitle = inputString[inputString.find("--title")+8:]
        dbCursor.execute("UPDATE POSTS SET Title = ? WHERE PID = ?",(newTitle,ID))
    elif splitCommand[2] == "--content":
        newContent = inputString[inputString.find("--content")+10:]
        dbCursor.execute("UPDATE POSTS SET Content = ? WHERE PID = ?",(newContent,ID))
    close_db(dbConnection)
    return 2
        
def comments(inputString, currentUser):
    splitCommand = inputString.split(" ")
    try:
        test = int(splitCommand[1])
    except:
        return -1
    ID = int(splitCommand[1])
    dbConnection, dbCursor = connect_db()
    dbCursor.execute("SELECT * FROM POSTS WHERE PID = ?",(ID,))
    result = dbCursor.fetchall()
    if len(result) == 0:
        close_db(dbConnection)
        return 0
    content = inputString[inputString.find(splitCommand[1])+len(splitCommand[1])+1:]
    dbCursor.execute("INSERT INTO COMMENTS (User,Postid,Content) VALUES(?,?,?)",(currentUser,ID,content))
    close_db(dbConnection)
    return 1

def client_thread(connection, ip, port, buffer_size = 8192):
    dbConnection = sqlite3.connect("BBS.db")
    dbCursor = dbConnection.cursor()
    
    loginState = False
    loginName = ""

    welcomeString = "********************************\n** Welcome to the BBS server. **\n********************************\n% "
    sendString = welcomeString.encode("utf8")
    connection.sendall(sendString)
    while 1:
        sendMessage = ""
        receivedDataBinary = connection.recv(buffer_size)
        receivedData = receivedDataBinary.decode("utf8").rstrip()
        command = receivedData.split(' ')
        #print(receivedData)
        if command[0] == "exit":
            if len(command) != 1:
                sendMessage = "Usage exit"
            else:
                break
        elif command[0] == "register":
            if len(command) != 4:
                sendMessage = "Usage register <username> <email> <password>"
            else:
                state = register(receivedData)
                if state == 0:
                    sendMessage = "Username is already used."
                else:
                    sendMessage = "Register successfully."
        elif command[0] == "login":
            if loginState == True:
                sendMessage = "Please logout first."
            elif len(command) != 3:
                sendMessage = "Usage login <username> <password>"
            else:
                state = login(receivedData)
                if state == 0:
                    sendMessage = "Login failed."
                else:
                    loginState = True
                    loginName = str(command[1])
                    sendMessage = "Welcome, " + loginName + "."
        elif command[0] == "logout":
            if len(command) != 1:
                sendMessage = "Usage logout"
            elif loginState == False:
                sendMessage = "Please login first."
            else:
                sendMessage = "Bye, " + loginName + "."
                loginState = False
                loginName = ""
        elif command[0] == "whoami":
            if len(command) != 1:
                sendMessage = "Usage whoami"
            elif loginState == False:
                sendMessage = "Please login first."
            else:
                sendMessage = loginName
        elif command[0] == "create-board":
            if loginState == False:
                sendMessage = "Please login first."
            elif len(command) != 2:
                sendMessage = "Usage create-board <name>"
            else:
                state = create_board(receivedData,loginName)
                if state:
                    sendMessage = "Create board successfully."
                else:
                    sendMessage = "Board already exist."
        elif command[0] == "create-post":
            if loginState == False:
                sendMessage = "Please login first."
            elif len(command) < 6 or command[2] != "--title" or "--content" not in command or command[3] == "--content" or receivedData.find("--content") + 9 == len(receivedData):
                sendMessage = "Usage create-post <board-name> --title <title> --content <content>"
            else:
                state = create_post(receivedData, loginName)
                if state:
                    sendMessage = "Create post successfully."
                else:
                    sendMessage = "Board does not exist."
        elif command[0] == "list-board":
            if len(command) > 1 and command[1][:2] != "##":
                sendMessage = "Usage list-board ##<key>"
            else:
                para = ""
                if len(command) > 1: para += receivedData[13:]
                result = list_board()
                maxL = max(10,get_max_board(result) + 5)
                sendMessage = f"    {'Index':<9}{'Name':<{maxL}}{'Moderator'}\n"
                for ele in result:
                    if para == "" or ele[1].find(para) != -1:
                        sendMessage += f"    {ele[0]:<9}{ele[1]:<{maxL}}{ele[2]}\n"
                sendMessage = sendMessage.rstrip()
        elif command[0] == "list-post":
            if len(command) < 2 or (len(command) > 2 and command[2][:2] != "##"):
                sendMessage = "Usage list-post <board-name> ##<key>"
            else:
                para = ""
                if len(command) > 2: para += receivedData[receivedData.find("##")+2:]
                state, result = list_post(command[1])
                if state:
                    maxL = max(10,get_max_post(result) + 5)
                    sendMessage = f"    {'ID':<7}{'Title':<{maxL}}{'Author':<{maxL}}{'Date'}\n"
                    for ele in result:
                        if para == "" or ele[1].find(para) != -1:
                            dateS = ele[5].split("-")
                            dateO = dateS[-2] + "/" + dateS[-1]
                            sendMessage += f"    {ele[0]:<7}{ele[1]:<{maxL}}{ele[4]:<{maxL}}{dateO}\n"
                    sendMessage = sendMessage.rstrip()
                else:
                    sendMessage = "Board does not exist."
        elif command[0] == "read":
            if len(command) != 2:
                sendMessage = "Usage read <post-id>"
            else:
                state,result = read(command[1])
                if state == 2:
                    sendMessage = "Usage read <post-id>"
                elif state == 1:
                    comment = get_comment(int(command[1]))
                    content = result[0][3].replace("<br>","\n    ")
                    sendMessage += f"    {'Author':<8}:{result[0][-2]}\n"
                    sendMessage += f"    {'Title':<8}:{result[0][1]}\n"
                    sendMessage += f"    {'Date':<8}:{result[0][-1]}\n    --\n    "
                    for c in content:
                        sendMessage += c
                    sendMessage += "\n    --\n    "
                    for ele in comment:
                        sendMessage += ele[1] + ": " + ele[3] + "\n    "
                    sendMessage = sendMessage.rstrip()
                else:
                    sendMessage = "Post does not exist."
        elif command[0] == "delete-post":
            if loginState == False:
                sendMessage = "Please login first."
            elif len(command) != 2:
                sendMessage = "Usage delete-post <post-id>"
            else:
                state = delete_post(command[1],loginName)
                if state == -1: sendMessage = "Usage delete-post <post-id>"
                elif state == 0: sendMessage = "Post does not exist."
                elif state == 1: sendMessage = "Not the post owner."
                else: sendMessage = "Delete successfully."
        elif command[0] == "update-post":
            if loginState == False:
                sendMessage = "Please login first."
            elif len(command) < 4 or (command[2] != "--title" and command[2] != "--content"):
                sendMessage = "Usage update-post <post-id> --title/content <new>"
            else:
                state = update_post(receivedData, loginName)
                if state == -1:
                    sendMessage = "Usage update-post <post-id> --title/content <new>"
                elif state == 0:
                    sendMessage = "Post does not exist."
                elif state == 1:
                    sendMessage = "Not the post owner."
                else:
                    sendMessage = "Update successfully."
        elif command[0] == "comment":
            if loginState == False:
                sendMessage = "Please login first."
            elif len(command) < 3:
                sendMessage = "Usage comment <post-id> <comment>"
            else:
                state = comments(receivedData,loginName)
                if state == -1:
                    sendMessage = "Usage comment <post-id> <comment>"
                elif state == 0:
                    sendMessage = "Post does not exist."
                else:
                    sendMessage = "Comment successfully."
        else:
            sendMessage = "Command Not Found"
        sendMessage += "\n% "
        encodedString = sendMessage.encode("utf8")
        connection.sendall(encodedString)

    #print("Child connection ends")
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
    dbCursor.execute("CREATE TABLE IF NOT EXISTS BOARDS(BID INTEGER PRIMARY KEY AUTOINCREMENT, Boardname TEXT NOT NULL UNIQUE, Moderator TEXT NOT NULL)")
    dbCursor.execute("CREATE TABLE IF NOT EXISTS POSTS(PID INTEGER PRIMARY KEY AUTOINCREMENT, Title TEXT NOT NULL, Board TEXT NOT NULL, Content TEXT NOT NULL, Author TEXT NOT NULL, Date TEXT NOT NULL)")
    dbCursor.execute("CREATE TABLE IF NOT EXISTS COMMENTS(CID INTEGER PRIMARY KEY AUTOINCREMENT, User TEXT NOT NULL, Postid INTEGER NOT NULL, Content TEXT NOT NULL)")
    close_db(dbConnection)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #print("Server socket created")

    try:
        sock.bind(("127.0.0.1", port))
        #print("Socket bind successfully")
    except:
        print("Bind Error: " + str(sys.exc_info()))
        sys.exit()

    sock.listen(20)
    #print("Socket is listening")

    while 1:
        connection, address = sock.accept()
        ip = address[0]
        port = address[1]
        #print("Accept conection from " + str(ip) + ": " + str(port))
        print("New connection.")
        try:
            Thread(target = client_thread, args = (connection, ip, port)).start()
        except:
            print("Thread creation error")
            traceback.print_exc()

    sock.close()

if __name__ == "__main__":
    main()
