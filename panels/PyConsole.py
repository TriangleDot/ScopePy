import sys, os
import traceback

from qt_extra import QtWebKit
_locals = {}
import sys
from qt_imports import *
#from ScopePy_API import API
from ScopePy_panels import PanelBase, load_panels
from pprint import pprint
import simpleQt as sqt
import csslib
import refclass as rc
from moreSqt import PrefBox
from ScopePy_utilities import DebugPrint,Connection
import threading as th
db = DebugPrint()
def dbg(text):
    db('PyConsole',text)
pb = PanelBase
HORIZ_SIZE = 600
VERT_SIZE = 650
#panels in API.panel_classes format is Ordered Dict

class Browser(pb):

    def drawPanel(self):
        """
            Initialize the browser GUI and connect the events
        """

        #QWidget.__init__(self)
        #self.resize(800,600)
        # = QWidget(self)

        self.mainLayout = QHBoxLayout()




        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.frame.setLineWidth(3)


        self.panels = QComboBox(self.frame)
        self.panels.addItems(list(self.API.panel_classes.keys()))
        self.connect(self.panels,SIGNAL('currentIndexChanged(const QString&)'),self.getDocs)


        self.gridLayout = QVBoxLayout(self.frame)

        #self.resize(150,400)
        self.gridLayout.addWidget(self.panels)
        self.resize(450,400)



        self.horizontalLayout = QHBoxLayout()
        self.tb_url = QLineEdit(self.frame)
        self.label = QLabel('Find:',self.frame)
        #self.bt_ahead = QPushButton(self.frame)


        #self.bt_ahead.setIcon(QIcon().fromTheme("go-next"))
        self.horizontalLayout.addWidget(self.label)
        #self.horizontalLayout.addWidget(self.bt_ahead)
        self.horizontalLayout.addWidget(self.tb_url)
        self.gridLayout.addLayout(self.horizontalLayout)

        #self.html = QtWebKit.QWebView()
        self.html = WebView()
        #self.html.setMinimumWidth(300)
        self.html.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)

        self.gridLayout.addWidget(self.html)
        self.mainLayout.addWidget(self.frame)
        #self.setCentralWidget()

        self.connect(self.tb_url, SIGNAL("returnPressed()"), self.findText)
        #self.connect(self.bt_back, SIGNAL("clicked()"), self.html.back)
        #self.connect(self.bt_ahead, SIGNAL("clicked()"), self.html.forward)

        self.setLayout(self.mainLayout)
        self.addCommsAction('setDocs',self.browse)
        self.addCommsAction('setHtml',self.docs)
        self.browse(None)
        self.show()








    def docs(self,htmlwrapper):
        f = open(os.path.join(os.path.expanduser('~'),'.ScopePy','tmp.html'),'w')
        f.write(htmlwrapper.html)
        f.flush()
        f.close()

        self.html.load(QUrl(os.path.join(os.path.expanduser('~'),'.ScopePy','tmp.html')))



    def getDocs(self,item):
        n = self.API.panel_classes[item]
        d = n.docs
        if d == None:
            self.browse(n.panel_class)
        else:
            w = rc.htmlWrapper(item)
            w.html = d
            self.docs(w)

    def browse(self,fomoc=None):
        """
            Show help for specific function, class, or module
        """
        import refclass as rc
        import inspect
        if hasattr(fomoc,'__viewhelp__'):
            fomoc = fomoc.__viewhelp__()
        dbg('browsing')
        dbg(fomoc)
        dbg(type(fomoc))
        if hasattr(fomoc,'__func__'):
            html = rc.functionToHtml(fomoc.__func__)


        elif fomoc == None:
            html = '<h1>about:blank</h1>'
        elif inspect.ismodule(fomoc):
            html = rc.moduleToHtml(fomoc,fomoc.__name__)
        elif inspect.isfunction(fomoc):
            html = rc.functionToHtml(fomoc)
        elif inspect.isbuiltin(fomoc):
            html = rc.functionToHtml(fomoc)
        elif inspect.isclass(fomoc):
            html = rc.classToHtml(fomoc,fomoc.__name__)
        else:

            fomoc = type(fomoc)
            if fomoc == None:
                html = '<h1>about:blank</h1>'
            elif inspect.ismodule(fomoc):
                html = rc.moduleToHtml(fomoc,fomoc.__name__)
            elif inspect.isfunction(fomoc):
                html = rc.functionToHtml(fomoc)
                #print(html)
            elif inspect.isbuiltin(fomoc):
                html = rc.functionToHtml(fomoc)
                #print(html)
            elif inspect.isclass(fomoc):

                html = rc.classToHtml(fomoc,fomoc.__name__)
            else:
                html = '<h1>Invalid Input</h1>'
        self.html.setHtml(html)
        self.html.show()

    def findText(self):
        self.html.findText(self.tb_url.text())



class WebView(QtWebKit.QWebView):

    def __init__(self,parent=None):

        super(WebView, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)


    def sizeHint(self):

        return QSize(300,300)

from collections import UserString
class StringVar(Connection,UserString):
     def setData(self,new_data):
         self.data = new_data
class runThread(QThread):
    def __init__(self,parent,func=None):
        self.func = func
        super(runThread,self).__init__(parent)

    def run(self):
        self.func()
class lockClass(object):
    def __init__(self,api):
        self.API = api
        for i in dir(API):
            self.__dict__[i] = self.API.__getattribute__(i)
    def __repr__(self):
        return '<locked API object>'
    def __viewhelp__(self):
        return self.API


