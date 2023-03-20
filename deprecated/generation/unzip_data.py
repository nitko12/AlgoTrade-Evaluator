import time
import datetime
import pandas as pd
import os
from tqdm import tqdm
import json
import zipfile


if __name__ == "__main__":

    for x in tqdm(os.listdir("data/data-aws")):
        path_to_zip_file = "data/data-aws/" + x
        directory_to_extract_to = "data/data-aws-unzipped/"

        with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
            zip_ref.extractall(directory_to_extract_to)

    print("Done")
