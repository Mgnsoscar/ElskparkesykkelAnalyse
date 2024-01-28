import traceback
import os
from PyQt5 import QtWidgets as qw, QtCore as qc, QtGui as qg

a = {}
a["left"]    = qc.Qt.AlignLeft
a["right"]   = qc.Qt.AlignRight
a["top"]     = qc.Qt.AlignTop
a["btm"]     = qc.Qt.AlignBottom
a["hcenter"] = qc.Qt.AlignHCenter
a["vcenter"] = qc.Qt.AlignVCenter
a["center"]  = qc.Qt.AlignCenter

class myframe(qw.QFrame):

    def __init__(self, Master, layoutType=None, objectName=None, radius=None, color=None, align=None, add=None, blur=None):

        qw.QFrame.__init__(self, Master)

        # This snippet of code peeks back into the code used to call each specific instance of this class.
        # This was the object name can automatically be the same as the instance name without need for extra code.
        # Another object name can also be defined when calling a new class instance

        if objectName == None:

            (filename, line_number, function_name, text) = traceback.extract_stack()[-2]
            objectName = text[:text.find('=')].strip()

        self.setObjectName(objectName)

        # Make shorter variables for alignment
        a = {}
        a["left"]    = qc.Qt.AlignLeft
        a["right"]   = qc.Qt.AlignRight
        a["top"]     = qc.Qt.AlignTop
        a["btm"]     = qc.Qt.AlignBottom
        a["hcenter"] = qc.Qt.AlignHCenter
        a["vcenter"] = qc.Qt.AlignVCenter
        a["center"]  = qc.Qt.AlignCenter

        # Here a layout is made according to the input. If no input there is no layout

        if layoutType   == "v":
            self.lay = qw.QVBoxLayout(self)
            self.lay.setContentsMargins(0, 0, 0, 0)
            self.lay.setSpacing(0)
        elif layoutType == "h":
            self.lay = qw.QHBoxLayout(self)
            self.lay.setContentsMargins(0, 0, 0, 0)
            self.lay.setSpacing(0)
        elif layoutType == "g":
            self.lay = qw.QGridLayout(self)
            self.lay.setContentsMargins(0,0,0,0)
            self.lay.setSpacing(0)


        # Dictionary with some of the most used stylesheet commands. Also doubles as an init for the stylesheet
        self.style = {}

        # Init frame as transparent and without border-radius
        if color == None:
            self.style["background-color"]          = "background-color: rgba(0, 0, 0, 0);"
        else:
            self.style["background-color"]          = f"background-color: rgba{color};"
        if radius == None:
            self.style["border-radius"]             = "border-radius:              0px;"  # Regular border radius
        else:
            self.style["border-radius"]             = f"border-radius:             {radius}px;"  # Regular border radius
        if add == True and align!=None:
            Master.lay.addWidget(self, 0, a[align])
        elif add == True and align==None:
            Master.lay.addWidget(self)
        if blur!=None:
            self.blur(blur)
        # Set the stylesheet
        self.updateStylesheet()

    # Update the stylesheet
    def updateStylesheet(self):

        self.stylesheet = "QFrame#"+self.objectName()+"{\n"

        for i in self.style:

            if self.style[i] != "":

                self.stylesheet += f"{self.style[i]}\n"

            elif self.style[i] == "":

                del self.style[i]

        self.stylesheet += "}"

        self.setStyleSheet(self.stylesheet)
    # Make frame transparent
    def transp(self):
        self.style["background-color"]  = f"background-color:           rgba(0, 0, 0, 0);"
        self.updateStylesheet()
    # Set custom background color
    def bg(self, r, g, b, a):
        self.style["background-color"]  = f"background-color:           rgba({r}, {g}, {b}, {a});"
        self.updateStylesheet()
    # Set border radius for all four corners
    def radius(self, radius):
        self.style["border-radius"]     = f"border-radius:              {radius}px;"
        self.updateStylesheet()
    # Set custom border radius configuration
    def customradius(self, topleft, topright, bottomright, bottomleft):
        self.style["border-top-left-radius"]        = f"border-top-left-radius:     {topleft}px;"
        self.style["border-top-right-radius"]       = f"border-top-right-radius:    {topright}px;"
        self.style["border-bottom-right-radius"]    = f"border-bottom-right-radius: {bottomright}px;"
        self.style["border-bottom-left-radius"]     = f"border-bottom-left-radius:  {bottomleft}px;"
        self.updateStylesheet()
    # Add command to the stylesheet like normally, except here you need a keyword
    def addstyle(self, commandKey, command):
        self.style[commandKey] = command
        self.updateStylesheet()
    # Change object name
    def name(self, name):
        self.setObjectName(name)
        self.updateStylesheet()
    # Configure margins
    def margins(self, x, y, z, g):
        self.lay.setContentsMargins(x, y, z, g)
    # Configure spacing
    def spacing(self, spacing):
        self.lay.setSpacing(spacing)
    #configure alignment of the frame
    def align(self, alignment):
        if alignment == "hcenter":
            self.setAlignment(qc.Qt.AlignHCenter)
        elif alignment == "reft":
            self.setAlignment(qc.Qt.AlignLeft)
        elif alignment == "right":
            self.setAlignment(qc.Qt.AlignRight)
        elif alignment == "bottom":
            self.setAlignment(qc.Qt.AlignBottom)
        elif alignment == "vcenter":
            self.setAlignment(qc.Qt.AlignVCenter)
        elif alignment == "center":
            self.setAlignment(qc.Qt.AlignCenter)
    def blur(self, state, radius=None):
        blureffect = qw.QGraphicsBlurEffect()
        if radius != None:
            blureffect.setBlurRadius(radius)
        if state == True:
            self.setGraphicsEffect(blureffect)
        if state == False:
            self.setGraphicsEffect(None)
