
'''
Help on refclass script: Use htmlWrapper to compile this script
    --< : start list
    --+ : list item
    >-- : end list

    ++< paragraph start
    >++ paragraph end

    %->%  name of title:    create reference to title

    %*% : title

    --( : start code

    )-- : end code

    #!#rrggbb:: color

    #$: bold

functions:
    toHtml
    moduleToHtml
    functionToHtml
    classToHtml


'''
import inspect
a = None
def toHtml(text,title):
    '''
refclass script compiler. OUT OF DATE
Use refclass.htmlWrapper for new version
'''
    
    startHtml = '''
<html>
<title> ScopePy HelpPage: %s </title>
<style>
/* ScopePy colours:
 
  ffaa00 = oramge
  ffa02f = orange
  d7801a = darker orange
  ca0619 = red
  b1b1b1 = light grey
  7EE4A0 = light green
  323232 = dark grey
  343434 = dark grey
  212121 = darker grey
  1e1e1e = even darker grey
  000000 = black
*/


h1, h2 { color: red;
     background-color: #343434;
     border-width: 5px;
     /* /* width: 800px */ */;
     padding: 8px;
	border-style: double;
       border-color: #ffa02f; 
       margin-left: 8px;}
       
body { font-family: "Liberation Serif", serif;
       color: #ffaa00;
       
       background-color: black;
        }
                                          
p { text-align: justify;
    text-indent: 1em; 
    color: #ffa02f;
    background-color: #323232 }

b { text-align: justify;
    text-indent: 1em; 
    color: #d7801a;
    background-color: #323232 }
    
a { text-align: justify;
    text-indent: 5em; 
    color: white;
    background-color: #0055ff }
pre { font-weight: bold;
    color: green;
    /*margin-left: 30px;*/
    /* width: 800px */
    background-color: white;
    border-style: groove;
    border-color: blue;
    /*padding: 8px;*/}

ul { list-style-type: disk; }

h1, h2 { border-bottom: 1px vlack dashed; }

.p_wrapper {margin-left: 8px;
			padding: 8px;
			background: #323232;
			/* width: 800px */;
			border-style: outset;
			border-color: #b1b1b1;
			}

.sp_bullets {
	list-style-type: square;
	}
.sidebar {
	border-style: groove;
    border-color: #d7801a;
	background-color: #323232;
	/*position: absolute;*/
	padding: 0px;
	width: 280px;
	side: right;
	
}
.inside {
	background-color: black;
	/*position: absolute;*/
	padding: 0;
	
	
}
</style>
<body>
<h1>%s</h1>
!fp
<a>Made Using ScopePy's Html Genorator</a>
</body>
</html>''' % (title,title)
    lines = text.split('\n')
    endHtml = ''
    #print(lines)
    for e, i in enumerate(lines):
        na = True
        ni = i
        if '++<' in i:
            endHtml += '\n <div class="p_wrapper"><p>'
            na = False
            ni = i.replace('++<','')
            #print('p: ',endHtml)

        if '>++' in i:
            endHtml += '\n </p></div><br>'  # Daddy Tweak added <br>
            na = False
            ni = i.replace('>++','')
            #print('pe: ',endHtml)

        if '--<' in i:
            endHtml += '\n <div class="p_wrapper"> <p> <div class="sp_bullets">'
            na = False
            ni = i.replace('--<','')

        if '>--' in i:
            endHtml += '\n </div></p></div>'
            na = False
            ni = i.replace('>--','')

        if '--+' in i:
            ni = i.replace('--+','')
            endHtml += '\n <li><p>%s</li></p>' % ni
            na = False

        if '--(' in i:
            endHtml += '\n <pre><br>'
            na = False
            ni = i.replace('--(','')

            #print('c: ',endHtml)

        if ')--' in i:
            endHtml += '\n </pre><br>'
            na = False
            ni = i.replace(')--','')
            #print('ce: ',endHtml)

        if '%*%' in i:
            ni = i.replace('%*%','')
            endHtml += '\n <li><h3><a name="%s" />%s</h3></li>' % (ni,ni)
            na = False

        if '%<-%' in i:
            ni = i.replace('%<-%','')
            endHtml += '\n <a name="%s" />' % (ni)
            na = False

        if '#!' in i:
            ei = i.replace('#!','')
            colors = ei.split('::')
            endHtml += '\n <font color=%s>%s</font>' % (colors[0],colors[1])
            na = False

        if '#$' in i:
            ni = i.replace('#$','')
            
            endHtml += '\n<b>%s</b>' % ni
            na = False

        if '%->%' in i:
            ni = i.replace('%->%','')
            link, ni = ni.split(':')
            endHtml += '\n <li><a href="tmp.html#%s">%s </a></li>' % (link,ni) # TODO: in ScopePy, always save to file tmp.html

        if na:
            endHtml += ni+' ' # [Daddy tweak] +'<br>' - removed so that words wrap better at different sizes

    nnba = startHtml.replace('!fp',endHtml)
    return nnba

        

        
        

        

        
        
    
    


