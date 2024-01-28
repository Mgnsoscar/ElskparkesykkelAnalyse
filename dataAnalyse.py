import  pandas                      as      pd
import  matplotlib.pyplot           as      plt
import  numpy                       as      np
import  scipy.stats                 as      stats
import  json
import  os
from    datetime                    import  *



class Avgang():

    def __init__(  self,  direction,  actualTime,  expectedTime,  passengers  ):

        # Initialize member variables
        self.direction      =  direction
        self.actualTime     =  actualTime
        self.scheduledTime  =  expectedTime
        self.passengers     =  passengers
        self.eScooters      =  0
        self.eScooterTime   =  []
        self.temperature    =  None
        self.wind           =  None
        self.rain           =  None

    # Member function that prints the variables to conosole in a readable fashion
    def printAvgang(  self  ):

        # Check direction to decide if self.passengers is boarding or leaving the subway
        if self.direction == "Ankomst":

            onOrOff = "Avstigende"

        else:

            onOrOff = "Påstigende"

        # Print values to console
        print(  f"\t{  self.direction  }:\t{  self.scheduledTime  } ( "
                f"{  self.actualTime.time()  } )\t\t"
                f"{  onOrOff  }: {  self.passengers  } \t\t\t"
                f"Sparkesykler: {self.eScooters} \t\t\t"
                f"Temperatur (C): {self.temperature} \t\t\t"
                f"Vind (m/s): {self.wind} \t\t\t"
                f"Nedbør (mm/t): {self.rain}")