class mywidget(qw.QWidget):

    def __init__(self, Master, layoutType=None, objectName=None, add=None, align=None, radius=None):

        qw.QWidget.__init__(self, Master)

        # This snippet of code peeks back into the code used to call each specific instance of this class.
        # This was the object name can automatically be the same as the instance name without need for extra code.
        # Another object name can also be defined when calling a new class instance

        if objectName == None:

            (filename, line_number, function_name, text) = traceback.extract_stack()[-2]
            objectName = text[:text.find('=')].strip()

        self.setObjectName(objectName)

        # Make shorter variables for alignment
        a = {}
        a["left"] = qc.Qt.AlignLeft
        a["right"] = qc.Qt.AlignRight
        a["top"] = qc.Qt.AlignTop
        a["btm"] = qc.Qt.AlignBottom
        a["hcenter"] = qc.Qt.AlignHCenter
        a["vcenter"] = qc.Qt.AlignVCenter
        a["center"] = qc.Qt.AlignCenter

        # Here a layout is made according to the input. If no input there is no layout

        if layoutType   == "v":
            self.lay = qw.QVBoxLayout(self)
            self.lay.setContentsMargins(0, 0, 0, 0)
            self.lay.setSpacing(1)
        elif layoutType == "h":
            self.lay = qw.QHBoxLayout(self)
            self.lay.setContentsMargins(0, 0, 0, 0)
            self.lay.setSpacing(1)
        elif layoutType == "g":
            self.lay = qw.QGridLayout(self)
            self.lay.setContentsMargins(0,0,0,0)
            self.lay.setSpacing(0)

        # Dictionary with some of the most used stylesheet commands. Also doubles as an init for the stylesheet
        self.style = {}

        # Init frame as transparent and without border-radius
        self.style["background-color"]              = "background-color: rgba(0, 0, 0, 0);"
        if add == True and align != None:
            Master.lay.addWidget(self, 0, align)
        elif add == True and align == None:
            Master.lay.addWidget(self)
        if radius == None:
            self.style["border-radius"] = "border-radius:              0px;"  # Regular border radius
        else:
            self.style["border-radius"] = f"border-radius:             {radius}px;"  # Regular border radius

        # Set the stylesheet
        self.updateStylesheet()
    # Update the stylesheet
    def updateStylesheet(self):

        self.stylesheet = "QWidget{"+"\n"
        for i in self.style:

            if self.style[i] != "":

                self.stylesheet += f"{self.style[i]}\n"

            elif self.style[i] == "":

                del self.style[i]

        self.stylesheet += "}"

        self.setStyleSheet(self.stylesheet)

    # Make frame transparent
    def transp(self):
        self.style["background-color"]  = f"background-color:           rgba(0, 0, 0, 0);"
        self.updateStylesheet()
    # Set custom background color
    def bg(self, r, g, b, a):
        self.style["background-color"]  = f"background-color:           rgba({r}, {g}, {b}, {a});"
        self.updateStylesheet()
    # Set border radius for all four corners
    def radius(self, radius):
        self.style["border-radius"]     = f"border-radius:              {radius}px;"
        self.updateStylesheet()
    # Set custom border radius configuration
    def customradius(self, topleft, topright, bottomright, bottomleft):
        self.style["border-top-left-radius"]        = f"border-top-left-radius:     {topleft}px;"
        self.style["border-top-right-radius"]       = f"border-top-right-radius:    {topright}px;"
        self.style["border-bottom-right-radius"]    = f"border-bottom-right-radius: {bottomright}px;"
        self.style["border-bottom-left-radius"]     = f"border-bottom-left-radius:  {bottomleft}px;"
        self.updateStylesheet()
    # Add command to the stylesheet like normally, except here you need a keyword
    def addstyle(self, commandKey, command):
        self.style[commandKey] = command
        self.updateStylesheet()
    # Change object name
    def name(self, name):
        self.lay.setObjectName(name)
    # Configure margins
    def margins(self, x, y, z, g):
        self.lay.setContentsMargins(x, y, z, g)
    # Configure spacing
    def spacing(self, spacing):
        self.lay.setSpacing(spacing)
    #configure alignment of the frame
    def align(self, alignment):
        if alignment == "hcenter":
            self.setAlignment(qc.Qt.AlignHCenter)
        elif alignment == "reft":
            self.setAlignment(qc.Qt.AlignLeft)
        elif alignment == "right":
            self.setAlignment(qc.Qt.AlignRight)
        elif alignment == "bottom":
            self.setAlignment(qc.Qt.AlignBottom)
        elif alignment == "vcenter":
            self.setAlignment(qc.Qt.AlignVCenter)
        elif alignment == "center":
            self.setAlignment(qc.Qt.AlignCenter)
