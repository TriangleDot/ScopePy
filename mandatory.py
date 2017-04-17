import inspect
class MandatoryError(Exception):
    pass
def check(args,argtypes):
    """
Arguments:
-----------
args: list of arguments
argtypes: list of argument types
info
-----
Checkes if mandatory args are the right type. If not, raises an error

Use:
------
>>> def function(s,l,v):
...     check([s,l,v],[str,list,bool])
...
>>>
"""
    c = 0
    for i in args:
        if not isinstance(i,argtypes[c]):
            raise MandatoryError("Argument # "+str(c)+" must be a "+str(argtypes[c])+" Not A "+str(type(i))+" " )
        c += 1
        if c > len(argtypes):
            return
def silentCheck(args,argtypes):
    """
Arguments:
-----------
args: list of arguments
argtypes: list of argument types
info
-----
The same as check, but instead or raising an error, it just returnes
(bool: False if error got caused.,int: argument that caused error: None if no errors.
Use:
------
>>> def function(s,l,v):
...     silentCheck([s,l,v],[str,list,bool])
...
>>>
"""
    c = 0
    for i in args:
        if not isinstance(i,argtypes[c]):
            return (False,c)
        c += 1
        if c > len(argtypes):
            return (True,None)
    
        
    

