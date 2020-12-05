#!/usr/bin/env python3

import worker
from PySide2 import QtCore, QtWidgets, QtGui

class MainWindow(QtWidgets.QWidget):
    def __init__(self, app):
        super().__init__()

        self.app = app

        self.setGeometry(500, 400, 500, 400)

        self.setWindowModified(True)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowIcon(QtGui.QIcon(app.get_icon()))

        qRect = self.frameGeometry()
        qRect.moveCenter(QtWidgets.QDesktopWidget().availableGeometry().center())
        self.move(qRect.topLeft())

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        img = QtGui.QPixmap(app.get_icon())
        logo = QtWidgets.QLabel(self)
        logo.setPixmap(img)
        logo.setAlignment(QtCore.Qt.AlignBaseline| QtCore.Qt.AlignCenter)
        layout.addWidget(logo, 1, QtCore.Qt.AlignBaseline| QtCore.Qt.AlignCenter)

        title = QtWidgets.QLabel(self)
        title.setText("OZW Admin")
        title.setFont(QtGui.QFont("Times", 28, QtGui.QFont.Bold))
        layout.addWidget(title, 0, QtCore.Qt.AlignBaseline| QtCore.Qt.AlignCenter)


        self.header = QtWidgets.QLabel(self)
        self.header.setText("Checking plugs")
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.header, 0, QtCore.Qt.AlignBaseline| QtCore.Qt.AlignCenter)

        self.desc = QtWidgets.QLabel(self)
        self.desc.setText('...')
        self.desc.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.desc, 0, QtCore.Qt.AlignBaseline| QtCore.Qt.AlignCenter)

        self.pgbar = QtWidgets.QProgressBar(self)
        layout.addWidget(self.pgbar)

        self.plugs = []
        self.pgval = 0

        self.pw = worker.PlugsWorker(self)
        self.exit_code = 0

    def close(self):
        return super().close()

    def quit(self):
        self.pw.stop()
        self.close()
        self.app.exit(self.exit_code)

    def updateExitCode(self, code):
        if code in [0, 255, 256]:
            self.exit_code = code

    def showEvent(self, event):
        super().showEvent(event)
        self.pw.run()

    def updateFinised(self):
        if self.exit_code != 0:
            self.header.setText(f'{self.header.text()} - A manual restart is required!')
            self.desc.setText("Exit and launch OZWAdmin again.")

            self.layout().removeWidget(self.pgbar)
            self.pgbar.deleteLater()

            button = QtWidgets.QPushButton("Exit")
            button.clicked.connect(self.quit)
            self.layout().addWidget(button)

        else:
            self.quit()

    def updateProgress(self):
        self.pgval = (self.pgval + 1)
        self.pgbar.setValue(self.pgval)

    def updateText(self, header, desc):
        self.header.setText(header)
        self.desc.setText(desc)

    def get_plugs(self):
        if len(self.plugs) != 0:
            return self.plugs

        yaml = self.app.get_yaml()
        for app_data in yaml['apps'].values():
            for plug in app_data['plugs']:
                provider = None
                for xplug, values in yaml['plugs'].items():
                    if xplug != plug:
                        continue
                    provider = values['default-provider']
                    break
                self.plugs.append({'provider': provider, 'name': plug})

        self.pgbar.setRange(0,len(self.plugs))

        return self.plugs

