from PyQt5.QtCore import QObject, Qt


class QueryInputKeyEaster(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
                self.parent.enterQuery()
                return True
            elif event.key() == Qt.Key_Return and event.modifiers() & Qt.ShiftModifier:
                self.parent.queryInput.insertPlainText("\n")
                return True
        return False