class mybutton(qw.QPushButton):

    def __init__(self, Master, objectName=None, radius=None, color=None, hover=None, pressed=None, add=None, align=None, disabled=None, text=None, size=None):

        qw.QPushButton.__init__(self, Master)

        # This snippet of code peeks back into the code used to call each specific instance of this class.
        # This was the object name can automatically be the same as the instance name without need for extra code.
        # Another object name can also be defined when calling a new class instance

        if objectName == None:

            (filename, line_number, function_name, Text) = traceback.extract_stack()[-2]
            objectName = Text[:Text.find('=')].strip()

        self.setObjectName(objectName)

        # Make shorter variables for alignment
        a = {}
        a["left"] = qc.Qt.AlignLeft
        a["right"] = qc.Qt.AlignRight
        a["top"] = qc.Qt.AlignTop
        a["btm"] = qc.Qt.AlignBottom
        a["hcenter"] = qc.Qt.AlignHCenter
        a["vcenter"] = qc.Qt.AlignVCenter
        a["center"] = qc.Qt.AlignCenter

        # Dictionary with some of the most used stylesheet commands. Also doubles as an init for the stylesheet
        self.style = {}

        # Init some styles:
        if color == None:
            self.style["background-color"]              = "background-color: rgba(0, 0, 0, 255);"
        else:
            self.style["background-color"]              = f"background-color: rgba{color};"
        if hover == None:
            self.hover                                  = ""
        else:
            self.hover                                  = f"QPushButton#{self.objectName()}:hover{{background-color: rgba{hover};}}"
        if pressed == None:
            self.press                                  = ""
        else:
            self.press                                  = f"QPushButton#{self.objectName()}:pressed{{background-color: rgba{pressed};}}"
        if disabled == None:
            self.disbld                                 = ""
        else:
            self.disbld                                 = f"QPushButton#{self.objectName()}:disabled{{background-color: rgba{disabled};}}"
        if radius==None:
            self.style["border-radius"]                 = f"border-radius:              0px;"  # Regular border radius
        else:
            self.style["border-radius"]                 = f"border-radius:              {radius}px;"  # Regular border radius
        if add == True and align!=None:
            Master.lay.addWidget(self, 0, a[align])
        elif add == True and align==None:
            Master.lay.addWidget(self)
        if text!=None:
            self.setText(text)

        # Set the stylesheet
        self.updateStylesheet()
    # Update the stylesheet
    def updateStylesheet(self):

        self.stylesheet = "QPushButton#"+self.objectName()+"{\n"
        for i in self.style:

            if self.style[i] != "":

                self.stylesheet += f"{self.style[i]}\n"

            elif self.style[i] == "":

                del self.style[i]

        self.stylesheet += "}\n"

        if self.hover != "":
            self.stylesheet += self.hover + "\n"
        if self.press != "":
            self.stylesheet += self.press + "\n"
        if self.disbld != "":
            self.stylesheet += self.disbld + "\n"

        self.setStyleSheet(self.stylesheet)

    # Make button transparent
    def transp(self):
        self.style["background-color"]  = f"background-color:           rgba(0, 0, 0, 0);"
        self.updateStylesheet()
    # Set custom background color
    def bg(self, r, g, b, a):
        self.style["background-color"]  = f"background-color:           rgba({r}, {g}, {b}, {a});"
        self.updateStylesheet()
    # Set border radius for all four corners
    def radius(self, radius):
        self.style["border-radius"]     = f"border-radius:              {radius}px;"
        self.updateStylesheet()
    # Set custom border radius configuration
    def customradius(self, topleft, topright, bottomright, bottomleft):
        self.style["border-top-left-radius"]        = f"border-top-left-radius:     {topleft}px;"
        self.style["border-top-right-radius"]       = f"border-top-right-radius:    {topright}px;"
        self.style["border-bottom-right-radius"]    = f"border-bottom-right-radius: {bottomright}px;"
        self.style["border-bottom-left-radius"]     = f"border-bottom-left-radius:  {bottomleft}px;"
        self.updateStylesheet()
    def hcolor(self, r, g, b, a):
        self.hover = f"QPushButton#{self.objectName()}:hover{{background-color: rgba({r}, {g}, {b}, {a});}}"
        self.updateStylesheet()
    def pcolor(self, r, g, b, a):
        self.press = f"QPushButton#{self.objectName()}:pressed{{background-color: rgba({r}, {g}, {b}, {a});}}"
        self.updateStylesheet()
    # Add command to the stylesheet like normally, except here you need a keyword
    def addstyle(self, commandKey, command):
        self.style[commandKey] = command
        self.updateStylesheet()
    # Change object name
    def name(self, name):
        self.lay.setObjectName(name)
    def align(self, alignment):
        if alignment == "hcenter":
            self.setAlignment(qc.Qt.AlignHCenter)
        elif alignment == "reft":
            self.setAlignment(qc.Qt.AlignLeft)
        elif alignment == "right":
            self.setAlignment(qc.Qt.AlignRight)
        elif alignment == "bottom":
            self.setAlignment(qc.Qt.AlignBottom)
        elif alignment == "vcenter":
            self.setAlignment(qc.Qt.AlignVCenter)
        elif alignment == "center":
            self.setAlignment(qc.Qt.AlignCenter)
