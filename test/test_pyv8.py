import datetime
import PyV8


class Global(PyV8.JSClass):
    def __init__(self):
        # We must calculate the offset here because timezones are screwy
        self.offset = datetime.datetime.now()
        ctx = PyV8.JSContext(self)
        ctx.enter()
        self.offset = ctx.eval("offset") - self.offset

    def now(self):
        local = datetime.datetime.utcnow()
        return local - self.offset

    def out(self, string):
        print(string)


g = Global()
ctx = PyV8.JSContext(g)  # create another context with the global object
ctx.enter()

print("---------------------------")

javascript_global_now = ctx.eval("d=now();out('now()='+d);d")
print("javascript_global_now=%s, tz=%s" % (javascript_global_now, javascript_global_now.tzname()))
print("---------------------------")
javascript_now = ctx.eval("d=new Date();out('new Date()='+d);d")
print("GMT!!!! javascript_now=%s, tz=%s" % (javascript_now, javascript_now.tzname()))
print("---------------------------")

python_now = datetime.datetime.utcnow()
print("python_now=%s, tz=%s" % (python_now, python_now.tzname()))
