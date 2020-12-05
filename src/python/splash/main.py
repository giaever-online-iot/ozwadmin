#!/usr/bin/env python3
import sys, app, main_window

def run():
    _app = app.App(sys.argv)
    main = main_window.MainWindow(_app)
    main.show()
    sys.exit(_app.exec_())

if __name__ == '__main__':
    run()
