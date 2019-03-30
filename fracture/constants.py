import os
import logging


# ------------------------------------------------------------------------------
# -- Define the logger for fracture
log = logging.getLogger('fracture')


# ------------------------------------------------------------------------------
# -- This is the location we look to for all the built in plugins, that is
# -- to say plugins which are 'always on'
BUILT_IN_PLUGIN_DIR = os.path.join(
    os.path.dirname(__file__),
    'built-in',
)
