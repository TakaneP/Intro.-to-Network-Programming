#!/usr/bin/python3
import socket
import sys
import boto3
import os
import time
import hashlib

signature = "bing-xun-np-hw"
student = "0516305"
loginName = ""
bucketName = ""
objDir = "./obj/"

def action(receivedData, sendData, ID):
    global loginName, bucketName
    s3 = boto3.resource('s3')
    splitSend = sendData.split(" ")
    splitReceived = receivedData.split(" ")
    if receivedData == "Register successfully.":
        userName = hashlib.md5(splitSend[1].encode(encoding="UTF-8")).hexdigest()
        s3.create_bucket(Bucket=student+userName+signature)
    elif splitReceived[0] == "Welcome,":
        loginName = splitReceived[1][:-1]
        bucketName = student + hashlib.md5(loginName.encode(encoding="UTF-8")).hexdigest() + signature
    elif receivedData == "Create post successfully":
        contentBeg = sendData.find("--content")
        content = sendData[contentBeg + 10:]
        content += "\n    --\n    "
        fileName = "post-" + str(ID) + ".txt"
        with open(objDir + fileName, "w") as f:
            f.write(content)
        currentBucket = s3.Bucket(bucketName)
        currentBucket.upload_file(objDir + fileName, fileName)
        os.remove(objDir + fileName)
    elif sendData == "read" and receivedData != "Post does not exist.":
        titlePos = receivedData.find("Title")
        author = receivedData[13:titlePos-5]
        currentBucket = s3.Bucket(student + hashlib.md5(author.encode(encoding="UTF-8")).hexdigest() + signature)
        readPostName = "post-" + str(ID) + ".txt"
        targetObject = currentBucket.Object(readPostName)
        content = targetObject.get()['Body'].read().decode()
        content = content.replace("<br>","\n    ")
        printMes = ""
        for c in content:
            printMes += c
        printMes = printMes.rstrip()
        print(printMes + "\n% ", end = '')
    elif splitSend[0] == "delete-post" and receivedData == "Delete successfully.":
        currentBucket = s3.Bucket(bucketName)
        deletePostName = "post-" + splitSend[1] + ".txt"
        targetObject = currentBucket.Object(deletePostName)
        targetObject.delete()
    elif splitSend[0] == "update-post" and receivedData == "Update successfully." and splitSend[2] == "--content":
        currentBucket = s3.Bucket(bucketName)
        updatePostName = "post-" + splitSend[1] + ".txt"
        targetObject = currentBucket.Object(updatePostName)
        content = targetObject.get()['Body'].read().decode()
        oldContent = content[:content.find("--")]
        oldComment = content[content.find("--"):]
        newContent = sendData[sendData.find("--content")+10:] + "\n    "
        newContent += oldComment
        targetObject.delete()
        with open(objDir + updatePostName, "w") as f:
            f.write(newContent)
        currentBucket.upload_file(objDir + updatePostName, updatePostName)
        os.remove(objDir + updatePostName)
    elif splitSend[0] == "comment" and "Comment successfully." in receivedData:
        author = receivedData.split(".")[1]
        comment = sendData[sendData.find(splitSend[1])+len(splitSend[1])+1:]
        currentBucket = s3.Bucket(student + hashlib.md5(author.encode(encoding="UTF-8")).hexdigest() + signature)
        commentPostName = "post-" + splitSend[1] + ".txt"
        targetObject = currentBucket.Object(commentPostName)
        content = targetObject.get()['Body'].read().decode()
        content += loginName + ": " + comment + "\n    "
        targetObject.delete()
        with open(objDir + commentPostName, "w") as f:
            f.write(content)
        currentBucket.upload_file(objDir + commentPostName, commentPostName)
        os.remove(objDir + commentPostName)
    elif splitSend[0] == "mail-to" and "Sent successfully." in receivedData:
        contentBeg = sendData.find("--content")
        content = sendData[contentBeg + 10:]
        fileName = "mail-" + str(ID) + ".txt"
        with open(objDir + fileName, "w") as f:
            f.write(content)
        receiverBucketName = student + hashlib.md5(splitSend[1].encode(encoding="UTF-8")).hexdigest() + signature
        currentBucket = s3.Bucket(receiverBucketName)
        currentBucket.upload_file(objDir + fileName, fileName)
        os.remove(objDir + fileName)
    elif splitSend[0] == "retr-mail" and receivedData != "Please login first." and receivedData != "No such mail.":
        currentBucket = s3.Bucket(bucketName)
        readMailName = "mail-" + str(ID) + ".txt"
        targetObject = currentBucket.Object(readMailName)
        content = targetObject.get()['Body'].read().decode()
        content = content.replace("<br>","\n    ")
        printMes = ""
        for c in content:
            printMes += c
        print(printMes + "\n% ", end = '')
    elif splitSend[0] == "delete-mail" and receivedData != "Please login first." and receivedData != "No such mail.":
        currentBucket = s3.Bucket(bucketName)
        deleteMailName = "mail-" + str(ID) + ".txt"
        targetObject = currentBucket.Object(deleteMailName)
        targetObject.delete()

