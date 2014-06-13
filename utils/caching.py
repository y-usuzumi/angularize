cache_repo = defaultdict(defaultdict(dict))

def cached(cache_name):
    def decorate(func):
        @wraps(func)
        def wrapper(*args):
            global cache_repo
            if cache_repop[cache_name][
            
        
