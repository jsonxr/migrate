import datetime
import unittest
import PyV8


#=============================================================================
# Schema Yml Tests
#=============================================================================

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


class TestJavascript(unittest.TestCase):

    def test_javascript(self):
        ctxt = PyV8.JSContext()           # create a context with an implicit global object
        ctxt.enter()                      # enter the context (also support with statement)
        value = ctxt.eval("1+2")
        assert value == 3

    def test_javascript_withglobal(self):
        ctx = PyV8.JSContext(Global())  # create another context with the global object
        ctx.enter()
        js_global_now = ctx.eval("now()")
        js_now = ctx.eval("new Date()") + datetime.timedelta(seconds=1)
        py_now = datetime.datetime.utcnow() + datetime.timedelta(seconds=2)
        print("js_global_now=%s" % js_global_now)
        print("js_now=%s" % js_now)
        print("py_now=%s" % py_now)

        assert type(js_now) is datetime.datetime
        assert js_global_now <= js_now
        assert js_now <= py_now


#=============================================================================
# main
#=============================================================================

def main():
    unittest.main()

if __name__ == '__main__':
    main()
