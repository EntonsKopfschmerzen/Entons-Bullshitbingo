import sys
import random
import json
import os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QGridLayout, QComboBox, QLineEdit, QMessageBox, QFileDialog, QSlider, QToolBar, QCheckBox, QColorDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QPixmap, QPainter, QKeySequence, QColor, QFont, QShortcut, QAction

class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel(
            "ALT-Taste zum Enternen der Leiste.\n\n"
            "Rechtsklick gedrückt halten zum Verschieben der Bingokarte.\n\n"
            "STRG+Q: Screenshot erstellen.\n\n"
            "STRG+E: Exportieren (ohne markierte Felder).\n\n"
            "STRG+S: Speichern (mit markierten Feldern)"
        )
        layout.addWidget(self.label)
        self.setLayout(layout)
        

