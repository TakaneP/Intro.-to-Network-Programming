#!/usr/bin/python3
import socket
import sqlite3
import sys
import traceback
import time
from threading import Thread
import hashlib
def register(inputString):
    splitCommand = inputString.split(' ')
    userName = splitCommand[1]
    email = splitCommand[2]
    password = splitCommand[3]
    bucketName = "0516305" + hashlib.md5(userName.encode(encoding="UTF-8")).hexdigest() + "bing-xun-np-hw"
    dbConnection, dbCursor = connect_db()
    try:
        dbCursor.execute("INSERT INTO USERS (Username,Email,Password,Bucketname) VALUES(?,?,?,?)",(userName,email,password,bucketName))
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
        return 0,0
    dbCursor.execute("INSERT INTO POSTS (Title, Board, Author, Date) VALUES(?,?,?,?)",(title, boardName, currentUser, date))
    lastRowId = dbCursor.lastrowid
    close_db(dbConnection)
    return 1,lastRowId

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
            if i == 1 or i == 3:
                maxL = max(maxL,len(t[i]))
    return maxL

def get_max_mail(result):
    maxL = 0
    for t in result:
        for i in range(1,len(t)):
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

'''def get_comment(postId):
    dbConnection, dbCursor = connect_db()
    dbCursor.execute("SELECT * FROM COMMENTS WHERE Postid = ?",(postId,))
    result = dbCursor.fetchall()
    close_db(dbConnection)
    return result
'''
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
    #elif splitCommand[2] == "--content":
        #newContent = inputString[inputString.find("--content")+10:]
        #dbCursor.execute("UPDATE POSTS SET Content = ? WHERE PID = ?",(newContent,ID))'''
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
    author = ""
    if len(result) == 0:
        close_db(dbConnection)
        return 0,author
    content = inputString[inputString.find(splitCommand[1])+len(splitCommand[1])+1:]
    #dbCursor.execute("INSERT INTO COMMENTS (User,Postid,Content) VALUES(?,?,?)",(currentUser,ID,content))
    close_db(dbConnection)
    return 1, result[0][-2]

def mail_to(inputString, currentUser):
    splitCommand = inputString.split(' ')
    date = time.strftime("%Y-%m-%d", time.localtime())
    userName = splitCommand[1]
    subjectBeg = inputString.find("--subject")
    contentBeg = inputString.find("--content")
    subject = inputString[subjectBeg + 10:contentBeg]
    content = inputString[contentBeg + 10:]

    dbConnection, dbCursor = connect_db()
    dbCursor.execute("SELECT Username FROM USERS WHERE Username = ?",(userName,))
    result = dbCursor.fetchall()
    if len(result) == 0:
        close_db(dbConnection)
        return 0,0
    dbCursor.execute("INSERT INTO MAILS (Sender, Receiver, Subject, Date) VALUES(?,?,?,?)",(currentUser, userName, subject, date))
    lastRowId = dbCursor.lastrowid
    close_db(dbConnection)
    return 1,lastRowId

def list_mail(inputString, currentUser):
    dbConnection, dbCursor = connect_db()
    dbCursor.execute("SELECT * FROM MAILS WHERE Receiver = ?",(currentUser,))
    result = dbCursor.fetchall()
    close_db(dbConnection)
    return result

