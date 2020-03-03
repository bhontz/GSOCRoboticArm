"""
    Code to support the GSOC uARM Robotic Arm Event Display.
    For more information, visit: https://www.github.com/bhontz/GSOCRoboticArm

"""
import os, sys, time, math
from tkinter import *
from uarm.wrapper import SwiftAPI

class MainApplication(Frame):
    def __init__(self, master, uArm):
        self.master = master
        self.uArm = uArm
        self.strName = StringVar()
        self.strOutput = StringVar()
        self.bgcolor = "#00ae58"
        Frame.__init__(self, master)
        self.config_gui()
        self.create_widgets()
        return

    def config_gui(self):
        self.master.title("GSOC Robotics")
        self.master.geometry("800x400")
        self.master.resizable(True, True)
        self.master.configure(background="#00ae58", highlightcolor='yellow', highlightthickness=3)
        return

    def create_widgets(self):
        lb = Label(self.master, text="Welcome to GSOC Robotics!", bg=self.bgcolor, fg='yellow', font=("Omnes", 32))
        lb.pack(fill=X)
        lbsub = Label(self.master, text = "Please type in your name:", fg='yellow', bg=self.bgcolor,font=("Omnes",24))
        lbsub.pack(fill=X)
        entry = Entry(self.master, textvariable=self.strName, fg='white', bg=self.bgcolor, font=("Omnes", 24, "bold"))
        entry.pack(fill=X, pady=20, padx=50, expand=FALSE)
        entry.focus_force()
        # entry.bind('<Return>', self.plotName)
        btnSubmit = Button(self.master, text="Submit", font=("Omnes", 28), command=self.plotName)
        btnSubmit.pack(fill=Y, pady=5)
        btnClose = Button(self.master, text="Close", font=("Omnes", 8), command=self.master.quit)
        btnClose.pack(fill=Y, pady=30)
        return

    def plotName(self):
        while (self.uArm.arm().get_is_moving()):
            continue
        time.sleep(0.5)
        self.master.update()
        try:
            name = self.strName.get()
            self.uArm.setScope(name)
            x = self.uArm.x0
            y = self.uArm.y0

            time.sleep(2)
            self.uArm.arm().set_position(x=x, y=y, z=10)  # get to first character
            self.uArm.pen_down()

            for c in name:
                # print("x:{0} y:{1}, scope:{2}\n".format(x,y,self.uArm.scope))
                self.uArm.pen_down()
                self.uArm.LetterSelect(c)()
                self.uArm.pen_up()
                y = y - (1.1 * self.uArm.scope)
                self.uArm.arm().set_position(x=x, y=y, z=10)
                time.sleep(0.5)

            # need to clear out the Entry field between usages
            self.strName.set("")
            self.master.update()
            self.uArm.arm().set_position(x=200, y=0, z=10)  # return to neutral position
            self.uArm.arm().set_servo_angle(angle=90)
            time.sleep(0.5)
            self.uArm.arm().set_wrist(angle=90)
            time.sleep(0.5)

        except ValueError:
            pass
        return


