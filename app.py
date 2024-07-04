import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPixmap, QPainter
import threading
from mss import mss
import time

def svg_to_pixmap(svg_path, width, height):
    renderer = QSvgRenderer(svg_path)
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap

class ScreenRecorderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_recording = False
        self.output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "records")
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def initUI(self):
        self.setWindowTitle('Screen Recorder')
        self.setGeometry(300, 300, 300, 150)

        layout = QVBoxLayout()
        self.record_button = QPushButton('', self)
        play_icon = svg_to_pixmap('play_icon.svg', 32, 32)
        self.record_button.setIcon(QIcon(play_icon))
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button)

        self.setLayout(layout)

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        stop_icon = svg_to_pixmap('stop_icon.svg', 32, 32)
        self.record_button.setIcon(QIcon(stop_icon))
        output_file = os.path.join(self.output_dir, f"recording_{len(os.listdir(self.output_dir)) + 1}.mp4")
        threading.Thread(target=self.record_screen, args=(output_file,), daemon=True).start()

    def stop_recording(self):
        self.is_recording = False
        play_icon = svg_to_pixmap('play_icon.svg', 32, 32)
        self.record_button.setIcon(QIcon(play_icon))

    def record_screen(self, output_file):
        with mss() as sct:
            monitor = sct.monitors[0]  # Capture the primary monitor
            
            width = monitor["width"]
            height = monitor["height"]
            
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(output_file, fourcc, 30.0, (width, height))

            while self.is_recording:
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
                out.write(frame)
                time.sleep(1/30)  # Adjust for desired frame rate

            out.release()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ScreenRecorderApp()
    ex.show()
    sys.exit(app.exec_())