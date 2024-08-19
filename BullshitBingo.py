import sys
import random
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QGridLayout, QComboBox, QLineEdit, QMessageBox, QFileDialog, QShortcut, QSlider
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QKeySequence


class BingoCardWindow(QWidget):
    def __init__(self, size, terms, opacity, parent=None):
        super().__init__(parent)
        self.size = size
        self.terms = terms
        self.grid_layout = QGridLayout()
        self.setWindowFlags(Qt.FramelessWindowHint)  # Entfernt die Titelleiste
        self.setWindowOpacity(opacity) 

        cardLenght = ((self.size)*100)
        cardHeight = cardLenght
        self.setFixedSize(cardLenght, cardHeight)


        # Layout-Einstellungen
        self.grid_layout.setSpacing(0)  # Setze den Abstand zwischen den Widgets auf 0
        self.grid_layout.setContentsMargins(0, 0, 0, 0)  # Setze die Ränder des Layouts auf 0

        # Shuffle und Grid erstellen
        random.shuffle(self.terms)
        self.buttons = []
        for i in range(self.size):
            row = []
            for j in range(self.size):
                term = self.terms[i * self.size + j]
                print(term)
                feldText = self.textLaengeAnpassen(term) # type: ignore
                button = QPushButton(feldText)
            
                button.setCheckable(True)
                button.setFixedSize(100, 100)
                button.setStyleSheet("""
                    QPushButton {
                        font-size: 16px;
                        font-weight: bold;
                        background-color: #f0f0f0;
                        border: 2px solid #0078d4;
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
                self.grid_layout.addWidget(button, i, j)
                row.append(button)
            self.buttons.append(row)
        
        #Export-Buttons
        self.button_layout = QVBoxLayout
        self.save_button = QPushButton("Speichern")
        self.save_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        self.save_button.clicked.connect(lambda: self.export_card("PLBingocard.json", marked=False))

        self.export_button = QPushButton("Teilen")
        self.export_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)

        self.export_button.clicked.connect(lambda: self.export_card("Bingocard", marked=False))

        self.setLayout(self.grid_layout)

        # Fenster ziehen ermöglichen
        self.old_pos = None

    # Ersetze den bisherigen Inhalt der format_text-Methode durch den folgenden Code:
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
        if event.button() == Qt.RightButton:
            self.old_pos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.old_pos = None

    

    def export_card(self, filename: str, marked=False):
        pixmap = QPixmap(self.size * 100, self.size * 100)
        pixmap.fill(Qt.white)
        painter = QPainter(pixmap)

        for i in range(self.size):
            for j in range(self.size):
                term = self.terms[i * self.size + j]
                rect = self.grid_layout.itemAtPosition(i, j).widget().geometry()
                painter.drawRect(rect)
                painter.drawText(rect, Qt.AlignCenter, term)
                if marked and self.buttons[i][j].isChecked():
                    painter.fillRect(rect, Qt.green)

        painter.end()
        pixmap.save(filename)


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

        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Gib die Wörter mit Kommas getrennt ein")

        self.create_button = QPushButton("Karte erstellen")
        self.create_button.clicked.connect(self.create_card)

        self.import_button = QPushButton("Karte importieren")
        self.import_button.clicked.connect(self.import_card)

        self.opacitySlider = QSlider()
        self.opacitySlider.setOrientation(Qt.Horizontal)
        self.opacitySlider.setMinimum(0)
        self.opacitySlider.setMaximum(80) 
        self.opacitySlider.setValue(0)
        self.opacitySlider.valueChanged.connect(self.update_opacityLabel)
        
        self.opacityLabel = QLabel("Transparenz: 0%")

        self.layout.addWidget(self.size_label)
        self.layout.addWidget(self.size_combo)
        self.layout.addWidget(self.word_input)
        self.layout.addWidget(self.create_button)
        self.layout.addWidget(self.import_button)        
        self.layout.addWidget(self.opacityLabel)
        self.layout.addWidget(self.opacitySlider)

    def update_opacityLabel(self):
        size = self.opacitySlider.value()
        self.opacityLabel.setText(f"Transparenz: {size}%")

    def create_card(self):
        opacity = (100-self.opacitySlider.value())/100
        size_str = self.size_combo.currentText()
        size = int(size_str[0])
        terms = self.word_input.text().split(', ')

        if len(terms) < size * size:
            QMessageBox.warning(self, "Fehler", f"Du brauchst mindestens {size * size} Wörter!")
            return

        self.card_window = BingoCardWindow(size, terms, opacity)
        self.card_window.show()

        layout = QVBoxLayout()
        self.card_window.setLayout(layout)

    def import_card(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Karte importieren", "", "JSON Files (*.json)", options=options)
        if filename:
            with open(filename, 'r') as f:
                data = json.load(f)
                size = data['size']
                terms = data['terms']
                self.card_window = BingoCardWindow(size, terms)
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

    def export_card(self, marked=False):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Karte exportieren", "", "PNG Files (*.png);;JSON Files (*.json)", options=options)
        if filename.endswith(".png"):
            self.card_window.export_card(filename, marked)
        elif filename.endswith(".json"):
            size = self.card_window.size
            terms = self.card_window.terms
            marked_status = [[self.card_window.buttons[i][j].isChecked() for j in range(size)] for i in range(size)]
            data = {'size': size, 'terms': terms, 'marked': marked_status}
            with open(filename, 'w') as f:
                json.dump(data, f)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BingoApp()
    window.show()
    sys.exit(app.exec_())