def delete_mail(mid):
    dbConnection, dbCursor = connect_db()
    dbCursor.execute("DELETE FROM MAILS WHERE MID = ?",(mid,))
    close_db(dbConnection)

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
                state, rowID = create_post(receivedData, loginName)
                if state:
                    sendMessage = "Create post successfully." + str(rowID)
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
                count = 0
                for ele in result:
                    if para == "" or ele[1].find(para) != -1:
                        count += 1
                        sendMessage += f"    {count:<9}{ele[1]:<{maxL}}{ele[2]}\n"
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
                            dateS = ele[4].split("-")
                            dateO = dateS[-2] + "/" + dateS[-1]
                            sendMessage += f"    {ele[0]:<7}{ele[1]:<{maxL}}{ele[3]:<{maxL}}{dateO}\n"
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
                    #comment = get_comment(int(command[1]))
                    #content = result[0][3].replace("<br>","\n    ")
                    sendMessage += f"    {'Author':<8}:{result[0][-2]}\n"
                    sendMessage += f"    {'Title':<8}:{result[0][1]}\n"
                    sendMessage += f"    {'Date':<8}:{result[0][-1]}\n    --\n    "
                    '''for c in content:
                        sendMessage += c
                    sendMessage += "\n    --\n    "
                    for ele in comment:
                        sendMessage += ele[1] + ": " + ele[3] + "\n    "'''
                    #sendMessage = sendMessage.rstrip()
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
                state, author = comments(receivedData,loginName)
                if state == -1:
                    sendMessage = "Usage comment <post-id> <comment>"
                elif state == 0:
                    sendMessage = "Post does not exist."
                else:
                    sendMessage = "Comment successfully." + author
        elif command[0] == "mail-to":
            if loginState == False:
                sendMessage = "Please login first."
            elif len(command) < 6 or command[2] != "--subject" or "--content" not in command or command[3] == "--content" or receivedData.find("--content") + 9 == len(receivedData):
                sendMessage = "Usage mail-to <username> --subject <subject> --content <content>"
            else:
                state, rowID = mail_to(receivedData, loginName)
                if state:
                    sendMessage = "Sent successfully." + str(rowID)
                else:
                    sendMessage = command[1] + " does not exist."
        elif command[0] == "list-mail":
            if loginState == False:
                sendMessage = "Please login first."
            elif len(command) != 1:
                sendMessage = "Usage list-mail"
            else:
                result = list_mail(receivedData, loginName)
                maxL = max(10,get_max_mail(result) + 5)
                sendMessage = f"    {'ID':<6}{'Subject':<{maxL}}{'From':<{maxL}}{'Date'}\n"
                count = 0
                for ele in result:
                    count += 1
                    dateS = ele[-1].split("-")
                    dateO = dateS[-2] + "/" + dateS[-1]
                    sendMessage += f"    {count:<6}{ele[-2]:<{maxL}}{ele[1]:<{maxL}}{dateO}\n"
                sendMessage = sendMessage.rstrip()
        elif command[0] == "retr-mail":
            if loginState == False:
                sendMessage = "Please login first."
            elif len(command) != 2 or command[1].isdigit() == False:
                sendMessage = "Usage retr-mail <mail#>"
            else:
                result = list_mail(receivedData, loginName)
                retrNum = int(command[1])
                if retrNum == 0 or retrNum > len(result):
                    sendMessage = "No such mail."
                else:
                    retrNum -= 1
                    sendMessage += f"    {'Subject':<8}:{result[retrNum][-2]}\n"
                    sendMessage += f"    {'From':<8}:{result[retrNum][1]}\n"
                    sendMessage += f"    {'Date':<8}:{result[retrNum][-1]}\n    --" + str(result[retrNum][0])
        elif command[0] == "delete-mail":
            if loginState == False:
                sendMessage = "Please login first."
            elif len(command) != 2 or command[1].isdigit() == False:
                sendMessage = "Usage delete-mail <mail#>"
            else:
                result = list_mail(receivedData, loginName)
                retrNum = int(command[1])
                if retrNum == 0 or retrNum > len(result):
                    sendMessage = "No such mail."
                else:
                    retrNum -= 1
                    delete_mail(int(result[retrNum][0]))
                    sendMessage = "Mail deleted." + str(result[retrNum][0])
        else:
            sendMessage = "Command Not Found"
        if len(receivedData) == 0:
            sendMessage = "%"
        else:
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
    dbCursor.execute("CREATE TABLE IF NOT EXISTS USERS(UID INTEGER PRIMARY KEY AUTOINCREMENT, Username TEXT NOT NULL UNIQUE, Email TEXT NOT NULL, Password TEXT NOT NULL, Bucketname TEXT NOT NULL)")
    dbCursor.execute("CREATE TABLE IF NOT EXISTS BOARDS(BID INTEGER PRIMARY KEY AUTOINCREMENT, Boardname TEXT NOT NULL UNIQUE, Moderator TEXT NOT NULL)")
    dbCursor.execute("CREATE TABLE IF NOT EXISTS POSTS(PID INTEGER PRIMARY KEY AUTOINCREMENT, Title TEXT NOT NULL, Board TEXT NOT NULL, Author TEXT NOT NULL, Date TEXT NOT NULL)")
    dbCursor.execute("CREATE TABLE IF NOT EXISTS MAILS(MID INTEGER PRIMARY KEY AUTOINCREMENT, Sender TEXT NOT NULL, Receiver TEXT NOT NULL, Subject TEXT NOT NULL, Date TEXT NOT NULL)")
    #dbCursor.execute("CREATE TABLE IF NOT EXISTS COMMENTS(CID INTEGER PRIMARY KEY AUTOINCREMENT, User TEXT NOT NULL, Postid INTEGER NOT NULL, Content TEXT NOT NULL)")
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