def moduleToHtml(module,title,c='module'):
    '''
Compiles a module to html
'''
    classobj = module
    other = ''
    if hasattr(classobj,'__version__'):
        other += '<b><font color="purple">Version:</font> </b>%s' % str(classobj.__version__)

    if hasattr(classobj,'__credits__'):
        ncredits = classobj.__credits__.replace('\n','<br>')
        other += '<br><b><font color="#4bd3ff">Credits:</font> </b>%s' % str(ncredits)
    
        
    startHtml = '''
<html>
<title>SCOPEPY: Reference of %s </title>

<style>
/* ScopePy colours:
 
  ffaa00 = oramge
  ffa02f = orange
  d7801a = darker orange
  ca0619 = red
  b1b1b1 = light grey
  7EE4A0 = light green
  323232 = dark grey
  343434 = dark grey
  212121 = darker grey
  1e1e1e = even darker grey
  000000 = black
*/


h1, h2 { color: red;
     background-color: #343434;
     border-width: 5px;
     /* width: 800px */;
     padding: 8px;
	border-style: double;
       border-color: #ffa02f; 
       margin-left: 8px;}
       
body { font-family: "Liberation Serif", serif;
       color: #ffaa00;
       
       background-color: black;
        }

table { font-family: "Liberation Serif", serif;
       color: #ffaa00;
       
       background-color: black;
        }
                                          
p { text-align: justify;
    text-indent: 1em; 
    color: white;
    background-color: #323232 }

b { text-align: justify;
    text-indent: 1em; 
    color: #d7801a;
    background-color: #323232 }
    
a { text-align: justify;
    text-indent: 5em; 
    color: white;
    background-color: #0055ff }
pre { font-weight: bold;
    color: green;
    margin-left: 30px;
    /* width: 800px */;
    background-color: white;
    border-style: groove;
    border-color: blue;
    padding: 8px;}

ul { list-style-type: disk; }

h1, h2 { border-bottom: 1px vlack dashed; }

.p_wrapper {margin-left: 8px;
			padding: 8px;
			background: #323232;
			/* width: 800px */;
			border-style: outset;
			border-color: #b1b1b1;
			}

.sp_bullets {
	list-style-type: square;
	}
.sidebar {
	border-style: groove;
    border-color: #d7801a;
	background-color: #323232;
	/*position: absolute;*/
	padding: 0px;
	width: 280px;
	side: right;
	
}
.inside {
	background-color: black;
	/*position: absolute;*/
	padding: 0;
	
	
}
.class1 {
    border-color: #5cce49;
    border-style: groove;
}
.class2 {
    border-color: #4c29ff;
    border-style: groove;
}
</style>
<body>
<h1>%s</h1>
<br>
<div class="p_wrapper"><p>
%s
</div>
</p></div>
<br>
<br>
<div class="class1">
<p>
!fp
</p></div>
<a>Made Using ScopePy's Html Genorator</a>
</body>
</html>''' % (title,title,other)
    #lines = text.split('\n')
    endHtml = ''
    #print(lines)
    data = {}
    endHtml += '\n <div class="p_wrapper"><h4>Help for this %s:</h4><pre>%s</pre></div><br><br><br>' % (c,inspect.getdoc(classobj))
    for i in classobj.__dict__:
        ni = classobj.__dict__[i]
        if inspect.isfunction(ni):
            a = inspect.getfullargspec(ni)
            docs = inspect.getdoc(ni)
            if docs != None:
                ndocs = docs.replace('\n','<br>')
            else:
                ndocs = 'No Avalible Documentation For This Function'
            endHtml += '''<div class="p_wrapper">
\n<font color="#ca0619">function </font><b>%s (args=%s)</b>
<br><p>%s</p></div><br><br>
''' % (i,str(a.args),functionHelp(ndocs))

        elif inspect.isclass(ni):
            endHtml += classToHtml(ni,i,jc=True)
        else:
            data[i]=ni

    for i in data:
        if type(data[i]) == property:
            endHtml += '''<div class="p_wrapper">
\n<font color="#e458c0">property </font><b>%s</b>
<br></div><br><br> ''' % i
            
    endHtml += '</div><br><br>'
    
    endHtml+= '''<table border="1" style="width:100%">
<tr>
    <th>Name</th>
    <th>Value</th>
    <th>Type</th>
  </tr>'''
    for i in data:
        '''
        <table border="1" style="width:100%">
  <tr>
    <td>Jill</td>
    <td>Smith</td> 
    <td>50</td>
  </tr>
  <tr>
    <td>Eve</td>
    <td>Jackson</td> 
    <td>94</td>
  </tr>
</table>
'''
        k = i
        i = data[k]
        value = str(i).replace('<','')
        value = value.replace('>','')
        ntype = str(type(i)).replace('<','')
        ntype = value.replace('>','')
        
        endHtml += '''
<tr>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
  </tr>
        ''' % (k,value,ntype)
        
        

            
    endHtml += '\n '
    nnba = startHtml.replace('!fp',endHtml)
    return nnba
        
