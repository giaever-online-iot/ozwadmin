#!/usr/bin/env python3

import os, pathlib, subprocess, re
import yaml


from PySide2 import Qt, QtCore, QtWidgets, QtGui

class App(QtWidgets.QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.__env = Environment()
        self.__boot = True if 'boot' in argv else False

    def get_icon(self) -> str:
        return f"{self.__env.get_base()}/gui/ozwadmin.png"

    def get_yaml(self) -> str:
        with open(self.__env.get_yaml()) as yaml_file:
            return yaml.full_load(yaml_file)

    def get_env(self) -> str:
        return self.__env

    def boot(self) -> bool:
        return self.__boot

class Environment(object):
    def __init__(self):
        self.__env = 'snap' if os.getenv('SNAP') is not None else 'local'
        self.__base = f"{os.getenv('SNAP')}/meta" if self.__env == 'snap' else f"{pathlib.Path(__file__).parent.absolute()}/../../../snap"

    def get_yaml(self) -> str:
        return f"{self.__base}/{'snap' if self.__base.endswith('meta') else 'snapcraft'}.yaml"

    def get_base(self) -> str:
        return self.__base

    def is_connected(self, plug, provider) -> bool:

        if self.__env != "snap":
            op = subprocess.check_output(['snap', 'connections', 'ozwadmin'], encoding="UTF-8")
            regex = r"ozwadmin\:" + plug + r"\s+" + (provider if provider is not None else '' ) + r"\:" + plug
            return True if re.search(regex, op) else False

        p = subprocess.run(['snapctl', 'is-connected', plug], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.returncode == 0
