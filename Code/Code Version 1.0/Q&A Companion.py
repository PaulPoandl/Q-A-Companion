import sys
import nltk
import re
import string
from nltk.chat.util import Chat, reflections
from PyQt5 import QtWidgets, QtGui, QtCore; 
from PyQt5.QtWidgets import QLineEdit, QMessageBox, QMainWindow, QAction, QFileDialog, QColorDialog, QFontDialog, QStyleFactory, QGridLayout, QWidget, QTextEdit, QPushButton, QComboBox, QLabel, QCheckBox, QRadioButton, QVBoxLayout, QHBoxLayout, QGroupBox, QStyle
from PyQt5.QtGui import QIcon, QColor, QTextDocument, QTextCursor, QPageSize, QPainter, QPdfWriter
from PyQt5.QtCore import Qt, QMargins, QIODevice
import subprocess
from PyQt5.QtWidgets import QActionGroup
from PyQt5.QtWidgets import QDialogButtonBox, QDialog
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5 import QtPrintSupport
import os


def get_pairs_from_file(file_path):
    pairs = []
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip().split("=")
                pattern = line[0].strip()
                response = line[1].strip()
                pairs.append([pattern, [response]])
    except:
        pairs = []
    return pairs


class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Q&A Companion")
        self.setGeometry(100, 100, 600, 400)
        icon = QIcon("Q&A Companion.ico")
        self.setWindowIcon(icon)

        # Create widgets
        self.patterns = []

        self.file_path_text = QtWidgets.QLineEdit()
        self.file_path_text= QLineEdit()
        self.file_path_text.setPlaceholderText("File Path")
        self.file_path_button = QtWidgets.QPushButton("Select File")
        self.file_path_button.clicked.connect(self.showDialog)

        self.input_text = QtWidgets.QLineEdit()
        self.input_text= QLineEdit()
        self.input_text.setPlaceholderText("Enter your message")
        self.input_button = QtWidgets.QPushButton("Submit")
        self.input_button.clicked.connect(self.sendMessage)

        self.output_text = QtWidgets.QTextEdit()
        self.output_text.setReadOnly(True)

        self.clear_button = QtWidgets.QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_conversation)

        # Create menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        edit_menu = menubar.addMenu('Edit')
        help_menu = menubar.addMenu('Help')
        external_menu = menubar.addMenu('External')
        preferences_menu = menubar.addMenu('Preferences')

        # Create actions for file menu
        open_file_action = QAction('Open File', self)
        open_file_action.setShortcut('Ctrl+O')
        open_file_action.triggered.connect(self.showDialog)
        file_menu.addAction(open_file_action)

        save_as_file_action = QAction('Save As', self)
        save_as_file_action.setShortcut('Ctrl+Shift+S')
        save_as_file_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_file_action)

        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Create actions for edit menu
        font_action = QAction('Font', self)
        font_action.setShortcut('Ctrl+F')
        font_action.triggered.connect(self.change_font)
        edit_menu.addAction(font_action)

        color_action = QAction('Color', self)
        color_action.setShortcut('Ctrl+C')
        color_action.triggered.connect(self.change_color)
        edit_menu.addAction(color_action)

        print_action = QAction('Print', self)
        print_action.setShortcut('Ctrl+P')
        print_action.triggered.connect(self.print_conversation)
        edit_menu.addAction(print_action)

        # Create actions for help menu
        help_action = QAction('Help', self)
        help_action.setShortcut('Ctrl+H')
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        about_action = QAction('About', self)
        about_action.setShortcut('Ctrl+A')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Create actions for external menu
        external_action = QAction('Editor', self)
        external_action.setShortcut('Ctrl+E')
        external_action.triggered.connect(self.start_external_program)
        external_menu.addAction(external_action)

        # Create actions for preferences menu
        theme_group = QActionGroup(self)

        light_theme_action = QAction('Light', self, checkable=True)
        light_theme_action.triggered.connect(lambda: self.change_theme('light'))
        theme_group.addAction(light_theme_action)
        preferences_menu.addAction(light_theme_action)

        dark_theme_action = QAction('Dark', self, checkable=True)
        dark_theme_action.triggered.connect(lambda: self.change_theme('dark'))
        theme_group.addAction(dark_theme_action)
        preferences_menu.addAction(dark_theme_action)

        preferences_action = QAction('Preferences', self)
        preferences_action.setShortcut('Ctrl+,')
        preferences_action.triggered.connect(self.show_preferences)
        preferences_menu.addAction(preferences_action)

        # Create toolbar
        toolbar = self.addToolBar('Toolbar')
        toolbar.addAction(open_file_action)
        toolbar.addAction(save_as_file_action)
        toolbar.addAction(font_action)
        toolbar.addAction(color_action)
        toolbar.addAction(print_action)
        toolbar.addAction(help_action)
        toolbar.addAction(external_action)

        # Create layout
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.file_path_text, 0, 0)
        layout.addWidget(self.file_path_button, 0, 1)
        layout.addWidget(self.input_text, 1, 0)
        layout.addWidget(self.input_button, 1, 1)
        layout.addWidget(self.output_text, 2, 0, 1, 3)
        layout.addWidget(self.clear_button, 3, 2)
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def showDialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "Text Files (*.txt);;All Files (*)", options=options)
        if fileName:
            self.file_path_text.setText(fileName)

    def clear_conversation(self):
        self.output_text.clear()
    
    def sendMessage(self):
        file_path = self.file_path_text.text()
        if not file_path:
            self.output_text.append("Please select a file first.")
            return

        input_text = self.input_text.text()
        self.input_text.setText("")
        if not input_text:
            return

        self.output_text.append("You: " + input_text)

        pairs = get_pairs_from_file(file_path)
        chatbot = Chat(pairs, reflections)
        response = chatbot.respond(input_text)
        
        if response is not None:
            self.output_text.append("Bot: " + response)
        else:
            self.output_text.append("Bot: Sorry, I don't have a response for that.")

    def show_help(self):
        try:
            with open("help.txt", "r") as f:
                help_text = f.read()
        except:
            help_text = "Sorry, the help file is not available."

        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Help")
        icon = QIcon("Q&A Companion.ico")
        help_dialog.setWindowIcon(icon)
        help_dialog.resize(400, 400)
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setPlainText(help_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(help_dialog.accept)
        layout.addWidget(button_box)
        help_dialog.setLayout(layout)
        help_dialog.exec_()

    def show_about(self):
        about_text = "Q&A Companion\n\nVersion 1.0\n\nDeveloped by AI Command Hub(Paul Poandl)\n\nCopyright (c) 2023\n\nContact under: Paul.Poandl@gmail.com \ aicommandhub@gmail.com"

        msg = QMessageBox()
        msg.setWindowTitle("About")
        msg.setText(about_text)
        icon = QIcon("Q&A Companion.ico")
        msg.setWindowIcon(icon)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def change_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.output_text.setFont(font)

    def change_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.output_text.setTextColor(color)

    def start_external_program(self):
        try:
            # Ausführen des Befehls in der Kommandozeile
            os.startfile("Q&A Companion - Editor.py")
        except:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("Failed to start external program.")
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()

    def change_theme(self, theme):
        if theme == 'light':
            QtWidgets.QApplication.setStyle(QStyleFactory.create('Fusion'))
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Window, QtGui.QColor(240, 240, 240))
            palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(0, 0, 0))
            palette.setColor(QtGui.QPalette.Base, QtGui.QColor(255, 255, 255))
            palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(245, 245, 245))
            palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(255, 255, 220))
            palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(0, 0, 0))
            palette.setColor(QtGui.QPalette.Text, QtGui.QColor(0, 0, 0))
            palette.setColor(QtGui.QPalette.Button, QtGui.QColor(240, 240, 240))
            palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(0, 0, 0))
            palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 0, 0))
            palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(76, 163, 224))
            palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
            QtWidgets.QApplication.setPalette(palette)
        elif theme == 'dark':
            QtWidgets.QApplication.setStyle(QStyleFactory.create('Fusion'))
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
            palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))
            palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
            palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
            palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(255, 255, 220))
            palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(255, 255, 255))
            palette.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
            palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
            palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(255, 255, 255))
            palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 0, 0))
            palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(76, 163, 224))
            palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
            QtWidgets.QApplication.setPalette(palette)

    def show_preferences(self):
        preferences_dialog = PreferencesDialog(self)
        preferences_dialog.exec_()

    def save_as_file(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save As", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            with open(file_name, "w") as f:
                f.write(self.output_text.toPlainText())

    def print_conversation(self):
        dialog = QtPrintSupport.QPrintDialog()
        if dialog.exec_() == QDialog.Accepted:
            printer = dialog.printer()
            document = QTextDocument()
            document.setPlainText(self.output_text.toPlainText())
            document.print_(printer)

class PreferencesDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setWindowModality(Qt.ApplicationModal)

        # Create widgets
        theme_label = QLabel("Theme:")
        self.theme_combo_box = QComboBox()
        self.theme_combo_box.addItem("Light")
        self.theme_combo_box.addItem("Dark")
        self.theme_combo_box.currentIndexChanged.connect(self.change_theme)


        # Create layout
        layout = QVBoxLayout()
        theme_group_box = QGroupBox("Theme")
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo_box)
        theme_group_box.setLayout(theme_layout)
        layout.addWidget(theme_group_box)


        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def change_theme(self, index):
        theme = self.theme_combo_box.currentText().lower()
        if theme == 'light':
            QtWidgets.QApplication.setStyle(QStyleFactory.create('Fusion'))
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Window, QtGui.QColor(240, 240, 240))
            palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(0, 0, 0))
            palette.setColor(QtGui.QPalette.Base, QtGui.QColor(255, 255, 255))
            palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(245, 245, 245))
            palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(255, 255, 220))
            palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(0, 0, 0))
            palette.setColor(QtGui.QPalette.Text, QtGui.QColor(0, 0, 0))
            palette.setColor(QtGui.QPalette.Button, QtGui.QColor(240, 240, 240))
            palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(0, 0, 0))
            palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 0, 0))
            palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(76, 163, 224))
            palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
            QtWidgets.QApplication.setPalette(palette)
        elif theme == 'dark':
            QtWidgets.QApplication.setStyle(QStyleFactory.create('Fusion'))
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
            palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))
            palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
            palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
            palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(255, 255, 220))
            palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(255, 255, 255))
            palette.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
            palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
            palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(255, 255, 255))
            palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 0, 0))
            palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(76, 163, 224))
            palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
            QtWidgets.QApplication.setPalette(palette)

if __name__ == '__main__':
    nltk.download("punkt")
    app = QtWidgets.QApplication([])
    gui = Window()
    gui.show()
    app.exec_()
