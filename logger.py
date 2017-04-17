import os
def debug(msg):
    import inspect
    others = inspect.getouterframes(inspect.currentframe())[1] # 4
    print('[%s:%i:%s]: %s' % (os.path.split(others[1])[1],
        others[2],others[3],msg))
    
