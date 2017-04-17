import ScopePy_panels as panels
import simpleQt as sqt
from PyQt4.QtGui import *

class Panel(sqt.SimpleBase):
    def drawPanel(self):
        pass
__panels__ ={'<panel name>':panels.PanelFlags(Panel)}
