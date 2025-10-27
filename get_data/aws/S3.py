import logging
import os

import boto3
import pandas as pd

logging.basicConfig(level=logging.INFO)

class S3:
	def __init__(self):
		session = boto3.Session(
			region_name='eu-central-1'
		)
		self.s3 = session.client('s3')

	# writes to s3 bucket
	def write(self, filenames: pd.Series, local_path: str, bucket_name: str, s3_folder: str = None, run_date: str = None):
		for i, filename in enumerate(filenames):
			local_file_path = os.path.join(local_path, str(filename))
			if local_file_path == '/Users/ellabaruch/Documents/Ella/work/SampleData/Photos/nan':
				continue
			# s3_key = s3_folder + run_date + str(filename)
			s3_key = str(filename)
			self.s3.upload_file(local_file_path, bucket_name, s3_key)
			logging.info(f"""Uploaded {filename} to s3 bucket {bucket_name}""")

	# returns list of filenames in bucket
	def list_files(self, bucket_name):
		logging.info(f"""--------------------listing files in bucket {bucket_name}""")
		paginator = self.s3.get_paginator("list_objects_v2")
		page_iterator = paginator.paginate(Bucket=bucket_name)

		filenames = []

		for page in page_iterator:
			if "Contents" in page:
				for obj in page["Contents"]:
					filenames.append(obj["Key"])

		logging.info(f"""--------------------done listing files in bucket {bucket_name}""")

		return filenames

	# returns amount of files in bucket
	def count_files(self, bucket_name):
		logging.info(f"""--------------------Counting total images in bucket""")
		paginator = self.s3.get_paginator("list_objects_v2")
		count = 0

		for page in paginator.paginate(Bucket=bucket_name):
			for obj in page.get("Contents", []):
				if obj["Key"].lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp", ".tiff")):
					count += 1
		logging.info(f"""--------------------Total images in bucket '{bucket_name}': {count}""")