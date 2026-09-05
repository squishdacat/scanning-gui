from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QGridLayout, QDialog, QMessageBox, QVBoxLayout, QSizePolicy, QComboBox
from PyQt6.QtGui import QColor, QPalette, QScreen 
from PyQt6.QtCore import Qt
from PIL import Image
from io import BytesIO
import os
from  saneyaml import load
import functools
import pwd
import subprocess 
from time import sleep
import datetime
UTSUSHI_EXECUTABLE = os.environ.get("SCANNING_UTSUSHI_EXECUTABLE")



def change_user(uid, gid=None):
    if gid is None:
        gid = uid
    def preexec_fn():
        os.setgid(gid)
        os.setgroups([gid])
        os.setuid(uid)
    return preexec_fn


def scanFile(path):
    os.system(f'utsushi scan --image-format PNG --long-paper-mode > {path}.png')

class Color(QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scanning GUI")
        widget = self.createMainMenu()
        self.setCentralWidget(widget)
        self.show()
        
    def createMainMenu(self):
        masterLayout = QVBoxLayout()
        layout = QGridLayout()
        buttons = []
        for i,key in enumerate(YAML_CONFIG):
            setupButton = QPushButton(key) 
            setupButton.setObjectName(key)
            setupButton.clicked.connect(functools.partial(self.buttonPressed,key))
            setupButton.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
            buttons.append(setupButton) 
            row = 0
            column = 0
            
            if i % 2 == 0:
                column = 0
            else:
                column = 1
            
            if i >= 2:
                row = 1
                
            layout.addWidget(buttons[i],row,column)
        
        mainButtons = QWidget()
        mainButtons.setLayout(layout) 
        if "People" in fullYamlConfig:
            correspondentSelector = QComboBox()
            correspondentSelector.addItems(fullYamlConfig["People"])
            correspondentSelector.currentIndexChanged.connect(self.correspondentChanged_index)
            correspondentSelector.currentTextChanged.connect(self.correspondentChanged_text)
            masterLayout.addWidget(correspondentSelector)
        masterLayout.addWidget(mainButtons)
        widget = QWidget()
        widget.setLayout(masterLayout)
        return widget

    def correspondentChanged_index(self,i):
        currentCorrespondent["index"] = i
    
    def correspondentChanged_text(self,name):
        currentCorrespondent["name"] = name

    def buttonPressed(self,name):
        print(f"Button {name} pressed")
        print(name in YAML_CONFIG)
        buttons = []
        if name in YAML_CONFIG and YAML_CONFIG[name]["type"] == "menu":
            windowLayout = QVBoxLayout()
            newButtons = YAML_CONFIG[name]["options"]
            layout = QGridLayout()
            row = -1
            for i,key in enumerate(newButtons):
                setupButton = QPushButton(key) 
                setupButton.setObjectName(key)
                setupButton.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
                setupButton.clicked.connect(functools.partial(self.subMenuButtonPressed,key,name))
                
                column = 0
                
                if i % 2 == 0:
                    column = 0
                    row += 1
                else:
                    column = 1
                
                print(f"i: {i}, row:{row}")
                layout.addWidget(setupButton,row,column)
            mainMenu = self.createMainMenu()
            backButton = QPushButton("Back")
            backButton.clicked.connect(functools.partial(self.loadMainMenu,mainMenu))
            buttonsWidget = QWidget()
            buttonsWidget.setLayout(layout)
            correspondentSelector = QComboBox()
            if "People" in fullYamlConfig:
                correspondentSelector.addItems(fullYamlConfig["People"])
                correspondentSelector.setCurrentIndex(currentCorrespondent["index"])
                windowLayout.addWidget(correspondentSelector)
            
            windowLayout.addWidget(buttonsWidget)
            windowLayout.addWidget(backButton)
            fullWidget = QWidget()
            fullWidget.setLayout(windowLayout)
                    
            window.setCentralWidget(fullWidget)
            
    def loadMainMenu(self,widget):
        window.setCentralWidget(widget)
        
    def subMenuButtonPressed(self,name,menu):
        print(f"Name: {name} Menu: {menu}")
        subMenuEntries = YAML_CONFIG[menu]["options"]
        entryOptions = subMenuEntries[name]
        if entryOptions["type"] == "scan":
                scanArgs = ["scan","--no-interface","--image-format","PDF"]
                if "long-paper-mode" in entryOptions and entryOptions["long-paper-mode"] == True:
                    scanArgs.append("--long-paper-mode")
                    scanArgs.append("--scan-area")
                    scanArgs.append("Auto Detect")
                if "duplex" in entryOptions and entryOptions["duplex"] == True:
                    scanArgs.append("--duplex")
                outcome = subprocess.run(scanArgs,executable=UTSUSHI_EXECUTABLE,capture_output=True)
                if outcome.returncode == 0:
                    #stream = BytesIO(outcome.stdout)
                    #image = Image.open(stream)
                    #image.save(f"{homeDir}/{entryOptions["file-name"]}-{datetime.datetime.now()}.png")
                    pdf = open(f"{homeDir}/{entryOptions["file-name"]}-{datetime.datetime.now()}.pdf","bw") 
                    pdf.write(outcome.stdout)
                    pdf.close()
                    dlg = QMessageBox(self)
                    dlg.setIcon(QMessageBox.Icon.Information)
                    dlg.setWindowTitle("Success")
                    dlg.setText("Scanning successful")
                    dlg.exec()
                    mainMenu = self.createMainMenu()
                    dlg.accepted.connect(functools.partial(self.loadMainMenu,mainMenu))
                else:
                    if "Please load the document(s) into the Automatic Document Feeder" in str(outcome.stderr):
                        dlg = QMessageBox(self)
                        dlg.setIcon(QMessageBox.Icon.Warning)
                        dlg.setWindowTitle("Error")
                        dlg.setText("Error: No document in scanner")
                        dlg.exec() 
                    else:
                        logFilePath = f"{logDir}/{datetime.datetime.now()}-error.log"
                        dlg = QMessageBox(self)
                        dlg.setIcon(QMessageBox.Icon.Critical)
                        dlg.setWindowTitle("Unexpected error")
                        with open(logFilePath,"w") as log:
                            log.write(str(outcome.stderr))
                            dlg.setText(f"An unexpected error occured, see log at {logFilePath}")
                        dlg.exec()

def main():
    global app, fullYamlConfig, homeDir, logDir, YAML_CONFIG, window, currentCorrespondent, UTSUSHI_EXECUTABLE
    app = QApplication([])
    app.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTouchEvents, True)
    config_path = os.environ.get("SCANNING_GUI_CONFIG", "menu.yaml")
    fullYamlConfig = load(open(config_path).read())
    homeDir = fullYamlConfig["Home Directory"]
    logDir = fullYamlConfig["Log Directory"]
    YAML_CONFIG = fullYamlConfig["Menu"]
    window = MainWindow()
    if "People" in fullYamlConfig and isinstance(fullYamlConfig["People"], list):
        currentCorrespondent = {"index": 0, "name": fullYamlConfig["People"][0]}
    window.showFullScreen()
    app.exec()

if __name__ == "__main__":
    main()
