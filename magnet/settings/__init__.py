from .base import *

try:
    if os.environ['magnet_env'] == 'production':
        from .production import *
except KeyError:
    from .development import *