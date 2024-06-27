"""
File that allows to define Hook IMPLEMENTATIONS for specific Hook SPECIFICATIONS
that describes the point at which you want to inject additional behaviour

The Hook implementation should have the same name as the specification.
The Hook must provide a concrete implementation
with a subset of the corresponding specification’s parameters
(you do not need to use them all).
"""
import os
import pdb
import sys
import logging
import traceback

from kedro.framework.hooks import hook_impl

LOGGER = logging.getLogger(__name__)

def is_debug_mode():
    DEBUG_MODE = os.getenv("DEBUG_MODE")
    if DEBUG_MODE is not None:
        return DEBUG_MODE.strip().lower() == 'true'

class PostMortemHook:

    if not is_debug_mode():
        LOGGER.warn("PostMortemHook expects the env. var DEBUG_MODE set to True")

    @hook_impl
    def on_node_error(self):
        if is_debug_mode():
            # We don't need the actual exception since it is within this stack frame
            _, _, traceback_object = sys.exc_info()

            #  Print the traceback information for debugging ease
            traceback.print_tb(traceback_object)

            # Drop you into a post mortem debugging session
            pdb.post_mortem(traceback_object)

        else:
            LOGGER.warn("PostMortemHook expects the env. var DEBUG_MODE set to True")

    @hook_impl
    def on_pipeline_error(self):

        if is_debug_mode():
            # We don't need the actual exception since it is within this stack frame
            _, _, traceback_object = sys.exc_info()

            #  Print the traceback information for debugging ease
            traceback.print_tb(traceback_object)

            # Drop you into a post mortem debugging session
            pdb.post_mortem(traceback_object)

        else:
            LOGGER.warn("PostMortemHook expects the env. var DEBUG_MODE set to True")
