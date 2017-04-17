'''
<svg width="120" height="100">
<rect x="20" y="0" width="100" height="100" stroke=#ffa02f stroke-width="2" fill=#207700 />
  <text x="20" y="70" font-size="80" fill=#000000>Qt</text>
 <text x="0" y="70" font-size="80" fill=#207700 stroke=#ffa02f>S</text>
 <text x="40" y="100" font-size="25" fill=#207700 stroke=#ffa02f>imple</text>
</svg>
simpleQt: simple panel making for ScopePy:
widgets:
    label
    button
    entry
    textarea
    graph
    combobox
    MiniConsole
    table?
positioners:
    frame
    SimpleBase
'''

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import ScopePy_graphs as spg 
import ScopePy_panels as panel
from ScopePy_graphs import GraphWidget
from ScopePy_channel import ScopePyChannel,plotLineStyle

## [label]
class label:
    def __init__(self,frame,name):
        self.widget = QLabel(name)
        #frame.grid.addWidget(self.widget,row,col)

## [frame]
class frame(QFrame):
    def __init__(self,panel):
        super(frame, self).__init__()
        self.grid = QGridLayout(self)
        self.setLayout(self.grid)
        self.panel = panel
        
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setLineWidth(3)
        
    def position(self,lol):
        '''
        lol: List of lists of widgets
        '''
        c = 0
        for i in lol:
            nc = 0
            for ni in i:
                try:
                    self.grid.addWidget(ni.widget,c,nc)
                except AttributeError:
                    self.grid.addWidget(ni,c,nc)
                    
                nc += 1
            c += 1
        

        
#panel.PanelBase.initialise
class SimpleBase(panel.PanelBase):
    def initialise(self):
        self.grid = QGridLayout(self)
        self.setLayout(self.grid)
        self.init()

    def init(self):
        pass
    def position(self,lol):
        '''
        lol: List of lists of widgets or frames
        '''
        c = 0
        for i in lol:
            nc = 0
            for ni in i:
                try:
                    self.grid.addWidget(ni.widget,c,nc)
                except AttributeError:
                    self.grid.addWidget(ni,c,nc)
                    
                nc += 1
            c += 1
            
def empty():
    """
    Inserts an empty space.
    Example:
    what you want:
    label button
          button
          button
    to make that  you would use:
    [[label,button],[empty(),button],[empty(),button]]
    """
    return QWidget()
## [button]
class button:
    """
the simple button Widget!
args:
    frame = frame (self)
    row: row on grid layout
    col: column on grid layout
    name: text on button
Bindings:
    bindClicked(function) > runs function when button pressed
This is part of ScopePy
    """
    def __init__(self,frame,name):
        self.widget = QPushButton(name)
        self.button = self.widget
        #frame.grid.addWidget(self.button,row,col)
        self.panel = frame

    def bindClicked(self,function):
        self.button.clicked.connect(function)
        
    def disable(self):
        self.button.setDisabled(True)
        
    def enable(self):
        self.button.setEnabled(True)

    def setShortcut(self,cut):
        self.widget.setShortcut(QKeySequence(cut))



## [entry]
class entry:
    """
the one line entry Widget!
args:
    frame = frame (self)
    row: row on grid layout
    col: column on grid layout

Bindings:
    bindReturn(function) > runs when return pressed > gives your function the arg text.
    bindChanged(function) > runs when text changed > gives your function the arg text.
"""
    def __init__(self,frame,onlyInt=False,onlyFloat=False):
        self.line = QLineEdit()
        self.widget = self.line
        
        float_regex = QRegExp(r"[\.0-9\-\+e\*\/]+")
        float_validator = QRegExpValidator(float_regex)
        
        int_regex = QRegExp(r"[0-9]+")
        int_validator = QRegExpValidator(int_regex)
        #frame.grid.addWidget(self.line,row,col)
        if onlyFloat:
            self.line.setValidator(float_validator)
        if onlyInt:
            self.line.setValidator(int_validator)
        self.panel = frame

    def bindReturn(self,function):
        self.panel.connect(self.line,SIGNAL('returnPressed()'),self.returnfunc)
        self.rf = function

    def returnfunc(self):
        self.rf(self.line.text())

    def bindChanged(self,function):
        self.panel.connect(self.line,SIGNAL('textChanged(str)'),function)

    def setText(self,text):
        self.line.setText(text)

    @property
    def text(self):
        return self.line.text()