class mylabel(qw.QLabel):

    def __init__(self,  Master,     objectName=None,    color=None,     add=None,   bcolor=None,
                        size=None,  text=None,          font=None,      align=None):

        qw.QLabel.__init__(self, Master)

    #### I want my class to have a custom font family called Roboto. In the following code i
    #### iterate over the resource folder to upload these to the QPyQt5 font local database

        directory = 'Resources\Fonts'

        # iterate over files in directory
        for filename in os.listdir(directory):
            Font = os.path.join(directory, filename)

            # If it is a file: (don't need to check for right filetype as i know everything in the folder.
            if os.path.isfile(Font):
                qg.QFontDatabase.addApplicationFont(f"{Font}")
        db = qg.QFontDatabase()

        # Dictionary with some of the most used stylesheet commands. Also doubles as an init for the stylesheet
        self.style = {}
        if font == None:
            self.font = db.font("Roboto", "Normal", 12)
            self.font.setWeight(60)
            self.setFont(self.font)
        else:
            self.font = db.font(font[0], font[1], 12)
            self.font.setWeight(font[2])
            self.setFont(self.font)

        if objectName != None:
            self.setObjectName(None)
        if color == None:
            self.style["color"]             = "color: rgba(255, 255, 255, 255);"
        else:
            self.style["color"]             = f"color: rgba{color};"
        if bcolor == None:
            self.style["background-color"]  = "background-color: rgba(255, 255, 255, 0);"
        else:
            self.style["background-color"]  = f"background-color: rgba{bcolor};"
        if size == None:
            self.font.setPixelSize(12)
            self.setFont(self.font)
        else:
            self.font.setPixelSize(size)
            self.setFont(self.font)
        if text != None:
            self.setText(text)
        if align!=None:
            self.align(align)
        if add == True:
            Master.lay.addWidget(self)


        # Set the stylesheet
        self.updateStylesheet()

    # Update the stylesheet
    def updateStylesheet(self):

        self.stylesheet = ""
        for i in self.style:

            if self.style[i] != "":

                self.stylesheet += f"{self.style[i]}\n"

            elif self.style[i] == "":

                del self.style[i]

        self.setStyleSheet(self.stylesheet)

    # Make button transparent
    def transp(self):
        self.style["background-color"]  = f"background-color:           rgba(0, 0, 0, 0);"
        self.updateStylesheet()
    # Set custom background color
    def bg(self, r, g, b, a):
        self.style["background-color"]  = f"background-color:           rgba({r}, {g}, {b}, {a});"
        self.updateStylesheet()
    # Set border radius for all four corners
    def radius(self, radius):
        self.style["border-radius"]     = f"border-radius:              {radius}px;"
        self.updateStylesheet()
    # Set custom border radius configuration
    def customradius(self, topleft, topright, bottomright, bottomleft):
        self.style["border-top-left-radius"]        = f"border-top-left-radius:     {topleft}px;"
        self.style["border-top-right-radius"]       = f"border-top-right-radius:    {topright}px;"
        self.style["border-bottom-right-radius"]    = f"border-bottom-right-radius: {bottomright}px;"
        self.style["border-bottom-left-radius"]     = f"border-bottom-left-radius:  {bottomleft}px;"
        self.updateStylesheet()
    # Add command to the stylesheet like normally, except here you need a keyword
    def addstyle(self, commandKey, command):
        self.style[commandKey] = command
        self.updateStylesheet()
    # Change object name
    def name(self, name):
        self.lay.setObjectName(name)
    def align(self, alignment):
        if alignment == "hcenter":
            self.setAlignment(qc.Qt.AlignHCenter)
        elif alignment == "reft":
            self.setAlignment(qc.Qt.AlignLeft)
        elif alignment == "right":
            self.setAlignment(qc.Qt.AlignRight)
        elif alignment == "bottom":
            self.setAlignment(qc.Qt.AlignBottom)
        elif alignment == "vcenter":
            self.setAlignment(qc.Qt.AlignVCenter)
        elif alignment == "center":
            self.setAlignment(qc.Qt.AlignCenter)
    def blur(self, state, radius=None):
        blureffect = qw.QGraphicsBlurEffect()
        if radius != None:
            blureffect.setBlurRadius(radius)
        if state == True:
            self.setGraphicsEffect(blureffect)
        if state == False:
            self.setGraphicsEffect(None)
