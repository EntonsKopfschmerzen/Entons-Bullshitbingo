import sys
import random
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QDialog, 
    QPushButton, QLabel, QGridLayout, QComboBox, QLineEdit, QMessageBox, QFileDialog, QSlider, QToolBar, QCheckBox, QColorDialog, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QPixmap, QPainter, QKeySequence, QColor, QFont, QShortcut, QAction

class ColorsSelectDialog(QDialog):
    def __init__(self, parent=None, farben = None):
        super().__init__(parent)
        self.setWindowTitle("Farben auswählen")
        self.resize(300, 200)

        self.layout = QVBoxLayout()

        if farben is not None:
            self.colors = farben[:]
        else:
            self.colors = [
                QColor("#0000FF"), QColor("#36648B"), QColor("#6959CD"), QColor("#00868B"),
                QColor("#000080"), QColor("#7FFFD4"), QColor("#FF4040"), QColor("#CD9B9B"),
                QColor("#8B4513"), QColor("#228B22"), QColor("#ADFF2F"), QColor("#C1FFC1")
            ]
        self.buttons = []
        for i in range(12):
            btn = QPushButton(f"Farbe {i+1} wählen")
            print(f"Button-Farbe {i}: {self.colors[i].name()}")
            btn.setStyleSheet(f"background-color: {self.colors[i].name()}")
            btn.clicked.connect(lambda _, idx=i: self.choose_color(idx))
            self.layout.addWidget(btn)
            self.buttons.append(btn)

        # Fertig-Button
        fertig_btn = QPushButton("Fertig")
        fertig_btn.clicked.connect(self.accept)
        self.layout.addWidget(fertig_btn)

        self.setLayout(self.layout)

    def choose_color(self, idx):
        color = QColorDialog.getColor(self.colors[idx], self)
        if color.isValid():
            self.colors[idx] = color
            self.buttons[idx].setStyleSheet(f"background-color: {color.name()}")