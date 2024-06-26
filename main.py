import sys
from typing import cast

import PySide6.QtSvg
from PySide6 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
from PySide6.QtCore import QSettings, Qt, SIGNAL
import pandas


class MainGraph(QtWidgets.QMdiSubWindow):

    def __init__(self, x_label: str = 'x', y_label: str = 'y', parent=None):
        super(MainGraph, self).__init__(parent)

        self.graphWidget = pg.PlotWidget(self)
        styles = {'color': 'b', 'font-size': '15px'}
        self.graphWidget.setLabel(self.tr('left'), y_label, **styles)
        self.graphWidget.setLabel(self.tr('bottom'), x_label, **styles)
        self.layout().addWidget(self.graphWidget)
        self.graphWidget.setBackground('w')

        self.x = list()
        self.y = list()

    def draw_graph(self, parameter_x, parameter_y):
        self.graphWidget.setBackground('w')
        self.graphWidget.plot(parameter_x, parameter_y, pen=pg.mkPen(color=(0, 0, 0)))

    @property
    def x_label(self) -> str:
        return self.graphWidget.plotItem.getAxis(self.tr('bottom')).label()

    @x_label.setter
    def x_label(self, text: str) -> None:
        self.graphWidget.setLabel(self.tr('bottom'), text)

    @property
    def y_label(self) -> str:
        return self.graphWidget.plotItem.getAxis(self.tr('left')).label()

    @y_label.setter
    def y_label(self, text: str) -> None:
        self.graphWidget.plotItem.setLabel(self.tr('left'), text)


class Dialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)

        # Называем окно
        self.setWindowTitle(self.tr("New Windows"))

        self.formGroupBox = QtWidgets.QGroupBox(self.tr("Parameter"))
        layout = QtWidgets.QFormLayout()
        self.X = QtWidgets.QLineEdit(self)
        layout.addRow(self.tr("X:"), self.X)
        self.Y = QtWidgets.QLineEdit(self)
        layout.addRow(self.tr("Y:"), self.Y)
        self.formGroupBox.setLayout(layout)

        self.buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel, self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        # Добавляем buttonBox в layout
        mainLayout.addWidget(self.buttonBox)
        # Устанавливаем layout в QDialog
        self.setLayout(mainLayout)

    @property
    def x_label(self) -> str:
        return self.X.text()

    @x_label.setter
    def x_label(self, text: str) -> None:
        self.X.setText(text)

    @property
    def y_label(self) -> str:
        return self.Y.text()

    @y_label.setter
    def y_label(self, text: str) -> None:
        self.Y.setText(text)


class MyWindows(QtWidgets.QMainWindow):
    num_x = list()
    num_y = list()

    def __init__(self, parent=None):
        super(MyWindows, self).__init__(parent)
        self.mdi = QtWidgets.QMdiArea(self)
        self.setCentralWidget(self.mdi)
        # Имя основного окна
        self.setWindowTitle(self.tr("Function window"))
        # Размер окна задаем здесь
        self.setGeometry(400, 100, 1000, 800)
        self.settings = QSettings('Parameter.ini', QSettings.IniFormat)

        self.quest = QtWidgets.QFileDialog(self)

        # Создаем панели меню
        menu_bar = self.menuBar()
        # Добавляем подменю
        file_menu = menu_bar.addMenu(self.tr('File'))

        # Добавляем подменю свои функции
        new_file = QtGui.QAction(QtGui.QIcon(self.tr('./assets/new.png')), self.tr('New windows'), self)
        open_file = QtGui.QAction(QtGui.QIcon(self.tr('./assets/open.png')), self.tr('Open'), self)
        quit_from_file = QtGui.QAction(QtGui.QIcon(self.tr('./assets/quit.png')), self.tr('Quit'), self)
        # Прописываем что выводит при наведении на иконку
        new_file.setStatusTip(self.tr('Create a new windows'))
        open_file.setStatusTip(self.tr('Open the file'))
        quit_from_file.setStatusTip(self.tr('Close program'))

        # При нажатии New windows вызывается его функция
        new_file.triggered.connect(self.new_windows)
        open_file.triggered.connect(self.open_file)
        quit_from_file.triggered.connect(self.close_file)
        # Отвечает за открытия окошка File
        file_menu.addAction(new_file)
        file_menu.addAction(open_file)
        file_menu.addSeparator()
        file_menu.addAction(quit_from_file)

        # Горячие клавиши
        new_file.setShortcut(QtGui.QKeySequence.StandardKey.New)
        open_file.setShortcut(QtGui.QKeySequence.StandardKey.Open)
        quit_from_file.setShortcut(QtGui.QKeySequence.StandardKey.Quit)

        # status bar
        self.status_bar = self.statusBar()

        self.load_settings()

    def new_windows(self, ):
        # Создать объект Dialog()
        dialog = Dialog(self)
        dialog.x_label = self.tr('x')
        dialog.y_label = self.tr('y')
        # Вызываем созданное нами окно
        if dialog.exec():
            # Окно которое должно потом высветиться
            new: MainGraph = cast(MainGraph, self.mdi.addSubWindow(MainGraph(parent=self.mdi)))
            new.x_label = self.tr('x')
            new.y_label = self.tr('y')

            new.show()

    def open_file(self):
        # Начальный путь
        self.quest.setDirectory(r'C:\images')
        # Какой тип файла мы ищем
        self.quest.setNameFilter("Images (*.csv)")
        # Просмотр файлов
        self.quest.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)
        if self.quest.exec():
            # Помещается выбранный файл
            filenames = self.quest.selectedFiles()
            for filename in filenames:
                file = pandas.read_csv(filename, delimiter=',')
                new: MainGraph = cast(MainGraph, self.mdi.addSubWindow(MainGraph(parent=self.mdi)))
                new.x_label = file.columns[0]
                new.y_label = file.columns[1]
                new.draw_graph([num for num in file.T.iloc[0]], [num for num in file.T.iloc[1]])

                new.show()

    def close_file(self) -> None:
        self.close()

    def load_settings(self):
        self.restoreGeometry(self.settings.value(self.tr('Geometry')))
        self.restoreState(self.settings.value(self.tr('WindowState')))

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.settings.setValue(self.tr('WindowState'), self.saveState())
        self.settings.setValue(self.tr('Geometry'), self.saveGeometry())
        return super().closeEvent(event)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        contextMenu = QtWidgets.QMenu(self)

        newfile = contextMenu.addAction('New')
        copy = contextMenu.addAction('Copy')
        contextMenu.exec(self.mapToGlobal(event.pos()))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    widget = MyWindows()
    widget.show()

    sys.exit(app.exec())
