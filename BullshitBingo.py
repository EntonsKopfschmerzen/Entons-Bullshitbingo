import sys
import random
import json
import os
from BingoCard import BingoCardWindow 
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QGridLayout, QComboBox, QLineEdit, QMessageBox, QFileDialog, QSlider, QToolBar, QCheckBox, QColorDialog, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QPixmap, QPainter, QKeySequence, QColor, QFont, QShortcut, QAction

class BingoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bullshit Bingo")
        #self.setGeometry(100, 100, 400, 300)
        self.resize(600, 500)
        self.setFixedSize(self.size())

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
   
        self.central_widget.setLayout(self.layout)

        self.size_label = QLabel("Feldgröße:")
        self.size_combo = QComboBox()
        self.size_combo.addItems(["3x3", "4x4", "5x5"])
        self.word_count_label = QLabel("Wörter eingegeben: 0")

        self.fontsize_inputLabel = QLabel("Schriftgröße: ")
        self.fontsize_input = QSpinBox()
        self.fontsize_input.setRange(8, 48)
        self.fontsize_input.setValue(16)
        # Beispiel: Abstand zwischen Label und QSpinBox verringern
        fontsize_layout = QVBoxLayout()
        fontsize_layout.setSpacing(2)
        fontsize_layout.addWidget(self.fontsize_inputLabel)
        fontsize_layout.addWidget(self.fontsize_input)


        self.word_input = QTextEdit()
        self.word_input.setPlaceholderText("Gib die Wörter mit Komma getrennt ein: Apfel, Keks, Baum...")
        self.word_input.textChanged.connect(self.update_word_count)
        self.word_input.setFixedHeight(60)

        self.create_button = QPushButton("Karte erstellen")
        self.create_button.clicked.connect(self.create_card)

        self.import_button = QPushButton("Karte importieren")
        self.import_button.clicked.connect(self.import_card)

        self.opacitySlider = QSlider()
        self.opacitySlider.setOrientation(Qt.Orientation.Horizontal)
        self.opacitySlider.setMinimum(0)
        self.opacitySlider.setMaximum(80) 
        self.opacitySlider.setValue(0)
        self.opacitySlider.valueChanged.connect(self.update_opacityLabel)

        
        self.opacityCheckbox = QCheckBox("Transparenz deaktivieren (empfohlen für Streamer*innen, Funktion on-stream evtl. buggy!)")
        self.opacityLabel = QLabel("Transparenz: 0%")

 
        self.bingo_pushed_color = "#000000"
        self.bingo_notPushed_color = "#f0f0f0"

        self.color_button_notMarked = QPushButton("Farbe auswählen")
        self.color_button_notMarked.clicked.connect(lambda: self.pick_color("unchecked"))
        self.color_button_notMarked_label = QLabel("Farbe für nicht markierte Felder wählen")
        

        self.color_button_marked = QPushButton("Farbe auswählen")
        self.color_button_marked.clicked.connect(lambda: self.pick_color("checked"))
        self.color_button_marked_label = QLabel("Farbe für markierte Felder wählen")


        self.layout.addWidget(self.size_label)
        self.layout.addWidget(self.size_combo)
        self.layout.addWidget(self.word_count_label)
        self.layout.addWidget(self.word_input)
        self.layout.addWidget(self.create_button)
        self.layout.addWidget(self.import_button)
        self.layout.addLayout(fontsize_layout) 
        self.layout.addWidget(self.opacityCheckbox)   
        self.layout.addWidget(self.opacityLabel)
        self.layout.addWidget(self.opacitySlider)
        self.layout.addWidget(self.color_button_notMarked_label)
        self.layout.addWidget(self.color_button_notMarked)
        self.layout.addWidget(self.color_button_marked_label) 
        self.layout.addWidget(self.color_button_marked)


    def pick_color(self, mode):
        color = QColorDialog.getColor()
        if color.isValid():
            if mode == "unchecked":
                self.bingo_notPushed_color = color.name()
                print("unchecked: " , self.bingo_notPushed_color)
            elif mode == "checked":
                self.bingo_pushed_color = color.name()
                print("checked: " , self.bingo_notPushed_color)

    def update_opacityLabel(self):
        size = self.opacitySlider.value()
        self.opacityLabel.setText(f"Transparenz: {size}%")

    def update_word_count(self):
        text = self.word_input.toPlainText()
        words = text.split(', ')
        num_words = len(words)
        self.word_count_label.setText(f"Wörter eingegeben: {num_words}")

    def create_card(self):
        size_str = self.size_combo.currentText()
        size = int(size_str[0])
        terms = self.word_input.toPlainText().split(', ')
        self.fontSize = self.fontsize_input.value().__str__()
        print("Schriftgröße: ", self.fontSize)

        if len(terms) < size * size:
            QMessageBox.warning(self, "Fehler", f"Du brauchst mindestens {size * size} Wörter!")
            return
        
        if self.opacityCheckbox.isChecked():
            self.opacity_level = 1.0
            print("opacity level 1")
        else:
            self.opacity_level = (100-self.opacitySlider.value())/100
            print("opacity level " , self.opacity_level)

        self.card_window = BingoCardWindow(size, terms, self.opacity_level, self.bingo_notPushed_color, self.bingo_pushed_color, self.fontSize, shuffle=True)
        ##self.card_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.card_window.show()

        layout = QVBoxLayout()
        self.card_window.setLayout(layout)

    def colorPickActionNotMarked(self):
    
        self.blub = self.notMarkedFieldcolor

    def colorPickActionMarked(self):
        self.markedFieldcolor = QColorDialog.getColor()

    def import_card(self):
        self.fontSize = self.fontsize_input.value()
        print("Schriftgröße: ", self.fontSize)
        filename, _ = QFileDialog.getOpenFileName(self, "Karte importieren", "", "JSON Files (*.json)")
        if filename:
            with open(filename, 'r') as f:
                data = json.load(f)
                size = data['size']
                terms = data['terms']
                self.opacity_level = (100-self.opacitySlider.value())/100
                self.card_window = BingoCardWindow(size, terms, self.opacity_level, self.bingo_notPushed_color, self.bingo_pushed_color, self.fontSize, shuffle=False)
                self.card_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)    
                self.card_window.show()

                for i in range(size):
                    for j in range(size):
                        if data['marked'][i][j]:
                            self.card_window.buttons[i][j].setChecked(True)

                save_button = QPushButton("Karte speichern")
                save_button.clicked.connect(lambda: self.export_card(marked=False))
                save_marked_button = QPushButton("Karte mit Markierungen speichern")
                save_marked_button.clicked.connect(lambda: self.export_card(marked=True))

                layout = QVBoxLayout()
                layout.addWidget(save_button)
                layout.addWidget(save_marked_button)
                self.card_window.setLayout(layout)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BingoApp()
    window.show()
    sys.exit(app.exec())