class myinput(qw.QLineEdit):

    def __init__(self,  Master,     objectName=None,    label=None,     color=None,     add=None, radius=None,
                        size=None,  text=None,          font=None,      align=None,     textcolor=None):

        qw.QLineEdit.__init__(self, Master)

        # Here a layout is made according to the input. If no input there is no layout
        if label == True:
            self.lay = qw.QVBoxLayout(self)
            self.lay.setContentsMargins(0, 0, 0, 0)
            self.lay.setSpacing(1)
            self.label = mylabel(self)


        # This snippet of code peeks back into the code used to call each specific instance of this class.
        # This was the object name can automatically be the same as the instance name without need for extra code.
        # Another object name can also be defined when calling a new class instance
        if objectName == None:
            (filename, line_number, function_name, text) = traceback.extract_stack()[-2]
            objectName = text[:text.find('=')].strip()
        self.setObjectName(objectName)

        # Make shorter variables for alignment
        a = {}
        a["left"] = qc.Qt.AlignLeft
        a["right"] = qc.Qt.AlignRight
        a["top"] = qc.Qt.AlignTop
        a["btm"] = qc.Qt.AlignBottom
        a["hcenter"] = qc.Qt.AlignHCenter
        a["vcenter"] = qc.Qt.AlignVCenter
        a["center"] = qc.Qt.AlignCenter

        # Dictionary with some of the most used stylesheet commands. Also doubles as an init for the stylesheet
        self.style = {}

        if objectName != None:
            self.setObjectName(objectName)
        if color == None:
            self.style["background-color"] = "background-color: rgba(255, 255, 255, 255);"
        else:
            self.style["background-color"] = f"background-color: rgba{color};"
        if textcolor == None:
            self.style["color"] = "color: rgba(255, 255, 255, 255);"
        else:
            self.style["color"] = f"color: rgba{textcolor};"
        if radius==None:
            self.style["border-radius"]    = "border-radius: 0px;"
        else:
            self.style["border-radius"]    = f"border-radius: {radius}px;"
        if text != None:
            self.setText(text)
        if size !=None:
            self.style["font-size"]        =f"font-size: {size}px;"
        if add == True and align==True:
            Master.lay.addWidget(self, 0, a[align])
        elif add == True and align!=True:
            Master.lay.addWidget(self)

        # Create an input mask:
        self.setText("00:00:00")
        self.setInputMask("99:99:99")

        # Define the initial input validator
        self.reg_ex = qc.QRegExp("[0-2]{1}[0-3]{1}" + ":" + "[0-5]{1}[0-9]{1}" + ":" + "[0-5]{1}[0-9]{1}")
        self.input_validator1 = qg.QRegExpValidator(self.reg_ex, self)
        self.setValidator(self.input_validator1)

        # Define the input validator for when the timer is running:
        self.reg_ex2 = qc.QRegExp("[0-9]{2}")
        self.input_validator2 = qg.QRegExpValidator(self.reg_ex2, self)

        # Set the stylesheet
        self.updateStylesheet()

    # Update the stylesheet
    def updateStylesheet(self):

        self.stylesheet = ""
        for i in self.style:

            if self.style[i] != "":

                self.stylesheet += f"{self.style[i]}\n"

            elif self.style[i] == "":

                del self.style[i]

        self.setStyleSheet(self.stylesheet)

    # Make button transparent
    def transp(self):
        self.style["background-color"] = f"background-color:           rgba(0, 0, 0, 0);"
        self.updateStylesheet()
    # Set custom background color
    def bg(self, r, g, b, a):
        self.style["background-color"] = f"background-color:           rgba({r}, {g}, {b}, {a});"
        self.updateStylesheet()
    # Set border radius for all four corners
    def radius(self, radius):
        self.style["border-radius"] = f"border-radius:              {radius}px;"
        self.updateStylesheet()
    # Set custom border radius configuration
    def customradius(self, topleft, topright, bottomright, bottomleft):
        self.style["border-top-left-radius"] = f"border-top-left-radius:     {topleft}px;"
        self.style["border-top-right-radius"] = f"border-top-right-radius:    {topright}px;"
        self.style["border-bottom-right-radius"] = f"border-bottom-right-radius: {bottomright}px;"
        self.style["border-bottom-left-radius"] = f"border-bottom-left-radius:  {bottomleft}px;"
        self.updateStylesheet()
    # Add command to the stylesheet like normally, except here you need a keyword
    def addstyle(self, commandKey, command):
        self.style[commandKey] = command
        self.updateStylesheet()
    # Change object name
    def name(self, name):
        self.lay.setObjectName(name)
    def align(self, alignment):
        if alignment == "hcenter":
            self.setAlignment(qc.Qt.AlignHCenter)
        elif alignment == "reft":
            self.setAlignment(qc.Qt.AlignLeft)
        elif alignment == "right":
            self.setAlignment(qc.Qt.AlignRight)
        elif alignment == "bottom":
            self.setAlignment(qc.Qt.AlignBottom)
        elif alignment == "vcenter":
            self.setAlignment(qc.Qt.AlignVCenter)
        elif alignment == "center":
            self.setAlignment(qc.Qt.AlignCenter)
    def valida(self, validator):
        self.regx = qc.QRegExp(validator)
        self.vali = qg.QRegExpValidator(self.regx, self)
        self.setValidator(self.vali)

