import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox


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
