import tkSimpleDialog
import time
import motor as motor
import numpy as np
import cv2 as cv
import opencv_greyscale as imgprocess
from tkinter import *
from picamera import PiCamera
from matplotlib import pyplot as plt

#######################
#***IMAGE THRESHOLD***#
#######################
lower = 100
upper = 268

#######################
#Camera Initialization#
#######################
camera = PiCamera()
camera.rotation = 180
camera.resolution = (1024, 768)

##################
#Motor Parameters#
##################
max_range = 350
default_speed = 500

########
#Camera#
########
def CameraCapture():
    camera.capture('pic.jpg')
    cv.imshow('image', cv.imread('/home/pi/Documents/pic.jpg', 0))
    cv.waitKey(0)
    cv.destroyAllWindows()
    return

def ShowProcessed():
    #Load image
    img = cv.imread('pic.jpg', 0)
    #Denoise image
    dst = cv.fastNlMeansDenoising(img)
    #Isolating pixels
    mask = cv.inRange(dst, lower, upper)
    res = cv.bitwise_and(dst, dst, mask = mask)

    cv.imshow('processed', res)
    cv.waitKey(0)
    cv.destroyAllWindows()
    return

def ShowHistogram():
    img = cv.imread('/home/pi/Documents/pic.jpg', 0)
    dst = cv.fastNlMeansDenoising(img)
    plt.hist(dst.ravel(), 256, [0, 256])
    plt.show()
    return

def StartPreview():
    camera.start_preview()
    return

def StopPreview():
    camera.stop_preview()
    return

###############
#Miscellaneous#
###############
def dummyFunction():
    return

########
#Script#
########
result = {}
def RunScript(init, steps, inc, filename):
    #Initial typing
    init = float(init)
    steps = int(steps)
    inc = float(inc)
    filename = str(filename)
    
    #Set motor speed
    motor.SetSpeed(default_speed)

    #Move back to initial position first
    motor.Move(init)
    while(motor.CheckMove()):
        time.sleep(1)

    #MainForLoop
    print("Running script...")
    for i in range(steps):
        savename = filename + str(i) + ".jpg"

        if (init+(inc*i)) > max_range:
            motor.Move(max_range)
            while(motor.CheckMove()):
                time.sleep(1)
            
            camera.capture(savename)
            print("Captured!")
            
            #Image processing
            result[init+(inc*i)] = imgprocess.CalcAvgDiameter(savename, lower, upper)
            print(result)
            break
        
        motor.Move(init+(inc*i))
        while(motor.CheckMove()):
            time.sleep(1)
        
        camera.capture(savename)
        print("Captured!")
        
        #Image processing
        result[init+(inc*i)] = imgprocess.CalcAvgDiameter(savename, lower, upper)
        print(result)

    #End
    print("Done!")

    #Result processing
    fPos = min(result.keys(), key=(lambda k: result[k]))
    fDiam = result[fPos]
    fPos = init + fPos
    print("Min diameter: ", fDiam, " pixels at ", fPos)

###################
#Result Processing#
###################
def PlotGraph():
    result_sorted = sorted(result.items())
    x,y = zip(*result_sorted)
    plt.plot(x, y)
    plt.show()
    return

#####
#GUI#
#####
class App:
    def __init__(self, master):        
        label1 = Label(master, text="Main Controls:")
        label1.grid(row=1, column=3)
        self.run = Button(master, text="Positional Operation", command=Run)
        self.run.grid(row=2, column=2)
        self.alarm_rst = Button(master, text="Alarm Reset", command=motor.AlarmReset)
        self.alarm_rst.grid(row=2, column=3)
        self.check_pos = Button(master, text="Check Position", command=motor.CheckPosition)
        self.check_pos.grid(row=2, column=4)
        self.quit = Button(master, text="Quit", fg="red", command=master.quit)
        self.quit.grid(row=2, column=5)
        self.run_script = Button(master, text="Run Script", command=ScriptSettings)
        self.run_script.grid(row=3, column=3)
        self.plot_result = Button(master, text="Plot Results", command=PlotGraph)
        self.plot_result.grid(row=3, column=4)
        
        label2 = Label(master, text="Manual Input")
        label2.grid(row=4, column=3)
        self.left = Button(master, text="<Left", command=motor.GoLeft)
        self.left.grid(row=5, column=2)
        self.stop = Button(master, text="Stop", fg="red", command=motor.Stop)
        self.stop.grid(row=5, column=3)
        self.right = Button(master, text="Right>", command=motor.GoRight)
        self.right.grid(row=5, column=4)
        self.home = Button(master, text="Home", command=motor.GoHome)
        self.home.grid(row=6, column=3)

        label3 = Label(master, text="Camera Controls")
        label3.grid(row=7, column=3)
        self.show_histogram = Button(master, text="Show Histogram", command=ShowHistogram)
        self.show_histogram.grid(row=8, column=2)
        self.show_processed = Button(master, text="Show Processed", command=ShowProcessed)
        self.show_processed.grid(row=9, column=2)
        self.start_preview = Button(master, text="Start Preview", command=StartPreview)
        self.start_preview.grid(row=8, column=3)
        self.stop_preview = Button(master, text="Stop Preview", command=StopPreview)
        self.stop_preview.grid(row=9, column=3)
        self.camera_capture = Button(master, text="Camera Capture", command=CameraCapture)
        self.camera_capture.grid(row=8, column=4)
        
        motor.CheckReady()
        motor.CheckMove()
        motor.CheckAlarm()

class ScriptInput(tkSimpleDialog.Dialog):
    def body(self, master):
        Label(master, text="Initial position:").grid(row=0)
        Label(master, text="Steps:").grid(row=1)
        Label(master, text="Increment:").grid(row=2)
        Label(master, text="Filename:").grid(row=3)

        self.init = Entry(master)
        self.steps = Entry(master)
        self.increment = Entry(master)
        self.filename = Entry(master)

        self.init.grid(row=0, column=1)
        self.steps.grid(row=1, column=1)
        self.increment.grid(row=2, column=1)
        self.filename.grid(row=3, column=1)
        
        return

    def apply(self):
        RunScript(self.init.get(), self.steps.get(), self.increment.get(), self.filename.get())

def ScriptSettings():
    dialog = ScriptInput(root)
    
class DataInput(tkSimpleDialog.Dialog):
    def body(self, master):
        Label(master, text="Position:").grid(row=0)
        Label(master, text="Speed:").grid(row=1)

        self.position = Entry(master)
        self.speed = Entry(master)

        self.position.grid(row=0, column=1)
        self.speed.grid(row=1, column=1)
        
        return

    def apply(self):
        motor.SetSpeed(self.speed.get())
        motor.time.sleep(0.2)
        motor.Move(self.position.get())

def Run():
    dialog = DataInput(root)

######
#Main#
######
root = Tk()
app = App(root)
root.mainloop()
root.destroy()
