import ScopePy_panels as panels
import simpleQt as sqt
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSvg import *
import os
def getext(filename):
    return filename.split('.')[1]
class NotesClient(object):
    
    def __init__(self,API,note_name):
        self.panel = API.panelID(note_name)
        self.API = API
        

    def sendList(self,listofstr,list_type='o'):
        """
list_type: o = Numbered List
    u = Bulletin :ist
    """
        
        tosend = '<%sl>' % list_type
        for i in listofstr:
            tosend += '<li>%s</li>' % i
        tosend += '</%sl>' % list_type
        self.send(tosend)
    def senditalics(self,text):
        self.send('<em>%s</em>' % text)

    def sendbold(self,text):
        self.send('<b>%s</b>' % text)

    def sendunderlined(self,text):
        self.send('<u>%s</u>' % text)

    def sendstrike(self,text):
        self.send('<strike>%s</strike>' % text)

    def italics(self,text):
        return '<em>%s</em>' % text

    def bold(self,text):
        return '<b>%s</b>' % text

    def underlined(self,text):
        return '<u>%s</u>' % text

    def strike(self,text):
        return '<strike>%s</strike>' % text

    def subscript(self,text):
        return '<sub>%s</sub>' % text

    def sendsubscript(self,text):
        self.send('<sub>%s</sub>' % text)

    def superscript(self,text):
        return '<sup>%s</sup>' % text

    def sendsuperscript(self,text):
        self.send('<sup>%s</sup>' % text)

    def sendcolor(self,text,color):
        self.send('<font color="%(color)s">%(message)s</font>' % {'color':color,'message':text})

    
        
        

    def send(self,text,atend=''):
        self.API.sendComms('NotesAPIText',self.panel,text+atend)

    def save(self,filename):
        self.API.sendComms('NotesAPISave',self.panel,filename)

    def load(self,filename):
        self.API.sendComms('NotesAPILoad',self.panel,filename)
        
class Panel(sqt.SimpleBase):
    def drawPanel(self):
        self.isSaveable = True
        self.notebox = sqt.Textarea(self)
        self.position([[self.notebox]])
        #self.italic = False
        #self.underline = False
        self.text = self.notebox.widget
        self.figure = 0
        self.addCommsAction('NotesAPIText',self.handleInsert)
        self.addCommsAction('NotesAPISave',self.baseSave)
        self.addCommsAction('NotesAPILoad',self.baseLoad)
        self.addKeyboardShortcuts([['Save','Ctrl+S',self.save],['Open','Ctrl+O',self.openFile]])

    def handleInsert(self,text):
        self.text.insertHtml(text)
    
    
    def saveData(self):
        print('Saving Data')
        data = self.standardSaveData
        data['text'] = self.notebox.html
        return data
    def restoreData(self,panel_data):
        self.notebox.widget.setHtml(panel_data['text'])

