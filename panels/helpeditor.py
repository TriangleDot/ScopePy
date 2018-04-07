import ScopePy_panels as panels

from qt_webview import QWebView
from panels.PyConsole import WebView
from qt_imports import *
import refclass
import simpleQt as sqt
import os

class panel(sqt.SimpleBase):
    def drawPanel(self):
        self.filename = None
        self.edit = QTextEdit(self)
        self.webview = WebView(self)
        self.position([[self.edit,self.webview]])

        self.highlighter = XMLHighlighter(self.edit.document())

    def setFkeys(self):

        self.Fkeys = [
                     ['F5','Run!',self.run],
                     ['F6','Open',self.open],
                     ['F8','Save',self.save],
                     ]
    def open(self):
        fname = QFileDialog.getOpenFileName(self,'Open',self.API.filePath)
        with open(fname,'r') as f:
            txt = f.read()
        self.edit.setPlainText(txt)
        self.filename = fname
        self.API.filepath = os.path.split(self.filename)[0]

    def saveas(self):
        fname = QFileDialog.getSaveFileName(self,'Save',self.API.filepath)
        with open(fname,'w') as f:
            f.write(self.edit.toPlainText())
        self.filename = fname
        self.API.filepath = os.path.split(self.filename)[0]
    def save(self):
        if self.filename == None:
            self.saveas()
            return
        with open(self.filename,'w') as f:
            f.write(self.edit.toPlainText())
    def run(self):
        txt = self.edit.toPlainText()
        lines = txt.split('\n')
        c,title = lines[0].split(':')
        lines.pop(0)
        txt = '\n'.join(lines)
        if c == 'title ':
            pass
        else:
            title='No Title!'

        w = refclass.htmlWrapper(title)
        w.html = txt
        with open(os.path.join(os.path.expanduser('~'),'.ScopePy','helptmp.html'),'w') as f:
            f.write(w.html)
        url = QUrl(os.path.join(os.path.expanduser('~'),'.ScopePy','helptmp.html'))
        self.webview.setUrl(url)


__panels__ = {'Help Editor':panels.PanelFlags(panel)}



# ============================================================================
#%% Syntax highlighter
# ============================================================================
# Taken off the web

class XMLHighlighter(QSyntaxHighlighter):

    #INIT THE STUFF
    def __init__(self, parent=None):
        super(XMLHighlighter, self).__init__(parent)

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(Qt.darkMagenta)
        keywordFormat.setFontWeight(QFont.Bold)

        keywordPatterns = ["\\b?xml\\b", "/>", ">", "<"]

        self.highlightingRules = [(QRegExp(pattern), keywordFormat)
                for pattern in keywordPatterns]

        xmlElementFormat = QTextCharFormat()
        xmlElementFormat.setFontWeight(QFont.Bold)
        xmlElementFormat.setForeground(QColor(36,217,255))
        self.highlightingRules.append((QRegExp("\\b[A-Za-z0-9_]+(?=[\s/>])"), xmlElementFormat))

        xmlAttributeFormat = QTextCharFormat()
        xmlAttributeFormat.setFontItalic(True)
        xmlAttributeFormat.setForeground(QColor(217,0,217))
        self.highlightingRules.append((QRegExp("\\b[A-Za-z0-9_]+(?=\\=)"), xmlAttributeFormat))

        self.valueFormat = QTextCharFormat()
        self.valueFormat.setForeground(Qt.darkYellow)

        self.valueStartExpression = QRegExp("\"")
        self.valueEndExpression = QRegExp("\"(?=[\s></])")

        singleLineCommentFormat = QTextCharFormat()
        singleLineCommentFormat.setForeground(Qt.gray)
        self.highlightingRules.append((QRegExp("<!--[^\n]*-->"), singleLineCommentFormat))

    #VIRTUAL FUNCTION WE OVERRIDE THAT DOES ALL THE COLLORING
    def highlightBlock(self, text):

        #for every pattern
        for pattern, format in self.highlightingRules:

            #Create a regular expression from the retrieved pattern
            expression = QRegExp(pattern)

            #Check what index that expression occurs at with the ENTIRE text
            index = expression.indexIn(text)

            #While the index is greater than 0
            while index >= 0:

                #Get the length of how long the expression is true, set the format from the start to the length with the text format
                length = expression.matchedLength()
                self.setFormat(index, length, format)

                #Set index to where the expression ends in the text
                index = expression.indexIn(text, index + length)

        #HANDLE QUOTATION MARKS NOW.. WE WANT TO START WITH " AND END WITH ".. A THIRD " SHOULD NOT CAUSE THE WORDS INBETWEEN SECOND AND THIRD TO BE COLORED
        self.setCurrentBlockState(0)

        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.valueStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self.valueEndExpression.indexIn(text, startIndex)

            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.valueEndExpression.matchedLength()

            self.setFormat(startIndex, commentLength, self.valueFormat)

            startIndex = self.valueStartExpression.indexIn(text, startIndex + commentLength);
