from    programGUI  import  *
from    dataAnalyse import *
import  sys

# Fetch the gui and run the program
if __name__ == "__main__":

    # Skriv inn marginene du bruker her
    tilMargin, fraMargin = 7, 5

    # Skriv inn excel-fila du bruker her
    filnavn = "Barneskole.xlsx"

    # Initialize a PyQt5 application
    application = qw.QApplication(  sys.argv  )

    # Initialize the program
    Main = Main(  fraMargin, tilMargin, filnavn  )

    # Show the program
    Main.show()

    # Exit the program when the window is closed
    sys.exit(  application.exec_()  )