class Console(QPlainTextEdit,Connection):
    def __init__(self, prompt='-->: ', startup_message='', parent=None):
        super(Console,self).__init__()
        self.start('Console')
        self.setWindowTitle("python qt console")
        QPlainTextEdit.__init__(self, parent)
        self._locals = {}
        self.prompt = prompt
        self.config = conf.load('PyEditor')
        self.maxHistory = int(conf.check(self.config,['CONSOLE','history'],'100'))
        self.Cconnect = lambda :Connection.connect(self)

        self.loadHistory()
        self.namespace = {}
        self.construct = []
        self.inputMode = False
        #self._locals['input'] = self.c_input
        self.print_lock = QReadWriteLock()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        #self.setMaximumWidth(HORIZ_SIZE)
        #self.setMaximumHeight(VERT_SIZE/2)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setUpdatesEnabled(True)


        self.setGeometry(50, 75, 600, 400)
        self.setWordWrapMode(QTextOption.WrapAnywhere)
        self.setUndoRedoEnabled(False)

        font = conf.check(self.config,['CONSOLE','font'],'Courier')

        try:
            ros = self.config.get('RunOnStartup',[])
        except:
            ros = []

        self._locals['console'] = self
        self.document().setDefaultFont(QFont(font, 10, QFont.Normal))
        self.showMessage(startup_message)
        for i in ros:
            self.setCommand('console.runfile("%s")' % (i))
            self.runCommand(self.getCommand())

            self.newPrompt()
            self.old_history.pop(-1)
            self.history = self.old_history

    def minimumSizeHint(self):
        """
        Set the minimum size

        """

        return QSize(200,300)

    def loadHistory(self):

        try:
            f = open(os.path.join(os.path.expanduser('~'),'.ScopePy','PythonHistory.log'),'rb')
        except FileNotFoundError:
            self.saveHistory('')

            f = open(os.path.join(os.path.expanduser('~'),'.ScopePy','PythonHistory.log'),'rb')
        t = f.read().decode()
        f.close()
        h = t.split(';')
        if len(h) > self.maxHistory:
            diff = len(h) - self.maxHistory
            for i in range(diff):
                h.pop(i)
            f = open(os.path.join(os.path.expanduser('~'),'.ScopePy','PythonHistory.log'),'wb')
            f.write(';'.join(h).encode())
            f.flush()
            f.close()
        self.old_history = h
        self.history_index = len(self.old_history)
        self.history = self.old_history


    def saveHistory(self,command):

        t = command+';'
        f = open(os.path.join(os.path.expanduser('~'),'.ScopePy','PythonHistory.log'),'ab')
        f.write(t.encode())
        f.flush()
        f.close()


    def updateNamespace(self, namespace):
        self.namespace.update(namespace)

    def showMessage(self, message):
        self.appendPlainText(message)
        self.newPrompt()

    def newPrompt(self):
        if self.construct:
            prompt = '.' * len(self.prompt)
        else:
            prompt = self.prompt
        self.appendPlainText(prompt)
        self.moveCursor(QTextCursor.End)

    def getCommand(self):
        doc = self.document()
        curr_line = doc.findBlockByLineNumber(doc.lineCount() - 1).text()
        curr_line = curr_line.rstrip()
        curr_line = curr_line[len(self.prompt):]
        return curr_line

    def setCommand(self, command):
        if self.getCommand() == command:
            return
        self.moveCursor(QTextCursor.End)
        self.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        for i in range(len(self.prompt)):
            self.moveCursor(QTextCursor.Right, QTextCursor.KeepAnchor)
        self.textCursor().removeSelectedText()
        self.textCursor().insertText(command)
        self.moveCursor(QTextCursor.End)

    def getConstruct(self, command):
        if self.construct:
            prev_command = self.construct[-1]
            self.construct.append(command)
            if not prev_command and not command:
                ret_val = '\n'.join(self.construct)
                self.construct = []
                return ret_val
            else:
                return ''
        else:
            if command and command[-1] == (':'):
                self.construct.append(command)
                return ''
            else:
                return command

    def getHistory(self):
        return self.history

    def setHistory(self, history):
        self.history = history

    def addToHistory(self, command):
        if command and (not self.old_history or self.old_history[-1] != command):
            self.old_history.append(command)
            self.saveHistory(command)
        self.history_index = len(self.history)

    def getPrevHistoryEntry(self):
        if self.old_history:
            if self.getCommand() == '':
                self.history = self.old_history
            else:

                if self.getCommand() in self.history:
                    pass
                else:
                    self.history = []
                    for i in self.old_history:
                        if i.startswith(self.getCommand()):
                            self.history.append(i)

            self.history_index = max(0, self.history_index - 1)
            #print(self.history)
            try:
                return self.history[self.history_index]
            except IndexError:
                self.history_index = max(0, len(self.history))
                try:
                    self.history_index = max(0, self.history_index -1)
                    return self.history[self.history_index]
                except IndexError:
                    return ''
        return ''

    def getNextHistoryEntry(self):
        if self.old_history:
            hist_len = len(self.history)
            self.history_index = min(hist_len, self.history_index + 1)
            if self.history_index < hist_len:
                return self.history[self.history_index]
        return ''

    def getCursorPosition(self):
        return self.textCursor().columnNumber() - len(self.prompt)

    def setCursorPosition(self, position):
        self.moveCursor(QTextCursor.StartOfLine)
        for i in range(len(self.prompt) + position):
            self.moveCursor(QTextCursor.Right)

    def c_input(self,msg):
        '''
Show a message as a prompt on the Python editor's console.
example:
>>>: input('msg: ')
msg: test
test
>>>:
'''
        self.inputMessage = ''
        self.defaultPrompt = self.prompt
        self.prompt = msg
        self.API = self._locals['API']
        self.inputMode = True
        self.isreafy = False

        var = StringVar('')
        var.start('Console')
        self.addConnection(var,lambda self:self.inputMessage,self)

        return var




    def runCommand(self,command=None):
        #self.setWindowTitle("*python qt console*")
        self.history = self.old_history
        #self.API = self._locals['API']
        if command == None:
            command = self.getCommand()
        self.addToHistory(command)

        command = self.getConstruct(command)
        if command == 'quit()':
            #raise NotImplementedError('Invalid Use of quit in Python console')
            self.destroy()


        if command:
            tmp_stdout = sys.stdout
            tmp_stderr = sys.stderr

            class stdoutProxy():
                def __init__(self, write_func, lock):
                    self.write_func = write_func
                    self.skip = False
                    self.lock = lock

                def write(self, text):
                    self.lock.lockForWrite()
                    if not self.skip:

                        stripped_text = text.rstrip('\n')

                        self.write_func(stripped_text)

                        QCoreApplication.processEvents()
                    self.skip = not self.skip
                    self.lock.unlock()

            sys.stdout = stdoutProxy(self.appendPlainText,self.print_lock)
            sys.stderr = stdoutProxy(self.appendPlainText,self.print_lock)

            try:
                try:
                    result = eval(command,globals(),self._locals)

                    if result != None:
                        self.appendPlainText(repr(result))
                except SyntaxError:
                    try:
                        exec(command,globals(),self._locals)
                    except KeyboardInterrupt:
                        self.appendPlainText('\n'+"KeyboardInterrupt!")
                        sys.stdout = tmp_stdout
                        sys.stderr = tmp_stderr
                        self.newPrompt()
                        self.setWindowTitle("python qt console")
                        self.kill()
                        return
            except SystemExit:
                self.close()
            except:
                traceback_lines = traceback.format_exc().split('\n')
                # Remove traceback mentioning this file, and a linebreak
                for i in (2,1,-1):
                    traceback_lines.pop(i)

                self.appendPlainText('\n'.join(traceback_lines))

            sys.stdout = tmp_stdout
            sys.stderr = tmp_stderr



        #self.setWindowTitle("python qt console")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.isreafy = True
            self.Cconnect()
            if self.inputMode == True:


                cm = self.getCommand()
                self.prompt = self.defaultPrompt
                self.newPrompt()
                noz = True
            else:
                self.runCommand(self.getCommand())

                self.newPrompt()
                noz = False
            if noz:
                self.inputMode = False
                self.inputMessage=cm
            return
        if event.key() == Qt.Key_Home:

            self.setCursorPosition(0)
            return
        if event.key() == Qt.Key_PageUp:

            return
        elif event.key() in (Qt.Key_Left, Qt.Key_Backspace):

            if self.getCursorPosition() == 0:

                return
        elif event.key() == Qt.Key_Up:

            self.setCommand(self.getPrevHistoryEntry())

            return
        elif event.key() == Qt.Key_Down:

            self.setCommand(self.getNextHistoryEntry())

            return
        elif event.key() == Qt.Key_D and event.modifiers() == Qt.ControlModifier:

            self.restart()

        elif event.key() == Qt.Key_C and event.modifiers() == Qt.AltModifier:

            self.restart()

        if (event.type() == QEvent.KeyPress and
            event.key() == Qt.Key_Tab):
            text = self.getCommand()
            a,b = text.split(".")
            print(a)
            print(b)
            tlist = dir(a)

            anserlist = []
            for i in tlist:
                if i.startswith(b):
                    anserlist.append(i)

            if len(anserlist) != 1:
                return True

            else:

                self.setCommand(a+anserlist[0])

            return True



        super(Console, self).keyPressEvent(event)



    def commands(self):
        self.showMessage("""
        updateNamespace()
        showMessage(message)
        newPrompt()
        getCommand()
        setCommand(command)
        getConstruct()
        getHistory()
        setHistory(history)
        addToHistory(command)
        getPrevHistoryEntry()
        getNextHistoryEntry()
        getCursorPosition()
        setCursorPosition()
        runCommand()
        KeyPressEvent()
        kill()

        This is the help for are special commands""")

    def kill(self):
        self.newPrompt()
        self.setCommand("quit()")
        self.runCommand()


    def runfile(self,filename):
        self._locals['__name__'] = '__main__'
        self._locals['__file__'] = filename
        self._locals['pprint'] = pprint
        f = conf.load('PyEditor')
        fn = conf.check(f,['EDITOR','runname'],'^f')
        fn = fn.replace('^f','%s')

        f = open(filename,'r')
        lines = f.readlines()
        f.close()
        l = lines[0].replace('\n','')
        l = l.replace('\r','')
        if l == '#!@MathChannel':
            self.API.load_math_functions()


        #exec(compile(open(filename,'r').read(),fn % filename,'exec'),globals(),self._locals)
        import runpy
        #t = QThread(self)
        #target=lambda :

        glbs = runpy.run_path(filename,self._locals,run_name='__main__')
        self._locals.update(glbs)

        #t.start()


    def restart(self):
        self.close()
        if 'panel' in self._locals:
            panel = self._locals['panel']
            msg = '''
----------RESTART----------
'''

            mc = Console(self.prompt,msg)
            mc._locals = self._locals
            panel.position([[mc],[self._locals['editor']]])
            panel.console = mc
            mc._locals['console'] = mc

        del self


