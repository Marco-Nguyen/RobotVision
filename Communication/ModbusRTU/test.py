# # importing libraries
# import sys

# from PyQt5 import QtCore
# from PyQt5 import QtGui
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *


# class Window(QMainWindow):

#     def __init__(self):
#         super().__init__()

#         # setting title
#         self.setWindowTitle("Python ")

#         # setting geometry
#         self.setGeometry(100, 100, 400, 600)

#         # calling method
#         self.UiComponents()

#         # showing all the widgets
#         self.show()

#     # method for widgets
#     def UiComponents(self):

#         # variables
#         # count variable
#         self.count = 0

#         # start flag
#         self.start = False

#         # creating push button to get time in seconds
#         button = QPushButton("Set time(s)", self)

#         # setting geometry to the push button
#         button.setGeometry(125, 100, 150, 50)

#         # adding action to the button
#         button.clicked.connect(self.get_seconds)

#         # creating label to show the seconds
#         self.label = QLabel("//TIMER//", self)

#         # setting geometry of label
#         self.label.setGeometry(100, 200, 200, 50)

#         # setting border to the label
#         self.label.setStyleSheet("border : 3px solid black")

#         # setting font to the label
#         self.label.setFont(QFont('Times', 15))

#         # setting alignment ot the label
#         self.label.setAlignment(Qt.AlignCenter)

#         # creating start button
#         start_button = QPushButton("Start", self)

#         # setting geometry to the button
#         start_button.setGeometry(125, 350, 150, 40)

#         # adding action to the button
#         start_button.clicked.connect(self.start_action)

#         # creating pause button
#         pause_button = QPushButton("Pause", self)

#         # setting geometry to the button
#         pause_button.setGeometry(125, 400, 150, 40)

#         # adding action to the button
#         pause_button.clicked.connect(self.pause_action)

#         # creating reset button
#         reset_button = QPushButton("Reset", self)

#         # setting geometry to the button
#         reset_button.setGeometry(125, 450, 150, 40)

#         # adding action to the button
#         reset_button.clicked.connect(self.reset_action)

#         # creating a timer object
#         timer = QTimer(self)

#         # adding action to timer
#         timer.timeout.connect(self.showTime)

#         # update the timer every tenth second
#         timer.start(100)

#     # method called by timer
#     def showTime(self):

#         # checking if flag is true
#         if self.start:
#             # incrementing the counter
#             self.count -= 1

#             # timer is completed
#             if self.count == 0:

#                 # making flag false
#                 self.start = False

#                 # setting text to the label
#                 self.label.setText("Completed !!!! ")

#         if self.start:
#             # getting text from count
#             text = str(self.count / 10) + " s"

#             # showing text
#             self.label.setText(text)

#     # method called by the push button

#     def get_seconds(self):

#         # making flag false
#         self.start = False

#         # getting seconds and flag
#         second, done = QInputDialog.getInt(self, 'Seconds', 'Enter Seconds:')

#         # if flag is true
#         if done:
#             # changing the value of count
#             self.count = second * 10

#             # setting text to the label
#             self.label.setText(str(second))

#     def start_action(self):
#         # making flag true
#         self.start = True

#         # count = 0
#         if self.count == 0:
#             self.start = False

#     def pause_action(self):

#         # making flag false
#         self.start = False

#     def reset_action(self):

#         # making flag false
#         self.start = False

#         # setting count value to 0
#         self.count = 0

#         # setting label text
#         self.label.setText("//TIMER//")


# # create pyqt5 app
# App = QApplication(sys.argv)

# # create the instance of our Window
# window = Window()

# # start the app
# sys.exit(App.exec())

# # import logging
# # import random
# # import sys
# # import time

# # from PyQt5.QtCore import QRunnable, Qt, QThreadPool
# # from PyQt5.QtWidgets import (
# #     QApplication,
# #     QLabel,
# #     QMainWindow,
# #     QPushButton,
# #     QVBoxLayout,
# #     QWidget,
# # )

# # logging.basicConfig(format="%(message)s", level=logging.INFO)

# # # 1. Subclass QRunnable


# # class Runnable(QRunnable):
# #     def __init__(self, n):
# #         super().__init__()
# #         self.n = n

# #     def run(self):
# #         # Your long-running task goes here ...
# #         for i in range(5):
# #             logging.info(f"Working in thread {self.n}, step {i + 1}/5")
# #             time.sleep(random.randint(700, 2500) / 1000)


