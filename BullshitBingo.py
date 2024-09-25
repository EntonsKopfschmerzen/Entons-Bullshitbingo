import sys
import random
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QGridLayout, QComboBox, QLineEdit, QMessageBox, QFileDialog, QSlider, QToolBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QPixmap, QPainter, QKeySequence, QColor, QFont, QShortcut, QAction


class BingoCardWindow(QMainWindow):
    def __init__(self, size, terms, opacity, parent=None, shuffle=True):
        super().__init__(parent)
        self.size = size
        self.terms = terms
        self.shuffle = shuffle
        self.layout = QGridLayout()
        self.totalBingo = 0

        self.toolbarMenu = QToolBar("Menu", self)
        self.toolbarMenu.addAction("Screenshot", lambda: self.safeCardAsScreenshot())
        self.toolbarMenu.addAction("Export", lambda: self.export_card(False))
        self.toolbarMenu.addAction("Speichern", lambda: self.export_card(True))
        self.toolbarMenu.addAction("?", lambda: self.openHelpWindow())
        self.addToolBar(self.toolbarMenu)
        self.toolbarMenu.setVisible(True)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)  # Entfernt die Titelleiste
        self.setWindowOpacity(opacity)
    
        print("Opacity: ", opacity)
        
        self.windowSize = self.sizeHint()
        self.toolbarSize = self.toolbarMenu.sizeHint()
        cardLength = (self.size * 100)
        cardHeight = (self.size * 100)
        cardHeight += self.toolbarSize.height()
        self.setFixedSize(cardLength, cardHeight)

        # Layout-Einstellungen
        self.layout.setSpacing(0)  # Setze den Abstand zwischen den Widgets auf 0
        self.layout.setContentsMargins(0, 0, 0, 0)  # Setze die Ränder des Layouts auf 0

        # Shuffle und Grid erstellen
        if self.shuffle == True:
            random.shuffle(self.terms)

        
        self.buttons_with_Bingo = []
        for i in range(self.size):
            bingoRow = []
            for j in range(self.size):
                bingoRow.append(False)
            self.buttons_with_Bingo.append(bingoRow)


        self.buttons = []
        for i in range(self.size):
            row = []
            for j in range(self.size):
                term = self.terms[i * self.size + j]
                print(term)
                feldText = self.textLaengeAnpassen(term) 
                button = QPushButton(feldText)
                button.setCheckable(True)
                button.setFixedSize(100, 100)
                button.setStyleSheet("""
                    QPushButton {
                        font-size: 16px;
                        font-weight: bold;
                        background-color: #f0f0f0;
                        border: 2px solid #9C9C9C;
                        border-radius: 0px;
                        color: #000;
                        padding: 0;
                    }
                    QPushButton:checked {
                        background-color: #000000;
                        color: white;
                    }
                    QPushButton:hover {
                        background-color: #616161;
                        color: white;             
                    }
                """)
                self.layout.addWidget(button, i, j)
                button.clicked.connect(lambda: self.check_bingo_action())
                row.append(button)
            self.buttons.append(row)
            
        #self.shortcut_export = QShortcut(QKeySequence('Ctrl+E'), self)
        #self.shortcut_export.activated.connect(lambda: self.export_card(False))

        #self.shortcut_export = QShortcut(QKeySequence('Ctrl+S'), self)
        #self.shortcut_export.activated.connect(lambda: self.export_card(True))
        
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.old_pos = None

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.AltModifier:
            self.toggle_toolbar_visibility()
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_E:
            self.export_card(False)
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_S:
            self.export_card(True)
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Q:
            self.safeCardAsScreenshot()
        if event.key() == Qt.Key.Key_H:
            self.openHelpWindow()

    def openHelpWindow(self):
        self.help_window = HelpWindow()
        self.help_window.show()

    def toggle_toolbar_visibility(self):
        self.windowSize = self.sizeHint()
        self.toolbarSize = self.toolbarMenu.sizeHint()
        is_visible = self.toolbarMenu.isVisible()  

        if is_visible:
            self.setFixedHeight(self.windowSize.height() - self.toolbarSize.height())
        else:
            self.setFixedHeight(self.windowSize.height() + self.toolbarSize.height())

        self.toolbarMenu.setVisible(not is_visible)  
        self.layout.update()
        self.adjustSize() 


    def check_bingo_action(self):
        self.checkBingo()
        self.bingo_color_change()
        print("Bingos: ", self.totalBingo)

    
    def bingo_color_change(self):
        bingoColor = "#000000"
        match self.totalBingo:
            case 0: bingoColor = "#000000"
            case 1: bingoColor = "#0000FF"
            case 2: bingoColor = "#36648B"
            case 3: bingoColor = "#6959CD"
            case 4: bingoColor = "#00868B"
            case 5: bingoColor = "#000080"
            case 6: bingoColor = "#7FFFD4"
            case 7: bingoColor = "#FF4040"
            case 8: bingoColor = "#CD9B9B"
            case 9: bingoColor = "#8B4513"
            case 10: bingoColor = "#228B22"
            case 11: bingoColor = "#ADFF2F"
            case 12: bingoColor = "#C1FFC1"

        stylesheetNonBingo = f"""
            QPushButton {{
                font-size: 16px;
                font-weight: bold;
                background-color: #f0f0f0;
                border: 2px solid #9C9C9C;
                border-radius: 0px;
                color: #000;
                padding: 0;
            }}
            QPushButton:checked {{
                background-color: #000000;
                color: white;
            }}
            QPushButton:hover {{
                background-color: #616161;
                color: white;             
            }}
        """

        stylesheetBingo = f"""
            QPushButton {{
                font-size: 16px;
                font-weight: bold;
                background-color: #f0f0f0;
                border: 2px solid #9C9C9C;
                border-radius: 0px;
                color: #000;
                padding: 0;
            }}
            QPushButton:checked {{
                background-color: {bingoColor};
                color: white;
            }}
            QPushButton:hover {{
                background-color: #616161;
                color: white;             
            }}
        """
        print("stylesheetBingoColor: ", stylesheetBingo)

        for row in range(self.size):
            for col in range(self.size):
                button = self.buttons[row][col]
                if self.buttons_with_Bingo[row][col]:
                    button.setStyleSheet(stylesheetBingo)
                else:
                    button.setStyleSheet(stylesheetNonBingo)
                button.repaint()  # Ensure the button is repainted

        self.buttons_with_Bingo = [[False] * self.size for _ in range(self.size)]

    def checkBingo(self):
        size = self.size  # Größe des Bingo-Felds
        self.totalBingo = 0   
        bingoTriggered = False
        #Überprüfe Zeilen
        for row in range(size):        
            if all(self.buttons[row][col].isChecked() for col in range(size)):
                self.totalBingo = self.totalBingo +1
                bingoTriggered = True
                for col in range(size):
                    self.buttons_with_Bingo[row][col] = True
            
        #Überprüfe Spalten
        for col in range(size):
            if all(self.buttons[row][col].isChecked() for row in range(size)):
                self.totalBingo = self.totalBingo +1
                bingoTriggered = True
                for row in range(size):
                    self.buttons_with_Bingo[row][col] = True

        #Überprüfe Hauptdiagonale (von oben links nach unten rechts)
        if all(self.buttons[i][i].isChecked() for i in range(size)):
            self.totalBingo = self.totalBingo +1
            bingoTriggered = True
            for i in range(size):
                self.buttons_with_Bingo[i][i] = True

        #Überprüfe Nebendiagonale (von oben rechts nach unten links)
        if all(self.buttons[i][size - 1 - i].isChecked() for i in range(size)):
            self.totalBingo = self.totalBingo +1
            bingoTriggered = True
            for i in range(size):
                self.buttons_with_Bingo[i][size - 1 - i] = True
        print(self.buttons_with_Bingo[0][0], ", ", self.buttons_with_Bingo[0][1], ", ", self.buttons_with_Bingo[0][2])
        print(self.buttons_with_Bingo[1][0], ", ", self.buttons_with_Bingo[1][1], ", ", self.buttons_with_Bingo[1][2])
        print(self.buttons_with_Bingo[2][0], ", ", self.buttons_with_Bingo[2][1], ", ", self.buttons_with_Bingo[2][2])


    def textLaengeAnpassen(self, text):
        max_length = 9
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            while len(word) > max_length:
                # Teile das Wort mit einem Bindestrich auf
                part = word[:max_length - 1] + '-'
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                lines.append(part)
                word = word[max_length - 1:]  # Rest des Wortes bleibt zur Weiterverarbeitung

            potential_line = current_line + " " + word if current_line else word

            if len(potential_line) <= max_length:
                current_line = potential_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return '\n'.join(lines)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.old_pos = event.globalPosition()
    
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition() - self.old_pos
            self.move(self.x() + int(delta.x()), int(self.y()) + int(delta.y()))
            self.old_pos = event.globalPosition()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.old_pos = None

    def export_card(self, marked):
        #options = QFileDialog.Option()
        filename, _ = QFileDialog.getSaveFileName(self, "Karte exportieren", "", "JSON Files (*.json)")
        if filename:
            size = self.size
            terms = self.terms
            if marked:
                marked_status = [[self.buttons[i][j].isChecked() for j in range(size)] for i in range(size)]
            else:
                marked_status = [[False for j in range(size)] for i in range(size)]
            
            data = {'size': size, 'terms': terms, 'marked': marked_status}
            with open(filename, 'w') as f:
                json.dump(data, f)

    def safeCardAsScreenshot(self):
        # Screenshot des aktuellen Bingo-Karten-Fensters
        pixmap = self.grab()
        filename, _ = QFileDialog.getSaveFileName(self, "Karte exportieren", "", "PNG Files (*.png)")
        if filename:
            # Speichern des Screenshots als Bilddatei
            pixmap.save(filename)
            print(f"Karte erfolgreich als {filename} gespeichert.")


class BingoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bullshit Bingo")
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.size_label = QLabel("Feldgröße:")
        self.size_combo = QComboBox()
        self.size_combo.addItems(["3x3", "4x4", "5x5"])
        self.word_count_label = QLabel("Wörter eingegeben: 0")

        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Gib die Wörter mit Komma getrennt ein: Apfel, Keks, Baum...")
        self.word_input.textChanged.connect(self.update_word_count)

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
        
        self.opacityLabel = QLabel("Transparenz: 0%")

        self.layout.addWidget(self.size_label)
        self.layout.addWidget(self.size_combo)
        self.layout.addWidget(self.word_count_label)
        self.layout.addWidget(self.word_input)
        self.layout.addWidget(self.create_button)
        self.layout.addWidget(self.import_button)        
        self.layout.addWidget(self.opacityLabel)
        self.layout.addWidget(self.opacitySlider)

    def update_opacityLabel(self):
        size = self.opacitySlider.value()
        self.opacityLabel.setText(f"Transparenz: {size}%")

    def update_word_count(self):
        text = self.word_input.text()
        words = text.split(', ')
        num_words = len(words)
        self.word_count_label.setText(f"Wörter eingegeben: {num_words}")

    def create_card(self):
        
        size_str = self.size_combo.currentText()
        size = int(size_str[0])
        terms = self.word_input.text().split(', ')

        if len(terms) < size * size:
            QMessageBox.warning(self, "Fehler", f"Du brauchst mindestens {size * size} Wörter!")
            return
        
        self.opacity_level = (100-self.opacitySlider.value())/100
        self.card_window = BingoCardWindow(size, terms, self.opacity_level, shuffle=True)
        self.card_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.card_window.show()

        layout = QVBoxLayout()
        self.card_window.setLayout(layout)

    def import_card(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Karte importieren", "", "JSON Files (*.json)")
        if filename:
            with open(filename, 'r') as f:
                data = json.load(f)
                size = data['size']
                terms = data['terms']
                self.opacity_level = (100-self.opacitySlider.value())/100
                self.card_window = BingoCardWindow(size, terms, self.opacity_level, shuffle=False)
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
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BingoApp()
    window.show()
    sys.exit(app.exec())

