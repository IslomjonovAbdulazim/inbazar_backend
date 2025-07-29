# Import all CRUD modules here
from . import user
from . import product
from . import category

# Import bot CRUD if available
try:
    from . import bot_user
except ImportError:
    # Bot CRUD not available yet
    pass