def functionToHtml(func):
    '''
compiles a function to html
'''
    
    startHtml = '''
<style>
/* ScopePy colours:
 
  ffaa00 = oramge
  ffa02f = orange
  d7801a = darker orange
  ca0619 = red
  b1b1b1 = light grey
  7EE4A0 = light green
  323232 = dark grey
  343434 = dark grey
  212121 = darker grey
  1e1e1e = even darker grey
  000000 = black
*/


h1, h2 { color: red;
     background-color: #343434;
     border-width: 5px;
     /* width: 800px */;
     padding: 8px;
	border-style: double;
       border-color: #ffa02f; 
       margin-left: 8px;}
       
body { font-family: "Liberation Serif", serif;
       color: #ffaa00;
       
       background-color: black;
        }

table { font-family: "Liberation Serif", serif;
       color: #ffaa00;
       
       background-color: black;
        }
                                          
p { text-align: justify;
    text-indent: 1em; 
    color: white;
    background-color: #323232 }

b { text-align: justify;
    text-indent: 1em; 
    color: #d7801a;
    background-color: #323232 }
    
a { text-align: justify;
    text-indent: 5em; 
    color: white;
    background-color: #0055ff }
pre { font-weight: bold;
    color: green;
    margin-left: 30px;
    /* width: 800px */;
    background-color: white;
    border-style: groove;
    border-color: blue;
    padding: 8px;}

ul { list-style-type: disk; }

h1, h2 { border-bottom: 1px vlack dashed; }

.p_wrapper {margin-left: 8px;
			padding: 8px;
			background: #323232;
			/* width: 800px */;
			border-style: outset;
			border-color: #b1b1b1;
			}

.sp_bullets {
	list-style-type: square;
	}
.sidebar {
	border-style: groove;
    border-color: #d7801a;
	background-color: #323232;
	/*position: absolute;*/
	padding: 0px;
	width: 280px;
	side: right;
	
}
.inside {
	background-color: black;
	/*position: absolute;*/
	padding: 0;
	
	
}
.class1 {
    border-color: #5cce49;
    border-style: groove;
}
.class2 {
    border-color: #4c29ff;
    border-style: groove;
}
</style>
<body>
!fp
</body>
<a>Made Using ScopePy's Html Genorator</a>
'''
    endHtml = ''
    a = inspect.getfullargspec(func)
    docs = inspect.getdoc(func)
    if docs != None:
        ndocs = docs.replace('\n','<br>')
    else:
        ndocs = 'No Avalible Documentation For This Function'
    endHtml += '''<div class="p_wrapper">
\n<font color="#ca0619">function </font><b>%s (args=%s)</b>
<br><p>%s</p></div><br><br>
''' % (func.__name__,str(a.args),functionHelp(ndocs))
    endHtml += '\n</body></html>'
    nnba = startHtml.replace('!fp',endHtml)
    return nnba
    
