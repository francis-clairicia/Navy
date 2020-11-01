# -*- coding: Utf-8 -*

from threading import Thread
from functools import wraps

def threaded_function(function):

    @wraps(function)
    def wrapper(*args, **kwargs):
        thread = Thread(target=function, name=function.__name__, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread
    
    return wrapper