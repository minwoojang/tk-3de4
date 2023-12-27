# 3DE4.script.hide: 			true
# 3DE4.script.startup: 			true

import os
import sys
import tde4
#from PySide2 import QtGui, QtCore, QtWidgets
# sys.path.append("O:\\inhouse\\Python\\Python37\\Lib\\site-packages")
# sys.path.append("O:\\inhouse\\rez-packages\\PySide\\1.2.4\\platform-windows\\arch-AMD64\\python")
if tde4.get3DEVersion().split()[-1] > '6':
    # sys.path.append("O:\\inhouse\\rez-packages\\PySide2\\5.12.9\\platform-windows\\arch-AMD64\\site-packages")
    from Qt.QtCore import *
    from Qt.QtGui import *
    from Qt.QtWidgets import *
else:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    

sys.path.append(
    os.path.join(os.getenv('TANK_CURRENT_PC'), 'install', 'core', 'python')
)
import sgtk

def _timer():
    QCoreApplication.processEvents()
    #QtCore.QCoreApplication.processEvents()
    # check for open file change
    global g_current_file
    cur_file = tde4.getProjectPath()
    if g_current_file != cur_file:
        if cur_file:
            engine = sgtk.platform.current_engine()
            context = engine.context
            new_context = engine.sgtk.context_from_path(cur_file, context)
            if new_context != context:
                sgtk.platform.change_context(new_context)
        g_current_file = cur_file

if __name__ == '__main__':
    engine = sgtk.platform.current_engine()
    if not engine:
        from tank_vendor.shotgun_authentication import ShotgunAuthenticator
        user = ShotgunAuthenticator(sgtk.util.CoreDefaultsManager()).get_user()
        sgtk.set_authenticated_user(user)
        context = sgtk.context.deserialize(os.environ.get("TANK_CONTEXT"))
        engine = sgtk.platform.start_engine('tk-3de4', context.sgtk, context)

    # Qt
    if not QCoreApplication.instance():
    #if not QtCore.QCoreApplication.instance():
        QApplication([])
        #QtGui.QApplication([])
        global g_current_file
        g_current_file = tde4.getProjectPath()
        tde4.setTimerCallbackFunction("_timer", 50)
        engine.post_qt_init()

