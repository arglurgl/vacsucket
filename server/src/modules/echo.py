import libs.modules as m

def echo(parameter):
    m.log.info("Got echo parameter: " + parameter)
    return parameter

m.register("echo", echo)
