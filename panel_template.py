import ScopePy_panels as panels
import simpleQt as sqt
from qt_imports import *

class Panel(sqt.SimpleBase):
    def drawPanel(self):
        pass
__panels__ ={'<panel name>':panels.PanelFlags(Panel)}