## [textarea]
import numpy as np
def lists_to_array(x_data,y_data,x_label,y_label):
    nData = len(x_data)
    data_array = np.zeros(nData,dtype=[(x_label,float),(y_label,float)])
        
        
    data_array[x_label] = np.array(x_data)
    data_array[y_label] = np.array(y_data)
    return data_array
class Textarea:
    """
    the multi line Text Area Widget!
    Args:
        frame = frame (self)
        row: row on grid layout
        col: column on grid layout

    Bindings:
        bindChanged(function) > runs when text changed > gives your function the arg text.
    """
    def __init__(self,frame):
        self.line = QTextEdit()
        self.widget = self.line
        #frame.grid.addWidget(self.line,row,col)
        self.panel = frame

    def  bindChanged(self,function):
        self.panel.connect(self.line,SIGNAL('textChanged(str)'),function)

    def setText(self,text):
        self.line.setText(text)

    

    @property
    def text(self):
        return self.line.toPlainText()

    @property
    def html(self):
        return self.line.toHtml()



## [Graph]

class graph:
    def __init__(self,frame,linecolor='#ff00ff',fillcolor='#00ff00',marker='',channelname='Firstchannel'):
        try:
            self.graph = spg.GraphWidget(frame.panel.preferences)
        except:
            self.graph = spg.GraphWidget(frame.preferences)
        self.widget = self.graph
        #frame.grid.addWidget(self.graph,row,col)
        self.frame = frame
        self.channel = {}
        self.addChannel(channelname,linecolor,fillcolor,marker)
        
    def addChannel(self,name,linecolor='#ff00ff',fillcolor='#00ff00',marker=''):
        linestyle = plotLineStyle(lineColour=linecolor,marker=marker,markerFillColour=fillcolor)
        self.channel[name] = ScopePyChannel("channel",linestyle)
        self.graph.addChannel(self.channel[name],chunkMode='latest')
        self.widget.update()
        
    def addData(self,name: str,datainarray: np.array):
        self.channel[name].addData2Channel(datainarray)
        self.widget.update()
        


## combo box
class combobox:
    def __init__(self,frame):
        self.widget = QComboBox(frame)
        self.frame = frame
        
    def addItem(self,item):
        self.widget.addItem(item)

    def addItems(self,items):
        self.widget.addItems(items)

    def clear(self):
        self.widget.clear()
        
    def insertSpace(self,index):
        self.widget.insertSeparator(index)
        
    @property
    def currentIndex(self):
        return self.widget.currentIndex()
        
    @currentIndex.setter
    def currentIndex(self,index):
        self.widget.setCurrentIndex(index)
        
    @property
    def currentText(self):
        #print(self.widget.currentText())
        return self.widget.currentText()
        
    @currentText.setter
    def currentText(self,value):
        items = self.items
        
        if value in items:
            self.currentIndex = items.index(value)
            
            
    def removeItem(self,index):
        self.widget.removeItem(index)
    
    @property
    def count(self):
        return self.widget.count()
        
    @property
    def items(self):
        """
        Return list of the text of all the items in the Combo box
        """
        return [self.widget.itemText(ind) for ind in range(self.count)]
        
    def bindChanged(self,command):
        self.frame.connect(self.widget,SIGNAL('currentIndexChanged(int)'),command)
        
    def bindTextChanged(self,command):
        self.frame.connect(self.widget,SIGNAL('currentIndexChanged(str)'),command)
        
        
    
