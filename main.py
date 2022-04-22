import struct
import os
from os import listdir
from os.path import isfile, join
import numpy as np
from scipy import integrate, signal
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

def getDirection(mat, mag):
    return mat / mag.reshape(-1,1)

def findForward(mat):
    M = mat.T @ mat
    eigenvals, eigenvecs = np.linalg.eigh(M)
    return eigenvecs[:,2]    

def calcSpeed(accel):
    return integrate.cumtrapz(accel*21.937, initial=0 ,dx=1/104)

def getForwardAccel(fileNum):
    raw = unpackFile(join(home,files[fileNum]))
    removeGravity(raw)
    mag = getMagnitude(raw)
    direction = getDirection(raw, mag)
    forward = findForward(raw)
    direction = direction.dot(forward)
    return mag*direction

def listCommand():
    global files
    files = [f for f in listdir(home) if isfile(join(home, f))]
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
        accel = getForwardAccel(num)
        smoothed = signal.savgol_filter(accel, 51, 3)
        time = np.linspace(0,accel.shape[0]/104,accel.shape[0])
        plt.plot(time,smoothed, label=files[num])
    plt.xlabel("Time (seconds)")
    plt.ylabel("Acceleration (Gs)")
    plt.show(block=False)
    return

def speedCommand(command):
    plt.close()
    if len(command) < 2:
        print("speed usage - 'speed <file number(s)>'")
        return
    nums = [int(given)-1 for given in command[1:]]
    for num in nums:
        if(num < 0 or num >= len(files)):
            print("No file with number",num)
        accel = getForwardAccel(num)
        speed = calcSpeed(accel)
        time = np.linspace(0,accel.shape[0]/104,accel.shape[0])
        plt.plot(time,speed, label=files[num])
    plt.xlabel("Time (seconds)")
    plt.ylabel("Speed (mph)")
    plt.show(block=False)
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

home = "C:\\Users\\Will\\Documents\\Year 3\\Project\\data"
commandList = """Commands:
    'list' - Lists the files in the home folder with a number assigned to each
    'accel <file number(s)>' -  Displays the acceleration graph of the numbered file from the list, 
                                optionally list more file numbers separated by spaces to compare on the same graph
    'speed <file number(s)>' -  Displays the speed graph of the numbered file from the list, 
                                optionally list more file numbers seperated by spaces to compare on the same graph
    'home <directory>' - Change the home directory that files will be displayed from
    'rename <file number> <new name>' - Rename the numbered file from the list
    'help' - Display this list of commands
    'quit' - Exit the program
    """

print("Default home folder is",home)
print(commandList)

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