##    def bold(self):
##        pass
##    def setitalic(self):
##        self.italic = not self.italic
##        self.notebox.widget.setFontItalic(self.italic)
##    def setunderline(self):
##        self.underline = not self.underline
##        self.notebox.widget.setFontUnderline(self.underline)

    def bold(self):

        if self.text.fontWeight() == QFont.Bold:

            self.text.setFontWeight(QFont.Normal)

        else:

            self.text.setFontWeight(QFont.Bold)

    def italic(self):

        state = self.text.fontItalic()

        self.text.setFontItalic(not state)

    def underline(self):

        state = self.text.fontUnderline()

        self.text.setFontUnderline(not state)

    def strike(self):

        # Grab the text's format
        fmt = self.text.currentCharFormat()

        # Set the fontStrikeOut property to its opposite
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())

        # And set the next char format
        self.text.setCurrentCharFormat(fmt)

    def superScript(self):

        # Grab the current format
        fmt = self.text.currentCharFormat()

        # And get the vertical alignment property
        align = fmt.verticalAlignment()

        # Toggle the state
        if align == QTextCharFormat.AlignNormal:

            fmt.setVerticalAlignment(QTextCharFormat.AlignSuperScript)

        else:

            fmt.setVerticalAlignment(QTextCharFormat.AlignNormal)

        # Set the new format
        self.text.setCurrentCharFormat(fmt)

    def subScript(self):

        # Grab the current format
        fmt = self.text.currentCharFormat()

        # And get the vertical alignment property
        align = fmt.verticalAlignment()

        # Toggle the state
        if align == QTextCharFormat.AlignNormal:

            fmt.setVerticalAlignment(QTextCharFormat.AlignSubScript)

        else:

            fmt.setVerticalAlignment(QTextCharFormat.AlignNormal)

        # Set the new format
        self.text.setCurrentCharFormat(fmt)

    def bulletList(self):

        cursor = self.text.textCursor()

        # Insert bulleted list
        cursor.insertList(QTextListFormat.ListDisc)

    def numberList(self):

        cursor = self.text.textCursor()

        # Insert list with numbers
        cursor.insertList(QTextListFormat.ListDecimal)

    def setFkeys(self):
        self.Fkeys = [
                     ['F4','Italics',self.italic],
                     
                     ['F6','Underline',self.underline],
                     
                     ['F5','Numbered List',self.numberList],
                     ['F8','Super Script',self.superScript],
                     ['F9','Sub Script',self.subScript],
                     ['F10','Bullet List',self.bulletList],
                     ]
    def setShiftFkeys(self):
        self.ShiftFkeys = [
            ['Shift+F7','Bold',self.bold],
            ['Shift+F6','Strike',self.strike],
            ['Shift+F4','Open',self.openFile],
            ['Shift+F8','Save',self.save],
            ['Shift+F9','Insert Plot',self.getplot]
            ]
    def save(self):
        #print( ';;'.join(['Notes/HTML files (*.note,*.html)','Test File (*.*)']))
        filename =QFileDialog.getSaveFileName(self,'Save File',os.path.join(self.API.filePath,'UntitledNote.note'),
                                                        ';;'.join(['Notes/HTML files (*.note *.html)','Test File (*.*)']))
        
        worked = filename != ''
        if worked:
            self.baseSave(filename)

    def baseSave(self,filename):
            ext = getext(filename)
            #print(ext)
            if ext == 'note' or ext == 'html':
                with open(filename,'w') as f:
                    f.write(self.text.toHtml())
            else:
                with open(filename,'w') as f:
                    f.write(self.text.toPlainText())

    def openFile(self):
            
        filename = QFileDialog.getOpenFileName(self,'Open File',os.path.join(self.API.filePath,'UntitledNote.note'),
                                       ';;'.join(['Notes/HTML files (*.note *.html)','Test File (*.*)']))

        worked = filename != ''
        #print( ';;'.join(['Notes/HTML files (*.note,*.html)','Test File (*.*)']))
        if worked:
            self.baseLoad(filename)

    def baseLoad(self,filename):
            ext = getext(filename)
            #print(ext)
            with open(filename,'r') as f:
                txt = f.read()
            
            if ext == 'note' or ext == 'html':
                self.text.setHtml(txt)
            else:
                self.text.setText(txt)
                

    def getplot(self):
        panels = self.API.getAllPanels(False)
        plots = []
        for i in panels:
            for n in i:
                if n.startswith('Plot '):
                    plots.append(n)
        d = viewList(plots)
        if d.exec_():
            selected = d.selected
            s = selected[0]
            self.plottosvg(self.API.getPanel(s).plot.scene)
                      
        
        
    def plottosvg(self,plotscene):
##    QSvgGenerator svgGen;
##
##svgGen.setFileName( "/home/nikolay/scene2svg.svg" );
##svgGen.setSize(QSize(200, 200));
##svgGen.setViewBox(QRect(0, 0, 200, 200));
##svgGen.setTitle(tr("SVG Generator Example Drawing"));
##svgGen.setDescription(tr("An SVG drawing created by the SVG Generator "
##                            "Example provided with Qt."));
##
##QPainter painter( &svgGen );
##scene.render( &painter );
        SCENESIZE = 500
        svgGen = QSvgGenerator()
        #svgGen.setViewBox(QRect(-SCENESIZE/2, -SCENESIZE/2, SCENESIZE, SCENESIZE))
        svgGen.setSize(QSize(500/2,500/2))
        svgGen.setTitle('Figure %i' % self.figure)
        svgGen.setDescription('A ScopePy Plot Transported to SVG.')
        svgGen.setFileName(os.path.join(os.path.expanduser('~'),'.ScopePy','tmp.svg'))
        painter = QPainter(svgGen)
        plotscene.render(painter)
        self.figure += 1
        painter.end()
        cursor = self.text.textCursor()
        cursor.insertImage(os.path.join(os.path.expanduser('~'),'.ScopePy','tmp.svg'))
class viewList(QDialog):
    def __init__(self,items=[]):
        super(viewList, self).__init__()
        layout = QVBoxLayout(self)
        ok = QPushButton('Ok',self)
        ok.clicked.connect(self.ok)
        
        cancel = QPushButton('Cancel',self)
        cancel.clicked.connect(self.cancel)
        self.list = QListWidget(self)
        layout.addWidget(self.list)
        layout.addWidget(ok)
        layout.addWidget(cancel)
        self.setLayout(layout)
        self.list.addItems(items)
        #self.show()
        

    
        

    def ok(self):
        selection = self.list.selectedItems()
        self.selected = [i.text() for i in selection]
        self.accept()
        
    def cancel(self):
        self.reject()
        
__panels__ ={'Notes':panels.PanelFlags(Panel)}