class PythonHighlighter(QSyntaxHighlighter):

    Rules = []

    def __init__(self, ds, parent=None):
        super(PythonHighlighter, self).__init__(parent)
        if ds == None:

            keywordFormat = QTextCharFormat()
            keywordFormat.setForeground(QColor(36,217,255))
            keywordFormat.setFontWeight(QFont.Bold)
            bultforFormat = QTextCharFormat()
            bultforFormat.setForeground(QColor(217,0,217))
            bultforFormat.setFontWeight(QFont.Bold)
            for pattern in ((r"\band\b", r"\bas\b", r"\bassert\b",
                    r"\bbreak\b", r"\bclass\b", r"\bcontinue\b",
                    r"\bdef\b", r"\bdel\b", r"\belif\b", r"\belse\b",
                    r"\bexcept\b",  r"\bfinally\b", r"\bfor\b",
                    r"\bfrom\b", r"\bglobal\b", r"\bif\b", r"\bimport\b",
                    r"\bin\b", r"\bis\b",  r"\bnot\b",
                    r"\bor\b", r"\bpass\b",  r"\braise\b",
                    r"\breturn\b", r"\btry\b", r"\bwhile\b", r"\bwith\b",
                    r"\byield\b",r"\bself\b")):
                PythonHighlighter.Rules.append((QRegExp(pattern),
                                               keywordFormat))

            for pattern in ((r"\blambda\b",r"\bprint\b",r"\bexec\b", r"\brange\b", r"\blist\b",
                             r"\bstr\b",r"\bint\b",r"\bfloat\b",r"\bdict\b",r"\bAPI\b",r"\blen\b")):
                PythonHighlighter.Rules.append((QRegExp(pattern),
                                               bultforFormat))
            commentFormat = QTextCharFormat()
            commentFormat.setForeground(QColor(0, 127, 0))
            commentFormat.setFontItalic(True)
            PythonHighlighter.Rules.append((QRegExp(r"#.*"),
                                            commentFormat))
            self.stringFormat = QTextCharFormat()
            self.stringFormat.setForeground(Qt.darkYellow)
            stringRe = QRegExp(r"""(?:'[^']*'|"[^"]*")""")
            stringRe.setMinimal(True)
            PythonHighlighter.Rules.append((stringRe, self.stringFormat))
            self.stringRe = QRegExp(r"""(:?"["]".*"["]"|'''.*''')""")
            self.stringRe.setMinimal(True)
            PythonHighlighter.Rules.append((self.stringRe,
                                            self.stringFormat))
            self.tripleSingleRe = QRegExp(r"""'''(?!")""")
            self.tripleDoubleRe = QRegExp(r'''"""(?!')''')

        else:
            keywordFormat = QTextCharFormat()
            keywordFormat.setForeground(QColor(ds['keywords']))
            keywordFormat.setFontWeight(QFont.Bold)
            bultforFormat = QTextCharFormat()
            bultforFormat.setForeground(QColor(ds['builtins']))
            bultforFormat.setFontWeight(QFont.Bold)
            for pattern in ((r"\band\b", r"\bas\b", r"\bassert\b",
                    r"\bbreak\b", r"\bclass\b", r"\bcontinue\b",
                    r"\bdef\b", r"\bdel\b", r"\belif\b", r"\belse\b",
                    r"\bexcept\b",  r"\bfinally\b", r"\bfor\b",
                    r"\bfrom\b", r"\bglobal\b", r"\bif\b", r"\bimport\b",
                    r"\bin\b", r"\bis\b",  r"\bnot\b",
                    r"\bor\b", r"\bpass\b",  r"\braise\b",
                    r"\breturn\b", r"\btry\b", r"\bwhile\b", r"\bwith\b",
                    r"\byield\b",r"\bself\b")):
                PythonHighlighter.Rules.append((QRegExp(pattern),
                                               keywordFormat))

            for pattern in ((r"\blambda\b",r"\bprint\b",r"\bexec\b", r"\brange\b", r"\blist\b",
                             r"\bstr\b",r"\bint\b",r"\bfloat\b",r"\bdict\b",r"\bAPI\b",r"\blen\b")):
                PythonHighlighter.Rules.append((QRegExp(pattern),
                                               bultforFormat))
            commentFormat = QTextCharFormat()
            commentFormat.setForeground(QColor(ds['comments']))
            commentFormat.setFontItalic(True)
            PythonHighlighter.Rules.append((QRegExp(r"#.*"),
                                            commentFormat))
            self.stringFormat = QTextCharFormat()
            self.stringFormat.setForeground(QColor(ds['strings']))
            stringRe = QRegExp(r"""(?:'[^']*'|"[^"]*")""")
            stringRe.setMinimal(True)
            PythonHighlighter.Rules.append((stringRe, self.stringFormat))
            self.stringRe = QRegExp(r"""(:?"["]".*"["]"|'''.*''')""")
            self.stringRe.setMinimal(True)
            PythonHighlighter.Rules.append((self.stringRe,
                                            self.stringFormat))
            self.tripleSingleRe = QRegExp(r"""'''(?!")""")
            self.tripleDoubleRe = QRegExp(r'''"""(?!')''')


    def highlightBlock(self, text):
        NORMAL, TRIPLESINGLE, TRIPLEDOUBLE = range(3)

        for regex, format in PythonHighlighter.Rules:
            i = regex.indexIn(text)
            while i >= 0:
                length = regex.matchedLength()
                self.setFormat(i, length, format)
                i = regex.indexIn(text, i + length)

        self.setCurrentBlockState(NORMAL)
        if self.stringRe.indexIn(text) != -1:
            return
        for i, state in ((self.tripleSingleRe.indexIn(text),
                          TRIPLESINGLE),
                         (self.tripleDoubleRe.indexIn(text),
                          TRIPLEDOUBLE)):
            if self.previousBlockState() == state:
                if i == -1:
                    try:
                        i = text.length()
                    except:
                        pass
                    self.setCurrentBlockState(state)
                self.setFormat(0, i + 3, self.stringFormat)
            elif i > -1:
                self.setCurrentBlockState(state)
                self.setFormat(i, len(text), self.stringFormat)


