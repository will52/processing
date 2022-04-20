import struct
import os
from os import listdir
from os.path import isfile, join
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
    'accel <file number(s)>' -  Displays the acceleration graph of the numbered file from the list, 
                                optionally list more file numbers seperated by spaces to compare on the same graph
    'speed <file number(s)>' -  Displays the speed graph of the numbered file from the list, 
                                optionally list more file numbers seperated by spaces to compare on the same graph
    'home <directory>' - Change the home directory that files will be displayed from
    'rename <file number> <new name>' - Rename the numbered file from the list
    'help' - Display this list of commands
    'quit' - Exit the program
    """

print("Default home folder is",home)
print(commandList)

def listCommand():
    for i in range(0,len(files)):
        print(i+1,"-",files[i])

def renameCommand(command):
    global files
    if len(command) < 3:
        print("rename usage - 'rename <file number> <new name>'")
        return
    num = int(command[1])-1
    if num < 0 or num >= len(files):
        print("No file with that number")
        return
    os.rename(join(home,files[num]),join(home,command[2]+".DAT"))
    files = [f for f in listdir(home) if isfile(join(home, f))]

def accelCommand(command):
    plt.close()
    if len(command) < 2:
        print("accel usage - 'accel <file number(s)>'")
        return
    nums = [int(given)-1 for given in command[1:]]
    for num in nums:
        if(num < 0 or num >= len(files)):
            print("No file with number",num)
        mat = unpackFile(join(home,files[num]))
        removeGravity(mat)
        mag = getMagnitude(mat)
        direction = normalise(mat,mag)
        forward = findForward(direction,mag)
        if forward is None:
            print("No forward acceleration found for",files[num])
            continue
        direction = direction.dot(forward)
        accel = mag*direction
        time = np.linspace(0,accel.shape[0]/104,accel.shape[0])
        plt.plot(time,accel, label=files[num])
    plt.xlabel("Time (seconds)")
    plt.ylabel("Acceleration (Gs)")
    plt.show(block=False)
    return

def speedCommand(command):
    return

def homeCommand(command):
    global home
    global files
    if len(command) < 2:
        print("home usage - 'home <directory>'")
        return
    home = command[1]
    print("New home directory:",home)
    files = [f for f in listdir(home) if isfile(join(home, f))]

files = [f for f in listdir(home) if isfile(join(home, f))]

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
    elif command[0] == "rename":
        renameCommand(command)
    elif command[0] == "help":
        print(commandList)
    elif command[0] == "quit":
        break
    else:
        print("Invalid command, use 'help' to see list of commands")