def classToHtml(classobj,title,c='class',jc = False):
    '''
compiles a class object into html
'''
    
    other = ''
    if hasattr(classobj,'__version__'):
        other += '<b><font color="purple">Version:</font> </b>%i' % classobj.__version__

    if hasattr(classobj,'__credits__'):
        ncredits = classobj.__credits__.replace('\n','<br>')
        other += '<br><b><font color="#4bd3ff">Credits:</font> </b>%s' % ncredits
    
        
    startHtml = '''
<html>
<title>SCOPEPY: Reference of %s </title>

<style>
/* ScopePy colours:
 
  ffaa00 = oramge
  ffa02f = orange
  d7801a = darker orange
  ca0619 = red
  b1b1b1 = light grey
  7EE4A0 = light green
  323232 = dark grey
  343434 = dark grey
  212121 = darker grey
  1e1e1e = even darker grey
  000000 = black
*/


h1, h2 { color: red;
     background-color: #343434;
     border-width: 5px;
     /* width: 800px */;
     padding: 8px;
	border-style: double;
       border-color: #ffa02f; 
       margin-left: 8px;}
       
body { font-family: "Liberation Serif", serif;
       color: #ffaa00;
       
       background-color: black;
        }

table { font-family: "Liberation Serif", serif;
       color: #ffaa00;
       
       background-color: black;
        }
                                          
p { text-align: justify;
    text-indent: 1em; 
    color: white;
    background-color: #323232 }

b { text-align: justify;
    text-indent: 1em; 
    color: #d7801a;
    background-color: #323232 }
    
a { text-align: justify;
    text-indent: 5em; 
    color: white;
    background-color: #0055ff }
pre { font-weight: bold;
    color: green;
    margin-left: 30px;
    /* width: 800px */;
    background-color: white;
    border-style: groove;
    border-color: blue;
    padding: 8px;}

ul { list-style-type: disk; }

h1, h2 { border-bottom: 1px vlack dashed; }

.p_wrapper {margin-left: 8px;
			padding: 8px;
			background: #323232;
			/* width: 800px */;
			border-style: outset;
			border-color: #b1b1b1;
			}

.sp_bullets {
	list-style-type: square;
	}
.sidebar {
	border-style: groove;
    border-color: #d7801a;
	background-color: #323232;
	/*position: absolute;*/
	padding: 0px;
	width: 280px;
	side: right;
	
}
.inside {
	background-color: black;
	/*position: absolute;*/
	padding: 0;
	
	
}
.class1 {
    border-color: #5cce49;
    border-style: groove;
}
.class2 {
    border-color: #4c29ff;
    border-style: groove;
}
</style>
<body>
<h1>%s</h1>
<br>
<div class="p_wrapper"><p>
%s
</div>
</p></div>
<br>
<br>
<div class="class1">
<p>
!fp
</p></div>
<a>Made Using ScopePy's Html Genorator</a>
</body>
</html>''' % (title,title,other)
    #lines = text.split('\n')
    endHtml = ''
    #print(lines)
    data = {}
    endHtml += '\n<div class="p_wrapper"> <h4>Help for %s %s:</h4><pre>%s</pre><br><div class="class2"><br><br>' % (c,title,inspect.getdoc(classobj))
    for i in classobj.__dict__:
        ni = classobj.__dict__[i]
        if inspect.isfunction(ni):
            a = inspect.getfullargspec(ni)
            docs = inspect.getdoc(ni)
            if docs != None:
                ndocs = docs.replace('\n','<br>')
            else:
                ndocs = 'No Avalible Documentation For This Function'
            endHtml += '''<div class="p_wrapper">
\n<font color="#ca0619">function </font><b>%s (args=%s)</b>
<br><p>%s</p></div><br><br>
''' % (i,str(a.args),functionHelp(ndocs))

        
        else:
            data[i]=ni

    for i in data:
        if type(data[i]) == property:
            endHtml += '''<div class="p_wrapper">
\n<font color="#e458c0">property </font><b>%s</b>
<br></div><br><br> ''' % i
            
    endHtml += '</div></div><br><br>'
    
##    endHtml+= '''<table border="1" style="width:100%">
##<tr>
##    <th>Name</th>
##    <th>Value</th>
##    <th>Type</th>
##  </tr>'''
##    for i in data:
##        '''
##        <table border="1" style="width:100%">
##  <tr>
##    <td>Jill</td>
##    <td>Smith</td> 
##    <td>50</td>
##  </tr>
##  <tr>
##    <td>Eve</td>
##    <td>Jackson</td> 
##    <td>94</td>
##  </tr>
##</table>
##'''
##        k = i
##        i = data[k]
##        value = str(i).replace('<','')
##        value = value.replace('>','')
##        ntype = str(type(i)).replace('<','')
##        ntype = value.replace('>','')
##        
##        endHtml += '''
##<tr>
##    <td>%s</td>
##    <td>%s</td>
##    <td>%s</td>
##  </tr>
##        ''' % (k,value,ntype)
        
        

            
    endHtml += '\n </div>'
    if jc:
        return endHtml
    
    nnba = startHtml.replace('!fp',endHtml)
    return nnba



