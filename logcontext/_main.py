import logging
import threading

from contextlib import contextmanager
from contextvars import ContextVar

context = ContextVar("context")

_main_context = threading.local()

logger = logging.getLogger("logcontext")

class _Context:
    def __init__(self, parent, msg, *args, level=logging.DEBUG, trace_level=None):
        self.parent = parent
        self.children = set()
        self.msg = msg
        self.args = args
        self.level = level
        self.trace = trace_level
        self._ctx = None

    def __enter__(self):
        if self._ctx is not None:
            raise RuntimeError("Context %r entered twice")
        if self.parent is not None:
            self.parent.children.add(self)
        self._ctx = context.set(self)
        if self.trace is not None:
            self._log(level=self.trace, add=">> ")

        return self

    def __exit__(self, et,ev,etb):
        context.reset(self._ctx)
        if self.trace is not None:
            self._log(level=self.trace, add="<< " if ev is None else "<E ")
        if self.parent is not None:
            self.parent.children.remove(self)
        self._ctx = None

    def _log(self, indent=0, add="", level=logging.DEBUG):
        if callable(self.msg):
            msg,args = msg(*self.args)
        else:
            msg,args = self.msg,self.args
        logger.log(level, add + " "*indent + msg, *args)

    def log_tree(self, indent=0, level=logging.DEBUG):
        if self.want_log():
            self._log(indent=indent, level=level)
            for c in self.children:
                c.log_tree(indent=indent+1, level=level)

    def want_log(self, level=logging.DEBUG):
        if self.level >= level:
            return True
        for c in self.children:
            if c.want_log(level):
                return True
        return False

    def log_backtrace(self, level=logging.DEBUG):
        ctx = self
        indent=0
        while ctx is not None:
            ctx._log(level=level, indent=indent)
            indent += 1
            ctx = ctx.parent

@contextmanager
def context_of(name, *args, **kw):
    with _Context(context.get(), name, *args, **kw) as ctx:
        yield ctx

@contextmanager
def main_context(name="MAIN", *args, **kw):
    with _Context(None, name, *args, **kw) as ctx:
        if hasattr(_main_context, "main"):
            raise RuntimeError("Parallel 'main_context' calls detected.")

        try:
            _main_context.main = ctx
            yield ctx
        finally:
            del _main_context.main


def log_backtrace(level=logging.DEBUG):
    """
    Log a back-trace of the current context
    """
    context.get().log_backtrace(level=level)


def log_tree(level=logging.DEBUG):
    _main_context.main.log_tree(level=level)


def current_context():
    return context.get()

