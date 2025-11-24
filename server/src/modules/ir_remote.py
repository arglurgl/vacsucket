import lib.modules as m
from lib.serial_defaults import con

if con:
    def ir_send(parameter):
            con.write(parameter.encode("utf-8"))
            return "serial send: " + parameter

m.register("s", ir_send)
