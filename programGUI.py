from    customQtWidgets         import  *
from    PyQt5.QtGui             import  QGuiApplication, QCursor
from    BlurWindow.blurWindow   import  blur
from    dataAnalyse             import  Data
from    datetime                import  *
import  numpy                   as      np


# The central unit of the GUI
class Main(qw.QMainWindow):
    def __init__(self, tilmargin: int, framargin: int, filnavn: str):

        # Bool to know if the window is maximized or normal
        self.maximized = False

        # initialize the main window, remove frames, make translucent, set size
        qw.QMainWindow.__init__(self)
        self.setWindowFlags(qc.Qt.FramelessWindowHint)
        self.setAttribute(qc.Qt.WA_TranslucentBackground)
        self.resize(1500//2, 1000//2)

        # Blur window
        hWnd = self.winId()
        blur(hWnd)
        blur(False)

        # Run the gui init
        GUI.init(self, tilmargin, framargin, filnavn)

        # Link some functions
        self.mainframe["1"].mouseMoveEvent = self.moveWindow
        functions.buttonconfig(self)

    # Make sure the window can be moved
    def moveWindow(self, event):
        if event.buttons() == qc.Qt.LeftButton:
            if self.maximized == True and event.globalPos().y() > 0:
                functions.max_restore(self)
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

    # Define function every time the mouse is pressed
    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        desktop = QGuiApplication.primaryScreen().availableGeometry()
        if self.pos().y() <= desktop.y() and QCursor.pos().y() <= 0:
            if self.maximized == False:
                functions.max_restore(self)

# The main frame containing the sub-elements of the gui
class GUI(Main):
    def init(self, tilmargin, framargin, filename):

        #### Init a centralwidget, add to main, init central frame, add to central widget
        self.cw = mywidget(self, "v", radius=10)
        self.cf = myframe(self.cw, "v", "cf", add=True, radius=10, color=(0, 0, 0, 200))
        self.setCentralWidget(self.cw)  # ,  self.cf.addstyle("image", "border-image: url(:/images/Background3.jpg);")

        #### Create 4 main frames
        mainframe = {}
        for i in range(1, 5):
            mainframe[str(i)] = myframe(self.cf, "h", f"mainframe{i}", add=True)

        mainframe["1"].customradius(9, 9, 0, 0), mainframe["1"].setFixedHeight(30), mainframe["1"].bg(0, 0, 0, 100)
        mainframe["4"].customradius(0, 0, 10, 10), mainframe["4"].setFixedHeight(10), mainframe["2"].margins(10, 10, 10, 0)
        mainframe["2"].spacing(10), mainframe["3"].margins(10, 10, 10, 10), mainframe["3"].setMinimumHeight(150)
        mainframe["3"].setMinimumHeight(350)
        self.mainframe = mainframe

        frameen = myframe(mainframe["3"], "h", "framen", add=True, radius=10, color=(0,0,0,120))
        frameen.setContentsMargins(10, 10, 10, 10)
        teksten = qw.QTextEdit(frameen)
        font = qg.QFont('Roboto', 8)
        teksten.setFont(font)
        frameen.lay.addWidget(teksten)
        teksten.setVerticalScrollBarPolicy(qc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        frameen.setStyleSheet("color: 'white';")
        teksten.setReadOnly(True)

        self.teksten = teksten

        #### Create 3 frames in the top mainframe
        topframe = {}
        for i in range(1, 4):
            topframe[str(i)] = myframe(mainframe["1"], "h", f"topframe{i}", add=True)

        topframe["3"].setFixedWidth(200), topframe["3"].margins(135, 0, 0, 0)
        topframe["1"].customradius(0, 0, 10, 0), topframe["1"].setFixedWidth(500)
        self.topframe = topframe

        #### Create three buttons in the top right frame, set radius, individual colors, hover- and pressed color
        button = {}
        for i in range(1, 4):
            button[str(i)] = mybutton(topframe["3"], objectName=f"button{i}", radius=7, add=True, align="center")
            button[str(i)].setFixedSize(14, 14)

        button["1"].bg(255, 255, 0, 255), button["1"].hcolor(255, 255, 0, 150), button["1"].pcolor(255, 255, 0, 50)
        button["2"].bg(0, 255, 0, 255), button["2"].hcolor(0, 255, 0, 150), button["2"].pcolor(0, 255, 0, 50)
        button["3"].bg(255, 0, 0, 255), button["3"].hcolor(255, 0, 0, 150), button["3"].pcolor(255, 0, 0, 50)
        self.button = button

        #### Create a title label
        title = mylabel(topframe["1"], font=("Roboto", "Light", 100), size=15, text="Kollektiv- eSpark- og værdata for Kolsås Stasjon 2022",
                        add=True, align="left")
        topframe["1"].margins(10, 0, 0, 0)

        #### Create a schedule in the top middle frame from the Schedule() class
        self.schedule = Schedule(mainframe["2"], self, filename, "v", "sched", add=True, tekst=self.teksten, tilmargin=tilmargin, framargin=framargin)

        #### Create 2 frames in the bottom mainframe
        btmframe = {}
        for i in range(1, 3):
            btmframe[str(i)] = myframe(mainframe["4"], "v", f"btmframe{i}", add=True)
        btmframe["2"].setFixedWidth(20)

        #### Create a label with credits
        credits = mylabel(btmframe["1"], text="Av: Magnus Støleggen",
                          font=("Roboto", "Italic", 50), size=8, add=True, color=(255, 255, 255, 100))
        btmframe["1"].margins(5, 0, 0, 0)

        #### Add size-grip to the bottom right corner
        sizegrip = qw.QSizeGrip(btmframe["2"])
        sizegrip.setStyleSheet("background-color: rgba(0,0,0,0);"), btmframe["2"].lay.addWidget(sizegrip, 0,
                                                                                                qc.Qt.AlignBottom)

# The frame that displays text and buttons and such
class Schedule(myframe):
    def __init__(self, Master, Main, filnavn,  *args, tekst=None, tilmargin=None, framargin=None, **kwargs ):
        myframe.__init__(self, Master, *args, **kwargs)

        self.data = Data(tilmargin, framargin, filnavn)

        #### Create central frame and add it to master layout
        scf = myframe(self, "v", radius=10, add=True)


        #### Create 7 content frames within the central frame
        contframe = {}
        for i in range(1, 8):
            contframe[str(i)] = myframe(scf, "h", f"contframe{i}", color=(0, 0, 0, 60), add=True)

        contframe["1"].customradius(8, 8, 0, 0), contframe["1"].setFixedHeight(50), contframe["5"].setFixedHeight(25)
        contframe["5"].transp(), contframe["7"].setFixedHeight(15), contframe["7"].customradius(0, 0, 10, 10)
        contframe["1"].bg(0, 0, 0, 120), contframe["7"].margins(0, 0, 0, 0)
        contframe["4"].setFixedHeight(50)

        # 1st frame
        # Subframes
        fromInputFrame  =   myframe(contframe["1"], "h", "fromInputFrame", add = True, color = (0,0,0,0) )
        butframe = myframe(contframe["1"], "h", "butframe", add=True, color=(0, 0, 0, 0))
        butframe.spacing(3)
        toInputFrame    =   myframe(contframe["1"], "h", "toInputFrame", add = True, color = (0,0,0,0) )

        self.timeknapp       =   mybutton(butframe, objectName="timeknapp", add=True, color=(255,255,255, 255), radius=5,
                                     text="time", hover=(255,255,255,100), pressed=(255,255,255,60), size=8)
        self.timeknapp.setMinimumWidth(40)
        self.timeknapp.setMinimumHeight(30)
        self.dagknapp        =   mybutton(butframe, objectName="dagknapp", add=True, color=(255,255,255, 255), radius=5,
                                     text="Dag", hover=(255,255,255,100), pressed=(255,255,255,60), size=8)
        self.dagknapp.setMinimumWidth(40)
        self.dagknapp.setMinimumHeight(30)
        self.ukeknapp        =   mybutton(butframe, objectName="ukeknapp", add=True, color=(255,255,255, 255), radius=5,
                                     text="Uke", hover=(255,255,255,100), pressed=(255,255,255,60), size=8)
        self.ukeknapp.setMinimumWidth(40)
        self.ukeknapp.setMinimumHeight(30)

        self.uke=False
        self.time=False

        self.timeknapp.clicked.connect(lambda: self.timePressed())
        self.dagknapp.clicked.connect(lambda: self.dagPressed())
        self.ukeknapp.clicked.connect(lambda: self.ukePressed())

        fromInputFrame.margins(5, 0, 5, 0)
        toInputFrame.margins(5, 0, 5, 0)

        # Inputs

        fromInput = myinput(    fromInputFrame,     "fromInput",                    color=(255, 255, 255, 255),
                                add=True,           textcolor = (0, 0, 0, 255),     size=15)
        fromInput.radius(5)
        fromInput.setValidator(None), fromInput.setInputMask(None), fromInput.setMinimumHeight(30)
        fromInput.setPlaceholderText("Fra dato (DD.MM)")

        toInput = myinput(toInputFrame, "toInput", color=(255, 255, 255, 255), add=True,
                            textcolor=(0, 0, 0, 255), size=15)
        toInput.radius(5)
        toInput.setValidator(None), toInput.setInputMask(None), toInput.setMinimumHeight(30)
        toInput.setPlaceholderText("Til dato (DD.MM)")

        self.fromInput, self.toInput = fromInput, toInput

        toInput.returnPressed.connect(lambda: self.printEntries(tekst))
        self.dagPressed()

        directionframe = myframe(contframe["2"], "h", "directionframe", add=True)
        directionframe.spacing(5)
        self.toButton = mybutton(directionframe, objectName="tobutton", add=True, color=(255, 255, 255, 255), radius=5,
                                 text="El-Sparkesykler til Kolsås Stasjon", hover=(255, 255, 255, 100), pressed=(255, 255, 255, 60), size=8)
        self.toButton.setMinimumWidth(40)
        self.toButton.setMinimumHeight(30)
        self.toButton.clicked.connect(lambda: self.toPressed())

        self.fromButton = mybutton(directionframe, objectName="frombutton", add=True, color=(255, 255, 255, 255), radius=5,
                                 text="El-Sparkesykler fra Kolsås stasjon", hover=(255, 255, 255, 100), pressed=(255, 255, 255, 60), size=8)
        self.fromButton.setMinimumWidth(40)
        self.fromButton.setMinimumHeight(30)
        self.fromButton.clicked.connect(lambda: self.fromPressed())

        self.bothButton = mybutton(directionframe, objectName="bothbutton", add=True, color=(255, 255, 255, 255), radius=5,
                                 text="El-Sparkesykler fra og til Kolsås stasjon", hover=(255, 255, 255, 100), pressed=(255, 255, 255, 60), size=8)
        self.bothButton.setMinimumWidth(40)
        self.bothButton.setMinimumHeight(30)
        self.bothButton.clicked.connect(lambda: self.bothPressed())

        lageframe   = myframe(contframe["3"], "h", "lageframe", add=True)
        lageframe.margins(0, 5, 0, 5)
        self.lagGraf    =   mybutton(lageframe, objectName="laggraf", add=True, color=(255, 255, 255, 255), radius=5,
                                 text="Lag graf", hover=(255, 255, 255, 100), pressed=(255, 255, 255, 60), size=8)
        self.lagGraf.setFixedWidth(70)
        self.lagGraf.setMinimumHeight(30)
        self.lagGraf.clicked.connect(lambda: self.makegraph())

        self.lagExcel    =   mybutton(lageframe, objectName="lagExcel", add=True, color=(255, 255, 255, 255), radius=5,
                                 text="Lag excelark", hover=(255, 255, 255, 100), pressed=(255, 255, 255, 60), size=8)
        self.lagExcel.setFixedWidth(70)
        self.lagExcel.setMinimumHeight(30)
        self.lagExcel.clicked.connect(lambda: self.makeExcel())

        self.prmin    =   mybutton(lageframe, objectName="prmin", add=True, color=(255, 255, 255, 255), radius=5,
                                 text="Elspark pr.min graf", hover=(255, 255, 255, 100), pressed=(255, 255, 255, 60), size=8)
        self.prmin.setFixedWidth(70)
        self.prmin.setMinimumHeight(30)
        self.prmin.clicked.connect(lambda: self.prMin())

        # 2 frame

        avgFrame = myframe(contframe["4"], "h", "avgFrame", add=True, color=(0, 0, 0, 60), radius=0)
        depFrame = myframe(contframe["4"], "h", "depFrame", add=True, color=(0, 0, 0, 60), radius=0)
        avglab   = mylabel(avgFrame, text="Avganger ",  add = True, align="center", size=15)
        deplab   = mylabel(depFrame, text="Ankomster",  add=True, align="center", size=15)
        avgFrame.addstyle("border", "border-right: 2px solid gray; ")
        depFrame.addstyle("border", "border-left: 2px solid gray; ")

        enframe = myframe(contframe["5"], "h", "enframe", color=(0,0,0,0), add=True)
        toframe = myframe(contframe["5"], "h", "toframe", color=(0, 0, 0, 0), add=True)

        #### Create 7 frames in frame 2
        labelframe, labbs = {}, {}
        for i in range(1, 8):
            labelframe[str(i)] = myframe(enframe, "h", f"labelframe{i}", color=(255, 255, 255, 40), add=True)
            if i < 7:
                labelframe[str(i)].addstyle("border", "border-right: 1px solid gray; " )
            labbs[str(i)] = mylabel(labelframe[str(i)], "h", f"labbsframe{i}", add=True, font=("Roboto", "Normal", 100))
            labbs[str(i)].addstyle("color", "color: rgb(255,255,255);"), labelframe[str(i)].margins(5, 0, 0, 0)

        labelframe["7"].addstyle("border", "border-right: 2px solid gray; ")
        labbs["1"].setText("Dato"),             labelframe["1"].setFixedWidth(60)
        labbs["2"].setText("Planlagt    |    Faktisk:"),         labelframe["2"].setMinimumWidth(130)
        labbs["3"].setText("Påstigende:"),      labelframe["3"].setMinimumWidth(85)
        labbs["4"].setText("Sparkesykler:"),  labelframe["4"].setMinimumWidth(90)
        labbs["5"].setText("Temp (C):"), labelframe["5"].setMinimumWidth(80)
        labbs["6"].setText("Vind (m/s):"),      labelframe["6"].setMinimumWidth(80)
        labbs["7"].setText("Nedbør (mm/t):"), labelframe["7"].setMinimumWidth(100)

        #### Create 7 frames in frame 4
        labelframe, labbs = {}, {}
        for i in range(1, 8):
            labelframe[str(i)] = myframe(toframe, "h", f"labelframe{i}", color=(255, 255, 255, 40), add=True)
            if i < 7:
                labelframe[str(i)].addstyle("border", "border-right: 1px solid gray; " )
            labbs[str(i)] = mylabel(labelframe[str(i)], "h", f"labbsframe{i}", add=True, font=("Roboto", "Normal", 100))
            labbs[str(i)].addstyle("color", "color: rgb(255,255,255);"), labelframe[str(i)].margins(5, 0, 0, 0)

        labelframe["1"].addstyle("border", "border-left: 2px solid gray; border-right: 1px solid gray; ")
        labbs["1"].setText("Dato"), labelframe["1"].setFixedWidth(60)
        labbs["2"].setText("Planlagt    |    Faktisk :"), labelframe["2"].setMinimumWidth(130)
        labbs["3"].setText("Avstigende:"), labelframe["3"].setMinimumWidth(85)
        labbs["4"].setText("Sparkesykler:"), labelframe["4"].setMinimumWidth(90)
        labbs["5"].setText("Temp (C):"), labelframe["5"].setMinimumWidth(80)
        labbs["6"].setText("Vind (m/s):"), labelframe["6"].setMinimumWidth(80)
        labbs["7"].setText("Nedbør (mm/t):"), labelframe["7"].setMinimumWidth(100)

        self.scrollarea = myscroll(contframe["6"])
        contframe["6"].lay.addWidget(self.scrollarea)

        self.display = Schedentry(self.scrollarea.scrollframe, "h", f"ja{1}")

        self.scrollarea.scrollframeLay.addWidget(self.display)

        self.bothPressed()


    def printEntries(self, tekst):

        try:

            if self.uke:
                nrWeeks = int(self.toInput.text()) - int(self.fromInput.text()) + 1

                # Create a datetime object for the first day of the year
                jan1 = datetime(2022, 1, 1)

                # Calculate the number of days to Monday of the first week
                daysToMonday = (7 - jan1.weekday()) % 7

                # Calculate the number of days to Monday of the desired week
                daysToFromWeek = daysToMonday + ( (int(self.fromInput.text()) - 1) * 7 )

                # Create a datetime object for Monday of the desired week
                fromDate = jan1 + timedelta(days=daysToFromWeek)


                nrDays = (7*nrWeeks) - 1
                # Create a datetime object for Sunday of the last week
                toDate = fromDate + timedelta( days = nrDays)

                if self.toInput.text() == "52":
                    toDate = datetime( 2022, 12, 31)

                fromDate = fromDate.strftime('%d.%m')
                toDate   = toDate.strftime('%d.%m')

                print(fromDate, toDate)

            else:
                fromDate    =   self.fromInput.text()
                toDate      =   self.toInput.text()

            arrivals    =   self.data.iterateThroughArrivals(  "Arrivals",    fromDate, toDate  )
            departures  =   self.data.iterateThroughArrivals(  "Departures", fromDate, toDate  )

            fradato = datetime(2022, int(fromDate[3:]), int(fromDate[:2]))
            todato = datetime(  2022, int(toDate[3:]), int(toDate[:2]))

            if todato < fradato:
                return

        except:

            return


        if len(  arrivals  ) > len(  departures  ):

            lengste     =   len(  arrivals  )

        elif len( departures  )  >  len(  arrivals  ):

            lengste     =   len(  departures  )

        else:

            lengste     =   len(  arrivals  )



        format = "<style> p { line-height: 125%; } </style>"
        tom    = "<p>&nbsp;</p>"
        tidavg          =   ""
        tidank          =   ""
        datoavg         =   ""
        datoank         =   ""
        avst            =   ""
        past            =   ""
        elsavg          =   ""
        elsank          =   ""
        tempank         =   ""
        tempavg         =   ""
        vindavg         =   ""
        vindank         =   ""
        regnavg         =   ""
        regnank         =   ""

        lastDate = fradato
        noerart = True
        lastank = lastDate
        lastavg = lastDate
        indeksavg = 0
        indeksank = 0
        counteravg = 0
        counterank = 0


        while noerart:

            for i in range( indeksavg, lengste ):

                try:

                    if i == lengste - 1:
                        noerart = False

                    if departures[i].actualTime.date() != lastavg.date():

                        lastavg = departures[i].actualTime
                        indeksavg = i

                        datoavg += "<p><hr></p>"
                        tidavg += "<p><hr></p>"
                        past += "<p><hr></p>"
                        elsavg += "<hr>"
                        tempavg += "<p><hr></p>"
                        vindavg += "<p><hr></p>"
                        regnavg += "<p><hr></p>"

                        break


                    datoavg += f"<p>{departures[i].actualTime.strftime('%d.%m')}</p>"
                    tidavg  += f"<p>{departures[i].scheduledTime.strftime('%H:%M:%S')}&nbsp;&nbsp;|&nbsp;&nbsp;{departures[i].actualTime.strftime('%H:%M:%S')}</p>"
                    if departures[i].passengers != 0:
                        past    += f"<p>{departures[i].passengers}</p>"
                    else:
                        past += tom
                    if departures[i].eScooters != 0:
                        elsavg  += f"<p>{departures[i].eScooters}</p>"
                    else:
                        elsavg += tom
                    tempavg += f"<p>{departures[i].temperature}</p>"
                    vindavg += f"<p>{departures[i].wind}</p>"
                    if departures[i].rain != 0:
                        regnavg += f"<p>{departures[i].rain}</p>"
                    else:
                        regnavg += tom

                except:

                    pass

                counteravg += 1


            for i in range( indeksank, lengste ):

                try:
                    if arrivals[i].actualTime.date() != lastank.date():

                        lastank = arrivals[i].actualTime
                        indeksank = i

                        datoank += "<p><hr></p>"
                        tidank += "<p><hr></p>"
                        avst += "<p><hr></p>"
                        elsank += "<p><hr></p>"
                        tempank += "<p><hr></p>"
                        vindank += "<p><hr></p>"
                        regnank += "<p><hr></p>"

                        break


                    datoank += f"<p>{arrivals[i].actualTime.strftime('%d.%m')}</p>"
                    tidank  += f"<p>{arrivals[i].scheduledTime.strftime('%H:%M:%S')}&nbsp;&nbsp;|&nbsp;&nbsp;{arrivals[i].actualTime.strftime('%H:%M:%S')}</p>"
                    if arrivals[i].passengers != 0:
                        avst    += f"<p>{arrivals[i].passengers}</p>"
                    else:
                        avst += tom
                    if arrivals[i].eScooters != 0:
                        elsank  += f"<p>{arrivals[i].eScooters}</p>"
                    else:
                        elsank += tom
                    tempank += f"<p>{arrivals[i].temperature}</p>"
                    vindank += f"<p>{arrivals[i].wind}</p>"
                    if arrivals[i].rain != 0:
                        regnank += f"<p>{arrivals[i].rain}</p>"
                    else:
                        regnank += tom
                except:

                    pass

                counterank += 1

            if counterank > counteravg:

                times = counterank - counteravg

                datoavg += ( tom * (times - 1) ) + "<p><hr></p>"
                tidavg += ( tom * (times - 1) ) + "<p><hr></p>"
                past += ( tom * (times - 1) ) + "<p><hr></p>"
                elsavg += ( tom * (times - 1) ) + "<p><hr></p>"
                tempavg += ( tom * (times - 1) ) + "<p><hr></p>"
                vindavg += ( tom * (times - 1) ) + "<p><hr></p>"
                regnavg += ( tom * (times - 1) ) + "<p><hr></p>"

            elif counteravg > counterank:
                times = counterank - counteravg

                datoank += ( tom * (times - 1) ) + "<p><hr></p>"
                tidank += ( tom * (times - 1) ) + "<p><hr></p>"
                avst += ( tom * (times - 1) ) + "<p><hr></p>"
                elsank += ( tom * (times - 1) ) + "<p><hr></p>"
                tempank += ( tom * (times - 1) ) + "<p><hr></p>"
                vindank += ( tom * (times - 1) ) + "<p><hr></p>"
                regnank += ( tom * (times - 1) ) + "<p><hr></p>"

            counteravg = 0
            counterank = 0


        self.display.labels["1"].setHtml(format + datoavg)
        self.display.labels["2"].setHtml(format + tidavg)
        self.display.labels["3"].setHtml(format + past )
        self.display.labels["4"].setHtml(format + elsavg )
        self.display.labels["5"].setHtml(format + tempavg )
        self.display.labels["6"].setHtml(format + vindavg )
        self.display.labels["7"].setHtml(format + regnavg )
        self.display.labels["8"].setHtml(format + datoank )
        self.display.labels["9"].setHtml(format + tidank )
        self.display.labels["10"].setHtml(format + avst )
        self.display.labels["11"].setHtml(format + elsank )
        self.display.labels["12"].setHtml(format + tempank )
        self.display.labels["13"].setHtml(format + vindank )
        self.display.labels["14"].setHtml(format + regnank )

        translate   =   \
            {
                "to"    :   ["til", "påstigende", "avganger"],
                "from"  :   ["fra" "avstigende", "ankomster"],
                "both"  :   ["til og fra", "på- og avstigende", "avganger og -ankomster"]
            }

        time        =   \
            {
                "hour"  :   "Timer",
                "day"   :   "Dato",
                "week"  :   "Ukedager"
            }

        if self.dag:

            scooters, passengers, percentages, _, spesCoeff, allRides  = \
                self.data.plotDays(fromDate, toDate)

            averageScooters     =   round( np.sum( np.array( scooters["both"]    ) ) / len( scooters["both"]    ), 2 )
            averageScootersTo   =   round( np.sum( np.array( scooters["to"]    ) ) / len( scooters["to"]    ), 2 )
            averageScootersFrom =   round( np.sum( np.array( scooters["from"]    ) ) / len( scooters["from"]    ), 2 )
            averagePassengers   =   round( np.sum( np.array( passengers["both"]  ) ) / len( passengers["both"]  ), 2 )
            averagePassengersTo   =   round( np.sum( np.array( passengers["to"]  ) ) / len( passengers["to"]  ), 2 )
            averagePassengersFrom   =   round( np.sum( np.array( passengers["from"]  ) ) / len( passengers["from"]  ), 2 )
            percentage          =   round( np.sum( np.array( percentages["both"] ) ) / len( percentages["both"] ), 2 )
            percentageTo          =   round( np.sum( np.array( percentages["to"] ) ) / len( percentages["to"] ), 2 )
            percentageFrom          =   round( np.sum( np.array( percentages["from"] ) ) / len( percentages["from"] ), 2 )

            tekst.setHtml(
                f"<p><u>Samlede faktiske verdier for hele perioden {fromDate} - {toDate}: </u></p>"
                f"<p>&nbsp;</p>"
                f"<p>Alle El-Sparkesykler til og fra Kolsås stasjon: {allRides['both']['total']}</p>"
                f"<p>Alle El-Sparkesykler til Kolsås stasjon: {allRides['to']['total']}</p>"
                f"<p>Alle El-Sparkesykler fra Kolsås stasjon: {allRides['from']['total']}</p>"
                f"<p>Alle El-Sparkesykler til og fra Kolsås stasjon relatert til T-bane: {allRides['both']['related']}</p>"
                f"<p>Alle El-Sparkesykler til Kolsås stasjon relatert til T-bane: {allRides['to']['related']}</p>"
                f"<p>Alle El-Sparkesykler fra Kolsås stasjon relatert til T-bane: {allRides['from']['related']}</p>"
                f"<p>Alle El-Sparkesykler til og fra Kolsås stasjon urelatert til T-bane: {allRides['both']['unrelated']}</p>"
                f"<p>Alle El-Sparkesykler til Kolsås stasjon urelatert til T-bane: {allRides['to']['unrelated']}</p>"
                f"<p>Alle El-Sparkesykler fra Kolsås stasjon urelatert til T-bane: {allRides['from']['unrelated']}</p>"
                f"<p>Prosent El-Sparkesykler til og fra Kolsås stasjon relatert til T-bane: {allRides['both']['percentage']} %</p>"
                f"<p>Prosent El-Sparkesykler til Kolsås stasjon relatert til T-bane: {allRides['to']['percentage']} %</p>"
                f"<p>Prosent El-Sparkesykler fra Kolsås stasjon relatert til T-bane: {allRides['from']['percentage']} %</p>"
                f"<p>&nbsp;</p>"
                f"<p><u>Korrelasjon mellom antall passasjerer og antall sparkesykkelturer regnet ut dag for dag for alle dager i perioden:</u></p>"
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Pearson's korrelasjon:</p>"
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {spesCoeff['eScootPass']['Pearson'][0]} (p-verdi: {spesCoeff['eScootPass']['Pearson'][1]})</p>"
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {spesCoeff['eScootFromPassTo']['Pearson'][0]} (p-verdi: {spesCoeff['eScootFromPassTo']['Pearson'][1]})</p>"
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {spesCoeff['eScootToPassFrom']['Pearson'][0]} (p-verdi: {spesCoeff['eScootToPassFrom']['Pearson'][1]})</p>" 
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Spearman's rank korrelasjon:</p>"
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {spesCoeff['eScootPass']['Spearman'][0]} (p-verdi: {spesCoeff['eScootPass']['Spearman'][1]})</p>"
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {spesCoeff['eScootFromPassTo']['Spearman'][0]} (p-verdi: {spesCoeff['eScootFromPassTo']['Spearman'][1]})</p>"
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {spesCoeff['eScootToPassFrom']['Spearman'][0]} (p-verdi: {spesCoeff['eScootToPassFrom']['Spearman'][1]})</p>" 
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Kendalls's tau korrelasjon:</p>"
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {spesCoeff['eScootPass']['Kendall'][0]} (p-verdi: {spesCoeff['eScootPass']['Kendall'][1]})</p>"
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {spesCoeff['eScootFromPassTo']['Kendall'][0]} (p-verdi: {spesCoeff['eScootFromPassTo']['Kendall'][1]})</p>"
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {spesCoeff['eScootToPassFrom']['Kendall'][0]} (p-verdi: {spesCoeff['eScootToPassFrom']['Kendall'][1]})</p>" 
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Gammakorrelasjon:</p>"
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {spesCoeff['eScootPass']['Gamma'][0]} (p-verdi: {spesCoeff['eScootPass']['Gamma'][1]})</p>"
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {spesCoeff['eScootFromPassTo']['Gamma'][0]} (p-verdi: {spesCoeff['eScootFromPassTo']['Gamma'][1]})</p>"
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {spesCoeff['eScootToPassFrom']['Gamma'][0]} (p-verdi: {spesCoeff['eScootToPassFrom']['Gamma'][1]})</p>" 
                f"<p>&nbsp;</p>"
                f"<p><u>Gjennomsnittsverdier pr. dag for perioden {fromDate} - {toDate}:</u></p>"
                f"<p>&nbsp;</p>"
    
                f"<p>Passasjerer på- og avstigende: {averagePassengers}"
                f"<p>Passasjerer avstigende       : {averagePassengersTo}</p>"
                f"<p>Passasjerer påstigende       : {averagePassengersFrom}</p>"
    
                f"<p>T-banerelaterte El-Sparkesykler til og fra stasjonen       : {averageScooters} "
                f"<p>T-banerelaterte El-Sparkesykler til stasjonen: {averageScootersTo} "
                f"<p>T-banerelaterte El-Sparkesykler fra stasjonen: {averageScootersFrom} "

                f"<p>T-banerelaterte El-Sparkesykler til og fra stasjonen ift. av- og påstigende passasjerer: {percentage} % "
                f"<p>T-banerelaterte El-Sparkesykler til stasjonen ift. påstigende passasjerer: {percentageTo} % "
                f"<p>T-banerelaterte El-Sparkesykler fra stasjonen ift. avstigende passasjerer: {percentageFrom} % "

                f"<p>&nbsp;</p>" )

        elif self.uke:


            scooters, passengers, percentages, _,  correlation, spesCoeff, allRides = self.data.plotAverageWeekday(self.fromInput.text(), self.toInput.text())


            noe = {"both" : ["til og fra", "Av- og påstigende", "av- og påstigende"],
                   "to"   : ["til", "Påstigende", "påstigende"],
                   "from" : ["fra", "Avstigende", "avstigende"]}
            dager =["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]
            dagg = ["Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn"]

            firstline = \
                f"<p><u>Samlede faktiske verdier for hele perioden uke {self.fromInput.text()} - {self.toInput.text()}: </u></p>"\
            f"<p>&nbsp;</p>"\
            f"<p>Alle El-Sparkesykler til og fra Kolsås stasjon: {allRides['both']['total']}</p>"\
            f"<p>Alle El-Sparkesykler til Kolsås stasjon: {allRides['to']['total']}</p>"\
            f"<p>Alle El-Sparkesykler fra Kolsås stasjon: {allRides['from']['total']}</p>"\
            f"<p>Alle El-Sparkesykler til og fra Kolsås stasjon relatert til T-bane: {allRides['both']['related']}</p>"\
            f"<p>Alle El-Sparkesykler til Kolsås stasjon relatert til T-bane: {allRides['to']['related']}</p>"\
            f"<p>Alle El-Sparkesykler fra Kolsås stasjon relatert til T-bane: {allRides['from']['related']}</p>"\
            f"<p>Alle El-Sparkesykler til og fra Kolsås stasjon urelatert til T-bane: {allRides['both']['unrelated']}</p>"\
            f"<p>Alle El-Sparkesykler til Kolsås stasjon urelatert til T-bane: {allRides['to']['unrelated']}</p>"\
            f"<p>Alle El-Sparkesykler fra Kolsås stasjon urelatert til T-bane: {allRides['from']['unrelated']}</p>"\
            f"<p>Prosent El-Sparkesykler til og fra Kolsås stasjon relatert til T-bane: {allRides['both']['percentage']} %</p>"\
            f"<p>Prosent El-Sparkesykler til Kolsås stasjon relatert til T-bane: {allRides['to']['percentage']} %</p>"\
            f"<p>Prosent El-Sparkesykler fra Kolsås stasjon relatert til T-bane: {allRides['from']['percentage']} %</p>"\
            f"<p>&nbsp;</p>"\
\
            f"<p><u>Korrelasjon mellom antall passasjerer og antall sparkesykkelturer regnet ut dag for dag for alle dager i perioden:</u></p>"\
            f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Pearson's korrelasjon:</p>"\
            f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {correlation['eScootPass']['Pearson'][0]} (p-verdi: {correlation['eScootPass']['Pearson'][1]})</p>"\
            f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {correlation['eScootFromPassTo']['Pearson'][0]} (p-verdi: {correlation['eScootFromPassTo']['Pearson'][1]})</p>"\
            f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {correlation['eScootToPassFrom']['Pearson'][0]} (p-verdi: {correlation['eScootToPassFrom']['Pearson'][1]})</p>"\
            f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Spearman's rank korrelasjon:</p>"\
            f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {correlation['eScootPass']['Spearman'][0]} (p-verdi: {correlation['eScootPass']['Spearman'][1]})</p>"\
            f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {correlation['eScootFromPassTo']['Spearman'][0]} (p-verdi: {correlation['eScootFromPassTo']['Spearman'][1]})</p>"\
            f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {correlation['eScootToPassFrom']['Spearman'][0]} (p-verdi: {correlation['eScootToPassFrom']['Spearman'][1]})</p>"\
        f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Kendalls's tau korrelasjon:</p>"\
        f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {correlation['eScootPass']['Kendall'][0]} (p-verdi: {correlation['eScootPass']['Kendall'][1]})</p>"\
        f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {correlation['eScootFromPassTo']['Kendall'][0]} (p-verdi: {correlation['eScootFromPassTo']['Kendall'][1]})</p>"\
        f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {correlation['eScootToPassFrom']['Kendall'][0]} (p-verdi: {correlation['eScootToPassFrom']['Kendall'][1]})</p>"\
        f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Gammakorrelasjon:</p>"\
        f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {correlation['eScootPass']['Gamma'][0]} (p-verdi: {correlation['eScootPass']['Gamma'][1]})</p>"\
        f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {correlation['eScootFromPassTo']['Gamma'][0]} (p-verdi: {correlation['eScootFromPassTo']['Gamma'][1]})</p>"\
        f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {correlation['eScootToPassFrom']['Gamma'][0]} (p-verdi: {correlation['eScootToPassFrom']['Gamma'][1]})</p>" \
\
        f"<p><u>Gjennomsnittsverdier pr. ukedag uke {self.fromInput.text()} - {self.toInput.text()}</u></p>" \
                        f"<p>&nbsp;</p>" \


            index = 0
            for dag in dager:
                firstline += f"<p><u>{dag}:</u></p>" \
                \
                f"<p>Passasjerer på- og avstigende: {passengers['both'][index]}" \
                f"<p>Passasjerer avstigende       : {passengers['to'][index]}</p>" \
                f"<p>Passasjerer påstigende       : {passengers['from'][index]}</p>" \
 \
                f"<p>T-banerelaterte El-Sparkesykler til og fra stasjonen       : {scooters['both'][index]} " \
                f"<p>T-banerelaterte El-Sparkesykler til stasjonen: {scooters['to'][index]} " \
                f"<p>T-banerelaterte El-Sparkesykler fra stasjonen: {scooters['from'][index]} " \
 \
                f"<p>T-banerelaterte El-Sparkesykler til og fra stasjonen ift. av- og påstigende passasjerer: {percentages['both'][index]} % " \
                f"<p>T-banerelaterte El-Sparkesykler til stasjonen ift. påstigende passasjerer: {percentages['to'][index]} % " \
                f"<p>T-banerelaterte El-Sparkesykler fra stasjonen ift. avstigende passasjerer: {percentages['from'][index]} % " \
\
                f"<p>Korrelasjon mellom antall passasjerer og antall el-sparkesykkelturer" \
                f" regnet ut {dag} for {dag} for alle {dag}er i perioden: </p>"   \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Pearson's korrelasjon:</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {spesCoeff[dagg[index]]['eScootPass']['Pearson'][0]} (p-verdi: {spesCoeff[dagg[index]]['eScootPass']['Pearson'][1]})</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {spesCoeff[dagg[index]]['eScootFromPassTo']['Pearson'][0]} (p-verdi: {spesCoeff[dagg[index]]['eScootFromPassTo']['Pearson'][1]})</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {spesCoeff[dagg[index]]['eScootToPassFrom']['Pearson'][0]} (p-verdi: {spesCoeff[dagg[index]]['eScootToPassFrom']['Pearson'][1]})</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Spearman's rank korrelasjon:</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {spesCoeff[dagg[index]]['eScootPass']['Spearman'][0]} (p-verdi: {spesCoeff[dagg[index]]['eScootPass']['Spearman'][1]})</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {spesCoeff[dagg[index]]['eScootFromPassTo']['Spearman'][0]} (p-verdi: {spesCoeff[dagg[index]]['eScootFromPassTo']['Spearman'][1]})</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {spesCoeff[dagg[index]]['eScootToPassFrom']['Spearman'][0]} (p-verdi: {spesCoeff[dagg[index]]['eScootToPassFrom']['Spearman'][1]})</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Kendalls's tau korrelasjon:</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {spesCoeff[dagg[index]]['eScootPass']['Kendall'][0]} (p-verdi: {spesCoeff[dagg[index]]['eScootPass']['Kendall'][1]})</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {spesCoeff[dagg[index]]['eScootFromPassTo']['Kendall'][0]} (p-verdi: {spesCoeff[dagg[index]]['eScootFromPassTo']['Kendall'][1]})</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {spesCoeff[dagg[index]]['eScootToPassFrom']['Kendall'][0]} (p-verdi: {spesCoeff[dagg[index]]['eScootToPassFrom']['Kendall'][1]})</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Gammakorrelasjon:</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {spesCoeff[dagg[index]]['eScootPass']['Gamma'][0]} (p-verdi: {spesCoeff[dagg[index]]['eScootPass']['Gamma'][1]})</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {spesCoeff[dagg[index]]['eScootFromPassTo']['Gamma'][0]} (p-verdi: {spesCoeff[dagg[index]]['eScootFromPassTo']['Gamma'][1]})</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {spesCoeff[dagg[index]]['eScootToPassFrom']['Gamma'][0]} (p-verdi: {spesCoeff[dagg[index]]['eScootToPassFrom']['Gamma'][1]})</p>" \
                f"<p>&nbsp;</p>"\
                f"<p>&nbsp;</p>"
                index+=1

            tekst.setHtml(firstline)

        elif self.time:

            scooters, passengers, percentages, _, correlation, spesCoeff, allRides = self.data.plotAverageHour(self.fromInput.text(), self.toInput.text())

            noe = {"both" : ["til og fra", "Avstigende og påstigende"],
                   "to"   : ["til", "Påstigende"],
                   "from" : ["fra", "Avstigende"]}
            dager =[4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 8, 19, 20, 21, 22, 23, 0, 1, 2]

            firstline = \
                f"<p><u>Samlede faktiske verdier for hele perioden {self.fromInput.text()} - {self.toInput.text()}: </u></p>" \
                f"<p>&nbsp;</p>" \
                f"<p>Alle El-Sparkesykler til og fra Kolsås stasjon: {allRides['both']['total']}</p>" \
                f"<p>Alle El-Sparkesykler til Kolsås stasjon: {allRides['to']['total']}</p>" \
                f"<p>Alle El-Sparkesykler fra Kolsås stasjon: {allRides['from']['total']}</p>" \
                f"<p>Alle El-Sparkesykler til og fra Kolsås stasjon relatert til T-bane: {allRides['both']['related']}</p>" \
                f"<p>Alle El-Sparkesykler til Kolsås stasjon relatert til T-bane: {allRides['to']['related']}</p>" \
                f"<p>Alle El-Sparkesykler fra Kolsås stasjon relatert til T-bane: {allRides['from']['related']}</p>" \
                f"<p>Alle El-Sparkesykler til og fra Kolsås stasjon urelatert til T-bane: {allRides['both']['unrelated']}</p>" \
                f"<p>Alle El-Sparkesykler til Kolsås stasjon urelatert til T-bane: {allRides['to']['unrelated']}</p>" \
                f"<p>Alle El-Sparkesykler fra Kolsås stasjon urelatert til T-bane: {allRides['from']['unrelated']}</p>" \
                f"<p>Prosent El-Sparkesykler til og fra Kolsås stasjon relatert til T-bane: {allRides['both']['percentage']} %</p>" \
                f"<p>Prosent El-Sparkesykler til Kolsås stasjon relatert til T-bane: {allRides['to']['percentage']} %</p>" \
                f"<p>Prosent El-Sparkesykler fra Kolsås stasjon relatert til T-bane: {allRides['from']['percentage']} %</p>" \
                f"<p>&nbsp;</p>" \
 \
                f"<p><u>Korrelasjon mellom antall passasjerer og antall sparkesykkelturer regnet ut time for time for alle timer i perioden:</u></p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Pearson's korrelasjon:</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {correlation['eScootPass']['Pearson'][0]} (p-verdi: {correlation['eScootPass']['Pearson'][1]})</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {correlation['eScootFromPassTo']['Pearson'][0]} (p-verdi: {correlation['eScootFromPassTo']['Pearson'][1]})</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {correlation['eScootToPassFrom']['Pearson'][0]} (p-verdi: {correlation['eScootToPassFrom']['Pearson'][1]})</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Spearman's rank korrelasjon:</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {correlation['eScootPass']['Spearman'][0]} (p-verdi: {correlation['eScootPass']['Spearman'][1]})</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {correlation['eScootFromPassTo']['Spearman'][0]} (p-verdi: {correlation['eScootFromPassTo']['Spearman'][1]})</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {correlation['eScootToPassFrom']['Spearman'][0]} (p-verdi: {correlation['eScootToPassFrom']['Spearman'][1]})</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Kendalls's tau korrelasjon:</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {correlation['eScootPass']['Kendall'][0]} (p-verdi: {correlation['eScootPass']['Kendall'][1]})</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {correlation['eScootFromPassTo']['Kendall'][0]} (p-verdi: {correlation['eScootFromPassTo']['Kendall'][1]})</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {correlation['eScootToPassFrom']['Kendall'][0]} (p-verdi: {correlation['eScootToPassFrom']['Kendall'][1]})</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Gammakorrelasjon:</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {correlation['eScootPass']['Gamma'][0]} (p-verdi: {correlation['eScootPass']['Gamma'][1]})</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {correlation['eScootFromPassTo']['Gamma'][0]} (p-verdi: {correlation['eScootFromPassTo']['Gamma'][1]})</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {correlation['eScootToPassFrom']['Gamma'][0]} (p-verdi: {correlation['eScootToPassFrom']['Gamma'][1]})</p>" \
 \
                f"<p>Gjennomsnittsverdier pr. time i perioden {self.fromInput.text()} - {self.toInput.text()}</p>" \
                        f"<p>&nbsp;</p>" \



            index = 0
            for dag in dager:
                firstline += f"<p><u>Time nr. {dag}:</u></p>" \
                \
                f"<p>Passasjerer på- og avstigende: {passengers['both'][index]}" \
                f"<p>Passasjerer avstigende       : {passengers['to'][index]}</p>" \
                f"<p>Passasjerer påstigende       : {passengers['from'][index]}</p>" \
 \
                f"<p>T-banerelaterte El-Sparkesykler til og fra stasjonen       : {scooters['both'][index]} " \
                f"<p>T-banerelaterte El-Sparkesykler til stasjonen: {scooters['to'][index]} " \
                f"<p>T-banerelaterte El-Sparkesykler fra stasjonen: {scooters['from'][index]} " \
 \
                f"<p>T-banerelaterte El-Sparkesykler til og fra stasjonen ift. av- og påstigende passasjerer: {percentages['both'][index]} % " \
                f"<p>T-banerelaterte El-Sparkesykler til stasjonen ift. påstigende passasjerer: {percentages['to'][index]} % " \
                f"<p>T-banerelaterte El-Sparkesykler fra stasjonen ift. avstigende passasjerer: {percentages['from'][index]} % " \
\
                f"<p>Korrelasjon mellom antall passasjerer og antall el-sparkesykkelturer" \
                f" regnet ut time {dag} for time {dag} for alle time {dag} i perioden: </p>"   \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Pearson's korrelasjon:</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {spesCoeff[dag]['eScootPass']['Pearson'][0]} (p-verdi: {spesCoeff[dag]['eScootPass']['Pearson'][1]})</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {spesCoeff[dag]['eScootFromPassTo']['Pearson'][0]} (p-verdi: {spesCoeff[dag]['eScootFromPassTo']['Pearson'][1]})</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {spesCoeff[dag]['eScootToPassFrom']['Pearson'][0]} (p-verdi: {spesCoeff[dag]['eScootToPassFrom']['Pearson'][1]})</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Spearman's rank korrelasjon:</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {spesCoeff[dag]['eScootPass']['Spearman'][0]} (p-verdi: {spesCoeff[dag]['eScootPass']['Spearman'][1]})</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {spesCoeff[dag]['eScootFromPassTo']['Spearman'][0]} (p-verdi: {spesCoeff[dag]['eScootFromPassTo']['Spearman'][1]})</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {spesCoeff[dag]['eScootToPassFrom']['Spearman'][0]} (p-verdi: {spesCoeff[dag]['eScootToPassFrom']['Spearman'][1]})</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Kendalls's tau korrelasjon:</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {spesCoeff[dag]['eScootPass']['Kendall'][0]} (p-verdi: {spesCoeff[dag]['eScootPass']['Kendall'][1]})</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {spesCoeff[dag]['eScootFromPassTo']['Kendall'][0]} (p-verdi: {spesCoeff[dag]['eScootFromPassTo']['Kendall'][1]})</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {spesCoeff[dag]['eScootToPassFrom']['Kendall'][0]} (p-verdi: {spesCoeff[dag]['eScootToPassFrom']['Kendall'][1]})</p>" \
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;Gammakorrelasjon:</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For alle passasasjerer og alle sparkesykkelturer: {spesCoeff[dag]['eScootPass']['Gamma'][0]} (p-verdi: {spesCoeff[dag]['eScootPass']['Gamma'][1]})</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For avstigende passasasjerer og sparkesykkelturer fra stasjonen: {spesCoeff[dag]['eScootFromPassTo']['Gamma'][0]} (p-verdi: {spesCoeff[dag]['eScootFromPassTo']['Gamma'][1]})</p>"\
                f"<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For påstigende passasasjerer og sparkesykkelturer til stasjonen: {spesCoeff[dag]['eScootToPassFrom']['Gamma'][0]} (p-verdi: {spesCoeff[dag]['eScootToPassFrom']['Gamma'][1]})</p>" \
                f"<p>&nbsp;</p>"\
                f"<p>&nbsp;</p>"
                index+=1

            tekst.setHtml(firstline)

    def dagPressed(self):
        if self.uke:
            self.fromInput.setText("")
            self.toInput.setText("")
        self.fromInput.setPlaceholderText("Fra dato (DD.MM)")
        self.toInput.setPlaceholderText("Til dato (DD.MM)")
        self.dag = True
        self.uke = False
        self.time = False
        self.dagknapp.setEnabled(False)
        self.ukeknapp.setEnabled(True)
        self.timeknapp.setEnabled(True)

    def ukePressed(self):
        self.fromInput.setText("")
        self.toInput.setText("")
        self.fromInput.setPlaceholderText("Fra uke nr.")
        self.toInput.setPlaceholderText("Til uke nr.")
        self.dag = False
        self.uke = True
        self.time = False
        self.dagknapp.setEnabled(True)
        self.ukeknapp.setEnabled(False)
        self.timeknapp.setEnabled(True)

    def prMin(self):
        self.data.scootersPrMinute(self.fromInput.text(), self.toInput.text(), self.direction)

    def timePressed(self):
        if self.uke:
            self.fromInput.setText("")
            self.toInput.setText("")
        self.fromInput.setPlaceholderText("Fra dato (DD.MM)")
        self.toInput.setPlaceholderText("Til dato (DD.MM)")
        self.dag = False
        self.time = True
        self.uke = False
        self.dagknapp.setEnabled(True)
        self.ukeknapp.setEnabled(True)
        self.timeknapp.setEnabled(False)

    def toPressed(self):
        self.direction = "to"
        self.toButton.setEnabled(False)
        self.fromButton.setEnabled(True)
        self.bothButton.setEnabled(True)

    def fromPressed(self):
        self.direction = "from"
        self.toButton.setEnabled(True)
        self.fromButton.setEnabled(False)
        self.bothButton.setEnabled(True)

    def bothPressed(self):
        self.direction = "both"
        self.toButton.setEnabled(True)
        self.fromButton.setEnabled(True)
        self.bothButton.setEnabled(False)
    def makegraph(self):

        try:

            if self.time:
                self.data.makeGraph(self.fromInput.text(), self.toInput.text(), self.direction, "hour")
            elif self.dag:
                self.data.makeGraph(self.fromInput.text(), self.toInput.text(), self.direction, "day")
            elif self.uke:
                self.data.makeGraph(self.fromInput.text(), self.toInput.text(), self.direction, "week")
        except:
            pass
    def makeExcel(self):

        try:
            if self.uke:
                self.data.makeExcelSheet( self.fromInput.text(), self.toInput.text(), type = 'week')
            else:
                self.data.makeExcelSheet( self.fromInput.text(), self.toInput.text() )
        except:
            pass



class Schedentry(myframe):

    def __init__(self, *args, **kwargs):

        myframe.__init__(self, *args, **kwargs)

        self.setSizePolicy(qw.QSizePolicy.Expanding, qw.QSizePolicy.Expanding)

        self.theme = (0, 0, 0, 80)

        # Create the display side of the stacked widget:
        schedie = myframe(self, "h", color=(0, 0, 0, 0))
        schedie.setSizePolicy(qw.QSizePolicy.Expanding, qw.QSizePolicy.Expanding)
        # Make 6 frames
        sched = {}
        fram1 = myframe(schedie, "h", "fram1", color=(0,0,0,0), add=True)
        fram2 = myframe(schedie, "h", "fram2", color=(0, 0, 0, 0), add=True)
        self.labels = {}
        for i in range(1, 15):
            if i < 8:
                sched[str(i)] = myframe(fram1, "h", f"schedframe{i}", color=self.theme, add=True)
            else:
                sched[str(i)] = myframe(fram2, "h", f"schedframe{i}", color=self.theme, add=True)
            if i < 14:
                sched[str(i)].addstyle("border", "border-right: 1px solid gray; ")

            self.labels[str(i)] = qw.QTextEdit(sched[str(i)])
            font = qg.QFont('Roboto', 8)
            self.labels[str(i)].setFont(font)
            self.labels[str(i)].setStyleSheet("color: 'white';")

            sched[str(i)].setSizePolicy(qw.QSizePolicy.Expanding, qw.QSizePolicy.Expanding)
            sched[str(i)].setMinimumHeight(500000)

            self.labels[str(i)].setSizePolicy(qw.QSizePolicy.Expanding, qw.QSizePolicy.Expanding)
            self.labels[str(i)].setVerticalScrollBarPolicy(qc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.labels[str(i)].setReadOnly(True)
            sched[str(i)].lay.addWidget(self.labels[str(i)])


            #self.labels[str(i)] = mylabel(sched[str(i)], add=True, size=10, text="Noe")
            sched[str(i)].margins(5, 0, 0, 0)

        sched["1"].setFixedWidth(60),       sched["1"].margins(10, 10, 10, 0)
        sched["2"].margins(10, 10, 10, 0),    sched["2"].setMinimumWidth(130)
        sched["3"].setMinimumWidth(85), sched["3"].margins(10, 10, 10, 0)
        sched["4"].setMinimumWidth(90), sched["4"].margins(10, 10, 10, 0)
        sched["5"].setMinimumWidth(80), sched["5"].margins(10, 10, 10, 0)
        sched["6"].setMinimumWidth(80), sched["6"].margins(10, 10, 10, 0)
        sched["7"].setMinimumWidth(100), sched["7"].margins(10, 10, 10, 0), sched["7"].addstyle("border", "border-right: 2px solid gray; ")
        sched["8"].setFixedWidth(60), sched["8"].margins(10, 10, 10, 0), sched["8"].addstyle("border", "border-left: 2px solid gray; border-right: 1px solid gray; ")
        sched["9"].margins(10, 10, 10, 0), sched["9"].setMinimumWidth(130)
        sched["10"].setMinimumWidth(85), sched["10"].margins(10, 10, 10, 0)
        sched["11"].setMinimumWidth(90), sched["11"].margins(10, 10, 10, 0)
        sched["12"].setMinimumWidth(80), sched["12"].margins(10, 10, 10, 0)
        sched["13"].setMinimumWidth(80), sched["13"].margins(10, 10, 10, 0)
        sched["14"].setMinimumWidth(100), sched["14"].margins(10, 10, 0, 0)

        self.sched = sched
        self.lay.addWidget(schedie)


    def Theme(self, key):
        if key == "dark":
            for i in self.sched:
                self.sched[i].bg(0, 0, 0, 120)
        elif key == "light":
            for i in self.sched:
                self.sched[i].bg(0, 0, 0, 50)

# Some functions that eases use
class functions(Main):

    def max_restore(self):

        if self.maximized == False:
            self.cw.radius(0), self.cf.radius(0), self.mainframe["1"].customradius(0, 0, 0, 0), self.showMaximized()
            self.maximized = True

        else:
            self.cw.radius(10), self.cf.radius(10), self.mainframe["1"].customradius(10, 10, 0, 0), self.showNormal()
            self.resize(self.width() + 1, self.height() + 1)
            self.maximized = False

    def buttonconfig(self):
        # close/maximize/minimize buttons:
        self.button["1"].clicked.connect(self.showMinimized), self.button["2"].clicked.connect(
            lambda: functions.max_restore(self))
        self.button["3"].clicked.connect(self.close)





