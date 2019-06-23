from PyQt5 import QtCore, QtGui, QtWidgets
from LedIndicatorWidget import LedIndicator
import sys
from processcontrol import ProcessControl
import time
import config as cfg
import psutil


class WatchProcessObject(QtCore.QObject):
    
    terminalUpdate = QtCore.pyqtSignal(str)
    processStopped = QtCore.pyqtSignal()
    sendStats = QtCore.pyqtSignal(dict)
    
    def __init__(self, proCtrl):
        super().__init__()
        self.pc = proCtrl

    def runWatcher(self):
        while True:
            if self.pc.is_running():
                out = self.pc.get_output()
                # Update terminal with output of process
                self.terminalUpdate.emit(out)
                # Send statistics to GUI
                self.sendStats.emit(self.getStats())
                # Wait to not clock CPU
                time.sleep(0.05)
                # Process has stopped
                if not self.pc.is_running():
                    self.processStopped.emit()
            else:
                time.sleep(0.05)

    def getStats(self):
        if not self.pc.is_running():
            return {"cpu": 0, "mem": 0}
        p = psutil.Process(self.pc.process.pid)
        p.cpu_percent()
        time.sleep(0.05)
        try:
            cpu = p.cpu_percent() / psutil.cpu_count()
            mem = p.memory_info()[0] / float(2 ** 20)
        except:
            cpu = 0
            mem = 0
        for child in p.children(recursive=True):
            mem += child.memory_info()[0] / float(2 ** 20)
            child.cpu_percent()
            time.sleep(0.05)
            try:
                cpu += child.cpu_percent() / psutil.cpu_count()
            except:
                pass
        return {"cpu": cpu, "mem": mem}


class ProcessControlFrame(QtWidgets.QFrame):

    def __init__(self, parent, proCtrl):
        super().__init__()

        self.proCtrl = proCtrl

        # parent should probably be a QtWidgets.QWidget() e.g. "scrollAreaWidgetContents"
        QtWidgets.QFrame(parent)
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.verticalFrameLayout = QtWidgets.QVBoxLayout(self)
        
        # Process row
        self.ProcessLayout = QtWidgets.QHBoxLayout()

        # Name
        self.processNameLabel = QtWidgets.QLabel(self)
        self.processNameLabel.setText(self.proCtrl.name)
        self.processNameLabel.setStyleSheet("font-weight: bold;")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.processNameLabel.sizePolicy().hasHeightForWidth())
        self.processNameLabel.setSizePolicy(sizePolicy)
        self.ProcessLayout.addWidget(self.processNameLabel)

        # Spacer
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.ProcessLayout.addItem(spacerItem)
        
        # Statistics
        self.statsNameLabel = QtWidgets.QLabel(self)
        self.statsNameLabel.setText("CPU: - , MEM: - ")
        self.ProcessLayout.addWidget(self.statsNameLabel)

        # LED
        self.led = LedIndicator(self)
        self.led.setDisabled(True)
        self.ProcessLayout.addWidget(self.led)

        # Run button
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

        # Stop button
        self.stopButton = QtWidgets.QPushButton(self)
        self.stopButton.setText("Stop")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stopButton.sizePolicy().hasHeightForWidth())
        self.stopButton.setSizePolicy(sizePolicy)
        self.stopButton.setMinimumSize(QtCore.QSize(30, 30))
        self.stopButton.setMaximumSize(QtCore.QSize(40, 40))
        self.ProcessLayout.addWidget(self.stopButton)

        # Checkbox output
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
        self.terminalTextEdit.setPlaceholderText("$ " + self.proCtrl.command)
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

        # Create Watcher Thread for surveying processControl
        self.watcherThread = QtCore.QThread()
        self.watcherThread.setObjectName("watcherThread")
        self.watchobj = WatchProcessObject(self.proCtrl)
        self.watchobj.moveToThread(self.watcherThread)
        self.watchobj.terminalUpdate.connect(self.updateTerminal)
        self.watchobj.processStopped.connect(self.processFinished)
        self.watchobj.sendStats.connect(self.updateStats)
        self.watcherThread.started.connect(self.watchobj.runWatcher)
        self.watcherThread.start()

        # Connect signals to functions
        self.connectSignals()

    def connectSignals(self):
        self.runButton.clicked.connect(self.run)
        self.stopButton.clicked.connect(self.stop)
        self.showOutputBox.stateChanged.connect(self.toggleTerminalVisibility)

    def run(self):
        if self.proCtrl.is_running():
            return
        self.updateTerminal("$ " + self.proCtrl.command + "\n")
        self.led.setChecked(True)
        self.proCtrl.start()

    def stop(self):
        self.processFinished()
        self.updateTerminal(">>> Stopped by user\n\n")

    def updateTerminal(self, newtext ):
        if newtext == "" or newtext == "\n":
            return
        existing = self.terminalTextEdit.toPlainText()
        self.terminalTextEdit.setPlainText(existing + newtext)
        self.terminalTextEdit.verticalScrollBar().setValue(self.terminalTextEdit.verticalScrollBar().maximum())

    def updateStats(self, stats):
        self.statsNameLabel.setText("CPU: " + str(round(stats["cpu"],2)) + "% , MEM: " + str(round(stats["mem"],2)) + " MiB ")

    def processFinished(self):
        self.led.setChecked(False)
        self.statsNameLabel.setText("CPU: - , MEM: - ")
        self.proCtrl.kill()

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

        for p in cfg.processlist:
            pc = ProcessControl(p["name"], p["command"])
            pcf = ProcessControlFrame(self.scrollAreaWidgetContents, pc)
            self.verticalLayout_2.addWidget(pcf)
            if p["autostart"]:
                pcf.run()

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
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.addProcess)
        self.horizontalLayout_4.addWidget(self.pushButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.setCentralWidget(self.centralwidget)

    def addProcess(self):
        self.newPcDialog = NewProcessControlDialog()
        if self.newPcDialog.exec_():
            name, cmd, autostart = self.newPcDialog.getNewProcessControl()
            # Add values to config
            with open("config.py","r") as f:
                cfg = f.read()
            index = cfg.find("]")
            newline = ',\n\t{"name": "' + str(name) + '", "command": "' + str(cmd) + '", "autostart": ' + str(autostart) + '}\n]'
            newcfg = cfg[:index-1] + newline
            with open("config.py","w") as f:
                f.write(newcfg)
            # Add pcf for current session
            newpc = ProcessControl(name, cmd)
            newpcf = ProcessControlFrame(self.scrollAreaWidgetContents, newpc)
            self.verticalLayout_2.insertWidget(self.verticalLayout_2.count()-1,newpcf)


class NewProcessControlDialog(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()
        self.setObjectName("Dialog")
        self.resize(400, 224)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.lineEdit_2 = QtWidgets.QLineEdit(self)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.verticalLayout.addWidget(self.lineEdit_2)
        self.checkBox = QtWidgets.QCheckBox(self)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout.addWidget(self.checkBox)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Add Process Control"))
        self.label.setText(_translate("Dialog", "Name / Description:"))
        self.label_2.setText(_translate("Dialog", "Command:"))
        self.checkBox.setText(_translate("Dialog", "Autostart (on start of DiscoveryPanel)"))
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()


    def getNewProcessControl(self):
        name = self.lineEdit.text()
        cmd = self.lineEdit_2.text()
        autostart = self.checkBox.isChecked()
        return (name, cmd, autostart)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    w = MainWindow()
    w.show()
    
    sys.exit(app.exec_())