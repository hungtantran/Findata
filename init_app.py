import sys


class FLAGS(object):
    def __init__(self):
        pass


def DEFINE_string(name, value):
    setattr(FLAGS, '%s_typeFlagVal' % name, type('string'))
    setattr(FLAGS, name, str(value) if value is not None else None)


def DEFINE_bool(name, value):
    setattr(FLAGS, '%s_typeFlagVal' % name, type(True))
    setattr(FLAGS, name, bool(value) if value is not None else None)


def DEFINE_float(name, value):
    setattr(FLAGS, '%s_typeFlagVal' % name, type(1.0) if value is not None else None)
    setattr(FLAGS, name, float(value))


def DEFINE_integer(name, value):
    setattr(FLAGS, '%s_typeFlagVal' % name, type(1) if value is not None else None)
    setattr(FLAGS, name, int(value))


def InitPythonPath():
    sys.path.append('.')
    sys.path.append('AnalyticPipeline')
    sys.path.append('Common')
    sys.path.append('Database')
    sys.path.append('DatabaseModel')
    sys.path.append('QueryService')
    sys.path.append('SEC')
    sys.path.append('Scripts')
    sys.path.append('UpdatePipeline')

    sys.path.append('gen-py')
    sys.path.append('gen-py/models')


def InitApp():
    for i in range(1, len(sys.argv)):
        arg = sys.argv[i]
        index = arg.find('=')
        if index == -1:
            continue

        name = arg[:index]
        value = arg[index+1:]

        typeVal = getattr(FLAGS, '%s_typeFlagVal' % name)
        val = None
        if (typeVal == type(True)):
            val = True if value == 'True' else False
        elif (typeVal == type('string')):
            val = value
        elif (typeVal == type(0)):
            val = int(value)
        elif (typeVal == type(1.0)):
            val = float(value)

        setattr(FLAGS, name, val)
        print('Set flag %s to %s' % (name, value))


InitPythonPath()
