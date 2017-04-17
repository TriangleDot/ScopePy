import simpleQt as sqt
import os
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class fileBrowseLine(sqt.frame):
    def __init__(self,panel,fname = os.path.expanduser('~'),filters=[],dirmode=False):
        super(fileBrowseLine,self).__init__(panel)
        self.edit = sqt.entry(self)
        self.dirmode = dirmode
        self.filters = filters
        self.edit.setText(fname)
        self.browse = sqt.button(self,'Browse [b]')
        self.browse.bindClicked(self.openfile)
        self.browse.setShortcut('b')
        self.position([[self.edit,self.browse]])

    def openfile(self):
        if not self.dirmode:
            fname = QFileDialog.getOpenFileName(self,'Browse Files',self.edit.text,';;'.join(self.filters))
        else:
             fname = QFileDialog.getExistingDirectory(self,'Browse Directories',self.edit.text)
        if fname != '':
            self.edit.setText(fname)
            self.emit(SIGNAL('FilenameChanged'),self.filename)

    

    @property
    def filename(self):
        return self.edit.text

    @filename.setter
    def setFilename(self,fname):
        self.edit.setText(fname)

class addChannel(sqt.frame):
    '''
options:
    channelname: channel name
    xaxis: X Axis Label
    yaxis: Y Axis Label
    creator: Create Channel Function,
        takes arguments (channelname,xaxis,yaxis)
    '''
    
    def __init__(self,panel,**options):
        super(addChannel,self).__init__(panel)
        self.panel = panel
        self.chname = options.get('channelname','New Channel')
        self.xaxis = options.get('xaxis','X Axis')
        self.creator = options.get('creator',print)

        self.yaxis = options.get('yaxis','Y Axis')
        self.name = sqt.entry(self)
        self.name.setText(self.chname)

        self.x = sqt.entry(self)
        self.x.setText(self.xaxis)

        self.y = sqt.entry(self)
        self.y.setText(self.yaxis)
        b = sqt.button(self,'Make Channel!')
        b.bindClicked(self.onClick)
        self.position([
            [sqt.label(self,'Channel Name:'),self.name],
            [sqt.label(self,'X Axis Label:'),self.x],
            [sqt.label(self,'Y Axis Label:'),self.y],
            [sqt.empty(),b]],
             )

    def onClick(self):
         x = self.x.text
         y = self.y.text
         name = self.name.text
         self.creator(name,x,y)
    @property
    def values(self):
        x = self.x.text
        y = self.y.text
        name = self.name.text
        return name,x,y
    def __setitem__(self,value,item):
        if value == 'xaxis':
            self.xaxis = item
            self.x.setText(item)

        elif value == 'yaxis':
            self.yaxis = item
            self.y.setText(item)

        elif value == 'channelname':
            self.chname = item
            self.name.setText(item)

        else:
            raise ValueError('Invalid Argument %s: Must be xaxis, yaxis, or channelname' % value)
    def __getitem__(self,value):
        v = self.values
        if value == 'xaxis':
            return v[1]
        elif value == 'yaxis':
            return v[2]
        elif value == 'channelname':
            return v[0]
        else:
            raise ValueError('Invalid Argument %s: Must be xaxis, yaxis, or channelname' % value)

    def __repr__(self):
        v = self.values
        xt = ''
        xt += '''<moreSqt.addChannel frame with values:
Channel Name: %s
X Axis Label: %s
Y Axis Label: %s
>
''' % v
        return xt
        
             
#import simpleQt as sqt
#from moreSqt import fileBrowseLine
class PrefBox(sqt.frame):
    def __init__(self,parent,paths=[],dirmode=True):
        self.selected = None
        super(PrefBox,self).__init__(parent)
        self.fnameline = fileBrowseLine(self,dirmode=dirmode)
        mainframe = sqt.frame(self)
        self.listbox = QListWidget(self)
        self.listbox.addItems(paths)
        self.connect(self.listbox,SIGNAL('currentTextChanged (const QString&)'),self.setSelected)
        buttonframe = sqt.frame(self)
        a = sqt.button(buttonframe,'Add [a]')
        a.setShortcut('a')
        d = sqt.button(buttonframe,'Delete [d]')
        d.setShortcut('d')
        #b = sqt.button(buttonframe,'Add')
        d.bindClicked(self.delete)
        a.bindClicked(self.add)
        buttonframe.position([[a],[d]])
        mainframe.position([[self.listbox,buttonframe]])
        self.position([[self.fnameline],[mainframe]])
        
        
        

    def delete(self):
        #ItemSelect = list(self.ListDialog.ContentList.selectedItems())
        for SelectedItem in self.listbox.selectedItems():
            self.listbox.takeItem(self.listbox.row(SelectedItem))
    def add(self):
        
        self.listbox.addItem(self.fnameline.filename)

    def setSelected(self,selected):
        self.selected = selected

    @property
    def path(self):
        itemsTextList =  [str(self.listbox.item(i).text()) for i in range(self.listbox.count())]
        return itemsTextList



    
        

    
             
        

if __name__ == '__main__':
    app = QApplication([])
    w = QWidget()
    f = PrefBox(w)
    #print(f['channelname'])
    #f['xaxis'] = 'XAX'
    #print(f)
    
    grid = QVBoxLayout(w)
    grid.addWidget(f)
    w.setLayout(grid)
    w.show()
    app.exec_()
    print(f.path)

