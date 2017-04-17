"""
Python CSS Reader/Writer

"""
## [errors]

class CsslibError(Exception):
    pass
## [read]
def passCss(filename):
    """
    Returns a dictionary of css from a file
    """
    f = open(filename,'r')
    lines = f.readlines()
    f.close()
    #print(lines)
    return baseCss(lines)
    
def baseCss(lines,add_vars=False):
    var = {}
    d = {}
    for i in lines:
        i.replace('\n','')
        i.replace('\r','')
        if '{' in i:
            ni = i.split('{')
            name = ni[0].strip()
            c = 0
            s1 = False
            ttgid = {}
            for nni in lines:
                
                if s1 == False:
                    if nni == i:
                        s1 = True
                    c += 1
                else:
                    if '}' in nni:
                        d[name]=ttgid
                        break
                    
                    s = nni.split(';')
                    #print(s)
                    if ':' in s[0]:
                        nl = s[0].split(':')
                        #print(nl)
                    #print(nl)
                    # [john] Use ":".join() to put anything with extra colons
                    # back together. Strip off spaces on value as well as key.
                    nnl = [nl[0].strip(),":".join(nl[1:]).strip()]
                    #print(nnl)
                    if nnl[1].startswith('$'):
                        try:
                            nnl[1] = var[nnl[1]]
                        except:
                            pass
                    if '/*' in nnl[0]:
                        pass
                    else:
                        ttgid[nnl[0]]=nnl[1]
                    #print(ttgid)
        elif i.startswith('$') and ':' in i:
            s = i.split(';')
            s = s[0].strip()
            v = s.split(':')
            var[v[0]]=v[1].strip()

    if add_vars:

        d['csslib_vars'] = var
    return d
    
def getCss(css):
    '''
    Returns a dictionary of css from a string
    css: string
    '''
    return baseCss(css.split('\n'))
    
def createCss(cssdict,filename):
    """
    Creates a css file from css dict
    """
    endstring = dictToCss(cssdict)
    f = open(filename,'w')
    f.write(endstring)
    f.flush()
    f.close()
    
    
def dictToCss(cssdict,replace_vars=True):
     """
     returnes css in string form, created from cssdict
     """
     endstring = ''
     if 'csslib_vars' in cssdict:
         for i in cssdict['csslib_vars']:
             endstring += '\n%s:%s;' % (i,cssdict['csslib_vars'][i])
     else:
         replace_vars = False
     
     for k in cssdict:
         if k != 'csslib_vars':
             i = cssdict[k]
             endstring += '\n%s{' % k
             for nk in i:
                 if replace_vars:
                     if i[nk] in list(cssdict['csslib_vars'].values()):
                         key = [k for k,v in list(cssdict['csslib_vars'].items()) if v==i[nk]][0]
                         #print(key)
                         #var = cssdict['csslib_vars'][key]
                         i[nk] = key
                 endstring += '\n    %s:%s;' % (nk,i[nk])

             endstring += '\n}'

     return endstring
                 
                    

    
    
