import os
from typing import Union, Tuple

from torchtext._internal.module_utils import is_module_available
from torchtext.data.datasets_utils import (
    _wrap_split_argument,
    _create_dataset_directory,
)

if is_module_available("torchdata"):
    from torchdata.datapipes.iter import FileOpener, IterableWrapper
    from torchtext._download_hooks import GDriveReader

URL = "https://drive.google.com/uc?export=download&id=0Bz8a_Dbh9QhbaW12WVVZS2drcnM"

MD5 = "fe39f8b653cada45afd5792e0f0e8f9b"

NUM_LINES = {
    "train": 3600000,
    "test": 400000,
}

_PATH = "amazon_review_polarity_csv.tar.gz"

_EXTRACTED_FILES = {
    "train": os.path.join("amazon_review_polarity_csv", "train.csv"),
    "test": os.path.join("amazon_review_polarity_csv", "test.csv"),
}


DATASET_NAME = "AmazonReviewPolarity"


@_create_dataset_directory(dataset_name=DATASET_NAME)
@_wrap_split_argument(("train", "test"))
def AmazonReviewPolarity(root: str, split: Union[Tuple[str], str]):
    """AmazonReviewPolarity Dataset

    For additional details refer to https://arxiv.org/abs/1509.01626

    Number of lines per split:
        - train: 3600000
        - test: 400000

    Args:
        root: Directory where the datasets are saved. Default: os.path.expanduser('~/.torchtext/cache')
        split: split or splits to be returned. Can be a string or tuple of strings. Default: (`train`, `test`)

    :returns: DataPipe that yields tuple of label (1 to 2) and text containing the review title and text
    :rtype: (int, str)
    """
    # TODO Remove this after removing conditional dependency
    if not is_module_available("torchdata"):
        raise ModuleNotFoundError(
            "Package `torchdata` not found. Please install following instructions at `https://github.com/pytorch/data`"
        )

    url_dp = IterableWrapper([URL])
    cache_compressed_dp = url_dp.on_disk_cache(
        filepath_fn=lambda x: os.path.join(root, _PATH),
        hash_dict={os.path.join(root, _PATH): MD5},
        hash_type="md5",
    )
    cache_compressed_dp = GDriveReader(cache_compressed_dp).end_caching(mode="wb", same_filepath_fn=True)

    cache_decompressed_dp = cache_compressed_dp.on_disk_cache(
        filepath_fn=lambda x: os.path.join(root, _EXTRACTED_FILES[split])
    )
    cache_decompressed_dp = (
        FileOpener(cache_decompressed_dp, mode="b").load_from_tar().filter(lambda x: _EXTRACTED_FILES[split] in x[0])
    )
    cache_decompressed_dp = cache_decompressed_dp.end_caching(mode="wb", same_filepath_fn=True)

    data_dp = FileOpener(cache_decompressed_dp, encoding="utf-8")
    return data_dp.parse_csv().map(fn=lambda t: (int(t[0]), " ".join(t[1:])))
