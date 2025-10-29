from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QStackedWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy, QScrollBar, QTextEdit
from PySide6.QtGui import QIcon, QMovie, QColor, QTextCharFormat, QFont, QTextCursor, QPainter, QPixmap
from PySide6.QtCore import Qt, QSize, QTimer, QPoint, QUrl
import sys
import os
import subprocess
import webbrowser
import json
import keyboard
import playsound
import requests
import asyncio
from typing import cast
from groq import Groq
from bs4 import BeautifulSoup
from pynput.keyboard import Key, Controller
from dotenv import dotenv_values
from datetime import datetime
from pynput import keyboard as pk
from win32com.client import Dispatch
from AppOpener import open as appopen, close as appclose
import random
import time
import mtranslate as mt
from pywhatkit import playonyt, search
import edge_tts
import pygame

# Load environment variables from a .env file.
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
current_dir = os.getcwd()

# Define paths for temporary files and graphics.
Old_Chat_Message = ""
TempDirPath = f"{current_dir}/frontend/Files"
GraphicsDirPath = f"{current_dir}/frontend/Graphics"

# === Helper Functions (made importable) ===

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's", "can you"]
    
    if any(word + " " in new_query for word in question_words):
        if new_query and new_query[-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if new_query and new_query[-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(f"{TempDirPath}/Mic.data", "w", encoding='utf-8') as file:
        file.write(Command)

def GetMicrophoneStatus():
    with open(f"{TempDirPath}/Mic.data", "r", encoding='utf-8') as file:
        Status = file.read()
    return Status

def MicButtonInitialized():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    Path = f"{GraphicsDirPath}/{Filename}"
    return Path

def TempDirectoryPath(Filename):
    Path = f"{TempDirPath}/{Filename}"
    return Path

def ShowTextToScreen(Text):
    with open(f"{TempDirPath}/Responses.data", "w", encoding='utf-8') as file:
        file.write(Text)
        
def SetAssistantStatus(Status):
    with open(f"{TempDirPath}/Status.data", "w", encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    with open(f"{TempDirPath}/Status.data", "r", encoding='utf-8') as file:
        Status = file.read()
    return Status

# === GUI Classes ===

class ChatSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(100)
        self.chat_text_edit = QTextEdit(self)
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setFrameShape(QFrame.NoFrame)
        self.chat_text_edit.setStyleSheet("background-color: black;")
        layout.addWidget(self.chat_text_edit)
        layout.setStretch(1, 1)
        text_color = QColor(Qt.blue)
        text_char_format = QTextCharFormat()
        text_char_format.setForeground(text_color)
        self.gif_label = QLabel(self)
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsDirectoryPath("jarvis.gif"))
        max_gif_size_w = 270
        if movie.currentPixmap().size().width() > 0:
            max_gif_size_h = int(max_gif_size_w * (movie.currentPixmap().size().height() / movie.currentPixmap().size().width()))
            movie.setScaledSize(QSize(max_gif_size_w, max_gif_size_h))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(message + "\n", format)
        self.chat_text_edit.setTextCursor(cursor)

    def loadMessages(self):
        global Old_Chat_Message
        with open(TempDirectoryPath("Responses.data"), "r", encoding='utf-8') as file:
            messages = file.read()
        if messages == " ":
            pass
        elif len(messages) <= 1:
            pass
        elif str(Old_Chat_Message) == str(messages):
            pass
        else:
            self.addMessage(messages, "white")
            Old_Chat_Message = messages
            
class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        screen = QApplication.primaryScreen()
        screen_width = screen.geometry().width()
        screen_height = screen.geometry().height()
        content_layout = QVBoxLayout(self)
        content_layout.setContentsMargins(0, 0, 0, 0)
        gif_label = QLabel(self)
        movie = QMovie(GraphicsDirectoryPath("jarvis.gif"))
        if movie.currentPixmap().size().width() > 0:
            max_gif_size_w = int(screen_width * 0.5)
            max_gif_size_h = int(max_gif_size_w * (movie.currentPixmap().size().height() / movie.currentPixmap().size().width()))
            movie.setScaledSize(QSize(max_gif_size_w, max_gif_size_h))
        gif_label.setAlignment(Qt.AlignCenter)
        gif_label.setMovie(movie)
        movie.start()
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.icon_label = QLabel(self)
        mic_icon_path = GraphicsDirectoryPath("Mic_on.png")
        pixmap = QPixmap(mic_icon_path)
        new_pixmap = pixmap.scaled(60, 60)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = True
        self.icon_label.mousePressEvent = self.toggle_icon
        self.icon_label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")
        content_layout.addWidget(self.icon_label)
        content_layout.addWidget(gif_label)
        self.setContentsMargins(0, 0, 0, 150)
        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(500)
    
    def SpeechRecogText(self):
        with open(TempDirectoryPath("Status.data"), "r", encoding='utf-8') as file:
            messages = file.read()
            self.icon_label.setText(messages)
            
    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath("Mic_on.png"), 60, 60)
            MicButtonInitialized()
        else:
            self.load_icon(GraphicsDirectoryPath("Mic_off.png"), 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        screen = QApplication.primaryScreen()
        screen_width = screen.geometry().width()
        screen_height = screen.geometry().height()
        layout = QVBoxLayout(self)
        label = QLabel(self)
        chat_section = ChatSection(self)
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
    
class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.current_screen = None
        self.stacked_widget = stacked_widget
        self.initUI()
    
    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignRight)
        home_button = QPushButton(QIcon(GraphicsDirectoryPath("Home.png")), "Home")
        home_button.setStyleSheet("height:40px; line-height:40px; background-color:white; color: black;")
        message_button = QPushButton(QIcon(GraphicsDirectoryPath("Chats.png")), "Chat")
        message_button.setStyleSheet("height:40px; line-height:40px; background-color:white; color: black;")
        self.minimize_button = QPushButton(QIcon(GraphicsDirectoryPath("Minimize2.png")), "")
        self.minimize_button.setStyleSheet("background-color:white; color: white;")
        self.minimize_button.clicked.connect(self.minimizeWindow)
        self.maximize_button = QPushButton(QIcon(GraphicsDirectoryPath("Maximize.png")), "")
        self.maximize_button.setStyleSheet("background-color:white; color: white;")
        self.maximize_button.clicked.connect(self.maximizeWindow)
        self.close_button = QPushButton(QIcon(GraphicsDirectoryPath("close.png")), "")
        self.close_button.setStyleSheet("background-color:white; color: white;")
        self.close_button.clicked.connect(self.closeWindow)
        
        line_frame = QFrame(self)
        line_frame.setFixedHeight(1)
        line_frame.setStyleSheet("border-color: black;")
        
        title_label = QLabel(f"{str(Assistantname).capitalize()} AI")
        title_label.setStyleSheet("color: black; font-size: 16px; background-color:white;")
        
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)

        self.setLayout(layout)
        self.setStyleSheet("background-color: white;")
        self.setFixedSize(self.parent().width(), 50)
        self.offset = None
        self.setMouseTracking(True)
        self.home_icon = QIcon(GraphicsDirectoryPath("Home.png"))
        self.chat_icon = QIcon(GraphicsDirectoryPath("Chats.png"))
        self.minimize_icon = QIcon(GraphicsDirectoryPath("Minimize.png"))
        self.maximize_icon = QIcon(GraphicsDirectoryPath("Maximize.png"))
        self.close_icon = QIcon(GraphicsDirectoryPath("close.png"))
        self.restore_icon = QIcon(GraphicsDirectoryPath("Restore.png"))
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)
        
    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent().close()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.position().toPoint()
    
    def mouseMoveEvent(self, event):
        if self.offset and event.buttons() == Qt.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.offset
            self.parent().move(new_pos)
            
    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)
            self.current_screen = message_screen
            
    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
        initial_screen = InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
            self.current_screen = initial_screen

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.setWindowFlags(Qt.FramelessWindowHint)

    def initUI(self):
        screen = QApplication.primaryScreen()
        screen_width = screen.geometry().width()
        screen_height = screen.geometry().height()
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen(self)
        message_screen = MessageScreen(self)
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        stacked_widget.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = CustomTopBar(self, stacked_widget)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(top_bar)
        main_layout.addWidget(stacked_widget)
        
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    GraphicalUserInterface()