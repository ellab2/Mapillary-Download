import os
import time

import pandas as pd
import requests

from global_conf import RETRY_ATTEMPTS, RETRY_BACKOFF, CONNECTION_TIMEOUT, ACCESS_TOKEN, SAVE_PATH, CHECKPOINT_EVERY, \
    SLEEP_BETWEEN_CALLS, BASE


def safe_get(url, params, retries=RETRY_ATTEMPTS, backoff=RETRY_BACKOFF):
    """GET with retry/backoff on transient errors."""
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=CONNECTION_TIMEOUT)
            if r.status_code == 200:
                return r.json()
            # handle Mapillary timeouts and transient errors
            try:
                err = r.json().get("error", {})
            except Exception:
                err = {}
            if r.status_code in (429, 500, 502, 503, 504) or err.get("code") == -2:
                sleep_s = backoff * (attempt + 1)
                print(f"HTTP {r.status_code} (code={err.get('code')}); retrying in {sleep_s:.1f}s …")
                time.sleep(sleep_s)
                continue
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:400]}")
        except requests.RequestException as e:
            if attempt == retries - 1:
                raise
            sleep_s = backoff * (attempt + 1)
            print(f"Request error {e.__class__.__name__}; retrying in {sleep_s:.1f}s …")
            time.sleep(sleep_s)

def get_image_info(image_id):
    """
    Returns (lat, lon, url) for a Mapillary image id.
    """
    url = f"{BASE}/{image_id}"
    params = {
        "fields": "id,computed_geometry,thumb_1024_url",
        "access_token": ACCESS_TOKEN,
    }
    data = safe_get(url, params)
    geom = (data or {}).get("computed_geometry", {})
    coords = geom.get("coordinates", [None, None])  # GeoJSON order: [lon, lat]
    lon, lat = (coords + [None, None])[:2]
    photo_url = (data or {}).get("thumb_1024_url")
    return lat, lon, photo_url

def write_output(df: pd.DataFrame, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if path.lower().endswith(".xlsx"):
        df.to_excel(path, index=False)
    else:
        df.to_csv(path, index=False)

def get_metadata(image_names):
    all_files = [str(f).strip() for f in image_names if str(f).strip().lower().endswith(".jpg")]
    if not all_files:
        print("No .jpg filenames provided in IMAGE_NAMES. Exiting.")
        return
    print(f"Loaded {len(all_files)} jpg filenames from fixed list.")

    def base_id(fn):  # strip extension to get the Mapillary image id
        return os.path.splitext(fn)[0].strip()

    # De-dup by image_id to avoid repeated lookups
    seen_ids = set()
    todo = []
    for fname in all_files:
        img_id = base_id(fname)
        if img_id not in seen_ids:
            todo.append((img_id, fname))
            seen_ids.add(img_id)

    print(f"{len(todo)} unique image IDs to fetch.")

    rows = []
    looked_up = 0
    new_df_cols = ["image_id", "image_name", "lat", "lon", "url"]

    # Optional: if SAVE_PATH exists, we overwrite — because you asked for only these images
    if os.path.exists(SAVE_PATH):
        print(f"NOTE: {SAVE_PATH} already exists and will be overwritten with ONLY these results.")

    for img_id, fname in todo:
        try:
            lat, lon, url = get_image_info(img_id)
            rows.append({
                "image_id": img_id,
                "image_name": fname,
                "lat": lat,
                "lon": lon,
                "urltophoto": url
            })
            looked_up += 1

            # Periodic checkpoint to reduce risk of losing progress
            if looked_up % CHECKPOINT_EVERY == 0:
                df_ckpt = pd.DataFrame(rows, columns=new_df_cols)
                write_output(df_ckpt, SAVE_PATH)
                print(f"[checkpoint] wrote {len(df_ckpt)} rows to: {SAVE_PATH}; processed {looked_up}/{len(todo)}")
        except Exception as e:
            print(f"Lookup failed for {img_id}: {e}")

        time.sleep(SLEEP_BETWEEN_CALLS)

    # Final write
    df = pd.DataFrame(rows, columns=new_df_cols)
    write_output(df, SAVE_PATH)

    print("Done.")
    abs_path = os.path.abspath(SAVE_PATH)
    print(f"Saved {len(df)} rows to: {abs_path}")