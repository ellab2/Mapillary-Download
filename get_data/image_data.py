import pandas as pd
from aws.S3 import S3
from data_functions import get_metadata
from global_conf import DATASET_PATH, BUCKET_NAME

aws_files = S3().list_files(bucket_name=BUCKET_NAME)
dataset = pd.read_csv(DATASET_PATH)
local_files = dataset['filename'].tolist()

diff = list(set(aws_files) ^ set(local_files))

get_metadata(diff)
