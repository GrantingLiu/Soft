from PyQt5.QtCore import Qt
from PyQt5.QtCore import QUrl

from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog
from PyQt5 import QtCore, QtGui, QtWidgets,QtMultimedia
from PyQt5.QtCore import QTimer,pyqtSignal
import sys

app = QApplication(sys.argv)
print("app")
url = QUrl.fromLocalFile(".\\res\\warm.mp3")
print("url")
content =  QtMultimedia.QMediaContent(url)
player = QtMultimedia.QMediaPlayer()
player.setMedia(content)
player.play()
print("play")
player.setVolume(10)
print("1")
sys.exit(app.exec())
