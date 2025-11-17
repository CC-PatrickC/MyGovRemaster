import os
import sys

env = os.environ.get('DJANGO_ENV', 'local').lower()

if env == 'production':
    from .production import *
elif env == 'local' or env == 'development' or env == 'dev':
    from .local import *
else:
    print(f"Warning: Unknown DJANGO_ENV='{env}'. Defaulting to 'local' settings.", file=sys.stderr)
    from .local import *