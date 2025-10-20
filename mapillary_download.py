import pandas as pd
import requests
from requests.adapters import HTTPAdapter, Retry
import os
import concurrent.futures
import argparse
from datetime import datetime
import sys

# ---------------------------------------------------------------------------
#  HTTP session setup (retry policy)
# ---------------------------------------------------------------------------
session = requests.Session()
retries_strategies = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 502, 503, 504],
)
session.mount('https://', HTTPAdapter(max_retries=retries_strategies))

# ---------------------------------------------------------------------------
#  ARGUMENT PARSING
# ---------------------------------------------------------------------------
def parse_args(argv=None):
    parser = argparse.ArgumentParser()

    df = pd.read_csv('sampled_200k_dataset.csv')

    parser.add_argument(
        'access_token',
        nargs='?',
        type=str,
        default='MLY|24526089073652399|5869d326ef9e8126a7ea9c6ee5a60c2c',
        help='Your Mapillary access token'
    )
    parser.add_argument(
        '--destination',
        type=str,
        default='/Users/ellabaruch/PycharmProjects/mapillary_download/dataset',
        help='Folder to save images'
    )
    parser.add_argument('--sequence_ids', nargs='*', help='Sequence IDs to download')
    parser.add_argument(
        '--image_ids',
        nargs='*',
        default=df['id'].astype(str).tolist(),
        help='Mapillary image IDs to process'
    )
    parser.add_argument('--image_limit', type=int, default=None, help='Max images to download')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files if they exist')
    parser.add_argument('-v', '--version', action='version', version='release 2.0')

    args = parser.parse_args(argv)

    if args.sequence_ids is None and args.image_ids is None:
        parser.error("Please provide at least one sequence_id or image_id")

    return args

# ---------------------------------------------------------------------------
#  IMAGE DOWNLOAD
# ---------------------------------------------------------------------------
def download(url, filepath):
    try:
        r = session.get(url, stream=True, timeout=10)
        r.raise_for_status()
        with open(str(filepath), "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"✅ Downloaded {filepath}")
    except Exception as e:
        print(f"⚠️ Failed to download {url}: {e}")

# ---------------------------------------------------------------------------
#  FETCH SINGLE IMAGE METADATA (to get URL)
# ---------------------------------------------------------------------------
def get_single_image_data(image_id, header):
    req_url = (
        f'https://graph.mapillary.com/{image_id}?fields='
        'thumb_original_url,captured_at,sequence'
    )
    try:
        r = session.get(req_url, headers=header, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"⚠️ Error fetching image {image_id}: {e}")
        return None

# ---------------------------------------------------------------------------
#  MAIN SCRIPT
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    args = parse_args()
    os.makedirs(args.destination, exist_ok=True)

    access_token = args.access_token
    header = {'Authorization': f'OAuth {access_token}'}

    # gather image IDs
    image_ids = args.image_ids or []
    if args.sequence_ids:
        for seq in args.sequence_ids:
            url = f'https://graph.mapillary.com/image_ids?sequence_id={seq}'
            r = session.get(url, headers=header)
            data = r.json()
            image_ids.extend([x['id'] for x in data.get('data', [])])

    if not image_ids:
        print("No images found.")
        sys.exit()

    print(f"Starting downloads for {len(image_ids)} images...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        for i, image_id in enumerate(image_ids):
            if args.image_limit is not None and i >= args.image_limit:
                break

            image_data = get_single_image_data(image_id, header)
            if not image_data or 'thumb_original_url' not in image_data:
                continue

            filename = f"{image_data['id']}.jpg"
            filepath = os.path.join(args.destination, filename)

            if not args.overwrite and os.path.exists(filepath):
                print(f"Skipping existing {filepath}")
                continue

            executor.submit(download, image_data['thumb_original_url'], filepath)

    print("✅ All downloads complete!")