## Mini Console
class MiniConsole(QWidget):
    def __init__(self,commands={}):
        QWidget.__init__(self)
        self.commands = commands
        self.commands['echo'] = self.echo
        #.args = args

        self.completer = QCompleter(list(self.commands.keys()))
        self.edit = QLineEdit()
        self.edit.setCompleter(self.completer)
        l = QVBoxLayout(self)
        self.label = QTextEdit()
        self.label.setReadOnly(True)
        l.addWidget(self.edit)
        l.addWidget(self.label)
        self.setLayout(l)
        self.edit.keyPressEvent = self.press
        self.history = []
        self.hnum = 0
        self._locals={}
        
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,
                                       QSizePolicy.Maximum))
        
        

    def echo(self,item):
        return str(item)

    def _check(self,txt):
        self.history.append(txt)
        if txt.startswith('$'):
            
            a,b = txt.split('=')
            if b.startswith('%'):
                b = b.replace('%','')
                b=float(b)
            self._locals[a]=b
            self.edit.clear()
            return
        try:
            command, args = txt.split('(')
            try:
                self.commands[command]
            except:
                self.label.setText('<font color=#ff0000>No Function named %s</font>' % command)
            args=args.replace(')','')
            argl = args.split(',')
            rrgs = []
            
            for i in argl:
                if i.startswith('$'):
                    rrgs.append(self._locals[i])
                elif i.startswith('%'):
                    i = i.replace('%','')
                    rrgs.append(float(i))
                else:
                    rrgs.append(i)
            
                            
            try:
                c = self.commands[command]
                try:
                    msg = c(*rrgs)
                    if type(msg) == tuple:
                        rmsg = str(msg[0])
                        self._locals[msg[1]]=msg[2]
                    else:
                        rmsg = str(msg)
                    self.label.setText('%s' % rmsg)
                except Exception as ec:
                    self.label.setText('<font color=#ff0000>Error: %s</font>' % ec)
            except:
                self.label.setText('<font color=#ff0000>No Function named %s</font>' % command)
        except:
            self.label.setText('<font color=#ff0000>Inproper syntax</font>')

        self.edit.clear()

    

        

    def press(self,event):
        
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self._check(self.edit.text())
            self.hnum = 0
            return
        if event.key() == Qt.Key_Up:
            self.setHistory()
            return

        QLineEdit.keyPressEvent(self.edit,event)

    def setHistory(self):
        try:
            self.edit.setText(self.history[self.hnum])
            self.hnum += 1
        except Exception as ec:
            print(ec)
            self.hnum = 0
            
            
    def sizeHint(self):
        """
        Set the minimum size
        
        """
        
        return QSize(7*70,14*8)

    
## Table Viewer
class TableBase(object):
    '''
A base helper-class for TabelArray
'''
    def __init__(self,lol=None):
        self.rows = []
        self.cols = []
        if lol != None:
            self._data = lol
            self.setData(self._data)
        else:
            self._data = [[]]
            self.rows = []
            self.cols = []

        

    def setData(self,lol):
        self._data = lol
        self.rows = []
        self.cols = []
        for e, i in enumerate(self._data):
                self.rows.append(i)

        for e,i in enumerate(self.rows[0]):
           
                
            
            c = []
            for i in self.rows:
                c.append(i[e])
            self.cols.append(c)

            #self.cols.append(col)

    def addCol(self,items=0):
        
        self.cols.append(items)
        for e, i in enumerate(self.rows):
            i.append(items[e])

    def addRow(self,items):
        self.rows.append(items)
        for e, i in enumerate(self.cols):
            i.append(items[e])
            

   
    def getCell(self,row,col):
        return self.rows[row][col]
    def setCell(self,row,col,value):
        self.rows[row].insert(col,value)
        self.cols[row].insert(row,value)

    

        
            



