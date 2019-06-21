from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from processcontrol import ProcessControl


class UpdateTerminalObject(QtCore.QObject):
    
    updated = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()
    
    def __init__(self, procControl):
        super().__init__()
        self.pc = procControl

    def runUpdate(self):
        while self.pc.is_running():
            out = self.pc.get_output()
            self.updated.emit(out)
            QtCore.QThread.sleep(0.05)
        self.finished.emit()


class ProcessControlFrame(QtWidgets.QFrame):

    def __init__(self, parent, proc):
        super().__init__()

        self.process = proc

        # parent should probably be a QtWidgets.QWidget() e.g. "scrollAreaWidgetContents"
        QtWidgets.QFrame(parent)
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.verticalFrameLayout = QtWidgets.QVBoxLayout(self)
        
        # Process row
        self.ProcessLayout = QtWidgets.QHBoxLayout()

        self.processNameLabel = QtWidgets.QLabel(self)
        self.processNameLabel.setText(self.process.name)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.processNameLabel.sizePolicy().hasHeightForWidth())
        self.processNameLabel.setSizePolicy(sizePolicy)
        self.ProcessLayout.addWidget(self.processNameLabel)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.ProcessLayout.addItem(spacerItem)

        self.runButton = QtWidgets.QPushButton(self)
        self.runButton.setText("Run")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.runButton.sizePolicy().hasHeightForWidth())
        self.runButton.setSizePolicy(sizePolicy)
        self.runButton.setMinimumSize(QtCore.QSize(30, 30))
        self.runButton.setMaximumSize(QtCore.QSize(40, 40))
        self.ProcessLayout.addWidget(self.runButton)

        self.showOutputBox = QtWidgets.QCheckBox(self)
        self.showOutputBox.setText("Output")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.showOutputBox.sizePolicy().hasHeightForWidth())
        self.showOutputBox.setSizePolicy(sizePolicy)
        self.showOutputBox.setMinimumSize(QtCore.QSize(30, 30))
        self.showOutputBox.setMaximumSize(QtCore.QSize(80, 35))
        self.ProcessLayout.addWidget(self.showOutputBox)

        self.verticalFrameLayout.addLayout(self.ProcessLayout)

        # Terminal view
        self.terminalTextEdit = QtWidgets.QPlainTextEdit(self)
        self.terminalTextEdit.setPlaceholderText("$ " + self.process.command)
        self.terminalTextEdit.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.terminalTextEdit.sizePolicy().hasHeightForWidth())
        self.terminalTextEdit.setSizePolicy(sizePolicy)
        self.terminalTextEdit.setMinimumSize(QtCore.QSize(0, 50))
        self.terminalTextEdit.setMaximumSize(QtCore.QSize(16777215, 100))
        self.terminalTextEdit.setStyleSheet("background: rgb(46, 52, 54);\ncolor: rgb(255,255,255);")
        self.terminalTextEdit.setReadOnly(True)
        self.terminalTextEdit.setBackgroundVisible(False)
        self.terminalTextEdit.setObjectName("terminalTextEdit")
        self.verticalFrameLayout.addWidget(self.terminalTextEdit)
        self.terminalTextEdit.setVisible(False)

        # Connect signals to functions
        self.connectSignals()

    def connectSignals(self):
        self.runButton.clicked.connect(self.run)
        self.showOutputBox.stateChanged.connect(self.toggleTerminalVisibility)

    def run(self):
        self.terminalTextEdit.setPlainText("$ " + self.process.command + "\n")
        self.process.start()
        #self.thread = UpdateTerminalThread(self.process)
        #self.thread.updated.connect(self.updateTerminal)
        #self.thread.finished.connect(self.processFinished)
        #self.thread.start()

        self.objThread = QtCore.QThread()
        self.obj = UpdateTerminalObject(self.process)
        self.obj.moveToThread(self.objThread)
        self.obj.finished.connect(self.processFinished)
        self.obj.updated.connect(self.updateTerminal)
        self.objThread.started.connect(self.obj.runUpdate)
        self.objThread.start()

    def updateTerminal(self, newtext ):
        if newtext == "" or newtext == "\n":
            return
        existing = self.terminalTextEdit.toPlainText()
        self.terminalTextEdit.setPlainText(existing + newtext)
        self.terminalTextEdit.verticalScrollBar().setValue(self.terminalTextEdit.verticalScrollBar().maximum())

    def processFinished(self):
        print("Finished")
        self.objThread.quit()
        self.objThread.wait()
        del self.objThread
        del self.obj

    def toggleTerminalVisibility(self):
        if self.terminalTextEdit.isVisible():
            self.terminalTextEdit.setVisible(False)
        else:
            self.terminalTextEdit.setVisible(True)
        


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.resize(698, 700)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 678, 647))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.pcFrames = []

        p1 = ProcessControl("Counting", "./testscript.sh")
        pcf = ProcessControlFrame(self.scrollAreaWidgetContents, p1)
        self.pcFrames.append(pcf)
        self.verticalLayout_2.addWidget(pcf)

        p2 = ProcessControl("Counting 2", "./testscript.sh")
        pcf2 = ProcessControlFrame(self.scrollAreaWidgetContents, p2)
        self.pcFrames.append(pcf2)
        self.verticalLayout_2.addWidget(pcf2)


        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_3.addWidget(self.scrollArea)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setText("Add process")
        self.pushButton.setEnabled(False)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_4.addWidget(self.pushButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.setCentralWidget(self.centralwidget)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    w = MainWindow()
    w.show()
    
    sys.exit(app.exec_())