class myscroll(qw.QFrame):
    def __init__(self, Master):
        qw.QFrame.__init__(self, Master)
        self.setMinimumSize(qc.QSize(644, 0))
        self.style = {}

        self.style["QScrollBar::handle:vertical:hover"] = "      {background-color: rgba(189, 223, 246,  180);}"
        self.style["QScrollBar::handle:vertical:pressed"] = "    {background-color: rgba(189,223, 246,  100);}"
        self.style["QScrollBar::sub-line:vertical:hover"] = "    {background-color: rgba(255, 0,   127,  0);  }"
        self.style["QScrollBar::sub-line:vertical:pressed"] = "  {background-color: rgba(185, 0,   92,   0);  }"
        self.style["QScrollBar::add-line:vertical:hover"] = "    {background-color: rgba(255, 0,   127,  0);  }"
        self.style["QScrollBar::add-line:vertical:pressed"] = "  {background-color: rgba(185, 0,   92,   0);  }"
        self.style["QScrollBar::sub-page:vertical"] = "          {background-color: rgba(0,   0,   0,    120);}"
        self.style["QScrollBar::add-page:vertical"] = "          {background-color: rgba(0,   0,   123,  120);}"
        self.style["QScrollBar::sub-line:vertical"] = "          {background-color: rgba(59,  59,  90,   120);     height: 0px;         border: none;  }"
        self.style["QScrollBar::add-line:vertical"] = "          {background-color: rgba(59,  59,  90,   0);       height: 0px;         border: none;  }"
        self.style["QScrollBar::handle:vertical"] = "            {background-color: rgba(0,   0,   0,    120);     min-height: 30px;    max-height: 5px;   border-radius: 4px;  }"
        self.style["QScrollBar:vertical"] = ("""                 {background:       rgba(0,   0,   0,    80);      width: 10px;          border: none;                
                                                                                                                  margin: 0px 0 0px 0; border-radius: 0px;  }""")
        self.style["QScrollBar::up-arrow:vertical"] = "          {background: none;}"
        self.style["QScrollBar::down - arrow: vertical"] = "     {background:none;}"
        self.style["QScrollBar::add-page:vertical"] = "          {background:none;}"
        self.style["QScrollBar::sub-page:vertical"] = "          {background: none;}"

        self.stylesheet = ""
        for i in self.style:
            self.stylesheet += f"{i}{self.style[i]}\n"

        self.setStyleSheet(self.stylesheet)


    
        self.setFrameShape(qw.QFrame.StyledPanel)
        self.setFrameShadow(qw.QFrame.Raised)
        self.setObjectName("contents")
    
        # Configure the layout for the content frame
        self.contentsLay = qw.QVBoxLayout(self)
        self.contentsLay.setContentsMargins(0, 0, 0, 0)
        self.contentsLay.setObjectName("contentsLay")
    
        # Create the scrolling area
        self.scrollarea = qw.QScrollArea(self)
        self.scrollarea.setStyleSheet("""QScrollArea    {background-color:rgba(0,0,0,0);     border-radius:15px;     border: 0px solid;}
                                                 QScrollBar::add-page:vertical, QScrollBar::sub-page:verticall              {background-color:rgba(0,0,0,0);}""")
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setObjectName("scrollarea")
    
        # Create the scrolling widget
        self.scrollwidget = qw.QWidget()
        self.scrollwidget.setGeometry(qc.QRect(0, 0, 880, 149))
        self.scrollwidget.setStyleSheet("background-color:rgba(0,0,0,0);")
        self.scrollwidget.setObjectName("scrollwidget")
    
        # Create layout for scrolling wisget
        self.scrollwidgetLay = qw.QVBoxLayout(self.scrollwidget)
        self.scrollwidgetLay.setContentsMargins(0, 0, 0, 0)
        self.scrollwidgetLay.setSpacing(0)
        self.scrollwidgetLay.setObjectName("scrollwidgetLay")
    
        # Create the scrolling frame
        self.scrollframe = qw.QFrame(self.scrollwidget)
        self.scrollframe.setMinimumSize(qc.QSize(0, 0))
        self.scrollframe.setStyleSheet("QFrame#scrollframe{background:none;}")
        self.scrollframe.setFrameShape(qw.QFrame.StyledPanel)
        self.scrollframe.setFrameShadow(qw.QFrame.Raised)
        self.scrollframe.setObjectName("scrollframe")
    
        # Create the scrolling frame layout
        self.scrollframeLay = qw.QVBoxLayout(self.scrollframe)
        self.scrollframeLay.setContentsMargins(0, 0, 11, 0)
        self.scrollframeLay.setSpacing(1)
        self.scrollframeLay.setObjectName("scrollframeLay")
        self.scrollframeLay.setAlignment(qc.Qt.AlignTop)
        self.scrollwidgetLay.addWidget(self.scrollframe)
        self.scrollarea.setWidget(self.scrollwidget)
        self.contentsLay.addWidget(self.scrollarea)

        self.scrollbar = self.scrollarea.verticalScrollBar()
        self.scrollbar.installEventFilter(self)

    def eventFilter(self, o, e):
        if o is self.scrollbar:
            if e.type() == qc.QEvent.Show:
                self.scrollframeLay.setContentsMargins(0, 0, 1, 0)
            elif e.type() == qc.QEvent.Hide:
                self.scrollframeLay.setContentsMargins(0, 0, 11, 0)
                qw.QApplication.processEvents()
        return False

