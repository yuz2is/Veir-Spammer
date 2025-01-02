import sys
import time
import pyperclip
import pyautogui
import keyboard
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QWidget, QSpinBox, QTextEdit, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty, QPoint, QRectF, QThread, pyqtSignal
from PyQt5.QtGui import QPainterPath, QRegion

class SpamThread(QThread):
    finished = pyqtSignal()
    stopped = pyqtSignal()

    def __init__(self, message, delay, count):
        super().__init__()
        self.message = message
        self.delay = delay
        self.count = count
        self.running = True

    def run(self):
        pyperclip.copy(self.message)
        time.sleep(1)

        for _ in range(self.count):
            if not self.running:
                self.stopped.emit()
                return
            pyautogui.hotkey("ctrl", "v")
            pyautogui.press("enter")
            time.sleep(self.delay)
        self.finished.emit()

    def stop(self):
        self.running = False

class WelcomeOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setStyleSheet("background-color: black; border-radius: 15px;")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setGeometry(parent.rect())
        self._opacity = 1.0
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)
        self.veir_label = QLabel("Veir")
        self.veir_label.setStyleSheet(
            "font-size: 48px; color: white; font-family: 'Rowdies', sans-serif; font-weight: bold;"
        )
        self.layout.addWidget(self.veir_label)
        self.start_button = QPushButton("Start")
        self.start_button.setFixedSize(200, 50)
        self.start_button.setStyleSheet(""" 
            QPushButton {
                background-color: #6A0DAD;
                color: white;
                font-size: 20px;
                font-family: 'Rowdies', sans-serif;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #5A0E9C;
            }
        """)
        self.start_button.clicked.connect(self.fade_out)
        self.layout.addWidget(self.start_button)

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.setStyleSheet(f"background-color: rgba(0, 0, 0, {value}); border-radius: 15px;")
        self.repaint()
        self.veir_label.setStyleSheet(
            f"font-size: 48px; color: rgba(255, 255, 255, {value}); font-family: 'Rowdies', sans-serif; font-weight: bold;"
        )
        self.start_button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(106, 13, 173, {value});
                color: rgba(255, 255, 255, {value});
                font-size: 20px;
                font-family: 'Rowdies', sans-serif;
                font-weight: bold;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: rgba(90, 14, 156, {value});
            }}
        """)

    def fade_out(self):
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.deleteLater)
        self.animation.start()

class SpamApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Veir Spammer")
        self.setGeometry(100, 100, 400, 300)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #000000; color: white; border-radius: 15px;")
        self.init_ui()
        self.setFixedSize(400, 300)
        path = QPainterPath()
        rect = QRectF(self.rect())
        path.addRoundedRect(rect, 15, 15)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())
        self.spam_thread = None
        self.overlay = WelcomeOverlay(self)
        self.overlay.show()

    def init_ui(self):
        layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        self.init_title_bar(layout)
        self.message_label = QLabel("Message:")
        self.message_label.setStyleSheet("font-size: 14px; color: white; font-family: 'Fredoka Light', sans-serif; font-weight: bold;")
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Welcome To Veir Spammer, Developed by yuz2is, have fun spamming, Press R to stop the spammer easier instead of pressing the Stop button.")
        self.message_input.setStyleSheet(
            "background-color: #333333; color: white; border-radius: 5px; padding: 5px; font-family: 'Fredoka Light', sans-serif; font-size: 14px;"
        )
        layout.addWidget(self.message_label)
        layout.addWidget(self.message_input)
        self.delay_label = QLabel("Delay (seconds):")
        self.delay_label.setStyleSheet("font-size: 14px; color: white; font-family: 'Fredoka Light', sans-serif; font-weight: bold;")
        self.delay_input = QDoubleSpinBox()
        self.delay_input.setMinimum(0.1)
        self.delay_input.setMaximum(10.0)
        self.delay_input.setSingleStep(0.1)
        self.delay_input.setValue(1.0)
        self.delay_input.setStyleSheet(
            "background-color: #333333; color: white; border-radius: 5px; padding: 5px;"
        )
        layout.addWidget(self.delay_label)
        layout.addWidget(self.delay_input)
        self.count_label = QLabel("Number of messages:")
        self.count_label.setStyleSheet("font-size: 14px; color: white; font-family: 'Fredoka Light', sans-serif; font-weight: bold;")
        self.count_input = QSpinBox()
        self.count_input.setMinimum(1)
        self.count_input.setMaximum(1000)
        self.count_input.setValue(10)
        self.count_input.setStyleSheet(
            "background-color: #333333; color: white; border-radius: 5px; padding: 5px;"
        )
        layout.addWidget(self.count_label)
        layout.addWidget(self.count_input)
        buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Spam")
        self.start_button.setStyleSheet(""" 
            QPushButton {
                background-color: #6A0DAD;
                color: white;
                font-size: 16px;
                font-family: 'Rowdies', sans-serif;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #5A0E9C;
            }
        """)
        self.start_button.clicked.connect(self.start_spam)
        buttons_layout.addWidget(self.start_button)
        self.stop_button = QPushButton("Stop Spam")
        self.stop_button.setStyleSheet(""" 
            QPushButton {
                background-color: #FF6347;
                color: white;
                font-size: 16px;
                font-family: 'Rowdies', sans-serif;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FF4500;
            }
        """)
        self.stop_button.clicked.connect(self.stop_spam)
        buttons_layout.addWidget(self.stop_button)
        layout.addLayout(buttons_layout)

    def init_title_bar(self, layout):
        title_bar = QHBoxLayout()
        self.title_label = QLabel("Veir Spammer")
        self.title_label.setStyleSheet("font-size: 16px; color: white; font-family: 'Rowdies', sans-serif; font-weight: bold;")
        title_bar.addWidget(self.title_label)
        title_bar.addStretch()
        self.minimize_button = QPushButton("_")
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setStyleSheet("background-color: #444; color: white; border-radius: 5px;")
        self.minimize_button.clicked.connect(self.showMinimized)
        title_bar.addWidget(self.minimize_button)
        self.close_button = QPushButton("X")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("background-color: #444; color: white; border-radius: 5px;")
        self.close_button.clicked.connect(self.close)
        title_bar.addWidget(self.close_button)
        layout.addLayout(title_bar)
        self.old_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def start_spam(self):
        message = self.message_input.toPlainText().strip()
        delay = self.delay_input.value()
        count = self.count_input.value()
        if not message:
            print("Message is empty!")
            return
        if self.spam_thread and self.spam_thread.isRunning():
            return
        self.spam_thread = SpamThread(message, delay, count)
        self.spam_thread.finished.connect(self.spam_finished)
        self.spam_thread.stopped.connect(self.spam_stopped)
        self.spam_thread.start()
        keyboard.add_hotkey('r', self.stop_spam)

    def stop_spam(self):
        if self.spam_thread and self.spam_thread.isRunning():
            self.spam_thread.stop()

    def spam_finished(self):
        print("Spam finished.")

    def spam_stopped(self):
        print("Spam stopped.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpamApp()
    window.show()
    sys.exit(app.exec_())
