import logging

from kedro.io import DataCatalog
from kedro.framework.hooks import hook_impl
from kedro.io.core import DatasetNotFoundError


LOGGER = logging.getLogger(__name__)


class PipelineMetadataHook:
    """
    A hook that will "dump" the pipelines consolidated catalog & parameters.
    This is helpful when the conf starts to become complex, with a lot of interpolations etc...
    The 2 yaml will allow for:
        - manual inspection 
        - and confirmation that the pipeline did run with the inputs we expected
    """
    @hook_impl
    def after_catalog_created(
        self,
        catalog: DataCatalog,
        conf_catalog,
        conf_creds,
        feed_dict,
        save_version,
        load_versions
        ) -> None:

        params = catalog.load("parameters")

        LOGGER.info("DUMPING PIPELINE METADATA (i.e params & catalog)")

        for name, obj in {"consolidated_parameters" : params,
                          "consolidated_catalog"    : conf_catalog,
                          }.items():
            try:
                catalog.save(name, obj)
            except DatasetNotFoundError:
                raise DatasetNotFoundError(
                        f"PipelineMetadataHook expects '{name}' to be declared in catalog."
                        )
