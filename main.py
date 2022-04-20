import struct
import os
import numpy as np
import matplotlib.pyplot as plt

def unpackFile(filename):
    size = os.path.getsize(filename)
    mat = np.zeros((int(size/12),3))
    file = open(filename, "rb")
    nextBytes = file.read(4)
    xyz = 0
    num = 0
    while nextBytes:
        mat[num,xyz] += struct.unpack('f',nextBytes)
        xyz += 1
        if(xyz > 2):
            xyz = 0
            num += 1
        nextBytes = file.read(4)
    return mat

def removeGravity(mat):
    gravity = np.mean(mat[:10],axis=0)
    mat -= gravity

def getMagnitude(mat):
    return np.linalg.norm(mat,axis=1)

def normalise(mat, mag):
    return mat / mag.reshape(-1,1)

def findForward(norm, mag):
    for i in range(0,mag.shape[0]):
        if mag[i] > 0.5:
            return norm[i]

def integrate(accel):
    return np.trapz(accel,dx=1/104)

home = "C:\\Users\\Will\\Documents\\Year 3\\Project\\data"
commandList = """Commands:
    'list' - Lists the files in the home folder with a number assigned to each
    'accel <file number(s)>' - Displays the acceleration graph of the numbered file from the list, optionally list more file numbers to compare on the same graph
    'speed <file number(s)>' - Displays the speed graph of the numbered file from the list, optionally list more file numbers to compare on the same graph
    'home <directory>' - Change the home directory that files will be displayed from
    'help' - Display this list of commands
    'quit' - Exit the program"""

print(commandList)

def listCommand():
    return

def accelCommand(command):
    return

def speedCommand(command):
    return

def homeCommand(command):
    return

while True:
    print(">",end='')
    command = input().split(" ")
    if command[0] == "list":
        listCommand()
    elif command[0] == "accel":
        accelCommand(command)
    elif command[0] == "speed":
        speedCommand(command)
    elif command[0] == "home":
        homeCommand(command)
    elif command[0] == "help":
        print(commandList)
    elif command[0] == "quit":
        break
    else:
        print("Invalid command, use 'help' to see list of commands")
