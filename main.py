import struct
import os
from os import listdir
from os.path import isfile, join
import numpy as np
from scipy import integrate, signal
import matplotlib.pyplot as plt

def unpackFile(filename):
    #initialise matrix of correct size
    size = os.path.getsize(filename)
    mat = np.zeros((int(size/12),3))
    #open file and read data into matrix, converting to floats
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
    #take average acceleration for first ~half second as gravity and remove
    gravity = np.mean(mat[:50],axis=0)
    mat -= gravity

def getMagnitude(mat):
    #calculate 3D hypotenuse length for xyz
    return np.linalg.norm(mat,axis=1)

def getDirection(mat, mag):
    #normalise vectors to length 1
    return mat / mag.reshape(-1,1)

def findForward(mat):
    #find average direction of all acceleration and take this as forwards
    M = mat.T @ mat
    eigenvals, eigenvecs = np.linalg.eigh(M)
    return eigenvecs[:,2]*-1    

def calcSpeed(accel):
    #integrate under acceleration curve to get speed curve
    return integrate.cumtrapz(accel*21.937, initial=0 ,dx=1/104)

def getForwardAccel(fileNum):
    #use all above functions to get 1D acceleration array from file
    raw = unpackFile(join(home,files[fileNum]))
    removeGravity(raw)
    mag = getMagnitude(raw)
    direction = getDirection(raw, mag)
    forward = findForward(raw)
    direction = direction.dot(forward)
    return mag*direction

def listCommand():
    #update list of files in directory and print them out with a number
    global files
    files = [f for f in listdir(home) if isfile(join(home, f)) and f.endswith(".DAT")]
    for i in range(0,len(files)):
        print(i+1,"-",files[i])

def renameCommand(command):
    #rename numbered file in list
    global files
    if len(command) < 3:
        print("rename usage - 'rename <file number> <new name>'")
        return
    num = int(command[1])-1
    if num < 0 or num >= len(files):
        print("No file with that number")
        return
    os.rename(join(home,files[num]),join(home,command[2]+".DAT"))
    files = [f for f in listdir(home) if isfile(join(home, f)) and f.endswith(".DAT")]

def accelCommand(command):
    #plot acceleration of given file(s) against time
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
    #plot speed of given file(s) against time
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
    #change home directory and update files list
    global home
    global files
    if len(command) < 2:
        print("home usage - 'home <directory>'")
        return
    home = command[1]
    print("New home directory:",home)
    files = [f for f in listdir(home) if isfile(join(home, f)) and f.endswith(".DAT")]

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

#update files list
files = [f for f in listdir(home) if isfile(join(home, f)) and f.endswith(".DAT")]

#take user commands infinitely until quit
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