class TextEdit(QTextEdit):

    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)


    def event(self, event):
        if (event.type() == QEvent.KeyPress and
            event.key() == Qt.Key_Tab):
            cursor = self.textCursor()
            cursor.insertText("    ")
            return True
        return QTextEdit.event(self, event)

import ScopePy_config as conf
class PyEditor(QMainWindow):

    def __init__(self, console, panel, filename=None, parent=None):
        super(PyEditor, self).__init__(parent)
        self.console = console
        self.panel = panel
        self.API = panel.API
        self.sqt = False
        self.config = conf.load('PyEditor')
        font = conf.check(self.config,['EDITOR','font'],'Courier')

        font = QFont(font, 11)
        font.setFixedPitch(True)
        self.editor = TextEdit()
        self.editor.setFont(font)
        self.editor.keyPressEvent = self.keyPressEvent

        tpath = self.API.getThemePath(self.API.preferences.theme)
        self.API.log.error(tpath)
        self.config = conf.load('PyEditor')
        try:
            ds = self.config['COLORS']
        except:
            ds = None

        self.highlighter = PythonHighlighter(ds,self.editor.document())
        self.setCentralWidget(self.editor)

        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.showMessage("Ready", 5000)

        fileNewAction = self.createAction("&New...", self.fileNew,
                QKeySequence.New, "filenew", "Create a Python file")


        run = self.createAction("&Run...", self.run,
                '', "Run", "Run a Python script")
        #run.setShortcut('F5')


        fileOpenAction = self.createAction("&Open...", self.fileOpen,
                QKeySequence.Open, "fileopen",
                "Open an existing Python file")
        self.fileSaveAction = self.createAction("&Save", self.fileSave,
                QKeySequence.Save, "filesave", "Save the file")
        self.fileSaveAsAction = self.createAction("Save &As...",
                self.fileSaveAs, icon="filesaveas",
                tip="Save the file using a new name")
        fileQuitAction = self.createAction("&Quit", self.close,
                "Ctrl+Q", "filequit", "Close the application")
        self.editCopyAction = self.createAction("&Copy",
                self.editor.copy, QKeySequence.Copy, "editcopy",
                "Copy text to the clipboard")
        self.editCutAction = self.createAction("Cu&t", self.editor.cut,
                QKeySequence.Cut, "editcut",
                "Cut text to the clipboard")
        self.editPasteAction = self.createAction("&Paste",
                self.editor.paste, QKeySequence.Paste, "editpaste",
                "Paste in the clipboard's text")

        self.editPasteAction = self.createAction("html",
                self.saveHtml, 'Shift+Alt+s', "saveashtml",
                "html")

        self.indentAction = self.createAction("indent",
                self.addIndent, 'Ctrl+]', "indent",
                "increase indentation level by 1")

        self.dedentAction = self.createAction("dedent",
                self.removeIndent, 'Ctrl+[', "dedent",
                "decrease indentation level by 1")

        self.mathTemp = self.createAction("Math Function",
                self.addMathTemplate, 'Ctrl+Shift+M', "math",
                "Create a template for a math function")

        fileMenu = self.menuBar().addMenu("&File")
        self.addActions(fileMenu, (fileNewAction, fileOpenAction,
                self.fileSaveAction, self.fileSaveAsAction, None,
                fileQuitAction,run))
        editMenu = self.menuBar().addMenu("&Edit")
        self.addActions(editMenu, (self.editCopyAction,
                self.editCutAction, self.editPasteAction,self.indentAction,self.dedentAction))
        fileToolbar = self.addToolBar("File")
        fileToolbar.setObjectName("FileToolBar")
        self.addActions(fileToolbar, (fileNewAction, fileOpenAction,
                                      self.fileSaveAction))
        editToolbar = self.addToolBar("Edit")
        editToolbar.setObjectName("EditToolBar")
        self.addActions(editToolbar, (self.editCopyAction,
                self.editCutAction, self.editPasteAction))

        tempTool = self.addToolBar("Templates")
        tempTool.setObjectName("TemplateToolBar")
        self.addActions(tempTool, (self.mathTemp,
                                    ))

        self.connect(self.editor,
                SIGNAL("selectionChanged()"), self.updateUi)
        self.connect(self.editor.document(),
                SIGNAL("modificationChanged(bool)"), self.changed)
        self.connect(QApplication.clipboard(),
                SIGNAL("dataChanged()"), self.updateUi)

        self.fkeys = [
                     ['F4','New',self.fileNew],
                     ['F5','Run',self.run],
                     ['F6','Open',self.fileOpen],
                     ['F8','Save',self.fileSave],
                     ['F10','Save as',self.fileSaveAs],
                     ['F9','To Console',self.to_console],
                     ]

        self.resize(800, 600)
        self.setWindowTitle("Python Editor")
        self.filename = filename
        self.indent = 0
        if self.filename is not None:
            self.loadFile()
        self.updateUi()

    def to_console(self):
        txt = self.editor.textCursor().selectedText()
        try:
            lines = txt.split('\u2029')
        except:
            lines = [txt]
        print(lines)
        import logger
        for t in lines:
            logger.debug(t)
            self.console.setCommand(t)
            self.console.runCommand()


    def updateUi(self, arg=None):
        self.fileSaveAction.setEnabled(
                self.editor.document().isModified())
        self.fileSaveAsAction.setEnabled(
                not self.editor.document().isEmpty())
        enable = self.editor.textCursor().hasSelection()
        self.editCopyAction.setEnabled(enable)
        self.editCutAction.setEnabled(enable)
        self.editPasteAction.setEnabled(self.editor.canPaste())

    def changed(self,mod):
        self.change = mod
        if mod:
            self.setWindowTitle("*Python Editor* - {}".format(
                        QFileInfo(self.filename).fileName()))

        else:
                self.setWindowTitle("Python Editor - {}".format(
                        QFileInfo(self.filename).fileName()))


    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/{}.png".format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action


    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)


    def closeEvent(self, event):
        if not self.okToContinue():
            event.ignore()


    def okToContinue(self):
        if self.editor.document().isModified():
            reply = QMessageBox.question(self,
                            "Python Editor - Unsaved Changes",
                            "Save unsaved changes?",
                            QMessageBox.Yes|QMessageBox.No|
                            QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Yes:
                return self.fileSave()
        return True
    def okToLeave(self):
        if self.editor.document().isModified():
            reply = QMessageBox.question(self,
                            "Python Editor - Unsaved Changes",
                            "Save unsaved changes?",
                            QMessageBox.Yes|QMessageBox.No|
                            QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return True
            elif reply == QMessageBox.Yes:
                return self.fileSave()
        return True


    def fileNew(self):
        if not self.okToContinue():
            return
        document = self.editor.document()
        document.clear()
        document.setModified(False)
        self.filename = None
        self.setWindowTitle("Python Editor - Unnamed")
        self.updateUi()


    def fileOpen(self):
        if not self.okToContinue():
            return
        dir = (os.path.dirname(self.filename)
               if self.filename is not None else ".")
        fname = QFileDialog.getOpenFileName(self,
                "Python Editor - Choose File", dir,
                "Python files (*.py *.pyw)")

        if fname:
            self.filename = fname
            self.loadFile()


    def loadFile(self):
        fh = None
        try:
            fh = QFile(self.filename)
            if not fh.open(QIODevice.ReadOnly):
                raise IOError(fh.errorString())
            stream = QTextStream(fh)
            stream.setCodec("UTF-8")
            self.editor.setPlainText(stream.readAll())
            self.editor.document().setModified(False)
            self.setWindowTitle("Python Editor - {}".format(
                    QFileInfo(self.filename).fileName()))
        except EnvironmentError as e:
            QMessageBox.warning(self, "Python Editor -- Load Error",
                    "Failed to load {}: {}".format(self.filename, e))
        finally:
            if fh is not None:
                fh.close()


    def fileSave(self):
        if self.filename is None:
            return self.fileSaveAs()
        fh = None
        try:
            fh = QFile(self.filename)
            if not fh.open(QIODevice.WriteOnly):
                raise IOError(fh.errorString())
            stream = QTextStream(fh)
            stream.setCodec("UTF-8")
            stream << self.editor.toPlainText()
            self.editor.document().setModified(False)
        except EnvironmentError as e:
            QMessageBox.warning(self, "Python Editor -- Save Error",
                    "Failed to save {}: {}".format(self.filename, e))
            return False
        finally:
            if fh is not None:
                fh.close()
        return True


    def fileSaveAs(self):
        filename = self.filename if self.filename is not None else "."
        filename = QFileDialog.getSaveFileName(self,
                "Python Editor -- Save File As", filename,
                "Python files (*.py *.pyw)")
        if filename:
            self.filename = filename
            self.setWindowTitle("Python Editor - {}".format(
                    QFileInfo(self.filename).fileName()))
            return self.fileSave()
        return False

    def sqtmode(self):
        if self.sqt:
            self.sqt  = False
        else:
            self.sqt = True

    def Indent(self,n=0):
        for i in range(n):
            self.editor.insertPlainText('    ')
    def run(self):
        if not self.sqt:
            self.console.setCommand('console.runfile("%s")' % (self.filename))
            self.console.runCommand(self.console.getCommand())

            self.console.newPrompt()
            self.console.old_history.pop(-1)
            self.console.history = self.console.old_history
            #self.console.runCommand()
        else:
            self.console.setCommand('exec(open("%s","r").read(),globals(),console._locals)' % (self.filename))
            self.console.runCommand()
            self.panel.runsqt(self.console._locals['__panels__'])

    def stop(self):
        self.console.newPrompt()
        self.console.isready = False
        while self.console.isready == True:
            return
        self.console.newPrompt()


    def saveHtml(self):
        #filename = self.filename if self.filename is not None else "."
        filename = QFileDialog.getSaveFileName(self,
                "Python Editor -- Save File As Html", self.filename,
                "Html files (*.html *.htm)")
        if filename:
            f = open(filename,'w')
            f.write(self.editor.toHtml())
            f.flush()
            f.close()
        return False

    def addIndent(self):
        self.indent += 1

    def removeIndent(self):
        self.indent -= 1

    def addMathTemplate(self):
        temp = '''#!@MathChannel

from ScopePy_channel import MathFunction


def math_function(chan):# you can have more than one channel argument!
    return (chan.x*2,chan.y*2) #You put in here what you want to be done to the channels...

mathFunctions = [] # add All math functions to this list!
ex = MathFunction()
ex.name = '<funcName>'
ex.description = '<WhatItDoes>'
ex.function = math_function

mathFunctions.append(ex)
'''
        self.editor.insertPlainText(temp)

    def keyPressEvent(self,e):
        #print(e.key())
        #print(self.indent)
        if e.key() == Qt.Key_Return:
            #rint('indenting!')
            self.editor.insertPlainText('\n')
            self.Indent(self.indent)
            return

        QTextEdit.keyPressEvent(self.editor,e)










import ScopePy_config as conf

#print(FUNKS)
class PyConsole(sqt.SimpleBase):
    def drawPanel(self):
        #super(PlugConsole).__init__(api)
        self.isSaveable = True
        welcome_message = '''
        This is ScopePy's Triangledot Python
        Interpreter.

        To use ScopePy's Python Interface, use
        Global Variables <API> <panel> <console> and <editor>
        For controling this panel.
        Type viewHelp(object) for graphical help
        '''
        self.stack = QStackedWidget()
        l = QVBoxLayout()
        l.addWidget(self.stack)
        w = QWidget()
        self.config = conf.load('PyEditor')
        if self.config == None:
            prompt = ">>>: "
        else:
            prompt = self.config['CONSOLE']['prompt']+' '
        globals()['API'] = self.API
        self.console =  Console(prompt=prompt,startup_message=welcome_message)
        self.editor = PyEditor(self.console,self)
##        layout = QVBoxLayout(self)
##        layout.addWidget(self.console)
##        layout.addWidget(self.editor)
##        w.setLayout(layout)
        #self.browser = Browser()
        lab = QLabel('')

        ef = sqt.frame(self)
        ef.position([[self.console],[lab],[self.editor]])
        self.editor.setWindowTitle = lab.setText
        self.position([[ef]])
        self.console.API = self.API
        self.console._locals["API"]=lockClass(self.API)
        self.console._locals["console"]=self.console
        self.console._locals["panel"]=self
        self.console._locals["editor"]=self.editor
        self.console._locals["viewHelp"]=self.help
        from pprint import pprint
        self.console._locals["pprint"]=pprint
        globals()['pprint'] = pprint

        self.setLayout(l)
        self.wd = {'main':w}
        self.stack.addWidget(w)


    def onClose(self):
        if self.editor.editor.document().isModified():
            #return self.editor.okToLeave()
            return None # TODO : Fix
        else:
            return None

    def setFkeys(self):

        self.Fkeys = self.editor.fkeys

    def minimumSizeHint(self):
        """
        Set the minimum size

        """

        return QSize(HORIZ_SIZE,VERT_SIZE)

    def openAndRun(self,filename):
        if filename != None:
            with open(filename,'r') as f:
                txt = f.read()
            self.editor.editor.setPlainText(txt)
            self.editor.filename = filename
            self.editor.run()

    def runsqt(self,flags):
        for i in flags:
            currentDockArea = self.API._gui.mainArea.currentWidget()
            currentDockArea.addWindow(QWidget(flags[i].panel_class),title='PyConsole - Running SQT: %s' % i)
    def help(self,fomoc):
        '''
Show graphical help on a module, function, or class
'''

        self.API.sendComms('setDocs',self.API.panelID('Docs Browser'),fomoc)
    def addChannel(self,channel):
        try:
            ch = self.API.channel_dict[channel]
        except:
            self.console.showMessage('Ghost Channel!')
            return
        name = channel.replace(' ','_')
        self.console.showMessage('Added new channel as varible <%s>' % name)

        ch = self.API.channel_dict[channel]
        self.console._locals[name] = ch

    def saveData(self):
        data = self.standardSaveData
        data['filename'] = self.editor.filename
        data['text'] = self.editor.editor.toPlainText()
        return data
    def restoreData(self,panel_data):
        self.editor.editor.setText(panel_data['text'])
        self.editor.filename = panel_data['filename']





from ScopePy_widgets import colorpicker
import ScopePy_config as conf
class settings(conf.ConfigBase):
    def drawPanel(self):
        frame = sqt.frame(self)
        self.c = sqt.combobox(self)
        self.c.addItems(['keywords','builtins','comments','strings'])
        self.color = colorpicker()
        self.set = sqt.button(frame,'set color!')
        self.set.bindClicked(self.setcolor)
        self.c.bindChanged(self.textChanged)
        self.datastore = {}
        self.getSettings()
        self.color.setNamedColor(self.datastore['keywords'])
        frame.position([[sqt.label(self,'Select and set python editor colors:')],
                       [self.c],
                       [self.color],
                       [self.set]])
        d = conf.DataStorage()
        prompt = sqt.frame(self)
        p = conf.check(self.config,['CONSOLE','prompt'],'>>>: ')

        pp = conf.check(self.config,['EDITOR','runname'],'^f')
        limit = int(conf.check(self.config,['CONSOLE','history'],'100'))
        self.spin = QSpinBox(self)
        self.spin.setMaximum(500)
        self.spin.setMinimum(20) # change back to 20
        self.spin.setValue(limit)
        self.promptentry = QLineEdit(p)
        self.runname = QLineEdit(pp)
        prompt.position([[sqt.label(self,'Enter Prompt for Python Console')],[self.promptentry],
                         [sqt.label(self,'Enter format of file name shown in <br> Python Editor errors:<br>use ^f as the filename')],
                         [self.runname],
                         [sqt.label(self,'Enter maximum amount of history.')],[self.spin]])
        loros = self.config.get('RunOnStartup',[])
        self.rosbox = PrefBox(self,paths=loros,dirmode=False)


        ff = sqt.frame(self)
        fonte = conf.check(self.config,['EDITOR','font'],'Courier')
        fontc = conf.check(self.config,['CONSOLE','font'],'Courier')

        self.fstore = {'editor-font':fonte,'console-font':fontc}
        b1 = QPushButton('Select Font')
        b2 = QPushButton('Select Font')
        b1.clicked.connect(self.setFont1)
        b2.clicked.connect(self.setFont2)

        ff.position([[sqt.label(ff,'Select font for editor:'),b1],
                     [sqt.label(ff,'Select font for console'),b2]])
        d['color'] = frame
        d['console'] = prompt
        d['font'] = ff
        d['Run On Startup'] = self.rosbox
        self.setupTabs(d)

    def getSettings(self):
        #tpath = self.API.getThemePath(self.API.preferences.theme)
        #self.API.log.error(tpath)
        #css = csslib.passCss(tpath)

        self.config = conf.load('PyEditor')
        if self.config == None:
            self.API.log.debug('No Python Editor Themes in this Theme!!!!\n')
            ds = {'keywords':'#6200cf',
                  'builtins':'#008fb0',
                  'comments':'#ff0000',
                  'strings':'#00a700'}

        else:
            ds = {'keywords':self.config['COLORS']['keywords'],
                  'builtins':self.config['COLORS']['builtins'],
                  'comments':self.config['COLORS']['comments'],
                  'strings':self.config['COLORS']['strings']}

        self.datastore = ds

    def setcolor(self):
        self.datastore[self.c.currentText] = self.color.name

##        tpath = self.API.getThemePath(self.API.preferences.theme)
##        self.API.log.error(tpath)
##        css = csslib.passCss(tpath)
##
##        css['Pyeditor::themes'] = self.datastore
##        csslib.createCss(css,tpath)

    def onSave(self):
        #self.config = conf.load('PyEditor')
        print('Saveing!')
        conf.save('PyEditor',{'COLORS':self.datastore,'CONSOLE':{'prompt':self.promptentry.text(),
                                                                 'font':self.fstore['console-font'],'history':str(self.spin.value())},
                              'EDITOR':{'runname':self.runname.text(),
                                        'font':self.fstore['editor-font']},
                              'RunOnStartup':self.rosbox.path})



    def textChanged(self,index):
        text = self.datastore[['keywords','builtins','comments','strings'][index]]
        self.color.setNamedColor(text)

    def setFont1(self):
        font = conf.check(self.config,['EDITOR','font'],'Courier')
        f ,suc= QFontDialog.getFont(QFont(font),self,'Select font for Editor')

        font = f.toString()

        if suc:

            font = font.split(',')
            self.fstore['editor-font'] = font[0]

    def setFont2(self):
        font = conf.check(self.config,['CONSOLE','font'],'Courier')
        f,suc = QFontDialog.getFont(QFont(font),self,'Select font for Console')

        font = f.toString()
        if suc:
            font = font.split(',')
            self.fstore['console-font'] = font[0]




welcome_message = '''
   ---------------------------------------------------------------
     Welcome to a triangledot qt Python interpreter.
   ---------------------------------------------------------------
'''
def fake_input(prompt):
    text, ok = QInputDialog.getText(console, prompt,
                prompt)

    return text

def runfile(filename):
    exec(open(filename).read(),globals(),console._locals)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    console = Console(startup_message=welcome_message)
    #console.updateNamespace({'application' : app, 'anum' : 1234})
    console.setWindowTitle("python qt console")
    console.setCommand("import __main__ as main")
    console.runCommand()
    input = fake_input
    console.show();
    sys.exit(app.exec_())

browserDocs = '''
%*% Use:
++<
using commands like
--(
viewHelp(fomoc)
)--
on the python editor and
--(
API.sendComms('setDocs',self.API.panelID('Docs Browser'),fomoc)
)--
From anything else.
Using those functions you can
show help for a function, module, or class (fomoc).
While as
--(
API.sendComms('setHtml',self.API.panelID('Docs Browser'),htmlWrapper)
)--
Using that function (from anywhere)
You use a  refclass.htmlWrapper and refclass script (use viewHelp(rc) on the python editor
for a discription of refclass script) to give it html like this.
>++
'''

import ScopePy_panels as panel
__panels__ = {"Python Editor":panel.PanelFlags(PyConsole,
                                                  open_on_startup=False,
                                                  location='main_area'),
              "Docs Browser":panel.PanelFlags(Browser,
                                                  open_on_startup=True,
                                                  single_instance=True,
                                                  on_panel_menu=False,
                                                  location='sidebar',
                                                  API_attribute_name='docsBrowser',
                                                  docs=browserDocs)}

__config__ = {'Python Editor':settings}
