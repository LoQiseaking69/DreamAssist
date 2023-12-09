import sys
import os
import asyncio
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QLabel
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QIcon
from PyQt5.QtCore import Qt, QRunnable, QThreadPool, QObject, pyqtSignal
from openai import AsyncOpenAI

# Function to find the correct path for resources (images, etc.)
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class BackgroundLabel(QLabel):
    def __init__(self, imagePath, parent=None):
        super().__init__(parent)
        self.pixmap = QPixmap(resource_path(imagePath))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(self.pixmap))
        painter.fillRect(self.rect(), painter.brush())

class Signals(QObject):
    finished = pyqtSignal(str)

class Worker(QRunnable):
    def __init__(self, user_input):
        super(Worker, self).__init__()
        self.user_input = user_input
        self.signals = Signals()

    def run(self):
        asyncio.run(self.fetch_response())

    async def fetch_response(self):
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Set your OpenAI API key
        try:
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",  # You can change the model as needed
                messages=[{"role": "user", "content": self.user_input}]
            )
            self.signals.finished.emit(response.choices[0].message.content)
        except Exception as e:
            self.signals.finished.emit(f"Error: {str(e)}")

class InputBox(QTextEdit):
    def __init__(self, chat_app, parent=None):
        super(InputBox, self).__init__(parent)
        self.chat_app = chat_app

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and not event.modifiers():
            self.chat_app.onSend()
        else:
            super(InputBox, self).keyPressEvent(event)

class ChatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("DreamAssist")
        self.setGeometry(100, 100, 1200, 600)
        self.setWindowIcon(QIcon(resource_path('Favicon.png')))
        self.backgroundLabel = BackgroundLabel("cyber_background.png")  # Image path is now handled by resource_path
        self.setCentralWidget(self.backgroundLabel)

        # Main horizontal layout
        self.mainLayout = QHBoxLayout(self.backgroundLabel)

        # Layout for chat interface
        self.chatLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.chatLayout, 1)

        # Clear Chat button
        self.clearChatButton = QPushButton("Clear Chat", self)
        self.clearChatButton.clicked.connect(self.clearChat)
        self.chatLayout.addWidget(self.clearChatButton)

        # Chat interface widgets
        self.chatBox = QTextEdit(self)
        self.chatBox.setReadOnly(True)
        self.chatBox.setStyleSheet("""
            background-color: rgba(0, 0, 255, 0.3); 
            background-image: url('""" + resource_path('Bg.PNG') + """');
            color: white;
            font: 18pt;
        """)
        self.chatBox.setAttribute(Qt.WA_TranslucentBackground)
        self.chatBox.setAttribute(Qt.WA_NoSystemBackground)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.chatBox)
        self.scrollArea.setStyleSheet("background-color: transparent;")

        self.inputBox = InputBox(self, self)
        self.inputBox.setFixedHeight(50)
        self.chatLayout.addWidget(self.scrollArea)
        self.chatLayout.addWidget(self.inputBox)

        self.sendButton = QPushButton("Send", self)
        self.sendButton.clicked.connect(self.onSend)
        self.chatLayout.addWidget(self.sendButton)

        # Add vertical menu to the right
        self.setupVerticalMenu()

        self.threadPool = QThreadPool()

    def setupVerticalMenu(self):
        # Vertical transparent purple menu
        self.verticalMenuWidget = QWidget(self)
        self.verticalMenuWidget.setStyleSheet("background-color: rgba(128, 0, 128, 0.5);")  # Transparent purple
        self.verticalMenuWidget.setFixedWidth(100)
        self.verticalMenuLayout = QVBoxLayout(self.verticalMenuWidget)

        # Button style
        button_style = "QPushButton { background-color: lightblue; border: none; }"

        # Add buttons/actions to the vertical menu
        terminal_button = QPushButton("Terminal", self)
        terminal_button.setStyleSheet(button_style)
        self.verticalMenuLayout.addWidget(terminal_button)

        files_button = QPushButton("Files", self)
        files_button.setStyleSheet(button_style)
        self.verticalMenuLayout.addWidget(files_button)

        agents_button = QPushButton("Agents", self)
        agents_button.setStyleSheet(button_style)
        self.verticalMenuLayout.addWidget(agents_button)

        # Add the vertical menu widget to the main layout
        self.mainLayout.addWidget(self.verticalMenuWidget)

    def clearChat(self):
        self.chatBox.clear()

    def resizeEvent(self, event):
        # Position the vertical menu
        self.verticalMenuWidget.move(self.width() - self.verticalMenuWidget.width() - 30, 30)
        QMainWindow.resizeEvent(self, event)

    def onSend(self):
        user_input = self.inputBox.toPlainText().strip()
        self.inputBox.clear()
        if not user_input:
            return

        self.chatBox.append(f"You: {user_input}")
        worker = Worker(user_input)
        worker.signals.finished.connect(self.displayResponse)
        self.threadPool.start(worker)

    def displayResponse(self, response):
        self.chatBox.append(f"DreamAssist: {response}")
        self.chatBox.verticalScrollBar().setValue(self.chatBox.verticalScrollBar().maximum())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ChatApp()
    ex.show()
    sys.exit(app.exec_())