baseHtml = '''
<html>
<title>SCOPEPY: Reference of %s </title>

<style>
/* ScopePy colours:
 
  ffaa00 = oramge
  ffa02f = orange
  d7801a = darker orange
  ca0619 = red
  b1b1b1 = light grey
  7EE4A0 = light green
  323232 = dark grey
  343434 = dark grey
  212121 = darker grey
  1e1e1e = even darker grey
  000000 = black
*/


h1, h2 { color: red;
     background-color: #343434;
     border-width: 5px;
     /* width: 800px */;
     padding: 8px;
	border-style: double;
       border-color: #ffa02f; 
       margin-left: 8px;}
       
body { font-family: "Liberation Serif", serif;
       color: #ffaa00;
       
       background-color: black;
        }

table { font-family: "Liberation Serif", serif;
       color: #ffaa00;
       
       background-color: black;
        }
                                          
p { text-align: justify;
    text-indent: 1em; 
    color: white;
    background-color: #323232 }

b { text-align: justify;
    text-indent: 1em; 
    color: #d7801a;
    background-color: #323232 }
    
a { text-align: justify;
    text-indent: 5em; 
    color: white;
    background-color: #0055ff }
pre { font-weight: bold;
    color: green;
    margin-left: 30px;
    /* width: 800px */;
    background-color: white;
    border-style: groove;
    border-color: blue;
    padding: 8px;}

ul { list-style-type: disk; }

h1, h2 { border-bottom: 1px vlack dashed; }

.p_wrapper {margin-left: 8px;
			padding: 8px;
			background: #323232;
			/* width: 800px */;
			border-style: outset;
			border-color: #b1b1b1;
			}

.sp_bullets {
	list-style-type: square;
	}
.sidebar {
	border-style: groove;
    border-color: #d7801a;
	background-color: #323232;
	/*position: absolute;*/
	padding: 0px;
	width: 280px;
	side: right;
	
}
.inside {
	background-color: black;
	/*position: absolute;*/
	padding: 0;
	
	
}
.class1 {
    border-color: #5cce49;
    border-style: groove;
}
.class2 {
    border-color: #4c29ff;
    border-style: groove;
}
</style>
<body>
<h1>%s</h1>
<br>
<div class="p_wrapper"><p>
%s
</div>
</p></div>
<br>
<br>
<div class="class1">
<div class="p_wrapper"><p>
!fp
</div></p></div>
<a>Made Using ScopePy's Html Genorator</a>
</body>
</html>''' 

def functionHelp(helptext,splitter='<br>'):
    lines = helptext.split(splitter)
    #et = '<ul>'
    et = ''
    incode = False
    done=False
    #print(lines)
    for e,i in enumerate(lines):
        try:
            nl = lines[e+1]
            doendbit = True
        except IndexError:
            #print('Last Line!')
            doendbit = False
        i = i.replace('>','&gt;')
        #i = i.replace('    ','&#09;')
        #i = i.replace('\t','&#09;')
        if doendbit:
            if nl.startswith('---'):
                et += '<u><h3>'+i+'</h3></u>'
                lines.pop(e+1)
                done=True
            elif nl.startswith('==='):
                et += '<u><h2>'+i+'</h2></u>'
                lines.pop(e+1)
                done=True
            elif nl.startswith('    ') or nl.startswith('\t'):
                it = i.split(':')
                try:
                    et += '<b>%s</b>:<em>%s</em><br>' % (it[0],it[1])
                    done=True
                except IndexError:
                    pass
                

        

        if i.startswith('&gt;&gt;&gt;') and incode==False: 
            
            et += '<pre>%s' % i
            incode = True
            done=True
        if incode == True and i.startswith('&gt;&gt;&gt;') == False and i.startswith('...')  == False:
            et += '</pre>'
            incode = False

        if i.startswith('*'):
            i.replace('*','')
            
            et+='<li>%s</li>' % i
            done=True
        if i.startswith('  ') or i.startswith('\t'):
            i = i.strip()
            et += '&nbsp;&nbsp;&nbsp;&nbsp;<em>%s</em>' % i
            done = True
            
        if done == False:
            et += '%s' % i
        done = False
        et += '<br>\n'

    #et += '</ul>'
    return et
        
            
            
            
            
        
class htmlWrapper(object):
        '''
w = htmlWrapper(title)
w.html = refclass script
w.html --> pure html (compiled refclass script)
'''
        
        def __init__(self,title='Help'):
            self._html = ''
            self.title = title
        
        
        
        @property
        def html(self):
            return toHtml(self._html,self.title)

        @html.setter
        def html(self,item):
            self._html = item

        