import data_sources.data_source_base_library as DS
class TableArray(DS.BaseDatasetTableWrapper):
    """
    Wrapper for HDF5/numpy array datasets when sending to the TableEditor
    
    Makes standard functions for accessing rows and columns, inserting, 
    deleting
    
    """
    
    def __init__(self,lol):
        """
        Create wrapper with the HDF5/numpy array
        
        Inputs
        ---------
        array : HDF5/numpy array
            e.g. Meas['Data/Measurement/dataset1']
        
        """
        
        
       
        
        # Store array
        self.array = TableBase(lol)
        
        # Read only flag - for completness with other wrappers
        # - prevents insertions and deletions
        self.readOnly = False
        
        

            
        
    def rowCount(self):
        return len(self.array.rows)
        
        
    def columnCount(self):
       return len(self.array.cols)
        
            
        
    def cell(self,row,col):
        """
        Return contents of array element given row and column
        
        """
        
        # TODO : filter infs and NaNs
        
        return self.array.getCell(row,col)
        
        
    def setCell(self,row,col,value):
        """
        Set contents of array element given row and column
        
        """
        
        self.array.setCell(row,col,value)
            
            
    
    def insertRows(self,position,rows=1):
        """
        Insert a set of new rows, set to zero
        
        Inputs
        ---------
        position : int
            row index where new rows will be inserted
            
        rows : int
            Number of rows to be inserted
            
        """
        self.array.addRow()
        
        
        
    def removeRows(self,position,rows=1):
        """
        Remove a set of rows
        
        Inputs
        ---------
        position : int
            row index where rows will be removed
            
        rows : int
            Number of rows to be deleted
            
        """
        
        print('Not Implimented Yet')
        #self.array = np.delete(self.array,rows2delete)
                
    
        
        
    def columnHeaders(self):
        """
        Return the names of the columns
        
        For recarrays this is the dtype.names field for normal arrays this
        returns a list of numbers converted to strings
        
        """
        
        return list(range(len(self.array.cols)))
            
            
            
    def getColumn(self,column_index):
        """
        Return a whole column as one numpy array
        
        """
        
        return np.array(self.array.cols[column_index])
    def columnFormat(self,col):
        return '%s'
        
import widgets.table_editor_lib as te   
class  Table:
    def __init__(self,frame,tbarray):
        self.frame = frame
        self.widget = te.TableEditorWidget()
        self.widget.setModel(te.TableEditorModel(tbarray))

    def setData(self,tbarray):
        self.widget.setModel(te.TableEditorModel(tbarray))

    def getSelection(self):
        '''
Returns a TableBase of the selection
'''
        
        l = self.widget.getStrSelection()
        nl = []
        for i in l:
            nl.append([i[0],i[1]])

        return TableBase(nl)
            

## Toggle Button
OFF = 'color: #00b599;'
ON = 'color: red;'

   
class ToggleButton(object):
    def __init__(self,parent,txt,state=False):
        self.widget = QPushButton(txt,parent)
        self.widget.setCheckable(True)
        self.panel = parent
        self.txt = txt
        self.state = state
        self.command = None
        self.txtdict = {True:None,
                        False:None}
        self.setState(state)
        
        self.widget.toggled.connect(self.onClick)
        

    def setButtonText(self,txt):
        self.txt = txt
        self.widget.setText(self.txt)

    def setButtonTextForState(self,txt,state):
        '''
        change text on button when state becomes argument "state"
        if txt is None, the text won't change when the state is changed.
        '''
        self.txtdict[state] = txt

    def setState(self,state):
        '''
        state: bool
            True is down, False is up
            '''
        if state:
            s = ON
            self.widget.setDown(True)
        else:
            s = OFF
            self.widget.setDown(False)
        
        self.widget.setStyleSheet(s)
        self.state = state
        if self.txtdict[state] != None:
            self.widget.setText(self.txtdict[state])
            
        if self.command:
            self.command(self.state)

    def onClick(self,pressed):
        if pressed:
            #print('%i was pressed!' % pin)
            #print('Is it an out: %s' % str(t))
            
            self.setState(True)
            
            
        else:
            self.setState(False)

    def bindStateChanged(self,command):
        '''
        command: function or method
            must take 1 argument: state (True=down, False=up)
        '''
        
        self.command = command
    