def main():
    if len(sys.argv) != 3:
        print("Usage ./server <server ip address> <port number>")
        exit()
    port = 7890
    ID = 0
    os.system("mkdir -p ./obj/")
    try:
        port = int(sys.argv[2])
    except:
        print("port number needs to be integers")
        exit()
    ip = sys.argv[1]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    receivedData = sock.recv(8192).decode("utf8").rstrip()
    print(receivedData + " ", end = '')
    while 1:
        sendData = input()
        if len(sendData) == 0:
            sendData = " "
        encoded = sendData.encode("utf8")
        sock.sendall(encoded)
        if sendData == "exit":
            break
        receivedData = sock.recv(8192).decode("utf8").rstrip()
        splitSend = sendData.split(" ")
        if "Create post successfully." in receivedData and splitSend[0] == "create-post":
            receivedData = receivedData[:-2]
            temp = receivedData.split(".") #Create post successfully. post-id
            ID = int(temp[1])
            print(temp[0] + ".\n% ", end = '')
            action(temp[0], sendData, ID)
        elif splitSend[0] == "read" and receivedData[:-2] != "Post does not exist.":
            print(receivedData[:-2], end = '')
            action(receivedData[:-2], splitSend[0], int(splitSend[1]))
        elif "Comment successfully." in receivedData and splitSend[0] == "comment":
            receivedData = receivedData[:-2]
            temp = receivedData.split(".")
            print(temp[0] + ".\n% ", end = '')
            action(receivedData, sendData, ID)
        elif "Sent successfully." in receivedData and splitSend[0] == "mail-to":
            receivedData = receivedData[:-2]
            temp = receivedData.split(".") #Sent successfully. mail-id
            ID = int(temp[1])
            print(temp[0] + ".\n% ", end = '')
            action(temp[0]+".", sendData, ID)
        elif splitSend[0] == "retr-mail" and receivedData[:-2] != "Please login first." and receivedData[:-2] != "No such mail.":
            receivedData = receivedData[:-2]
            temp = receivedData.split("--")
            ID = int(temp[1])
            print(temp[0] + "--\n    ", end = '')
            action(temp[0], sendData, ID)
        elif splitSend[0] == "delete-mail" and receivedData[:-2] != "Please login first." and receivedData[:-2] != "No such mail.":
            receivedData = receivedData[:-2]
            temp = receivedData.split(".")
            ID = int(temp[1])
            print(temp[0] + ".\n% ", end = '')
            action(temp[0], sendData, ID)
        else:
            print(receivedData + " ", end = '')
            action(receivedData[:-2], sendData, ID)
        time.sleep(0.5)
    sock.close()

if __name__ == "__main__":
    main()

