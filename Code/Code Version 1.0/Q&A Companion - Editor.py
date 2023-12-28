import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QWidget, QVBoxLayout, QFileDialog, QLabel, QAction, QMenu, QColorDialog, QFontDialog, QMessageBox
from PyQt5.QtCore import Qt, QRect, QFileInfo, QFile, QTextStream, QIODevice
from PyQt5.QtGui import QPainter, QColor, QTextFormat, QTextCursor, QTextCharFormat, QFont, QSyntaxHighlighter, QTextDocument
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QTextOption
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtGui import QColor, QTextCursor, QIcon
from PyQt5.QtCore import QProcess
from PyQt5.QtCore import QRegExp



class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

class TextEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()


        # Set the initial text color and background color
        self.setTextColor(Qt.black)
        self.setStyleSheet("background-color: white;")
        color = QColor(Qt.black)  # convert Qt.GlobalColor to QColor object
        self.setTextColor(color)  # set the text color using QColor object  # create a QTextEdit instance and set it as the self.editor attribute
        self.layout = QVBoxLayout(self)
       

        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)

        self.zoom_in_count = 0
        self.zoom_out_count = 0

        self.highlighter = None

    def setTextColor(self, color):
        """Set the text color and background color of the QTextEdit"""
        color_name = color.name() if isinstance(color, QColor) else color
        self.setStyleSheet(f"color: {color_name}; background-color: {self.palette().color(QPalette.Base).name()};")

    def line_number_area_width(self):
        digits = 1
        max_value = max(1, self.blockCount())
        while max_value >= 10:
            max_value //= 10
            digits += 1

        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, int(top), self.line_number_area.width(), int(self.fontMetrics().height()), Qt.AlignRight, number)


            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlight_current_line(self):
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            line_color = QColor(Qt.yellow).lighter(160)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def zoom_in(self):
        self.zoom_in_count += 1
        self.zoom_out_count = max(0, self.zoom_out_count - 1)
        self.zoomIn(1)

    def zoom_out(self):
        self.zoom_out_count += 1
        self.zoom_in_count = max(0, self.zoom_in_count - 1)
        self.zoomOut(1)

    def set_font(self):
        font, ok = QFontDialog.getFont(self.font(), self, options=QFontDialog.DontUseNativeDialog)
        if ok:
            self.setFont(font)

    def set_color(self):
        color = QColorDialog.getColor(Qt.white, self, options=QColorDialog.DontUseNativeDialog)
        if color.isValid():
            self.setTextColor(color)

    def set_background_color(self):
        color = QColorDialog.getColor(self.palette().color(QPalette.Base), self, options=QColorDialog.DontUseNativeDialog)
        if color.isValid():
            self.setStyleSheet("background-color: {};".format(color.name()))

    def set_word_wrap(self, enabled):
        self.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere if enabled else QTextOption.NoWrap)

    def indent_on_return(self):
        cursor = self.textCursor()
        if cursor.block().text().lstrip().startswith("def") or cursor.block().text().lstrip().startswith("class"):
            cursor.insertBlock()
            cursor.insertText("    ")
        else:
            cursor.insertBlock()


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.text_editor = TextEditor()
        self.setCentralWidget(self.text_editor)

        
        self.setWindowTitle("Q&A Companion - Editor")
        self.setGeometry(300, 300, 800, 600)
        icon = QIcon("Q&A Companion.ico")
        self.setWindowIcon(icon)

        self.statusBar()

        open_file_action = QAction('Open', self)
        open_file_action.setShortcut('Ctrl+O')
        open_file_action.setStatusTip('Open file')
        open_file_action.triggered.connect(self.open_file)

        save_file_action = QAction('Save', self)
        save_file_action.setShortcut('Ctrl+S')
        save_file_action.setStatusTip('Save file')
        save_file_action.triggered.connect(self.save_file)

        cut_action = QAction('Cut', self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.setStatusTip('Cut')
        cut_action.triggered.connect(self.text_editor.cut)

        copy_action = QAction('Copy', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.setStatusTip('Copy')
        copy_action.triggered.connect(self.text_editor.copy)

        paste_action = QAction('Paste', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.setStatusTip('Paste')
        paste_action.triggered.connect(self.text_editor.paste)

        undo_action = QAction('Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.setStatusTip('Undo')
        undo_action.triggered.connect(self.text_editor.undo)

        redo_action = QAction('Redo', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.setStatusTip('Redo')
        redo_action.triggered.connect(self.text_editor.redo)

        find_action = QAction('Find', self)
        find_action.setShortcut('Ctrl+F')
        find_action.setStatusTip('Find')
        find_action.triggered.connect(self.find_text)

        replace_action = QAction('Replace', self)
        replace_action.setShortcut('Ctrl+H')
        replace_action.setStatusTip('Replace')
        replace_action.triggered.connect(self.replace_text)

        font_action = QAction('Font', self)
        font_action.setStatusTip('Change font')
        font_action.triggered.connect(self.text_editor.set_font)

        color_action = QAction('Text Color', self)
        color_action.setStatusTip('Change text color')
        color_action.triggered.connect(self.text_editor.set_color)

        background_color_action = QAction('Background Color', self)
        background_color_action.setStatusTip('Change background color')
        background_color_action.triggered.connect(self.text_editor.set_background_color)

        word_wrap_action = QAction('Word Wrap', self)
        word_wrap_action.setCheckable(True)
        word_wrap_action.setChecked(True)
        word_wrap_action.setStatusTip('Enable word wrap')
        word_wrap_action.triggered.connect(self.text_editor.set_word_wrap)

        zoom_in_action = QAction('Zoom In', self)
        zoom_in_action.setShortcut('Ctrl++')
        zoom_in_action.setStatusTip('Zoom in')
        zoom_in_action.triggered.connect(self.text_editor.zoom_in)

        zoom_out_action = QAction('Zoom Out', self)
        zoom_out_action.setShortcut('Ctrl+-')
        zoom_out_action.setStatusTip('Zoom out')
        zoom_out_action.triggered.connect(self.text_editor.zoom_out)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(open_file_action)
        file_menu.addAction(save_file_action)

        edit_menu = menubar.addMenu('&Edit')
        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addAction(find_action)
        edit_menu.addAction(replace_action)

        format_menu = menubar.addMenu('&Format')
        format_menu.addAction(font_action)
        format_menu.addAction(color_action)
        format_menu.addAction(background_color_action)
        format_menu.addAction(word_wrap_action)
        format_menu.addAction(zoom_in_action)
        format_menu.addAction(zoom_out_action)

        self.show()

    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'Text Files (*.txt);;All Files (*)', options=options)
        if file_name:
            with open(file_name, 'r') as file:
                data = file.read()
                self.text_editor.setPlainText(data)

    def save_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'Text Files (*.txt);;All Files (*)', options=options)
        if file_name:
            file = QFile(file_name)
            if file.open(QIODevice.WriteOnly | QIODevice.Text):
                stream = QTextStream(file)
                stream << self.text_editor.toPlainText()
                file.close()

    def find_text(self):
        text, ok = QInputDialog.getText(self, "Find", "Enter text to find:")
        if ok:
            cursor = self.text_editor.document().find(text)
            if not cursor.isNull():
                self.text_editor.setTextCursor(cursor)

    def replace_text(self):
        find_text, ok = QInputDialog.getText(self, "Find", "Enter text to find:")
        if ok:
            replace_text, ok = QInputDialog.getText(self, "Replace", "Enter replacement text:")
            if ok:
                cursor = self.text_editor.textCursor()
                cursor.beginEditBlock()
                while True:
                    cursor = self.text_editor.document().find(find_text, cursor)
                    if cursor.isNull():
                        break
                    cursor.insertText(replace_text)
                cursor.endEditBlock()

    def closeEvent(self, event):
        if self.text_editor.document().isModified():
            reply = QMessageBox.question(self, 'Save Changes', 'Do you want to save changes before closing?', QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