class mystack(qw.QStackedWidget):

    def __init__(self, Master, layoutType=None, objectName=None, radius=None, color=None, align=None, add=None):

        global a

        qw.QStackedWidget.__init__(self, Master)

        # This snippet of code peeks back into the code used to call each specific instance of this class.
        # This was the object name can automatically be the same as the instance name without need for extra code.
        # Another object name can also be defined when calling a new class instance

        self.setObjectName(objectName)

        # Dictionary with some of the most used stylesheet commands. Also doubles as an init for the stylesheet
        self.style = {}

        # Init frame as transparent and without border-radius
        if color == None:
            self.style["background-color"]          = "background-color: rgba(0, 0, 0, 0);"
        else:
            self.style["background-color"]          = f"background-color: rgba{color};"
        if radius == None:
            self.style["border-radius"]             = "border-radius:              0px;"  # Regular border radius
        else:
            self.style["border-radius"]             = f"border-radius:             {radius}px;"  # Regular border radius
        if add == True and align!=None:
            Master.lay.addWidget(self, 0, a[align])
        elif add == True and align==None:
            Master.lay.addWidget(self)
        # Set the stylesheet
        self.updateStylesheet()

        # Create dict with stacked objects
        self.stacks = {}


    # Update the stylesheet
    def updateStylesheet(self):

        self.stylesheet = "QStackedWidget"+"{\n"
        for i in self.style:

            if self.style[i] != "":

                self.stylesheet += f"{self.style[i]}\n"

            elif self.style[i] == "":

                del self.style[i]

        self.stylesheet += "}"

        self.setStyleSheet(self.stylesheet)


    def addstack(self,  widget, widgetName):

        self.stacks[widgetName] = widget
        self.addWidget(self.stacks[widgetName])


    
