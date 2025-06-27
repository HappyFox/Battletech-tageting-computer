class EventDispatcher:

    def __init__(self):
        self.callback_fns = set()

    def dispatch_event(self, *args, **kwargs):
        for fn in self.callback_fns:
            fn(*args, **kwargs)

    def register_fn(self, fn):
        self.callback_fns.add(fn)

    def deregister_fn(self, fn):
        self.callback_fns.remove(fn)
