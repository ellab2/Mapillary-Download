# ----------------------------------------------- LOCAL PATHS ----------------------------------------------------------
DATASET_PATH = '../dataset.csv'
SAVE_PATH = "MissedData20251027.xlsx"
# --------------------------------------------------- S3 ---------------------------------------------------------------
BUCKET_NAME = 'image-model-dataset'
# --------------------------------------------- MAPILLARY TOKENS -------------------------------------------------------
# ACCESS_TOKEN = "MLY|24422725424056173|cdf5e992f6ac67e718d94388176e25a2"
ACCESS_TOKEN = "MLY|31207836615529489|196c38079e3613763c4958b60e8e5c61"
# ACCESS_TOKEN = "MLY|30953343454309714|c9bbb6e88980ca630a1b927d05e18731"
# ACCESS_TOKEN = "MLY|24249135821381222|00a6922c8d44cf0ff4bebbb9915221e0"
# ACCESS_TOKEN = "MLY|24422725424056173|cdf5e992f6ac67e718d94388176e25a2"
# ACCESS_TOKEN = "MLY|24367282199588973|ab329daf5f6318861103b44332e3b200"
# ACCESS_TOKEN = "MLY|24475726935382648|6a201517f3ec0c8293d2f84cb601ed31"
# ACCESS_TOKEN = "MLY|24174695898870614|8d4851b44c79fccee6d44867c3ba94bb"
# ---------------------------------------------- GENERAL VALUES --------------------------------------------------------
SLEEP_BETWEEN_CALLS = 0.2
CONNECTION_TIMEOUT = 20
RETRY_ATTEMPTS = 4
RETRY_BACKOFF = 1.5
CHECKPOINT_EVERY = 200
BASE = "https://graph.mapillary.com"