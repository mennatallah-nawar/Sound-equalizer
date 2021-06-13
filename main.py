from app import *
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_() #infinite loop

if __name__=='__main__':
    main()