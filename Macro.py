# -*- coding: utf-8 -*-
"""
Created on Sat May 23 13:33:19 2015

@author: finn

Triangledot on KDE
"""
#Triangledot
import os
def addMacro(name,path):
    
        
    f = open(os.path.join(os.path.expanduser("~"),".ScopePy","macro.ini"),"r")
    r = f.read()
    f.close()
    if name == '' or path == '':
        return
    f = open(os.path.join(os.path.expanduser("~"),".ScopePy","macro.ini"),"w")
    print(name)
    r+='\n'+name+":"+path+';'
    f.write(r)
    f.flush()
    f.close()
    
def getMacros():
    if os.path.exists(os.path.join(os.path.expanduser("~"),".ScopePy","macro.ini")) == False:
        os.mkdir(os.path.join(os.path.expanduser("~"),".ScopePy"))
        f=open(os.path.join(os.path.expanduser("~"),".ScopePy",'test.py'),'w')
        f.write('API.newTab("Test")\nAPI.newPlot("test")')
        f.flush()
        f.close()
        m = open(os.path.join(os.path.expanduser("~"),".ScopePy","macro.ini"),'w')
        m.writelines(['test:%s;' % os.path.join(os.path.expanduser("~"),".ScopePy",'test.py')])
        m.flush()
        m.close()
        getMacros()
        
    f = open(os.path.join(os.path.expanduser("~"),".ScopePy","macro.ini"),"r")
    r = f.readlines()
    f.close()
    extract = {}
    for i in r:
        
        a = i.split(":",-1)
        print('a='+str(a))
        nl = []
        for i in a:
            i = i.replace('\n','')
            print(i)
            i = i.replace(';','')
            nl.append(i)
            print(nl)
        print(extract)
        extract[nl[0]]=nl[1]
        print(extract)
    return extract