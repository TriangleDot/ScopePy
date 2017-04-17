# -*- coding: utf-8 -*-
"""
Created on Sat Sep 26 09:31:47 2015

@author: finn

Triangledot on KDE
"""
#Triangledot
import simpleQt as sqt
from PyQt4.QtGui import QFileDialog, QKeySequence, QSizePolicy
import ScopePy_panels as panel 
import numpy as np
import csslib as cl
import os



class runner(sqt.SimpleBase):
    def drawPanel(self):
#        try:
#            ros = cl.passCss(os.join(os.path.expanduser('~'),'.ScopePy','openatstart.css'))
#            nos = True
#            
#        except:
#            nos = False
#            
#        if nos:
#            rd = ros['scripts']
#            for i in rd:
#                try:
#                    exec(open(i,'r').read(),globals(),{'API':self.API})
#                except Exception as ex:
#                    print('Error: %s' % ex)
#                    
        self.addCommsAction('addScript',self.add)
            
        mainframe = sqt.frame(self)
        label1 = sqt.label(mainframe,'<h3><b> The Runner that runs python scripts:<br> A:add|R:Run|P:Run With Python Editor</b></h3>')
        label = sqt.label(mainframe,'Select script to run with Alt+&3')
        run = sqt.button(mainframe,'Run!')
        add = sqt.button(mainframe,'Add!')
        pyedit = sqt.button(mainframe,'Run With Python Editor!')
        self.c = sqt.combobox(mainframe)
        self.c.widget.setMaximumWidth(250)
        self.c.widget.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
        css = self.getcss()
        if css != None:
            for i in css:
                self.c.addItem(i)
        run.bindClicked(self.run)
        pyedit.bindClicked(self.pyeditRun)
        run.widget.setShortcut(QKeySequence("R"))
        pyedit.widget.setShortcut(QKeySequence("P"))
        add.widget.setShortcut(QKeySequence("A"))
        add.bindClicked(self.adder)
        label.widget.setBuddy(self.c.widget)
        mainframe.position([[label1,sqt.empty()],[label,sqt.empty()],[self.c,run],[sqt.empty(),add],[sqt.empty(),pyedit]])
        self.position([[mainframe],[sqt.empty()],[sqt.empty()],[sqt.empty()]])
        
        
        
        
    def add(self,scriptname):
        try:
            ros = cl.passCss(os.path.join(os.path.expanduser('~'),'.ScopePy','openatstart.css'))
            print(ros)
            nos = True
            print(ros['scripts'])
            
        except Exception as ec:
            print(ec)
            nos = False
            
        if nos:
            ros['scripts'][scriptname]=''
            print(ros)
            #nos = True
            print(ros['scripts'])
        else:
            ros = {'scripts':{scriptname:''}}
        cl.createCss(ros,os.path.join(os.path.expanduser('~'),'.ScopePy','openatstart.css'))
        
    def getcss(self):
       try:
           ros = cl.passCss(os.path.join(os.path.expanduser('~'),'.ScopePy','openatstart.css'))
           print(ros)
           print(ros['scripts'])
           return ros['scripts']
       except:
           pass
       
    def adder(self):
        filename = QFileDialog.getOpenFileName(self, 'Open file',os.path.expanduser('~'),'''python files (*.py);;All files (*)''')
        self.add(filename)
        self.c.addItem(filename)
        
    def run(self):
        fname = self.c.currentText
        try:
            exec(open(fname,'r').read(),globals(),{'API':self.API})
        except Exception as ex:
            print('Error: %s' % ex)

    def pyeditRun(self):
        fname = self.c.currentText
        try:
            panel = self.API.addPanel2MainArea('Python Editor')
        except:
            print('No Python Editor')
            return
        panel.openAndRun(fname)
                   
    def helptext(self):
        print('***********************************')
        print('    Help Text')
        print('add: scriptname')
        print('run')
        print('signal: addScript:scriptname')
        print('***********************************')
        
__panels__ = {"runner Alt-&2":panel.PanelFlags(runner,
                                                  open_on_startup=True,
                                                  location='sidebar',
                                                  has_gui=True,
                                                  on_panel_menu=False)}
