'''
Config for other stuff which are not panels
'''
from ScopePy_config import ConfigBase, colorpicker,DataStorage
import simpleQt as sqt
from moreSqt import PrefBox

class SetLog(ConfigBase):
    def drawPanel(self):
        frame = sqt.frame(self)
        label = sqt.label(self,'Turn Loging on Log on/off')
        self.slide = sqt.QSlider(sqt.Qt.Horizontal,self)
        self.slide.setMinimum(0)
        self.th = 0
        self.slide.setMaximum(1)
        if self.API._gui.onLog == True:
            self.slide.setValue(1)
        else:
            self.slide.setValue(0)
        self.connect(self.slide,sqt.SIGNAL("valueChanged(int)"),self.setcolor)

        frame.position([[label],[self.slide]])
        
        a = DataStorage()
        a['Where'] = frame
        self.setupTabs(a)

    def setcolor(self,i):
        self.th = i
    def onSave(self):
        if self.th == 1:
            self.API._gui.onLog = True
        else:
            self.API._gui.onLog = False



#
PREFS = ['script','panel','transformer',
         'mathFunction','dataSource']
class Prefs(ConfigBase):
    def drawPanel(self):
        self.prefs = self.API.preferences
        
        self.d = DataStorage()
        for i in PREFS:
            a = PrefBox(self,paths=self.prefs.__dict__[i+'Paths'])
            a.name = i
            self.d[i]=a
        self.setupTabs(self.d)

    def onSave(self):
        for i in self.d.keys():
            f = self.d[i]
            self.API.preferences.__dict__[f.name+'Paths'] = f.path
            self.API.preferences.save()
            

__config__ = {'Preferences':Prefs}