class uArm():
    def __init__(self):
        self.scope = 10
        self.x0 = 160
        self.y0 = 0
        self.swift = SwiftAPI(filters={'hwid':'USB VID:PID=2341:0042'})
        self.swift.waiting_ready(timeout=3)
        # self.swift.set_speed_factor(0.005)  # if you change this, be prepared for different movements!
        self.swift.set_mode(mode=0)
        time.sleep(0.5)
        self.swift.set_servo_angle(angle=90)
        self.swift.set_wrist(angle=90)
        self.swift.set_position(x=200,y=0,z=20) # start it off with a salute
        self.swift.set_buzzer(frequency=1000, duration=1) # signal ready
        self.lstValidCharSet = ['?','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',\
                           '-','0','1','2','3','4','5','6','7','8','9']
        self.lstLetter = [self.QuestionMark, self.LetterA, self.LetterB, self.LetterC, self.LetterD, self.LetterE, self.LetterF,\
                          self.LetterG, self.LetterH, self.LetterI, self.LetterJ, self.LetterK, self.LetterL, self.LetterM, self.LetterN,\
                          self.LetterO, self.LetterP, self.LetterQ, self.LetterR, self.LetterS, self.LetterT, self.LetterU, self.LetterV,\
                          self.LetterW, self.LetterX, self.LetterY, self.LetterZ, self.Hyphen,  self.Number0, self.Number1, self.Number2,\
                          self.Number3, self.Number4, self.Number5, self.Number6, self.Number7, self.Number8, self.Number9]

    def __del__(self):
        input("PLEASE SUPPORT uARM ARM!!, then strike ENTER to continue ...")
        self.swift.set_buzzer(frequency=600, duration=2)
        self.swift.set_position(x=200,y=0,z=20)
        self.swift.flush_cmd()
        self.swift.disconnect()
        del self.swift
        self.swift = None

    def arm(self):
        """
            Using this method to allow raw access to the uArm if required
        """
        return self.swift

    def insert_pen(self):
        self.swift.set_buzzer(frequency=1000, duration=0.5) # signal ready
        self.swift.set_servo_angle(angle=90)
        time.sleep(0.5)
        self.swift.set_wrist(angle=90)
        time.sleep(0.5)
        self.swift.set_position(x=200,y=0,z=0)
        while (self.swift.get_is_moving()):
            continue
        input("Set pen in universal holder, then strike ENTER to continue ...")
        self.swift.set_position(x=200,y=0,z=10)
        return

    def pen_up(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        self.swift.set_position(x, y, 10)
        time.sleep(0.5)
        return 10

    def pen_down(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        self.swift.set_position(x, y, 0)
        time.sleep(0.5)
        return 0

    def setScope(self, strName):
        """
            based upon the length of strName, determine the scope (char width) and starting X, Y positions
            assuming that the center of the page is 160,0
            x extent is 110 - 210, y extent 80 - (-80)  (x axis is PARALLEL to the arm, short edge of the paper)
        """
        if type(strName) == str:
            strName = strName[:26]  # going to truncate user input to a 26 characters max
            intLenName  = len(strName)
            if (intLenName < 4):
                self.scope = 40.0  # keeping it real
            else:
                self.scope = math.floor(160.0/(intLenName * 1.1))
            self.x0 = 160 - (0.5 * self.scope)
            self.y0 =  self.scope * intLenName * 1.1 / 2

        return

    def LetterSelect(self, c):
        """
            given char c, return the plotting function
            index 0 resolves to the question mark character
        """
        index = 0
        if type(c) == str:
            if c == ' ':
                return self.SpaceBar
            else:
                c = c.upper()
                if c in self.lstValidCharSet:
                    index = self.lstValidCharSet.index(c) - self.lstValidCharSet.index('A') + 1 # 0th item is '?'

                # if c in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']:
                #     index = ord(c) - ord('A') + 1  # using question mark as the 0th index item

        return self.lstLetter[index]  # return the function to use

"""
    remainder of this class contains individual methods for each character that the uARM can draw.
    If you add a new method (i.e. a new character to draw), don't forget to add a reference to your new method within 
    the lstValidCharSet and lstLetter arrays found within the __init__() method.

    Note that each of these characters is implemented as a "vector graphic", meaning that the size of the
    character will scale in accordance to the required height/width.  In this application, that is determined
    by the number of characters that are entered to draw (i.e. the fewer the number of characters, the larger the
    characters will be drawn.)
"""

    def SpaceBar(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 0.25 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = xo
        self.swift.set_position(x=x, y=y, z=z)
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.25 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def QuestionMark(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + (1.5 * self.scope)
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x + 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        x = x - 0.25 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x - 0.25 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterA(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        x = x + 2.0 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 2.0 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        x = x + self.scope
        y = y + 0.25 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=10)
        return

    def LetterB(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=10)
        return

    def LetterC(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 1.5 * self.scope
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x + 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterD(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterE(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        x = x - self.scope
        y = y + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        x = x - self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterF(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        x = x - self.scope
        y = y + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterG(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 1.5 * self.scope
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x + 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.25 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterH(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x - 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        x = x + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        y = y + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterI(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        y = y + 0.25 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        x = x - 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterJ(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 2.0 * self.scope
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x - 1.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterK(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        x = x - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x + self.scope
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        x = x - self.scope
        y = y + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x - self.scope
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterL(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        x = x - 2.0 * self.scope
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        y = y + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterM(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterN(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 2.0 * self.scope
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterO(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterP(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=10)
        return

    def LetterQ(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterR(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = xo
        y = yo - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterS(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + self.scope
        y = y + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterT(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        y = y + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterU(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x - 1.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 1.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterV(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x - 2.0 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 2.0 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterW(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x - 2.0 * self.scope
        y = y - 0.25 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + self.scope
        y = y - 0.25 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - self.scope
        y = y - 0.25 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 2.0 * self.scope
        y = y - 0.25 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterX(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x - 2.0 * self.scope
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x - 2.0 * self.scope
        y = y + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterY(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x - self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        x = x + self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x - self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def LetterZ(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        y = y + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 2.0 * self.scope
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        y = y + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def Hyphen(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + self.scope
        y = y - 0.25 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def Number0(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + self.scope
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def Number1(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 1.75 * self.scope
        y = y - 0.25 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x + 0.25 * self.scope
        y = y - 0.25 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 2 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        y = y - 0.25 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def Number2(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 1.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x + 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 1.5 * self.scope
        y = y + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def Number3(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 1.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x + 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def Number4(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x +  self.scope
        y = y - 0.75 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        y = y + 0.75 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + self.scope
        y = y - 0.7 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 2.0 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def Number5(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 2.0 * self.scope
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        y = y + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def Number6(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def Number7(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 2 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        y = y - self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 2 * self.scope
        y = y + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def Number8(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x + 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return

    def Number9(self):
        while (self.swift.get_is_moving()):
            continue
        x, y, z = self.swift.get_position()
        xo = x
        yo = y
        z = self.pen_up()
        x = x + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_down()
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y + 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x + 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        x = x - 0.5 * self.scope
        y = y - 0.5 * self.scope
        self.swift.set_position(x=x, y=y, z=z)
        z = self.pen_up()
        self.swift.set_position(x=xo, y=yo, z=z)
        return


if __name__ == '__main__':
    print ("hello from module %s. Python version: %s" % (sys.argv[0], sys.version))
    sys.stdout.write("--------------------------------------------------------------\n")
    sys.stdout.write("Start of %s Process: %s\n\n" % (sys.argv[0], time.strftime("%H:%M:%S", time.localtime())))

    uArm = uArm()
    uArm.insert_pen()
    print("Starting UI in 5 seconds ...")
    time.sleep(5)

    window = Tk()
    main_app = MainApplication(window, uArm)
    window.mainloop()
    # print("now out of main loop")

    del window
    window = None
    del uArm
    uArm = None

    sys.stdout.write("\n\nEnd of %s Process: %s.\n" % (sys.argv[0], time.strftime("%H:%M:%S", time.localtime())))
    sys.stdout.write("-------------------------------------------------------------\n")
