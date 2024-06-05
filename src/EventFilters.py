from PyQt5.QtCore import QObject, Qt, QEvent


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


class ButtonHoverHandler(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def eventFilter(self, obj, event):
        if obj in self.parent.starBtns and event.type() == QEvent.HoverEnter:
            self.parent.onHovered(self.parent.starBtns.index(obj) + 1)
        return super().eventFilter(obj, event)
    
class SearchInputKeyEater(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
                self.parent.search()
                return True
            elif event.key() == Qt.Key_Return and event.modifiers() & Qt.ShiftModifier:
                self.parent.webSearchInput.insertPlainText("\n")
                return True
        return False
