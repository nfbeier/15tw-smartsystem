import sys
from PyQt5.QtWidgets import QApplication
from "iris-ui" import Window  # Ensure this matches the actual file name and class name

def main():
    # Step 3: Initialize the QApplication
    app = QApplication(sys.argv)
    
    # Step 4: Create an instance of the Window class
    main_window = Window()
    
    # Step 5: Show the main window
    main_window.show()
    
    # Step 6: Execute the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()