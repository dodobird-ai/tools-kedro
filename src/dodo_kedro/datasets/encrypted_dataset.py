import os
import uuid
import base64
import hashlib

from cryptography.fernet import Fernet
from kedro.io.core import parse_dataset_definition
from kedro.io import AbstractDataset, DatasetError
from pyfakefs.fake_filesystem_unittest import Patcher


class EncryptedDataset(AbstractDataset):

    def __init__(self, dataset_config, key):
        super().__init__()
        self.dataset_config = dataset_config

        # we use as hash to allow for keys of arbitrary lengths
        hash = hashlib.sha256(key.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(hash)
        self.fernet = Fernet(fernet_key)

    def _save(self, data):
        dataset_class, dataset_params = parse_dataset_definition(self.dataset_config)

        # put aside the path declared in the catalog 
        # it will be used to save the encrypted data to disk.
        path_on_disk = dataset_params['filepath']
        dir_path = os.path.dirname(path_on_disk)
        os.makedirs(dir_path, exist_ok=True)

        with Patcher() as patcher:

            # change the filepath of the underlying dataset
            # to the path in our "virtual, fake, in-memory file system
            # we make this path unique with uuid for the code to be safe 
            # during concurrent / parallel run
            path_in_memory_fs = f'/tmp/fakefile_{uuid.uuid4()}.txt'
            dataset_params['filepath'] = path_in_memory_fs
            dataset = dataset_class(**dataset_params)

            # Use the underlying dataset's mechanism to save the data in "memory" and not to disk
            dataset.save(data)

            with open(path_in_memory_fs, 'rb') as f:
                content = f.read()


        encrypted_data = self.fernet.encrypt(content)

        # Save encrypted data to disk
        with open(path_on_disk, 'wb') as f:
            f.write(encrypted_data)


    def _load(self):

        with open(self.dataset_config['filepath'], 'rb') as encrypted_file:
            encrypted_bits = encrypted_file.read()

        decrypted_bits = self.fernet.decrypt(encrypted_bits)

        with Patcher() as patcher:

            path_in_memory_fs = '/tmp/fakefile.txt'

            with open(path_in_memory_fs, 'wb') as f:
                f.write(decrypted_bits)

            dataset_class, dataset_params = parse_dataset_definition(self.dataset_config)
            dataset_params['filepath'] = path_in_memory_fs 
            dataset = dataset_class(**dataset_params)
            data = dataset.load()

        return data


    def _describe(self): 
        return {"Encrypted Version of:": self.dataset_config}
