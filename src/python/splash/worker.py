#!/usr/bin/env python3

import sys, traceback, time
from PySide2 import QtCore

class Worker(QtCore.QRunnable):
    """Worker thread for running background tasks."""

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['progress_callback'] = self.signals.progress

    @QtCore.Slot()
    def run(self):
        try:
            result = self.fn(
                *self.args, **self.kwargs,
            )
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

class WorkerSignals(QtCore.QObject):
    finished = QtCore.Signal()
    error = QtCore.Signal(tuple)
    result = QtCore.Signal(object)
    progress = QtCore.Signal(tuple)

class PlugsWorker(QtCore.QObject):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.pool = QtCore.QThreadPool()
        self.stopped = False
        self.plugs = self.parent.get_plugs()

    def stop(self):
        self.stopped = True
        self.pool.waitForDone()

    def progress(self, state):
        state, plug = state
        if state:
            self.parent.updateProgress()
            self.parent.updateText(
                f'Plug «{plug["name"]}» connected!',
                'Continuing'
            )
        else:
            header = f'Missing plug «{plug["name"]}», please open the terminal and run:'
            if plug['provider'] is None:
                desc = f'$ snap connect ozwadmin:{plug["name"]}'
            else:
                desc = f'$ snap connect ozwadmin:{plug["name"]} {plug["provider"]}:{plug["name"]}'
            self.parent.updateText(header, desc)

    def error(self, err):
        self.stop()
        self.parent.updateText("Error", str(err))
        self.parent.updateExitCode(256)
        return

    def completed(self):
        self.parent.updateText('Plugs connected', "Continuing launch")
        self.parent.updateFinised()
        return

    def run(self):
        worker = Worker(fn=self.test)
        self.pool.start(worker)
        worker.signals.progress.connect(self.progress)
        worker.signals.finished.connect(self.completed)
        return

    def test(self, progress_callback):
        for plug in self.plugs:
            if self.stopped:
                break
            connected = False
            while not connected and not self.stopped:
                connected = self.parent.app.get_env().is_connected(plug['name'], plug['provider'])
                progress_callback.emit((connected, plug))
                if not connected:
                    self.parent.updateExitCode(255)
                    time.sleep(0.5)
        return