# Class that contains all data from the given datasets
class Data():

    # Function that runs when an object of the class is initialized
    def __init__(  self,  marginFrom: int,  marginTo: int, filename: str  ):

        # Make member variables with the margins (used to name excel files)
        self.__marginFrom       =   marginFrom
        self.__marginTo         =   marginTo

        # Make a variable with the main excel filename
        self.filename   =   filename

        # Collect desired data from the .xls files
        subwayData      =   pd.read_excel(  self.filename      ,  "T_banedata"   ,  usecols  =  [ 1, 2, 3, 5, 6, 8 ]  )
        eScooterFrom    =   pd.read_excel(  self.filename      ,  "FraKolsås_150",  usecols  =  [ 9 ]                 )
        eScooterTo      =   pd.read_excel(  self.filename      ,  "TilKolsås_150",  usecols  =  [ 8 ]                 )
        tempWind        =   pd.read_excel(  "temperaturer.xlsx",                    usecols  =  [ 2, 4, 3 ]           )
        rain            =   pd.read_excel(  "nedbor.xlsx"      ,                    usecols  =  [ 3 ]                 )

        # Make lists with desired data from subway arrivals/departures
        dates           =   list(  subwayData  [  "dato_MDY"    ]  )
        passengersOff   =   list(  subwayData  [  "avstigende"  ]  )
        passengersOn    =   list(  subwayData  [  "påstigende"  ]  )
        direction       =   list(  subwayData  [  "retning"     ]  )

        # Isolate actual time from excpected time and format for every departure/arrival
        actualTime      =   self.__formatTime(  list(  subwayData  [  "avgangfaktisk"   ]  ),  dates  )
        scheduledTime   =   self.__formatTime(  list(  subwayData  [  "avgangplanlagt"  ]  ),  dates  )

        # Create one list for departures and one for arrivals
        self.departures,    self.arrivals   =   self.__sortDepartures(  actualTime,    scheduledTime,  direction,
                                                                        passengersOn,  passengersOff            )

        # Make lists with eScooter departures/arrivals and sort them by date and time
        eScooterFrom    =   self.__pdDatetimeToDatetime(  sorted(  list(  eScooterFrom  [  "Rental Sta"  ]  )  )  )
        eScooterTo      =   self.__pdDatetimeToDatetime(  sorted(  list(  eScooterTo    [  "Rental End"  ]  )  )  )

        # Make member variables of the eScooter trips
        self.eFrom      =   eScooterFrom
        self.eTo        =   eScooterTo

        # Create a dictionary to sort all eScooter trips into dates year
        self.__eScooters    =   \
            {
                "to"    :   {
                                ( datetime( 2022, 1, 1) + timedelta( days = day ) ).date() : 0
                            for day in range( 365 )
                            },
                "from"  :   {
                                ( datetime( 2022, 1, 1) + timedelta( days = day ) ).date() : 0
                            for day in range( 365 )
                            },
                "both"  :   {
                                ( datetime( 2022, 1, 1) + timedelta( days = day ) ).date() : 0
                            for day in range( 365 )
                            },
            }

        # Make lists with desired weather data
        self.__weathertime     =   self.__makeDatetimeObjects(  list(  tempWind  [  "Tid(norsk normaltid)"      ]  )  )
        self.__temperature     =                                list(  tempWind  [  "Lufttemperatur"            ]  )
        self.__wind            =                                list(  tempWind  [  "Høyeste middelvind (1 t)"  ]  )
        self.__rain            =                                list(  rain      [  "Nedbør (1 t)"              ]  )

        # Run functions
        self.__assignScooters(  eScooterFrom,  eScooterTo,  marginFrom,  marginTo  )
        self.__getDateIndices()
        self.__assignWeather()

    # The timestamps on each subway departure/arrival goes to beyond 24:00. This is not desireable.
    # Reformats the timestamps of departures/arrivals to correctly formatted datetime objects
    def __formatTime(  self,  timestamps,  dates  ):

        # Iterate through each timestamp
        for timestamp in range(  len(  timestamps  )  ):

            # Creates a datetimeobject describing the day of the timestamp
            date    =   datetime(  dates[  timestamp  ].year,  dates[  timestamp  ].month,  dates[  timestamp  ].day  )

            # Sometimes excel autoformats timestamps to datetime objects, but then the date gets wrong
            # We fix this by trying to exctract the time as a string from the datetime object. If it is not
            # a datetime object, then the code will run the exception in stead that will do nothing basicly.
            try:

                timeString  =   timestamps[  timestamp  ].strftime(  '%H:%M:%S'  )

                if int(  timeString[  :2  ]  ) < 4:

                    timestamps[  timestamp  ]   =   str(  int(  timeString[  :2  ]  ) + 24  ) + timeString[  2:  ]

            except:

                pass

            # Check if the timestamp starts with 24 or more
            if int(  timestamps[  timestamp  ][  :2  ]  )  >=  24:

                # Reformats the string
                newFormat   =   str(  "0" + str(  int(  timestamps[  timestamp  ][  :2  ]  )  -  24  )  +
                                timestamps[  timestamp  ][  2:  ]  )

                # Makes sure the date is the day past midnight
                date  +=  timedelta(  days  =  1  )
            else:

                # Does nothing with the timestamp except convert it to a string
                newFormat   =   str(  timestamps[  timestamp  ]  )

            # Make a datetime object with the newly formatted timestamp
            timestamps[  timestamp  ]   =   datetime.strptime(  newFormat,  "%H:%M:%S"  ).replace(  year  = date.year ,
                                                                                                    month = date.month,
                                                                                                    day   = date.day   )
        return timestamps

    # Sort all subway arrivals/departures into their own list
    def __sortDepartures(  self,  avgangfaktisk,  avgangplanlagt,  retning,  passengersOn,  passengersOff  ):

        # Initalize lists for departures and arrivals
        departures     =   []
        arrivals       =   []

        # Iterate throug every departure/arrival
        for index in range(  len(  avgangplanlagt  )  ):

            # Check if it is an arrival
            if retning[index] == "Til":

                # Create an Arrival object with the arrival data and add to the list of arrivals
                arrivals.append(    Avgang(  "Ankomst"                  ,  avgangfaktisk[  index  ]  ,
                                             avgangplanlagt[  index  ]  ,  passengersOff[  index  ]  )  )
            else:

                # Create an Arrival object with the departure data and add to the list of departure
                departures.append(  Avgang(  "Avgang"                   ,   avgangfaktisk[  index  ]  ,
                                             avgangplanlagt[  index  ]  ,   passengersOn [  index  ]  )  )

        # Return the lists
        return departures, arrivals

    # Go through all eScooter trips and check if they are related to a departure/arrival. If so, assign it
    # to the related departure/arrival
    def __assignScooters(  self,  eScooterFrom,  eScooterTo,  marginFrom,  marginTo  ):

        # Create variable that keeps track of the index where the last loop stopped
        lastIndexChecked    =   0

        # Iterate through each eScooter trip that ended at Kolsås station
        for trip in eScooterTo:

            # Add trip to the list of the current day
            self.__eScooters[  "to"    ][  trip.date()  ]  +=  1
            self.__eScooters[  "both"  ][  trip.date()  ]  +=  1

            # Iterate through each departure from where the last iteration ended
            for i in range(  lastIndexChecked,  len(  self.departures)  ):

                # Fetch the given departure and calculate the time difference between it an the eScooter trip.
                # Use the scheduled time of departure.
                departure       =   self.departures[i]
                timeDifference  =   departure.scheduledTime - trip

                # Check if the eScooter trip ended within the margin of minutes before the scheduled subway departure.
                # Also check if any passengers got on.
                if 60 * marginTo >= timeDifference.total_seconds() > 0  and  \
                        departure.passengers - departure.eScooters > 0:

                    # Add one eScooter trip to the given subway departure and update the index where it found a match,
                    # but minus one so the current departure is checked again. This is because more than one eScooter
                    # trip can be realated to one departure. Lastly exit the loop.
                    self.departures[i].eScooters  +=  1
                    self.departures[i].eScooterTime.append(  trip  )
                    lastIndexChecked               =  i - 1
                    break

        # Reset lastIndexChecked to 0 since we're now checking eScooter trips departing from Kolsås station
        lastIndexChecked  =  0

        # Iterate through each eScooter trip that started at Kolsås station
        for trip in eScooterFrom:

            # Add trip to that list of the current day
            self.__eScooters[  "from"    ][  trip.date()  ]  +=  1
            self.__eScooters[  "both"    ][  trip.date()  ]  +=  1

            # Iterate through each arrival from where the last iteration ended
            for i in range(  lastIndexChecked,  len(  self.arrivals)  ):

                # Fetch the given arrival and calculate the time difference between it an the eScooter trip.
                # Use the actual time of arrival
                arrival         =   self.arrivals[ i ]
                timeDifference  =   trip - arrival.actualTime

                # Check if the eScooter trip started within the margin of minutes after the actual subway arrival.
                # Also check if any passengers got off.
                if 60 * marginFrom >= timeDifference.total_seconds() > 0  and  \
                        arrival.passengers - arrival.eScooters       > 0:

                    # Add one eScooter trip to the given subway arrival and update the index where it found a match,
                    # but minus one so the current arrival is checked again. This is because more than one eScooter
                    # trip can be realated to one arrival. Lastly exit the loop.
                    self.arrivals[i].eScooters    +=  1
                    self.arrivals[i].eScooterTime.append(  trip  )
                    lastIndexChecked               =  i - 1
                    break

    # Convert strings to datetime timestamps
    def __makeDatetimeObjects(  self,  weathertime  ):

        # Iterate through the timestamp og each weather data entry
        for time in range(  len(  weathertime  ) - 1  ):

            # Convert the string to a datetime timestamp
            weathertime[  time  ]   =   datetime.strptime(  weathertime[  time  ],  "%d.%m.%Y %H:%M"  )

        return weathertime

    # Convert pandas timestamps to datetime timestamps
    def __pdDatetimeToDatetime(  self,  timestamps  ):

        # Iterate through each timestamp
        for time in range(  len(  timestamps  )  ):

            # Convert pd_timestamp to datetime timestamp
            timestamps[  time  ]    =   timestamps[  time  ].to_pydatetime()

        # Return the updated list
        return timestamps

    # Find the weather that was at the time of each departure/arrival and update variables
    def __assignWeather(  self  ):

        # The indices where a new date from the previous iteration was found
        lastDepartureChecked        =   0
        lastArrivalChecked          =   0

        # Iterate through every weather timestamp
        for weatherIndex in range(  len(  self.__weathertime  ) - 1  ):

            # Extract the weather timestamp
            weathertime     =   self.__weathertime[  weatherIndex  ]

            # Iterate through each departure from where the previous iteration left off
            for index in range(  lastDepartureChecked,  len(  self.departures  )  ):

                # Extract the timestamp of the given departure
                departuretime       =   self.departures[  index  ].scheduledTime

                # Check if the departure is the same hour at the same date as the given weather timestamp
                if (  weathertime.date(),  weathertime.hour  )  ==  (  departuretime.date(),  departuretime.hour  ):

                    # Update the variables in the given departure
                    self.departures[  index  ].temperature  =   self.__temperature[  weatherIndex  ]
                    self.departures[  index  ].wind         =   self.__wind       [  weatherIndex  ]
                    self.departures[  index  ].rain         =   self.__rain       [  weatherIndex  ]

                else:

                    # Define where the next iteration self.departures list should start and stop the loop
                    lastDepartureChecked    =   index
                    break

            # Iterate through each arrival from where the previous iteration left off
            for index in range(  lastArrivalChecked,  len(  self.arrivals  )  ):

                # Extract the timestamp of the given departure
                arrivaltime   =   self.arrivals[  index  ].scheduledTime

                # Check if the arrival is the same hour at the same date as the given weather timestamp
                if (  weathertime.date(),  weathertime.hour  )  ==  (  arrivaltime.date(),  arrivaltime.hour  ):

                    # Update the variables in the given arrival
                    self.arrivals[  index  ].temperature  =   self.__temperature[  weatherIndex  ]
                    self.arrivals[  index  ].wind         =   self.__wind       [  weatherIndex  ]
                    self.arrivals[  index  ].rain         =   self.__rain       [  weatherIndex  ]

                else:

                    # Define where the next iteration self.arrivals list should start and stop the loop
                    lastArrivalChecked  =   index
                    break

    # Search through the list of arrivals/departures and eScooter rides and find
    # the index of the first entry on every day
    def __getDateIndices(  self  ):

        # Set control date Jan. 1st. and initialise the list of arrival indices
        controlDate                     =   datetime(  2022,  1,  1  )
        self.__dateIndicesArrivals      =   [ 0 ]

        # Iterate through every arrival
        for index in range(  len(  self.arrivals  )  ):

            # Fetch the actual time of given arrival
            time    =   self.arrivals[  index  ].actualTime

            # Check if arrival date  matches the control date
            if (  time.month,  time.day  )  !=  (  controlDate.month,  controlDate.day  ):

                # Change control date to the next day and add the index to the correct list of indices
                controlDate  +=  timedelta(  days = 1  )
                self.__dateIndicesArrivals.append(  index  )

        # Reset the control date to Jan. 1st. and initialise list of departure indices
        controlDate                     =   datetime(2022, 1, 1)
        self.__dateIndicesDepartures    =   [ 0 ]

        # Iterate through every departure
        for index in range(  len(  self.departures  )  ):

            # Fetch the time of scheduled departure
            time    =   self.departures[  index  ].scheduledTime

            # Check if day of departure matches the control date
            if (  time.month,  time.day  )  !=  (  controlDate.month,  controlDate.day  ):

                # Change control date to next day and add the index to the correct list of indices
                controlDate    +=  timedelta(  days = 1  )
                self.__dateIndicesDepartures.append(  index  )

    # Find all the indexes of arrivals/departures within a given time period
    def __getFromindexToindex(  self,  direction,  fromDate,  toDate):


        # Convert the dates to datetime objects
        fromDate    =   datetime(  2022,  int(  fromDate[ 3: ]  ),  int(  fromDate[ :2 ]  )  )
        toDate      =   datetime(  2022,  int(  toDate  [ 3: ]  ),  int(  toDate  [ :2 ]  )  )

        # Check if toDate is the last date in self.__dateIndicesArrivals
        if toDate == datetime(  2022, 12, 31  ):

            # Find how many days into the year each date is. Minus one to match dates in self.__dateIndices list.
            # Fetch first index of the given dates. Since it is the last day we fetch values to the end of the list
            if direction == "Arrivals":

                fromIndex   =   self.__dateIndicesArrivals[  fromDate.timetuple().tm_yday - 1  ]

            else:

                fromIndex   =   self.__dateIndicesDepartures[  fromDate.timetuple().tm_yday - 1  ]

            toIndex         =   None

        else:

            # Same as above, but in stead of fetching values to the end of the list, we fetch values until the
            # first index of the date after toDate
            if direction == "Arrivals":

                fromIndex   =   self.__dateIndicesArrivals[  fromDate.timetuple().tm_yday - 1  ]
                toIndex     =   self.__dateIndicesArrivals[  toDate.timetuple().tm_yday        ]

            else:

                fromIndex   =   self.__dateIndicesDepartures[  fromDate.timetuple().tm_yday - 1  ]
                toIndex     =   self.__dateIndicesDepartures[  toDate.timetuple().tm_yday        ]

        return fromIndex, toIndex

    # Prints arrivals within a given time period to console
    def printArrivals(  self,  fromDate = (  1, 1, 2022  ),  toDate = (  1, 1, 2022  )  ):

        # Fetch the correct indices
        fromIndex, toIndex  =   self.__getFromindexToindex(  "Arrivals",  fromDate,  toDate  )

        # Iterate through all arrivals within the chosen timespan
        for arrival in self.arrivals[  fromIndex : toIndex  ]:

            # Print the  given arrival
            arrival.printAvgang()

    # Print departures within a given time period to console
    def printDepartures(  self,  fromDate = (  1, 1, 2022  ),  toDate = (  1, 1, 2022  )  ):

        # Fetch the correct indices
        fromIndex, toIndex  =   self.__getFromindexToindex(  "Departures",  fromDate,  toDate  )

        # Iterate through all arrivals within the chosen timespan
        for departure in self.departures[  fromIndex : toIndex  ]:

            # Print the  given arrival
            departure.printAvgang()

    def iterateThroughArrivals(self, direction, fromDate, toDate  ):

        # Fetch the correct indices
        fromIndex, toIndex  =   self.__getFromindexToindex(  direction,  fromDate,  toDate  )

        # Choose correct list depending on the input
        if direction == "Arrivals":

            liste = self.arrivals

        else:

            liste = self.departures

        arrivals = []
        # Iterate through all arrivals within the chosen timespan
        for arrival in liste[  fromIndex : toIndex  ]:

            # Add the given arrival/departure to the list
            arrivals.append(arrival)

        return arrivals

    # Returns plottable lists of average stats for each hour in a time period
    def plotAverageHour(  self,  fromDate,  toDate  ):

        # Create datetime objects of the toDate and fromDate and calculate how many days
        # there are between them, including the fromDate and toDate.
        fromTime        =   datetime(  2022, int(  fromDate[ 3: ]  ), int(  fromDate[ :2 ]  )  )
        toTime          =   datetime(  2022, int(  toDate  [ 3: ]  ), int(  toDate  [ :2 ]  )  )
        days            =   (  toTime - fromTime  ).days + 1

        # Make list of all days in time period
        currentDate     =   fromTime
        allDays         =   []

        while currentDate <= toTime:

            allDays.append(  currentDate.date()  )
            currentDate     +=  timedelta(  days = 1  )

        # Create a list with the elements on the xAxis of the graph. Here hours from 04:00 to 02:00
        xAxis       =   [  i for i in range(  4, 24  )  ]
        xAxis.append(0)
        xAxis.append(1)
        xAxis.append(2)

        # Create dictionaries that collects all data pr. specific each hour. Will be used to find the correlation
        # coefficient between amount of passengers and eScooter rides.
        passengersPrHour        =   {  date   :   {    hour   :   0    for hour in xAxis   }   for date in allDays  }
        passengersToPrHour      =   {  date   :   {    hour   :   0    for hour in xAxis   }   for date in allDays  }
        passengersFromPrHour    =   {  date   :   {    hour   :   0    for hour in xAxis   }   for date in allDays  }
        eScootersPrHour         =   {  date   :   {    hour   :   0    for hour in xAxis   }   for date in allDays  }
        eScootersToPrHour       =   {  date   :   {    hour   :   0    for hour in xAxis   }   for date in allDays  }
        eScootersFromPrHour     =   {  date   :   {    hour   :   0    for hour in xAxis   }   for date in allDays  }

        # Make dictionaries to be filled with each hour data for every day in time frame.
        # Will be used to calculate the correlation coefficient between passengers and eScooter rides for each specific
        # hour, instead of the correlation hour to hour in general.
        passengersSpecificHour          =   {  hour    :   []   for hour in xAxis  }
        passengersToSpecificHour        =   {  hour    :   []   for hour in xAxis  }
        passengersFromSpecificHour      =   {  hour    :   []   for hour in xAxis  }
        eScootersSpecificHour           =   {  hour    :   []   for hour in xAxis  }
        eScootersToSpecificHour         =   {  hour    :   []   for hour in xAxis  }
        eScootersFromSpecificHour       =   {  hour    :   []   for hour in xAxis  }

        # Fetch the list of arrivals and departures in this time period
        arrivals    =   self.iterateThroughArrivals(  "Arrivals"  , fromDate, toDate  )
        departures  =   self.iterateThroughArrivals(  "Departures", fromDate, toDate  )

        # Create dictionaries for each stat. Keywords are the elements on the xAxis.
        eScooters       =   {  i : 0 for i in xAxis  }
        eScootersFrom   =   {  i : 0 for i in xAxis  }
        eScootersTo     =   {  i : 0 for i in xAxis  }
        passengers      =   {  i : 0 for i in xAxis  }
        passengersFrom  =   {  i : 0 for i in xAxis  }
        passengersTo    =   {  i : 0 for i in xAxis  }

        # Iterate through the arrivals
        for arrival in arrivals:

            # If arrival was after 23:59 on Dec. 31., break the foor loop
            if arrival.actualTime.year == 2023:

                break

            # If the actual time of arrival was during an hour on the xAxis, add it to that hour in the dictionary.
            if arrival.actualTime.hour in xAxis:

                # Add the passenger and eScooter count to a variable designated to the specific hour
                eScootersPrHour    [  arrival.actualTime.date()  ][  arrival.actualTime.hour  ]  +=  arrival.eScooters
                eScootersFromPrHour[  arrival.actualTime.date()  ][  arrival.actualTime.hour  ]  +=  arrival.eScooters
                passengersPrHour   [  arrival.actualTime.date()  ][  arrival.actualTime.hour  ]  +=  arrival.passengers
                passengersToPrHour [  arrival.actualTime.date()  ][  arrival.actualTime.hour  ]  +=  arrival.passengers

                # Add values to designated variables
                eScooters    [  arrival.actualTime.hour  ]  +=  arrival.eScooters
                eScootersFrom[  arrival.actualTime.hour  ]  +=  arrival.eScooters
                passengers   [  arrival.actualTime.hour  ]  +=  arrival.passengers
                passengersTo [  arrival.actualTime.hour  ]  +=  arrival.passengers

        # Iterate through the departures
        for departure in departures:

            # If departure was after 23:59 on Dec. 31., break the foor loop
            if departure.actualTime.year == 2023:

                break

            # If the scheduled time of departure was during an hour on the xAxis, add it to that hour in the dictionary.
            if departure.scheduledTime.hour in xAxis:

                # Add the passenger and eScooter count to a variable designated to the specific hour
                eScootersPrHour     [ departure.actualTime.date() ][ departure.actualTime.hour ] += departure.eScooters
                eScootersToPrHour   [ departure.actualTime.date() ][ departure.actualTime.hour ] += departure.eScooters
                passengersPrHour    [ departure.actualTime.date() ][ departure.actualTime.hour ] += departure.passengers
                passengersFromPrHour[ departure.actualTime.date() ][ departure.actualTime.hour ] += departure.passengers

                # Add values to designated variables
                eScooters     [  departure.actualTime.hour  ]  +=  departure.eScooters
                eScootersTo   [  departure.actualTime.hour  ]  +=  departure.eScooters
                passengers    [  departure.actualTime.hour  ]  +=  departure.passengers
                passengersFrom[  departure.actualTime.hour  ]  +=  departure.passengers

        # Initialize lists for the data each specific hour in the time frame
        passengersEachHour      =   []
        passengersToEachHour    =   []
        passengersFromEachHour  =   []
        eScootersEachHour       =   []
        eScootersToEachHour     =   []
        eScootersFromEachHour   =   []

        # Iterate through the keywords (dates) in passengersPrHour dictionary
        for date in passengersPrHour:

            # Iterate through the keywords (hours) of each subdictionary
            for hour in passengersPrHour[  date  ]:

                # Sort the data into lists containing all hours of every day
                passengersEachHour.append    (  passengersPrHour    [  date  ][  hour  ]  )
                passengersToEachHour.append  (  passengersToPrHour  [  date  ][  hour  ]  )
                passengersFromEachHour.append(  passengersFromPrHour[  date  ][  hour  ]  )
                eScootersEachHour.append     (  eScootersPrHour     [  date  ][  hour  ]  )
                eScootersToEachHour.append   (  eScootersToPrHour   [  date  ][  hour  ]  )
                eScootersFromEachHour.append (  eScootersFromPrHour [  date  ][  hour  ]  )

                # Sort the data for each hour into lists containing just that hour of the day
                passengersSpecificHour    [  hour  ].append(  passengersPrHour    [  date  ][  hour  ]  )
                passengersToSpecificHour  [  hour  ].append(  passengersToPrHour  [  date  ][  hour  ]  )
                passengersFromSpecificHour[  hour  ].append(  passengersFromPrHour[  date  ][  hour  ]  )
                eScootersSpecificHour     [  hour  ].append(  eScootersPrHour     [  date  ][  hour  ]  )
                eScootersToSpecificHour   [  hour  ].append(  eScootersToPrHour   [  date  ][  hour  ]  )
                eScootersFromSpecificHour [  hour  ].append(  eScootersFromPrHour [  date  ][  hour  ]  )

        # Here the 0 index will be the corr.coeff. and 1 index the p-value
        correlationPrSpecificHour   =   \
            {  hour : {
                        "eScootPass"       :   self.getCorrelationCoefficient(  eScootersSpecificHour     [  hour  ],
                                                                                passengersSpecificHour    [  hour  ]  ),
                        "eScootToPassFrom" :   self.getCorrelationCoefficient(  eScootersToSpecificHour   [  hour  ],
                                                                                passengersFromSpecificHour[  hour  ]  ),
                        "eScootFromPassTo" :   self.getCorrelationCoefficient(  eScootersFromSpecificHour [  hour  ],
                                                                                passengersToSpecificHour  [  hour  ]  )
                      }   for hour in xAxis
            }

        # Fetch the correlation coefficient pr. hour in general in the time frame
        generalCorrelation      = \
            {
                "eScootPass"        :   self.getCorrelationCoefficient(  eScootersEachHour,
                                                                         passengersEachHour  ),
                "eScootToPassFrom"  :   self.getCorrelationCoefficient(  eScootersToEachHour,
                                                                         passengersFromEachHour  ),
                "eScootFromPassTo"  :   self.getCorrelationCoefficient(  eScootersFromEachHour,
                                                                         passengersToEachHour  )
            }

        # Find total amount of scooters (including those not related to the subway) in the time frame
        totScooters         =   np.sum(  np.array(  [  self.__eScooters[  'both'  ][  date  ] for date in allDays  ]  )  )
        totScootersTo       =   np.sum(  np.array(  [  self.__eScooters[  'to'    ][  date  ] for date in allDays  ]  )  )
        totScootersFrom     =   np.sum(  np.array(  [  self.__eScooters[  'from'  ][  date  ] for date in allDays  ]  )  )

        # Find total amount of eScooter rides related to the subway in the time frame
        totRelScooters      =   np.sum(  np.array(  eScootersEachHour      )  )
        totRelScootersTo    =   np.sum(  np.array(  eScootersToEachHour    )  )
        totRelScootersFrom  =   np.sum(  np.array(  eScootersFromEachHour  )  )

        # Find percentages
        try:
            percentage      =   round(  (  totRelScooters     / totScooters      ) * 100, 2  )
            percentageTo    =   round(  (  totRelScootersTo   / totScootersTo    ) * 100, 2  )
            percentageFrom  =   round(  (  totRelScootersFrom / totScootersFrom  ) * 100, 2  )
        except:
            percentage      =   0
            percentageTo    =   0
            percentageFrom  =   0

        unrelatedScooters   = \
            {
                "both"  :   {
                                "related"       : totRelScooters,
                                "unrelated"     : totScooters - totRelScooters,
                                "total"         : totScooters,
                                "percentage"    : percentage
                            },
                "to"    :   {
                                "related"       : totRelScootersTo,
                                "unrelated"     : totScootersTo - totRelScootersTo,
                                "total"         : totScootersTo,
                                "percentage"    : percentageTo
                            },
                "from"  :   {
                                "related"       : totRelScootersFrom,
                                "unrelated"     : totScootersFrom - totRelScootersFrom,
                                "total"         : totScootersFrom,
                                "percentage"    : percentageFrom
                },
            }


        # Iterate through each element on the xAxis
        for hour in xAxis:

            # Fetch values from each xAxis keyword and divide by number of days to find the average. Two decimals
            eScooters     [  hour  ]    =   round(  eScooters     [  hour  ] / days, 2  )
            eScootersTo   [  hour  ]    =   round(  eScootersTo   [  hour  ] / days, 2  )
            eScootersFrom [  hour  ]    =   round(  eScootersFrom [  hour  ] / days, 2  )
            passengers    [  hour  ]    =   round(  passengers    [  hour  ] / days, 2  )
            passengersTo  [  hour  ]    =   round(  passengersTo  [  hour  ] / days, 2  )
            passengersFrom[  hour  ]    =   round(  passengersFrom[  hour  ] / days, 2  )

        # Create new lists with values for each hour in the same order as xAxis
        avgScootersPrHour               =   [  eScooters     [  hour  ] for hour in xAxis  ]
        avgScootersToPrHour             =   [  eScootersTo   [  hour  ] for hour in xAxis  ]
        avgScootersFromPrHour           =   [  eScootersFrom [  hour  ] for hour in xAxis  ]
        avgPassengersPrHour             =   [  passengers    [  hour  ] for hour in xAxis  ]
        avgPassengersToPrHour           =   [  passengersTo  [  hour  ] for hour in xAxis  ]
        avgPassengersFromPrHour         =   [  passengersFrom[  hour  ] for hour in xAxis  ]


        # Create a list with percentage of passengers in total using eScooters
        percentScooters     =   []
        # Iterate through average eScooters and passengers for each hour
        for avgScooters, avgPassengers in zip(  avgScootersPrHour, avgPassengersPrHour  ):

            # Try to divide eScooters by passengers to find percentage
            try:

                percentScooters.append(  round(  (  (  avgScooters / avgPassengers  ) * 100  ), 2  )  )

            # We cant divide by zero, so if passengers is zero, set the percentage to 0
            except ZeroDivisionError:

                percentScooters.append(  0  )

        # Same as above
        percentScootersTo   =   []
        for avgScooters, avgPassengers in zip(  avgScootersToPrHour, avgPassengersFromPrHour  ):

             try:

                percentScootersTo.append(  round(  (  (  avgScooters / avgPassengers  ) * 100  ), 2  )  )

             except ZeroDivisionError:

                percentScootersTo.append(  0  )

        # Same as above
        percentScootersFrom =   []
        for avgScooters, avgPassengers in zip(  avgScootersFromPrHour, avgPassengersToPrHour  ):

            try:

                percentScootersFrom.append(  round(  (  (  avgScooters / avgPassengers  ) * 100  ), 2  )  )

            except ZeroDivisionError:

                percentScootersFrom.append(  0  )

        # Convert integers in xAxis list to strings. This is so they won't be sorted when making the graph later
        strings     =   []
        for hour in xAxis:

            strings.append(  str(  hour  )  )

        xAxis   =   strings

        # Make dictionaries with average results
        averageScooters         =   \
            {
                "both"  :   avgScootersPrHour,
                "to"    :   avgScootersToPrHour,
                "from"  :   avgScootersFromPrHour
            }

        averagePassengers       =   \
            {
                "both"  :   avgPassengersPrHour,
                "to"    :   avgPassengersToPrHour,
                "from"  :   avgPassengersFromPrHour
            }

        averagePercentage       =   \
            {
                "both"  : percentScooters,
                "to"    : percentScootersTo,
                "from"  : percentScootersFrom
            }

        return averageScooters  , averagePassengers     , averagePercentage,    \
               xAxis            , generalCorrelation    , correlationPrSpecificHour,    \
               unrelatedScooters

    # Returns plottable lists with actual stats for each day in a time period
    def plotDays(  self,  fromDate,  toDate  ):

        # Fetch lists of arrivals and departures within the time period
        arrivals    =   self.iterateThroughArrivals(  "Arrivals"  , fromDate, toDate  )
        departures  =   self.iterateThroughArrivals(  "Departures", fromDate, toDate  )

        # Make datetime objects from the fromDate and toDate
        fromTime    =   datetime(  2022, int(  fromDate[ 3: ]  ), int(  fromDate[ :2 ]  )  )
        toTime      =   datetime(  2022, int(  toDate  [ 3: ]  ), int(  toDate  [ :2 ]  )  )

        # Initialize an empty list to be filled with elements on the xAxis
        xAxis           =   []

        # Make list of all days in time period
        currentDate     =   fromTime
        allDays         =   []

        while currentDate <= toTime:

            xAxis.append  (  str(  currentDate.strftime(  '%d.%m'  )  )  )
            allDays.append(  currentDate.date()  )
            currentDate     +=  timedelta(  days = 1  )

        # Create dictionaries for every stat with the elements on the xAxis as keywords
        eScooters       =   {  i : 0 for i in xAxis  }
        eScootersFrom   =   {  i : 0 for i in xAxis  }
        eScootersTo     =   {  i : 0 for i in xAxis  }
        passengers      =   {  i : 0 for i in xAxis  }
        passengersFrom  =   {  i : 0 for i in xAxis  }
        passengersTo    =   {  i : 0 for i in xAxis  }

        # Iterate through arrivals
        for arrival in arrivals:

            # If arrival was after 23:59 on Dec. 31., break the for-loop
            if arrival.actualTime.year == 2023:

                break

            # Add each stat of the arrival to the dictionaries under the keyword that is the date
            eScooters       [  str(  arrival.actualTime.strftime(  '%d.%m'  )  )  ]         +=  arrival.eScooters
            eScootersFrom   [  str(  arrival.actualTime.strftime(  '%d.%m'  )  )  ]         +=  arrival.eScooters
            passengers      [  str(  arrival.actualTime.strftime(  '%d.%m'  )  )  ]         +=  arrival.passengers
            passengersTo    [  str(  arrival.actualTime.strftime(  '%d.%m'  )  )  ]         +=  arrival.passengers

        # Same as for arrivals, but with departures
        for departure in departures:

            # If departure was after 23:59 on Dec. 31., break the foor loop
            if departure.scheduledTime.year == 2023:
                break

            eScooters       [  str(  departure.scheduledTime.strftime(  '%d.%m'  )  )  ]    +=  departure.eScooters
            eScootersTo     [  str(  departure.scheduledTime.strftime(  '%d.%m'  )  )  ]    +=  departure.eScooters
            passengers      [  str(  departure.scheduledTime.strftime(  '%d.%m'  )  )  ]    +=  departure.passengers
            passengersFrom  [  str(  departure.scheduledTime.strftime(  '%d.%m'  )  )  ]    +=  departure.passengers

        # Make new listst with stats for each date in the same order as the xAxis list.
        ScootersPrDay          =   [  eScooters        [date] for date in xAxis]
        ScootersToPrDay        =   [  eScootersTo      [date] for date in xAxis]
        ScootersFromPrDay      =   [  eScootersFrom    [date] for date in xAxis]
        PassengersPrDay        =   [  passengers       [date] for date in xAxis]
        PassengersToPrDay      =   [  passengersTo     [date] for date in xAxis]
        PassengersFromPrDay    =   [  passengersFrom   [date] for date in xAxis]

        corrCoeff   = \
            {
                "eScootPass"        : self.getCorrelationCoefficient(  ScootersPrDay,     PassengersPrDay      ),
                "eScootToPassFrom"  : self.getCorrelationCoefficient(  ScootersToPrDay,   PassengersFromPrDay  ),
                "eScootFromPassTo"  : self.getCorrelationCoefficient(  ScootersFromPrDay, PassengersToPrDay    )
            }

        # Find total amount of scooters (including those not related to the subway) in the time frame
        totScooters     =   np.sum(  np.array(  [  self.__eScooters[  'both'  ][  date  ] for date in allDays  ]  )  )
        totScootersTo   =   np.sum(  np.array(  [  self.__eScooters[  'to'    ][  date  ] for date in allDays  ]  )  )
        totScootersFrom =   np.sum(  np.array(  [  self.__eScooters[  'from'  ][  date  ] for date in allDays  ]  )  )

        # Find total amount of eScooter rides related to the subway in the time frame
        totRelScooters      =   np.sum(  np.array(  ScootersPrDay      )  )
        totRelScootersTo    =   np.sum(  np.array(  ScootersToPrDay    )  )
        totRelScootersFrom  =   np.sum(  np.array(  ScootersFromPrDay  )  )

        # Find percentages
        try:
            percentage      =   round(  (  totRelScooters     / totScooters      ) * 100, 2  )
            percentageTo    =   round(  (  totRelScootersTo   / totScootersTo    ) * 100, 2  )
            percentageFrom  =   round(  (  totRelScootersFrom / totScootersFrom  ) * 100, 2  )
        except:
            percentage      =   0
            percentageTo    =   0
            percentageFrom  =   0

        unrelatedScooters = \
            {
                "both"  :   {
                                "related"   : totRelScooters,
                                "unrelated" : totScooters - totRelScooters,
                                "total"     : totScooters,
                                "percentage": percentage
                            },
                "to"    :   {
                                "related"   : totRelScootersTo,
                                "unrelated" : totScootersTo - totRelScootersTo,
                                "total"     : totScootersTo,
                                "percentage": percentageTo
                            },
                "from"  :   {
                                "related"   : totRelScootersFrom,
                                "unrelated" : totScootersFrom - totRelScootersFrom,
                                "total"     : totScootersFrom,
                                "percentage": percentageFrom
                            },
            }

        # Create a list with percentage of passengers in total using eScooters
        percentScooters = []
        # Iterate through average eScooters and passengers for each hour
        for scooters, passengers in zip(  ScootersPrDay, PassengersPrDay  ):

            # Try to divide eScooters by passengers to fin percentage
            try:

                percentScooters.append(  round(  (  (  scooters / passengers  ) * 100  ), 2  )  )

            # We cant divide by zero, so if passengers is zero, set the percentage to 0
            except ZeroDivisionError:

                percentScooters.append(  0  )

        # Same as above, but for different stats
        percentScootersTo = []
        for scooters, passengers in zip(  ScootersToPrDay, PassengersFromPrDay  ):

            try:

                percentScootersTo.append(  round(  (  (  scooters / passengers  ) * 100  ), 2  )  )

            except ZeroDivisionError:

                percentScootersTo.append(0)

        # Same as above, but for different stats
        percentScootersFrom = []
        for scooters, passengers in zip(  ScootersFromPrDay, PassengersToPrDay  ):

            try:

                percentScootersFrom.append(round(  (  (  scooters / passengers  ) * 100  ), 2  )  )

            except ZeroDivisionError:

                percentScootersFrom.append(0)

        # Make dictionaries with results
        Scooters = \
            {
                "both"  :   ScootersPrDay,
                "to"    :   ScootersToPrDay,
                "from"  :   ScootersFromPrDay
            }

        Passengers = \
            {
                "both"  : PassengersPrDay,
                "to"    : PassengersToPrDay,
                "from"  : PassengersFromPrDay
            }

        Percentage = \
            {
                "both"  : percentScooters,
                "to"    : percentScootersTo,
                "from"  : percentScootersFrom
            }

        return Scooters, Passengers, Percentage, xAxis, corrCoeff, unrelatedScooters

    # Returns plottable lists with average stats pr. day of the week in a time period
    def plotAverageWeekday(  self,  fromWeek,  toWeek  ):

        nrWeeks         =   int(  toWeek  ) - int(  fromWeek  ) + 1

        # Create a datetime object for the first day of the year
        jan1            =   datetime(2022, 1, 1)

        # Calculate the number of days to Monday of the first week
        daysToMonday    =   (  7 - jan1.weekday()  ) % 7

        # Calculate the number of days to Monday of the desired week
        daysToFromWeek  =   daysToMonday + (  int(  fromWeek  ) - 1  ) * 7

        # Create a datetime object for Monday of the desired week
        fromDate        =   jan1 + timedelta(  days = daysToFromWeek  )

        # Create a datetime object for Sunday of the last week
        toDate          =   fromDate + timedelta( days = (  (  7 * nrWeeks  ) - 1  )  )

        # If the last day is in 2023, change it to be 31. Dec
        if toDate.year == 2023:

            toDate      =   datetime(  2022, 12, 31  )

        # Make list of all days in time period
        currentDate     =   fromDate
        allDays         =   []

        while currentDate <= toDate:

            allDays.append(  currentDate.date()  )
            currentDate     +=  timedelta(  days = 1  )

        # Format the datetime objects into strings to comply with self.iterateThrougArrivals()
        fromDate        =   fromDate.strftime(  '%d.%m'  )
        toDate          =   toDate.strftime  (  '%d.%m'  )

        # Create a list with days of the week
        xAxis           =   [  "Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn"  ]

        # Fetch the list of arrivals and departures in this time period
        arrivals        =   self.iterateThroughArrivals(  "Arrivals"  , fromDate, toDate  )
        departures      =   self.iterateThroughArrivals(  "Departures", fromDate, toDate  )

        # Create dictionaries that collects all data sorted by day. Will be used to find the correlation
        # coefficient between amount of passengers and eScooter rides later.
        passengersToPrDay           =   {  date : 0    for date in allDays  }
        passengersFromPrDay         =   {  date : 0    for date in allDays  }
        passengersPrDay             =   {  date : 0    for date in allDays  }
        eScootersToPrDay            =   {  date : 0    for date in allDays  }
        eScootersFromPrDay          =   {  date : 0    for date in allDays  }
        eScootersPrDay              =   {  date : 0    for date in allDays  }

        # Create dictionaries for each stat. Keywords are the elements on the xAxis.
        eScooters       =   {  i : 0 for i in xAxis  }
        eScootersFrom   =   {  i : 0 for i in xAxis  }
        eScootersTo     =   {  i : 0 for i in xAxis  }
        passengers      =   {  i : 0 for i in xAxis  }
        passengersFrom  =   {  i : 0 for i in xAxis  }
        passengersTo    =   {  i : 0 for i in xAxis  }

        # Iterate through the arrivals
        for arrival in arrivals:

            # If arrival was after 23:59 on Dec. 31., break the foor loop
            if arrival.actualTime.year == 2023:

                break

            # Uses the .weekday() function (returns an integer 0-6 corresponding to day of the week)
            # to add the arrival stats to correct dictionary keyword.
            eScooters           [  xAxis[  arrival.actualTime.weekday()  ]  ]       +=  arrival.eScooters
            eScootersFrom       [  xAxis[  arrival.actualTime.weekday()  ]  ]       +=  arrival.eScooters
            passengers          [  xAxis[  arrival.actualTime.weekday()  ]  ]       +=  arrival.passengers
            passengersTo        [  xAxis[  arrival.actualTime.weekday()  ]  ]       +=  arrival.passengers

            # Adds the values to dictionaries for each specific date
            eScootersPrDay      [  arrival.actualTime.date()  ]     +=  arrival.eScooters
            eScootersFromPrDay  [  arrival.actualTime.date()  ]     +=  arrival.eScooters
            passengersPrDay     [  arrival.actualTime.date()  ]     +=  arrival.passengers
            passengersToPrDay   [  arrival.actualTime.date()  ]     +=  arrival.passengers

        # Iterate through the departures
        for departure in departures:

            # If departure was after 23:59 on Dec. 31., break the foor loop
            if departure.scheduledTime.year == 2023:

                break

            # Uses the .weekday() function (returns an integer 0-6 corresponding to day of the week) to add
            # the departure stats to correct dictionary keyword.
            eScooters               [  xAxis[  departure.scheduledTime.weekday()  ]  ]    +=  departure.eScooters
            eScootersTo             [  xAxis[  departure.scheduledTime.weekday()  ]  ]    +=  departure.eScooters
            passengers              [  xAxis[  departure.scheduledTime.weekday()  ]  ]    +=  departure.passengers
            passengersFrom          [  xAxis[  departure.scheduledTime.weekday()  ]  ]    +=  departure.passengers

            # Adds the values to dictionaries for each specific date
            eScootersPrDay          [  departure.scheduledTime.date()  ]   +=  departure.eScooters
            eScootersToPrDay        [  departure.scheduledTime.date()  ]   +=  departure.eScooters
            passengersPrDay         [  departure.scheduledTime.date()  ]   +=  departure.passengers
            passengersFromPrDay     [  departure.scheduledTime.date()  ]   +=  departure.passengers

        # Create lists to hold each value for each day so that correlation can be calculated
        eachDay     =   {   "eScooters"  : [],  "eScootersTo"  : [],     "eScootersFrom"  : [],
                            "passengers" : [],  "passengersTo" : [],     "passengersFrom" : []  }

        eachWeekday =   {   weekday : {  "eScooters"  : [],  "eScootersTo"  : [],     "eScootersFrom"  : [],
                                         "passengers" : [],  "passengersTo" : [],     "passengersFrom" : []  }
                            for weekday in xAxis  }

        # Iterate through every date in allDays and add values to correct lists
        for day in allDays:

            eachDay[  "eScooters"       ].append(  eScootersPrDay       [  day  ]  )
            eachDay[  "eScootersTo"     ].append(  eScootersToPrDay     [  day  ]  )
            eachDay[  "eScootersFrom"   ].append(  eScootersFromPrDay   [  day  ]  )
            eachDay[  "passengers"      ].append(  passengersPrDay      [  day  ]  )
            eachDay[  "passengersFrom"  ].append(  passengersFromPrDay  [  day  ]  )
            eachDay[  "passengersTo"    ].append(  passengersToPrDay    [  day  ]  )

            eachWeekday[  xAxis[  day.weekday()  ]  ][  "eScooters"       ].append(  eScootersPrDay       [  day  ]  )
            eachWeekday[  xAxis[  day.weekday()  ]  ][  "eScootersTo"     ].append(  eScootersToPrDay     [  day  ]  )
            eachWeekday[  xAxis[  day.weekday()  ]  ][  "eScootersFrom"   ].append(  eScootersFromPrDay   [  day  ]  )
            eachWeekday[  xAxis[  day.weekday()  ]  ][  "passengers"      ].append(  passengersPrDay      [  day  ]  )
            eachWeekday[  xAxis[  day.weekday()  ]  ][  "passengersFrom"  ].append(  passengersFromPrDay  [  day  ]  )
            eachWeekday[  xAxis[  day.weekday()  ]  ][  "passengersTo"    ].append(  passengersToPrDay    [  day  ]  )

        # Make dictionaries with all the correlation coefficients:
        genCorrCoeff   =    \
        {
            "eScootPass"       : self.getCorrelationCoefficient(  eachDay[  "eScooters"       ],
                                                                  eachDay[  "passengers"      ]  ),
            "eScootToPassFrom" : self.getCorrelationCoefficient(  eachDay[  "eScootersTo"     ],
                                                                  eachDay[  "passengersFrom"  ]  ),
            "eScootFromPassTo" : self.getCorrelationCoefficient(  eachDay[  "eScootersFrom"   ],
                                                                  eachDay[  "passengersTo"    ]  )
        }

        specCorrCoeff   =   \
        {
            weekday :
            {
                "eScootPass"       : self.getCorrelationCoefficient(  eachWeekday[  weekday  ][  "eScooters"       ],
                                                                      eachWeekday[  weekday  ][  "passengers"      ]  ),
                "eScootToPassFrom" : self.getCorrelationCoefficient(  eachWeekday[  weekday  ][  "eScootersTo"     ],
                                                                      eachWeekday[  weekday  ][  "passengersFrom"  ]  ),
                "eScootFromPassTo" : self.getCorrelationCoefficient(  eachWeekday[  weekday  ][  "eScootersFrom"   ],
                                                                      eachWeekday[  weekday  ][  "passengersTo"    ]  )
            }   for weekday in xAxis
        }

        # Find total amount of scooters (including those not related to the subway) in the time frame
        totScooters     =   np.sum(  np.array(  [  self.__eScooters[  'both'  ][  date  ] for date in allDays  ]  )  )
        totScootersTo   =   np.sum(  np.array(  [  self.__eScooters[  'to'    ][  date  ] for date in allDays  ]  )  )
        totScootersFrom =   np.sum(  np.array(  [  self.__eScooters[  'from'  ][  date  ] for date in allDays  ]  )  )

        # Find total amount of eScooter rides related to the subway in the time frame
        totRelScooters      = np.sum(  np.array(  eachDay[  "eScooters"      ]  )  )
        totRelScootersTo    = np.sum(  np.array(  eachDay[  "eScootersTo"    ]  )  )
        totRelScootersFrom  = np.sum(  np.array(  eachDay[  "eScootersFrom"  ]  )  )

        # Find percentages
        try:
            percentage      =   round(  (  totRelScooters     / totScooters      ) * 100, 2  )
            percentageTo    =   round(  (  totRelScootersTo   / totScootersTo    ) * 100, 2  )
            percentageFrom  =   round(  (  totRelScootersFrom / totScootersFrom  ) * 100, 2  )
        except:
            percentage      =   0
            percentageTo    =   0
            percentageFrom  =   0

        unrelatedScooters = \
            {
                "both"  :   {
                                "related"   : totRelScooters,
                                "unrelated" : totScooters - totRelScooters,
                                "total"     : totScooters,
                                "percentage": percentage
                            },
                "to"    :   {
                                "related"   : totRelScootersTo,
                                "unrelated" : totScootersTo - totRelScootersTo,
                                "total"     : totScootersTo,
                                "percentage": percentageTo
                            },
                "from"  :   {
                                "related"   : totRelScootersFrom,
                                "unrelated" : totScootersFrom - totRelScootersFrom,
                                "total"     : totScootersFrom,
                                "percentage": percentageFrom
                            },
            }

        # Iterate through each weekday on the xAxis
        for weekday in xAxis:

            # Fetch values from each xAxis keyword and divide by number of days to find the average. Two decimals
            eScooters     [  weekday  ]     =   round(  eScooters     [  weekday  ] / nrWeeks, 2  )
            eScootersTo   [  weekday  ]     =   round(  eScootersTo   [  weekday  ] / nrWeeks, 2  )
            eScootersFrom [  weekday  ]     =   round(  eScootersFrom [  weekday  ] / nrWeeks, 2  )
            passengers    [  weekday  ]     =   round(  passengers    [  weekday  ] / nrWeeks, 2  )
            passengersTo  [  weekday  ]     =   round(  passengersTo  [  weekday  ] / nrWeeks, 2  )
            passengersFrom[  weekday  ]     =   round(  passengersFrom[  weekday  ] / nrWeeks, 2  )

        # Create new lists with values for each weekday in the same order as xAxis
        avgScootersPrWeekday                =   [  eScooters     [  weekday  ] for weekday in xAxis  ]
        avgScootersToPrWeekday              =   [  eScootersTo   [  weekday  ] for weekday in xAxis  ]
        avgScootersFromPrWeekday            =   [  eScootersFrom [  weekday  ] for weekday in xAxis  ]
        avgPassengersPrWeekday              =   [  passengers    [  weekday  ] for weekday in xAxis  ]
        avgPassengersToPrWeekday            =   [  passengersTo  [  weekday  ] for weekday in xAxis  ]
        avgPassengersFromPrWeekday          =   [  passengersFrom[  weekday  ] for weekday in xAxis  ]

        # Create a list with percentage of passengers in total using eScooters
        percentScooters     =   []
        # Iterate through average eScooters and passengers for each weekday
        for avgScooters, avgPassengers in zip(  avgScootersPrWeekday, avgPassengersPrWeekday  ):

            # Try to divide eScooters by passengers to find percentage
            try:

                percentScooters.append(  round(  (  (  avgScooters / avgPassengers  ) * 100  ), 2  )  )

            # We cant divide by zero, so if passengers is zero, set the percentage to 0
            except ZeroDivisionError:

                percentScooters.append(  0  )

        # Same as above
        percentScootersTo   =   []
        for avgScooters, avgPassengers in zip(  avgScootersToPrWeekday, avgPassengersFromPrWeekday  ):

             try:

                percentScootersTo.append(  round(  (  (  avgScooters / avgPassengers  ) * 100  ), 2  )  )

             except ZeroDivisionError:

                percentScootersTo.append(  0  )

        # Same as above
        percentScootersFrom =   []
        for avgScooters, avgPassengers in zip(  avgScootersFromPrWeekday, avgPassengersToPrWeekday  ):

            try:

                percentScootersFrom.append(  round(  (  (  avgScooters / avgPassengers  ) * 100  ), 2  )  )

            except ZeroDivisionError:

                percentScootersFrom.append(  0  )

        # Make dictionaries with results
        Scooters = \
            {
                "both"  : avgScootersPrWeekday,
                "to"    : avgScootersToPrWeekday,
                "from"  : avgScootersFromPrWeekday
            }

        Passengers = \
            {
                "both"  : avgPassengersPrWeekday,
                "to"    : avgPassengersToPrWeekday,
                "from"  : avgPassengersFromPrWeekday
            }

        Percentage = \
            {
                "both"  : percentScooters,
                "to"    : percentScootersTo,
                "from"  : percentScootersFrom
            }

        return Scooters, Passengers, Percentage, xAxis, genCorrCoeff, specCorrCoeff, unrelatedScooters

    # Makes and shows a type of graph depending on the input parameters
    def makeGraph(  self, fromDate, toDate, direction, type  ):

        # Fetch the xAxis and yAxis data depening on what type of graph is desired
        if type == "hour":

            scooters, passengers, percents, xAxis, _, _, _      =   self.plotAverageHour(  fromDate, toDate  )

        elif type == "day":

            scooters, passengers, percents, xAxis, _, _         =   self.plotDays(  fromDate, toDate  )

        elif type == "week":

            scooters, passengers, percents, xAxis, _, _, _      =   self.plotAverageWeekday(  fromDate, toDate  )

        elif type == "all":

            arrivals = self.iterateThroughArrivals("Arrivals", fromDate, toDate)
            departures = self.iterateThroughArrivals("Departures", fromDate, toDate)

            # Make a list with all arrivals and all departures
            allSubways  =   []
            allSubways.extend(  arrivals    )
            allSubways.extend(  departures  )

            # Sort the list by the scheduledTime property
            allSubways  =   sorted(  allSubways, key=lambda x: x.scheduledTime  )

            xAxis       =   [ str(sub.scheduledTime) for sub in allSubways  ]
            passengers  =   [sub.passengers for sub in allSubways  ]
            scooters    =   [sub.eScooters for sub in allSubways  ]

            fig, ax = plt.subplots()

            twin1 = ax.twinx()

            ax.bar(xAxis, passengers, label="Passasjerer")
            twin1.plot(xAxis, scooters, color="red", label="El-Sparkesykler")
            twin1.set_ylim(0, 50)
            ax.set_ylim(0, 120)

            twin1.set_ylabel(f"Antall el-sparkesykler i forbindelse med gitte avgang")
            ax.set_ylabel(" Antall passasjerer på gitte avgang")
            plt.title("Antall passasjerer og relaterte el-sparkesykler for hver eneste avgang mellom"
                      "01.06.2022 og 07.06.2022")



            plt.legend()

            plt.show()

            return

        translate   =   \
            {
                "to"    :   ["til", "Påstigende", "avganger"],
                "from"  :   ["fra", "Avstigende", "ankomster"],
                "both"  :   ["til og fra", "På- og avstigende", "avganger og -ankomster"]
            }

        time        =   \
            {
                "hour"  :   "Timer",
                "day"   :   "Dato",
                "week"  :   "Ukedager"
            }

        highestPassengerCount   =   0
        for passengerCount in passengers[  direction  ]:
            if passengerCount > highestPassengerCount:
                highestPassengerCount = passengerCount

        highestScooterCount   =   0
        for scooterCount in scooters[  direction  ]:
            if scooterCount > highestScooterCount:
                highestScooterCount = scooterCount

        highestPercentage   =   0
        for percentage in percents[  direction  ]:
            if percentage > highestPercentage:
                highestPercentage = percentage

        passLimit = highestPassengerCount + ((highestPassengerCount//10)*3 )
        if type == "hour":
            scooterLimit = highestScooterCount + 2
        elif highestScooterCount < 1:
            scooterLimit = highestScooterCount + 2
        else:
            scooterLimit = highestScooterCount + ( ( highestScooterCount//10) * 3 )
        percentageLimit = round((highestPercentage + 2), 0)

        fig, ax = plt.subplots()
        fig.subplots_adjust(right=0.75)



        twin1 = ax.twinx()
        twin2 = ax.twinx()

        # Offset the right spine of twin2.  The ticks and label have already been
        # placed on the right by twinx above.
        twin2.spines.right.set_position(("axes", 1.2))

        if type == "day":
            if len(  xAxis  ) > 14:
                p1 = ax.bar(xAxis, passengers[direction], color="grey", label=f"{translate[direction][1]} passasjerer")
            else:
                p1 = ax.bar(xAxis, passengers[direction], color="grey", label=f"{translate[direction][1]} passasjerer")
        else:
            p1 = ax.bar(xAxis, passengers[  direction  ], color="grey", label=f"{translate[direction][1]} passasjerer")
        p2, = twin1.plot(xAxis, scooters[  direction  ], "r-", label=f"Antall el-sparkesykkelturer {translate[direction][0]} t-bane")
        p3, = twin2.plot(xAxis, percents[  direction  ], "b-", label=f"El-sparkesyklende passasjerer i prosent")

        if type == "hour":
            plt.title(f"Snittverdier pr. time i perioden {fromDate} - {toDate}")
        elif type == "day":
            plt.title(f"Faktiske verdier pr. dag i perioden {fromDate} - {toDate}")
        elif type == "week":
            plt.title(f"Snittverdier pr. ukedag fra uke {fromDate} til uke {toDate}")

        ax.set_ylim(0, passLimit)
        twin1.set_ylim(0, scooterLimit)
        twin2.set_ylim(0, percentageLimit)

        ax.set_xlabel(time[type])
        ax.set_ylabel(f"{translate[direction][1]} passasjerer", fontsize=12)
        twin1.set_ylabel(f"Antall el-sparkesykler {translate[direction][0]} t-bane", fontsize=12)
        twin2.set_ylabel(f"Prosent el-sparkesykler {translate[direction][0]} t-bane ift. {translate[direction][1]}passasjerer", fontsize=12)


        twin1.yaxis.label.set_color(p2.get_color())
        twin2.yaxis.label.set_color(p3.get_color())

        firstOfTheMonth =   ["01.01", "01.02", "01.03", "01.04", "01.05", "01.06",
                             "01.07", "01.08", "01.09", "01.10", "01.11", "01.12"  ]

        # Set the labels on the xAxis ticks
        if type == "day":

            if len(  xAxis  ) > 14:

                interval = len(  xAxis  ) // 10

                if (  fromDate, toDate  ) == (  "01.01", "31.12"  ):

                    # Set the x-axis ticks to display only every n-th label
                    ax.set_xticks(  firstOfTheMonth  )

                elif( fromDate[:2], toDate[:2]  ) == (  "01", "01"  ):
                    fromMonth   =   int(  fromDate[ 3: ]  ) - 1
                    toMonth     =   int(  toDate  [ 3: ]  )
                    ax.set_xticks(  firstOfTheMonth[fromMonth:toMonth]  )
                else:

                    # Set the x-axis ticks to display only every n-th label
                    ax.set_xticks(xAxis[::interval])

            # Rotate the tick labels to avoid overlapping
            plt.xticks(rotation=45)

        tkw = dict(size=4, width=1.5)
        twin1.tick_params(axis='y', colors=p2.get_color(), **tkw)
        twin2.tick_params(axis='y', colors=p3.get_color(), **tkw)
        ax.tick_params(axis='x', **tkw)

        ax.legend(handles=[p1, p2, p3])

        plt.show()

    # Function that takes in a time period and plots average scooter trips pr. minute
    def scootersPrMinute(  self, fromDate, toDate, direction  ):

        if direction == "both":

            return


        # Convert the dates to datetime objects
        fromTime    =   datetime(  2022,  int(  fromDate[ 3: ]  ),  int(  fromDate[ :2 ]  )  )
        toTime      =   datetime(  2022,  int(  toDate  [ 3: ]  ),  int(  toDate  [ :2 ]  )  )

        # Make list of all days in time period
        currentDate     =   fromTime
        allDays         =   []

        while currentDate <= toTime:

            allDays.append(  currentDate.date()  )
            currentDate     +=  timedelta(  days = 1  )

        # Create dictionary with all minutes in an hour
        prMinute = \
            {
                i : 0 for i in range(  60  )
            }
        prMinuteOpHours = \
            {
                i : 0 for i in range(  60  )
            }

        prMinuteRelevant = \
            {
                i : 0 for i in range(  60  )
            }

        prMinuteRelevantOpHours = \
            {
                i : 0 for i in range(  60  )
            }

        # Check direction
        if direction == "from":

            eScoots =   self.eFrom
            subway  =   self.iterateThroughArrivals(  "Arrivals", fromDate, toDate  )

        elif direction == "to":

            eScoots    =   self.eTo
            subway     =   self.iterateThroughArrivals(  "Departures", fromDate, toDate  )


        translate = \
        {
            "from" : "fra",
            "to"   : "til"
        }

        # Add up trips pr minutes
        for trip in eScoots:

            if trip.date() in allDays:

                prMinute[  trip.minute  ]   +=  1

        # Add up trips pr minutes for relevant scooters
        for trip in subway:

            for eScooter in trip.eScooterTime:

                prMinuteRelevant[  eScooter.minute  ]   +=  1

        # Calculate average nr. of trips pr minute
        for minute in prMinuteRelevant:

            # Operational hours are generally from 05:00 to (not including) 02:00, meaning 21 hours.
            # There are occationally a departure or arrival after 02:00 or before 05:00, but that is so rare that
            # it makes litle sense to calculate average in operatinal hours with these.
            prMinuteRelevantOpHours[  minute  ]     =   prMinuteRelevant[  minute  ] / (  21 * len(  allDays  )  )
            prMinuteRelevant       [  minute  ]     =   prMinuteRelevant[  minute  ] / (  24 * len(  allDays  )  )

        # Calculate average nr. of trips pr minute
        for minute in prMinute:

            # Operational hours are generally from 05:00 to (not including) 02:00, meaning 21 hours.
            # There are occationally a departure or arrival after 02:00 or before 05:00, but that is so rare that
            # it makes litle sense to calculate average in operatinal hours with these.
            prMinuteOpHours[  minute  ]     =   prMinute[  minute  ] / (  21 * len(  allDays  )  )
            prMinute       [  minute  ]     =   prMinute[  minute  ] / (  24 * len(  allDays  )  )

        # Make a list with all scheduled times.
        schedTime   =   [  sub.scheduledTime.minute for sub in subway  ]

        # Separate out just the unique times
        uniqueList  =   list(  set(  schedTime  )  )

        # Create the x-axis
        xAxis                   =   []
        xAxis.extend(  [  f"xx:0{i}" for i in range(  10      )  ]  )
        xAxis.extend(  [  f"xx:{i}"  for i in range(  10, 60  )  ]  )

        # make ticks to go along the x-axis
        xticks          =   [  xAxis[ i ] for i in range(0, 60, 5) ]
        xticksLabels    =   [  str(i)     for i in xticks  ]


        totPrMin                =   [  prMinute                 [  minute  ] for minute in prMinute  ]
        totPrMinOpHours         =   [  prMinuteOpHours          [  minute  ] for minute in prMinuteOpHours   ]
        relevantPrMin           =   [  prMinuteRelevant         [  minute  ] for minute in prMinuteRelevant  ]
        relevantPrMinOpHours    =   [  prMinuteRelevantOpHours  [  minute  ] for minute in prMinuteRelevantOpHours  ]

        # plot the data including nonrelevant scooters, average over all hours
        plt.plot(xAxis, totPrMin)
        plt.xlabel("Minutter")
        plt.title(f"Snitt antall elsparkesykkelturer (inkludert urelevante) {translate[direction]} "
                  f"Kolsaas stasjon pr. min")
        plt.ylabel(f"Gjennomsnittlig elsparkesykler {translate[direction]} stasjonen pr. Min")
        plt.xticks( xticks, xticksLabels )


        # draw a vertical line at the arrivals/departures
        for time in uniqueList:

            plt.axvline(  x = time, color = 'r')

        # plot the data including nonrelevant scooters, average over all hours in operational hours for the subway
        plt.figure()  # create a new figure
        plt.plot(  xAxis, totPrMinOpHours  )
        plt.title(f"Snitt antall elsparkesykkelturer (inkluderte urelevante) {translate[direction]} "
                  f"Kolsaas stasjon pr. min i t-banens operasjonstimer")
        plt.xlabel("Minutter")
        plt.ylabel(f"Gjennomsnittlig elsparkesykler {translate[direction]} stasjonen pr. Min")
        plt.xticks( xticks, xticksLabels )

        # draw a vertical line at x=5
        for time in uniqueList:

            plt.axvline(  x = time, color = 'r')

        # Plot data for only relevant scooters, average over all hours
        plt.figure()  # create a new figure
        plt.plot(  xAxis, relevantPrMin  )
        plt.title(f"Snitt antall relevante elsparkesykkelturer {translate[direction]} Kolsaas stasjon pr. min")
        plt.xlabel("Minutter")
        plt.ylabel(f"Gjennomsnittlig elsparkesykler {translate[direction]} stasjonen pr. Min")
        plt.xticks( xticks, xticksLabels )

        # draw a vertical line at x=5
        for time in uniqueList:

            plt.axvline(  x = time, color = 'r')

        # Plot data for only relevant scooters, average over all hours in the subways operational hours
        plt.figure()  # create a new figure
        plt.plot(  xAxis, relevantPrMinOpHours  )
        plt.title(f"Snitt antall relevante elsparkesykkelturer {translate[direction]} Kolsaas stasjon pr. min "
                  f"i t-banens operasjonstid")
        plt.xlabel("Minutter")
        plt.ylabel(f"Gjennomsnittlig elsparkesykler {translate[direction]} stasjonen pr. Min")
        plt.xticks( xticks, xticksLabels )

        # draw a vertical line at x=5
        for time in uniqueList:

            plt.axvline(  x = time, color = 'r')

        # show the plot
        plt.show()

    # Finds the correlation coefficient between amount of passengers and eScooter rides based
    # on input data
    def getCorrelationCoefficient(  self, eScooters, passengers  ):

        correlationCoefficient, pValue      =   stats.pearsonr(  passengers, eScooters  )
        correlationCoefficient              =   round(  correlationCoefficient, 3  )

        spearmanRankCorr, spearmanPvalue    =   stats.spearmanr(  passengers, eScooters  )
        spearmanRankCorr                    =   round(  spearmanRankCorr, 3  )

        kendallsTau, kendallsPvalue         =   stats.kendalltau(  passengers, eScooters)
        kendallsTau                         =   round(  kendallsTau, 3  )

        gammaCorrelation, gammaPvalue       =   stats.weightedtau(  passengers, eScooters  )
        gammaCorrelation                    =   round(  gammaCorrelation, 3  )

        correlations    = \
            {
                "Pearson"   :   [  correlationCoefficient, pValue           ],
                "Spearman"  :   [  spearmanRankCorr      , spearmanPvalue   ],
                "Kendall"   :   [  kendallsTau           , kendallsPvalue   ],
                "Gamma"     :   [  gammaCorrelation      , gammaPvalue      ]
            }

        return correlations

    # Takes in a time period and makes an excell file with departures and arrivals in that time frame
    def makeExcelSheet(  self, fromDate, toDate, type = None  ):

        # Find correct starting and ending date if input is weeknumbers
        if type == "week":

            fromWeek        =   fromDate
            toWeek          =   toDate

            nrWeeks         =   int(  toWeek  ) - int(  fromWeek  ) + 1

            # Create a datetime object for the first day of the year
            jan1            =   datetime(  2022, 1, 1  )

            # Calculate the number of days to Monday of the first week
            daysToMonday    =   (  7 - jan1.weekday()  ) % 7

            # Calculate the number of days to Monday of the desired week
            daysToFromWeek  =   daysToMonday + (  int(  fromWeek  ) - 1  ) * 7

            # Create a datetime object for Monday of the desired week
            fromDate        =   jan1 + timedelta(  days = daysToFromWeek  )

            # Create a datetime object for Sunday of the last week
            toDate          =   fromDate + timedelta(  days = (  (  7 * nrWeeks  ) - 1  )  )

            # Extract date strings from datetime objects
            fromDate        =   fromDate.strftime(  '%d.%m'  )
            toDate          =   toDate.strftime  (  '%d.%m'  )

        # Fetch lists of arrivals and departures within the time period
        arrivals    =   self.iterateThroughArrivals(  "Arrivals"  , fromDate, toDate  )
        departures  =   self.iterateThroughArrivals(  "Departures", fromDate, toDate  )

        # Make a list with all arrivals and all departures
        allSubways  =   []
        allSubways.extend(  arrivals    )
        allSubways.extend(  departures  )

        # Sort the list by the scheduledTime property
        allSubways  =   sorted(  allSubways, key = lambda x: x.scheduledTime  )

        arrivalsDataFrame       =   \
            {
                "Dato"              :   [],
                "Planlagt ankomst"  :   [],
                "Faktisk ankomst"   :   [],
                "Avstigende"        :   [],
                "El-sparkesykler"   :   [],
                "Temperatur (C)"    :   [],
                "Middelvind (m/s)"  :   [],
                "Nedbør (mm/time)"  :   []
            }

        departuresDataFrame   =     \
            {
                "Dato"              :   [],
                "Planlagt avgang"   :   [],
                "Faktisk avgang"    :   [],
                "Påstigende"        :   [],
                "El-sparkesykler"   :   [],
                "Temperatur (C)"    :   [],
                "Middelvind (m/s)"  :   [],
                "Nedbør (mm/time)"  :   []
            }

        allSubwaysDataFrame     =     \
            {
                "Type"              :   [],
                "Dato"              :   [],
                "Planlagt tid"      :   [],
                "Faktisk tid"       :   [],
                "Passasjerer av/på" :   [],
                "El-sparkesykler"   :   [],
                "Temperatur (C)"    :   [],
                "Middelvind (m/s)"  :   [],
                "Nedbør (mm/time)"  :   []
            }

        # Iterate through the sorted list of all subways
        for subway in allSubways:

            # Add arrivals to the arrivals dataframe
            if subway.direction == "Ankomst":

                arrivalsDataFrame[  "Dato"              ].append(  subway.scheduledTime.strftime(  '%d.%m.%Y'  )  )
                arrivalsDataFrame[  "Planlagt ankomst"  ].append(  subway.scheduledTime.strftime(  '%H:%M:%S'     )  )
                arrivalsDataFrame[  "Faktisk ankomst"   ].append(  subway.actualTime.strftime(     '%H:%M:%S'  )  )
                arrivalsDataFrame[  "Avstigende"        ].append(  subway.passengers     )
                arrivalsDataFrame[  "El-sparkesykler"   ].append(  subway.eScooters      )
                arrivalsDataFrame[  "Temperatur (C)"    ].append(  subway.temperature    )
                arrivalsDataFrame[  "Middelvind (m/s)"  ].append(  subway.wind           )
                arrivalsDataFrame[  "Nedbør (mm/time)"  ].append(  subway.rain           )

            # Add departures to the departures dataframe
            elif subway.direction == "Avgang":

                departuresDataFrame[  "Dato"              ].append(  subway.scheduledTime.strftime(  '%d.%m.%Y'  )  )
                departuresDataFrame[  "Planlagt avgang"   ].append(  subway.scheduledTime.strftime(  '%H:%M:%S'     )  )
                departuresDataFrame[  "Faktisk avgang"    ].append(  subway.actualTime.strftime(     '%H:%M:%S'  )  )
                departuresDataFrame[  "Påstigende"        ].append(  subway.passengers     )
                departuresDataFrame[  "El-sparkesykler"   ].append(  subway.eScooters      )
                departuresDataFrame[  "Temperatur (C)"    ].append(  subway.temperature    )
                departuresDataFrame[  "Middelvind (m/s)"  ].append(  subway.wind           )
                departuresDataFrame[  "Nedbør (mm/time)"  ].append(  subway.rain           )

            # Add every subway to the allSubways dataframe

            allSubwaysDataFrame[  "Type"               ].append(  subway.direction      )
            allSubwaysDataFrame[  "Dato"               ].append(  subway.scheduledTime.strftime(  '%d.%m.%Y'  )  )
            allSubwaysDataFrame[  "Planlagt tid"       ].append(  subway.scheduledTime.strftime(  '%H:%M:%S'     )  )
            allSubwaysDataFrame[  "Faktisk tid"        ].append(  subway.actualTime.strftime(     '%H:%M:%S'  )  )
            allSubwaysDataFrame[  "Passasjerer av/på"  ].append(  subway.passengers     )
            allSubwaysDataFrame[  "El-sparkesykler"    ].append(  subway.eScooters      )
            allSubwaysDataFrame[  "Temperatur (C)"     ].append(  subway.temperature    )
            allSubwaysDataFrame[  "Middelvind (m/s)"   ].append(  subway.wind           )
            allSubwaysDataFrame[  "Nedbør (mm/time)"   ].append(  subway.rain           )

        # Create a pandas dataframe for each dictionary
        departuresDataFrame     =   pd.DataFrame(  departuresDataFrame  )
        arrivalsDataFrame       =   pd.DataFrame(  arrivalsDataFrame    )
        allSubwaysDataFrame     =   pd.DataFrame(  allSubwaysDataFrame  )

        # Set a custom file name
        if type == "week":

            filename    =   f"{  self.filename  }_Uke_{  fromWeek  }_til_Uke_{  toWeek  }_" \
                            f"marginFra_{  self.__marginFrom  }min_marginTil_{  self.__marginTo  }min.xlsx"

        else:

            filename    =   f"{  self.filename  }_{  fromDate  }_til_{  toDate  }_" \
                            f"marginFra_{  self.__marginFrom  }min_marginTil_{  self.__marginTo  }min.xlsx"

        # Create an Excel writer object to save the file
        writer          =       pd.ExcelWriter(  f'C:/Users/mgnso/OneDrive/Skrivebord/Excelark/{  filename  }',
                                                 engine = 'xlsxwriter'                                           )

        # Write each dataframe to a separate sheet in the file
        allSubwaysDataFrame.to_excel(  writer, sheet_name = 'Alle'     , index = False  )
        departuresDataFrame.to_excel(  writer, sheet_name = 'Avganger' , index = False  )
        arrivalsDataFrame.to_excel(    writer, sheet_name = 'Ankomster', index = False  )

        # Save the excel file
        writer.save()

    def makeExcelSheetHour(  self, fromDate, toDate ):

        # Create datetime objects of the toDate and fromDate and calculate how many days
        # there are between them, including the fromDate and toDate.
        fromTime        =   datetime(  2022, int(  fromDate[ 3: ]  ), int(  fromDate[ :2 ]  )  )
        toTime          =   datetime(  2022, int(  toDate  [ 3: ]  ), int(  toDate  [ :2 ]  )  )
        days            =   (  toTime - fromTime  ).days + 1

        # Make list of all days in time period
        currentDate     =   fromTime
        allDays         =   []

        while currentDate <= toTime:

            allDays.append(  currentDate.date()  )
            currentDate     +=  timedelta(  days = 1  )

        # Create a list with the elements on the xAxis of the graph. Here hours from 04:00 to 02:00
        xAxis       =   [ 0, 1, 2 ]
        xAxis.extend([  i for i in range(  4, 24  )  ])
        xAxis.append(0)
        xAxis.append(1)
        xAxis.append(2)

        # Create dictionaries that collects all data pr. specific each hour. Will be used to find the correlation
        # coefficient between amount of passengers and eScooter rides.
        passengersPrHour        =   {  date   :   {    hour   :   0    for hour in xAxis   }   for date in allDays  }
        eScootersPrHour         =   {  date   :   {    hour   :   0    for hour in xAxis   }   for date in allDays  }
        arrivalPrHour           =   {  date   :   {    hour   :   None for hour in xAxis   }   for date in allDays  }

        # Fetch the list of arrivals and departures in this time period
        arrivals    = self.iterateThroughArrivals("Arrivals", fromDate, toDate)
        departures  = self.iterateThroughArrivals("Departures", fromDate, toDate)

        # Make a list with all arrivals and all departures
        allSubways = []
        allSubways.extend(arrivals)
        allSubways.extend(departures)

        # Sort the list by the scheduledTime property
        allSubways  =   sorted(  allSubways, key = lambda x: x.scheduledTime  )

        # Iterate through the arrivals
        for arrival in allSubways:

            # If arrival was after 23:59 on Dec. 31., break the foor loop
            if arrival.actualTime.year == 2023:
                break

            # Add the passenger and eScooter count to a variable designated to the specific hour
            eScootersPrHour[arrival.actualTime.date()][arrival.actualTime.hour] += arrival.eScooters
            passengersPrHour[arrival.actualTime.date()][arrival.actualTime.hour] += arrival.passengers
            arrivalPrHour[arrival.actualTime.date()][arrival.actualTime.hour] = arrival

        allSubwaysDataFrame = \
            {
                "Dato": [],
                "Time": [],
                "Passasjerer av/på": [],
                "El-sparkesykler til/fra": [],
                "Temperatur (C)": [],
                "Middelvind (m/s)": [],
                "Nedbør (mm/time)": []
            }


        lastcheckedWeather = 0
        for date in passengersPrHour:

            for hour in passengersPrHour[date]:

                allSubwaysDataFrame["Dato"].append(date)
                allSubwaysDataFrame["Time"].append(hour)
                allSubwaysDataFrame["Passasjerer av/på"].append(passengersPrHour[date][hour])
                allSubwaysDataFrame["El-sparkesykler til/fra"].append(eScootersPrHour[date][hour])

                if passengersPrHour[date][hour] == 0:

                    for i in range(lastcheckedWeather, len(self.__weathertime)-1):

                        weathertime = self.__weathertime[i]
                        print(weathertime.date(), weathertime.hour, "\t", date, hour)
                        if (weathertime.date(), weathertime.hour) == ( date, hour):

                            allSubwaysDataFrame["Temperatur (C)"].append(self.__temperature[i])
                            allSubwaysDataFrame["Middelvind (m/s)"].append(self.__wind[i])
                            allSubwaysDataFrame["Nedbør (mm/time)"].append(self.__rain[i])

                            lastcheckedWeather = i
                            break

                else:

                    allSubwaysDataFrame["Temperatur (C)"].append(arrivalPrHour[date][hour].temperature)
                    allSubwaysDataFrame["Middelvind (m/s)"].append(arrivalPrHour[date][hour].wind)
                    allSubwaysDataFrame["Nedbør (mm/time)"].append(arrivalPrHour[date][hour].rain)



        # Create a pandas dataframe for each dictionary
        allSubwaysDataFrame = pd.DataFrame(allSubwaysDataFrame)



        filename = f"PrTime_{self.filename}_{fromDate}_til_{toDate}_" \
                       f"marginFra_{self.__marginFrom}min_marginTil_{self.__marginTo}min.xlsx"


        # Create an Excel writer object to save the file
        writer = pd.ExcelWriter(f'C:/Users/mgnso/OneDrive/Skrivebord/Excelark/{filename}',
                                engine='xlsxwriter')

        # Write each dataframe to a separate sheet in the file
        allSubwaysDataFrame.to_excel(writer, index=False)


        # Save the excel file
        writer.save()

    def makeExcelSheetDay(  self, fromDate, toDate ):

        # Create datetime objects of the toDate and fromDate and calculate how many days
        # there are between them, including the fromDate and toDate.
        fromTime        =   datetime(  2022, int(  fromDate[ 3: ]  ), int(  fromDate[ :2 ]  )  )
        toTime          =   datetime(  2022, int(  toDate  [ 3: ]  ), int(  toDate  [ :2 ]  )  )
        days            =   (  toTime - fromTime  ).days + 1

        # Make list of all days in time period
        currentDate     =   fromTime
        allDays         =   []

        while currentDate <= toTime:

            allDays.append(  currentDate.date()  )
            currentDate     +=  timedelta(  days = 1  )


        # Create dictionaries that collects all data pr. specific each hour. Will be used to find the correlation
        # coefficient between amount of passengers and eScooter rides.
        passengersPrHour        =   {  date   :   0      for date in allDays  }
        eScootersPrHour         =   {  date : 0 for date in allDays  }
        nedborPrDag =   {  date : 0 for date in allDays  }
        tempPrDag =   {  date : [] for date in allDays  }
        vindPrDag =   {  date : [] for date in allDays  }
        arrivalPrHour           =   {  date  : None for date in allDays  }

        # Fetch the list of arrivals and departures in this time period
        arrivals    = self.iterateThroughArrivals("Arrivals", fromDate, toDate)
        departures  = self.iterateThroughArrivals("Departures", fromDate, toDate)

        # Make a list with all arrivals and all departures
        allSubways = []
        allSubways.extend(arrivals)
        allSubways.extend(departures)

        # Sort the list by the scheduledTime property
        allSubways  =   sorted(  allSubways, key = lambda x: x.scheduledTime  )

        datesAllready = []
        # Iterate through the arrivals
        for arrival in allSubways:

            # If arrival was after 23:59 on Dec. 31., break the foor loop
            if arrival.actualTime.year == 2023:
                break

            # Add the passenger and eScooter count to a variable designated to the specific hour
            eScootersPrHour[arrival.actualTime.date()] += arrival.eScooters
            passengersPrHour[arrival.actualTime.date()] += arrival.passengers
            arrivalPrHour[arrival.actualTime.date()] = arrival
            vindPrDag[arrival.actualTime.date()].append(arrival.wind)
            tempPrDag[arrival.actualTime.date()].append(arrival.temperature)

            if ( arrival.actualTime.date(), arrival.actualTime.hour ) not in datesAllready:
                nedborPrDag[arrival.actualTime.date()] += arrival.rain

            datesAllready.append((arrival.actualTime.date(), arrival.actualTime.hour))

        for date in vindPrDag:

            try:
                vindPrDag[date] = round( sum(vindPrDag[date])/len(vindPrDag[date]), 2 )
            except:
                vindPrDag[date] = 0

            try:
                tempPrDag[date] = round( sum(tempPrDag[date])/len(tempPrDag[date]), 2)
            except:
                tempPrDag[date] = 0


        allSubwaysDataFrame = \
            {
                "Dato": [],
                "Passasjerer av/på": [],
                "El-sparkesykler til/fra": [],
                "Snittemperatur (C)": [],
                "Gjennomsnittsvind (m/s)": [],
                "Nedbør (mm/dag)": []
            }


        lastcheckedWeather = 0
        for date in passengersPrHour:

            allSubwaysDataFrame["Dato"].append(date)
            allSubwaysDataFrame["Passasjerer av/på"].append(passengersPrHour[date])
            allSubwaysDataFrame["El-sparkesykler til/fra"].append(eScootersPrHour[date])
            allSubwaysDataFrame["Nedbør (mm/dag)"].append(nedborPrDag[date])
            allSubwaysDataFrame["Gjennomsnittsvind (m/s)"].append(vindPrDag[date])
            allSubwaysDataFrame["Snittemperatur (C)"].append(tempPrDag[date])


        # Create a pandas dataframe for each dictionary
        allSubwaysDataFrame = pd.DataFrame(allSubwaysDataFrame)



        filename = f"PrDag_{self.filename}_{fromDate}_til_{toDate}_" \
                       f"marginFra_{self.__marginFrom}min_marginTil_{self.__marginTo}min.xlsx"


        # Create an Excel writer object to save the file
        writer = pd.ExcelWriter(f'C:/Users/mgnso/OneDrive/Skrivebord/Excelark/{filename}',
                                engine='xlsxwriter')

        # Write each dataframe to a separate sheet in the file
        allSubwaysDataFrame.to_excel(writer, index=False)


        # Save the excel file
        writer.save()
















