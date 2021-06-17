def reload(mod):
    import sys
    mod_name = mod.__name__
    del sys.modules[mod_name]
    # return __import__(mod_name)


def unload(mod):
    #removes module from the system
    mod_name = mod.__name__
    import sys
    if mod_name in sys.modules:
        del sys.modules[mod_name]

# def run(mod):
#     #executes a module (python file without .py)
#     #import would only run it once
#     unload(mod)
#     __import__(mod.__name__)

# Remove file or tree

def rm(d):
    import os
    try:
        if os.stat(d)[0] & 0x4000:  # Dir
            for f in os.ilistdir(d):
                if f[0] not in ('.', '..'):
                    rm("/".join((d, f[0])))  # File or Dir
            os.rmdir(d)
        else:  # File
            os.remove(d)
    except:
        print("rm of '%s' failed" % d)