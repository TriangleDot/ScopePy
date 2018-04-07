import sys, os,logging
import traceback
from qt_imports import QtCore

_locals = {}
import sys

from qt_imports import *

#import commands as com
import ScopePy_API as api
import re
"""
Version
==============================================================================
$Revision:: 17                            $
$Date:: 2015-03-23 19:44:56 -0400 (Mon, 2#$
$Author:: finn                            $
==============================================================================

"""
#==============================================================================
# License
#==============================================================================

"""
Copyright 2015 Finn Bainbridge

This file is part of ScopePy.

ScopePy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ScopePy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ScopePy.  If not, see <http://www.gnu.org/licenses/>.
"""


#==============================================================================
# Logger
#==============================================================================
# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add do nothing handler
logger.addHandler(logging.NullHandler())

# create console handler and set level to debug
con = logging.StreamHandler()
con.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('[%(asctime)s:%(name)s:%(levelname)s]: %(message)s')

# add formatter to ch
con.setFormatter(formatter)

# add ch to logger
logger.addHandler(con)

#==============================================================================

class Console(QPlainTextEdit):
    def __init__(self, prompt='>>>: ', startup_message='', parent=None):
        super(Console,self).__init__()
        self.setWindowTitle("ScopeScript console")
        QPlainTextEdit.__init__(self, parent)
        self._locals = {}
        self.prompt = prompt
        self.history = []
        self.namespace = {}
        self.construct = []
        self.api = api.API()


        self.setGeometry(50, 75, 600, 400)
        self.setWordWrapMode(QTextOption.WrapAnywhere)
        self.setUndoRedoEnabled(False)
        self.document().setDefaultFont(QFont("monospace", 10, QFont.Normal))
        self.showMessage(startup_message)
        self.newPrompt()

    def updateNamespace(self, namespace):
        self.namespace.update(namespace)

    def showMessage(self, message):
        self.appendPlainText(message)
        #self.newPrompt()

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

    def setHisory(self, history):
        self.history = history

    def addToHistory(self, command):
        if command and (not self.history or self.history[-1] != command):
            self.history.append(command)
        self.history_index = len(self.history)

    def getPrevHistoryEntry(self):
        if self.history:
            self.history_index = max(0, self.history_index - 1)
            return self.history[self.history_index]
        return ''

    def getNextHistoryEntry(self):
        if self.history:
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

#    def runCommand(self):
#        self.setWindowTitle("*python qt console*")
#
#
#        command = self.getCommand()
#        self.addToHistory(command)
#
#        command = self.getConstruct(command)
#
#        if command:
#            tmp_stdout = sys.stdout
#
#            class stdoutProxy():
#                def __init__(self, write_func):
#                    self.write_func = write_func
#                    self.skip = False
#
#                def write(self, text):
#                    if not self.skip:
#
#                        stripped_text = text.rstrip('\n')
#
#                        self.write_func(stripped_text)
#
#                        QCoreApplication.processEvents()
#                    self.skip = not self.skip
#
#            sys.stdout = stdoutProxy(self.appendPlainText)
#
#            try:
#                try:
#                    result = eval(command,globals(),self._locals)
#
#                    if result != None:
#                        self.appendPlainText(repr(result))
#                except SyntaxError:
#
#                    exec(command,globals(),self._locals)
#            except SystemExit:
#                self.close()
#            except:
#                traceback_lines = traceback.format_exc().split('\n')
#                # Remove traceback mentioning this file, and a linebreak
#                for i in (3,2,1,-1):
#                    traceback_lines.pop(i)
#
#                self.appendPlainText('\n'.join(traceback_lines))
#
#            sys.stdout = tmp_stdout
#        self.newPrompt()
#        self.setWindowTitle("python qt console")

    def scopeconnect(self):
        #coms = com.commands.commands
        self.setWindowTitle("*ScopeScript console*")


        command = self.getCommand()
        self.addToHistory(command)
        if command == '':
            self.newPrompt()
            self.setWindowTitle("ScopeScript console")
            return
        if command == 'help':
            self.showMessage(self.api.getHelpText())
            self.newPrompt()
            self.setWindowTitle("ScopeScript console")
            return
        else:
            try:
                agr = command.split("(")
                args = re.findall("\((.*)\)",command)
                comm = agr[0]
                #args = agr[1]
                arg = args[0].split(",")

                logger.debug("args = %s" % args)

                if arg:
                    logger.debug("Argument list is not None")
                else:
                    logger.debug("Argument list is none")

                self.showMessage("Sending Data To ScopePy... ")
                # --- connect to scopepy here! ---
                ok,error = self.api.sendCommand(comm,arg)
                if not ok:
                    self.showMessage("Error From ScopePy: %s" % error)
                else:
                    self.showMessage("ScopyPy liked your command.")




            except Exception as ec:
                self.showMessage("ConsoleError: Check your Command.")
                print(ec)
            #command = self.getConstruct(command)
            #print(type(command))
            self.newPrompt()
            self.setWindowTitle("ScopeScript console")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.scopeconnect()
            #self.runCommand()
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

            self.close()



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
        self.setCommand("quit()")
        self.runCommand()
welcome_message = '''
   ---------------------------------------------------------------
     Welcome to a triangledot ScopeScript  interpreter.
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
    #console.setWindowTitle("python qt console")
    #console.setCommand("import __main__ as main")
    #console.runCommand()
    input = fake_input
    console.show();
    sys.exit(app.exec_())
