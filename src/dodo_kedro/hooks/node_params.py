import logging
from typing import Any

from kedro.io import DataCatalog
from kedro.pipeline.node import Node
from kedro.framework.hooks import hook_impl


LOGGER = logging.getLogger(__name__)

class NodeParamsHook:
    """
    This hook will print the params with which each node will be ran.
    """
    @hook_impl
    def before_node_run(
        self,
        node: Node,
        catalog: DataCatalog,
        inputs: dict[str, Any],
        is_async: bool,
        session_id: str,
    ):
        """Hook to be invoked before a node runs.
        The arguments received are the same as those used by ``kedro.runner.run_node``

        Args:
            node: The ``Node`` to run.
            catalog: A ``DataCatalog`` containing the node's inputs and outputs.
            inputs: The dictionary of inputs dataset.
                The keys are dataset names and the values are the actual loaded input data,
                not the dataset instance.
            is_async: Whether the node was run in ``async`` mode.
            session_id: The id of the session.

        Returns:
            Either None or a dictionary mapping dataset name(s) to new value(s).
                If returned, this dictionary will be used to update the node inputs,
                which allows to overwrite the node inputs.
        """

        LOGGER.info(f"PARAMS FOR {node.name.upper()}")

        for k, v in inputs.items():
            if k.startswith('params'):
                if isinstance(v, (int, float, str, bool)):
                    LOGGER.info(f"{k.upper()} set to `{v}`")
                else:
                    LOGGER.info(k.upper())
                    LOGGER.info(v)