# # class Window(QMainWindow):
# #     def __init__(self, parent=None):
# #         super().__init__(parent)
# #         self.setupUi()

# #     def setupUi(self):
# #         self.setWindowTitle("QThreadPool + QRunnable")
# #         self.resize(250, 150)
# #         self.centralWidget = QWidget()
# #         self.setCentralWidget(self.centralWidget)
# #         # Create and connect widgets
# #         self.label = QLabel("Hello, World!")
# #         self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
# #         countBtn = QPushButton("Click me!")
# #         countBtn.clicked.connect(self.runTasks)
# #         # Set the layout
# #         layout = QVBoxLayout()
# #         layout.addWidget(self.label)
# #         layout.addWidget(countBtn)
# #         self.centralWidget.setLayout(layout)

# #     def runTasks(self):
# #         threadCount = QThreadPool.globalInstance().maxThreadCount()
# #         self.label.setText(f"Running {threadCount} Threads")
# #         pool = QThreadPool.globalInstance()
# #         for i in range(threadCount):
# #             # 2. Instantiate the subclass of QRunnable
# #             runnable = Runnable(i)
# #             # 3. Call start()
# #             pool.start(runnable)


# # app = QApplication(sys.argv)
# # window = Window()
# # window.show()
# # sys.exit(app.exec())

# # import sys
# # from PyQt5.QtWidgets import (QWidget,
# #                              QPushButton, QApplication, QGridLayout)
# # from PyQt5.QtCore import QThread, QObject, pyqtSignal


# # class Worker(QObject):

# #     finished = pyqtSignal()  # give worker class a finished signal

# #     def __init__(self, parent=None):
# #         QObject.__init__(self, parent=parent)
# #         self.continue_run = True  # provide a bool run condition for the class

# #     def do_work(self):
# #         i = 1
# #         while self.continue_run:  # give the loop a stoppable condition
# #             print(i)
# #             QThread.sleep(1)
# #             i = i + 1
# #         self.finished.emit()  # emit the finished signal when the loop is done

# #     def stop(self):
# #         self.continue_run = False  # set the run condition to false on stop


# # class Gui(QWidget):

# #     stop_signal = pyqtSignal()  # make a stop signal to communicate with the worker in another thread

# #     def __init__(self):
# #         super().__init__()
# #         self.initUI()

# #     def initUI(self):

# #         # Buttons:
# #         self.btn_start = QPushButton('Start')
# #         self.btn_start.resize(self.btn_start.sizeHint())
# #         self.btn_start.move(50, 50)
# #         self.btn_stop = QPushButton('Stop')
# #         self.btn_stop.resize(self.btn_stop.sizeHint())
# #         self.btn_stop.move(150, 50)

# #         # GUI title, size, etc...
# #         self.setGeometry(300, 300, 300, 220)
# #         self.setWindowTitle('ThreadTest')
# #         self.layout = QGridLayout()
# #         self.layout.addWidget(self.btn_start, 0, 0)
# #         self.layout.addWidget(self.btn_stop, 0, 50)
# #         self.setLayout(self.layout)

# #         # Thread:
# #         self.thread = QThread()
# #         self.worker = Worker()
# #         self.stop_signal.connect(self.worker.stop)  # connect stop signal to worker stop method
# #         self.worker.moveToThread(self.thread)

# #         self.worker.finished.connect(self.thread.quit)  # connect the workers finished signal to stop thread
# #         self.worker.finished.connect(self.worker.deleteLater)  # connect the workers finished signal to clean up worker
# #         self.thread.finished.connect(self.thread.deleteLater)  # connect threads finished signal to clean up thread

# #         self.thread.started.connect(self.worker.do_work)
# #         self.thread.finished.connect(self.worker.stop)

# #         # Start Button action:
# #         self.btn_start.clicked.connect(self.thread.start)

# #         # Stop Button action:
# #         self.btn_stop.clicked.connect(self.stop_thread)

# #         self.show()

# #     # When stop_btn is clicked this runs. Terminates the worker and the thread.
# #     def stop_thread(self):
# #         self.stop_signal.emit()  # emit the finished signal on stop


# # if __name__ == '__main__':
# #     app = QApplication(sys.argv)
# #     gui = Gui()
# #     sys.exit(app.exec_())
