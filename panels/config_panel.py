import ScopePy_panels as panel
from PyQt4.QtGui import *
import simpleQt as sqt

class configs(panel.PanelBase):
    def drawPanel(self,*args):
        print(args)
        if not args:
            
            self.conf = self.API.conf
        else:
            try:
                self.conf = {}
                for i in args:
                    self.conf[i] = self.API.conf[i]
            except Exception as ec:
                w = sqt.frame(self)
                w.position([[sqt.label(self,'<font color=#ff0000>Error in config %s - \n %s:\n %s</font>' % (i,ec.__class__.__name__,ec))]])
                w.onSave = lambda : None 
                self.conf = {'error':w}
        self.tabs = QTabWidget()
        #self.tabs.show()
        self.button = QPushButton('Save')
        self.button.clicked.connect(self.save)
        l = QVBoxLayout(self)
        l.addWidget(self.button)
        l.addWidget(self.tabs)
        
        self.widgets = {}
        for i in self.conf.keys():
            try:
                w = self.conf[i](self.API)
            except Exception as ec:
                w = sqt.frame(self)
                w.position([[sqt.label(self,'<font color=#ff0000>Error in config %s - \n %s:\n %s</font>' % (i,ec.__class__.__name__,ec))]])
                w.onSave = lambda : None 
            
            print(i)
            print(w)
            print(self.conf[i])
            #w.show()
            self.tabs.addTab(w,i)
            #self.tabs.addTab(w,i)
            self.widgets[i] = w

        self.setLayout(l)
        #self.tabs.show()
        

        

    def save(self):
        for i in self.widgets:
            self.widgets[i].onSave()


__panels__ = {'Config Viewer':panel.PanelFlags(configs,open_on_startup=False,location='main_area')}
