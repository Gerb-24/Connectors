import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QFileDialog
from PyQt6 import uic, QtCore
from PyQt6.QtGui import QIcon
from sidewalls import compile
import json
from copy import deepcopy


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('gui.ui', self)
        self.setWindowTitle("Connectors")
        self.setWindowIcon(QIcon('ui_images/appicon.ico'))
        self.setFixedSize(self.size())

        self.fileName = ''
        self.dirName = ''
        self.search_tex = ''
        self.wall_tex = ''
        self.floor_tex = ''
        self.ceiling_tex = ''
        self.corner_tex = ''

        self.vmf_btn.clicked.connect( self.load_vmf )

        self.search_le.textChanged.connect(lambda: self.set_search_tex(self.search_le.text()))
        self.wall_le.textChanged.connect(lambda: self.set_wall_tex(self.wall_le.text()))
        self.floor_le.textChanged.connect(lambda: self.set_floor_tex(self.floor_le.text()))
        self.ceiling_le.textChanged.connect(lambda: self.set_ceiling_tex(self.ceiling_le.text()))
        self.corner_le.textChanged.connect(lambda: self.set_corner_tex(self.corner_le.text()))

        self.compile_btn.clicked.connect( self._compile )
        self.save_settings_btn.clicked.connect( self.save )

        self.load_settings()

    def set_search_tex( self, s ):
        self.search_tex = s

    def set_wall_tex( self, s ):
        self.wall_tex = s

    def set_floor_tex( self, s ):
        self.floor_tex = s

    def set_ceiling_tex( self, s ):
        self.ceiling_tex = s

    def set_corner_tex( self, s ):
        self.corner_tex = s


    def _compile( self ):
        compile( self.fileName, self.search_tex, self.wall_tex, self.floor_tex, self.ceiling_tex, self.corner_tex )

    def save( self ):
        save_data = {
            "fileName":  self.fileName,
            "dirName":  self.dirName,
            "search_tex": self.search_tex,
            "wall_tex": self.wall_tex,
            "floor_tex": self.floor_tex,
            "ceiling_tex": self.ceiling_tex,
            "corner_tex": self.corner_tex,
             }
        json_data = json.dumps( save_data, indent=2 )
        with open("settings.json", "w") as f:
            f.write(json_data)

    def load_vmf( self ):
        filepath, _ = QFileDialog.getOpenFileName(self, "Load VMF", self.dirName, "VMF(*.vmf)")
        self.fileName = filepath
        self.dirName = os.path.dirname(filepath)
        self.vmf_le.setText(os.path.basename(filepath))

    def load_settings(self):
        with open("settings.json", "r") as f:
            load_data = json.loads(f.read())
        self.fileName = load_data["fileName"]
        self.vmf_le.setText(os.path.basename(self.fileName))
        self.dirName = load_data["dirName"]

        self.search_tex = load_data["search_tex"]
        self.search_le.setText(self.search_tex)

        self.wall_tex = load_data["wall_tex"]
        self.wall_le.setText(self.wall_tex)

        self.floor_tex = load_data["floor_tex"]
        self.floor_le.setText(self.floor_tex)

        self.ceiling_tex = load_data["ceiling_tex"]
        self.ceiling_le.setText(self.ceiling_tex)

        self.corner_tex = load_data["corner_tex"]
        self.corner_le.setText(self.corner_tex)



if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setStyleSheet(open('cssfiles/stylesheet.css').read())

    window = MyApp()
    window.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print(' Closing Window ... ')
