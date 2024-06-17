import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox,
                             QMainWindow, QDialog, QCheckBox)


class FeedbackPopup(QWidget):
    feedback_textedit: QTextEdit

    def __init__(self, rating, maxRating):
        super().__init__()
        self.rating = rating
        self.maxRating = maxRating
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        rating_label = QLabel()
        rating_label.setText(f"You rated: {self.rating}/{self.maxRating} stars")
        rating_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(rating_label)

        feedback_label = QLabel()
        feedback_label.setText("Please give us additional feedback on how we can improve our product:")
        layout.addWidget(feedback_label)

        self.feedback_textedit = QTextEdit()
        layout.addWidget(self.feedback_textedit)

        send_button = QPushButton("Send")
        send_button.clicked.connect(self.sendFeedback)
        layout.addWidget(send_button)

        self.setLayout(layout)
        self.setWindowTitle("Send Feedback")

    def sendFeedback(self):
        feedback_text = self.feedback_textedit.toPlainText()
        QMessageBox.information(self, "Feedback Sent",
                                f"Thank you for your feedback!\n\nRating: {self.rating}\nFeedback: {feedback_text}")
        self.close()


class FeatureDialog(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 200, 100)

        # Layout and widgets
        layout = QVBoxLayout()

        self.label = QLabel("Turn on text to speech")
        self.checkbox = QCheckBox("Enable text to speech")

        # Set initial checkbox state based on main_window's textToSpeech attribute
        self.checkbox.setChecked(self.main_window.textToSpeech)

        # Connect the checkbox state change to a method
        self.checkbox.stateChanged.connect(self.toggle_feature)

        layout.addWidget(self.label)
        layout.addWidget(self.checkbox)

        self.setLayout(layout)

    def toggle_feature(self, state):
        if state == 2:  # Checked
            self.main_window.textToSpeech = True
            self.label.setText("Text to speech is ON")
        else:  # Unchecked
            self.main_window.textToSpeech = False
            self.label.setText("Text to speech is OFF")
