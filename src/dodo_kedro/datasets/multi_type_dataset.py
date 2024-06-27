import logging

from kedro.io import AbstractDataset
from kedro.io.core import parse_dataset_definition


logger = logging.getLogger(__name__)

class MultiTypeDataset(AbstractDataset):
    def __init__(self, datasets: list):
        """
        Initializes a MultiTypeDataset to handle multiple data formats.
        Args:
            datasets: List of configurations for the datasets, each containing:
                      - 'type': The Kedro dataset type as a string (e.g., 'pandas.CSVDataset')
                      - plus additional parameters required by those datasets.
        """
        super().__init__()
        self.datasets = []

        # Dynamically create dataset instances from the provided configurations
        for dataset_config in datasets:
            dataset_class, dataset_params = parse_dataset_definition(dataset_config)
            self.datasets.append(dataset_class(**dataset_params))

    def _load(self):
        """Loads data from all configured datasets."""

        data = {}

        for dataset in self.datasets:
            data[dataset.__class__.__name__] = dataset.load()

            # TODO: first check that the data is actually the same.
            # TODO: precedence ? parquet is better than csv etc...???

            # WARNING: since all the datasets contain the same data
            # we simply return the first one
            return next(iter(data.values()))

    def _save(self, data):
        """Saves data to all configured datasets."""
        for dataset in self.datasets:
            dataset.save(data)

    def _describe(self):
        """Returns a description of all the datasets."""
        description = {}
        for dataset in self.datasets:
            # Use getattr to safely access an attribute that may not exist
            describe_method = getattr(dataset, '_describe', None)
            if callable(describe_method):
                description[dataset.__class__.__name__] = describe_method()
            else:
                description[dataset.__class__.__name__] = 'No description available'
        return description

    def _exists(self):
        """Check if all datasets exist."""
        return all(dataset.exists() for dataset in self.datasets)

    def _release(self):
        """Release any resources tied to the datasets."""
        for dataset in self.datasets:
            dataset.release()
