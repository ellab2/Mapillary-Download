import requests
import json
import os
import asyncio
import argparse
from datetime import datetime
from lib.exif_write import ExifEdit

def parse_args(argv =None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--sequence_id', type=str, help='The mapillary sequence id to download')
    parser.add_argument('--access_token', type=str, help='Your mapillary access token')

    global args
    args = parser.parse_args(argv)

def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)
    return wrapped

#@background
def download(url, fn, metadata=None):
  r = requests.get(url, stream=True)
  with open(str(fn), "wb") as f:
    f.write(r.content)
  write_exif(fn, metadata)

def write_exif(filename, data):
    '''
    Write exif metadata
    '''
    #{'thumb_original_url': 'https://scontent-cdg4-2.xx.fbcdn.net/m1/v/t6/An9Zy2SrH9vXJIF01QkBODyUbg7XSKfwL48UwHyvihSwvECGjVbG0vSw9uhxe2-Dq-k2eUcigb83buO6zo-7eVbykfp5aQIe1kgd-MJr66nU_H-o_mwBLZXgVbj5I_5WX-C9c6FxJruHkV962F228O0?ccb=10-5&oh=00_AfDOKD869DxL-4ZNCbVo8Rn29vsc0JyjMAU2ctx4aAFVMQ&oe=65256C25&_nc_sid=201bca',
    #  'captured_at': 1603459736644, 'geometry': {'type': 'Point', 'coordinates': [2.5174596904057, 48.777089857534]}, 'id': '485924785946693'}
    lat = data['geometry']['coordinates'][1]
    long = data['geometry']['coordinates'][0]
    altitude = data['altitude']
    bearing = data['compass_angle']
    timestamp=datetime.utcfromtimestamp(int(data['captured_at'])/1000)
    metadata = metadata = ExifEdit(filename)
    
    #metadata.read()
    
    try:
                
            # add to exif
        #metadata["Exif.GPSInfo.GPSLatitude"] = exiv_lat
        #metadata["Exif.GPSInfo.GPSLatitudeRef"] = coordinates[3]
        #metadata["Exif.GPSInfo.GPSLongitude"] = exiv_lon
        #metadata["Exif.GPSInfo.GPSLongitudeRef"] = coordinates[7]
        #metadata["Exif.GPSInfo.GPSMapDatum"] = "WGS-84"
        #metadata["Exif.GPSInfo.GPSVersionID"] = '2 0 0 0'
        #metadata["Exif.GPSInfo.GPSImgDirection"] = exiv_bearing
        #metadata["Exif.GPSInfo.GPSImgDirectionRef"] = "T"
        
        metadata.add_lat_lon(lat, long)
        metadata.add_altitude(altitude)
        metadata.add_date_time_original(timestamp)
        metadata.add_direction(bearing)
        metadata.write()
        print("Added geodata to: {0}".format(filename))
    except ValueError as e:
        print("Skipping {0}: {1}".format(filename, e))
if __name__ == '__main__':
    parse_args()

    if args.sequence_id == None:
        print('please provide the sequence_id')
        exit()

    if args.access_token == None:
        print('please provide the access_token')
        exit()

    sequence_id= args.sequence_id
    access_token = args.access_token

    # create the data folder
    if not os.path.exists('data'):
            os.makedirs('data')

    # create a folder for each unique sequence ID to group images by sequence
    if not os.path.exists('data/{}'.format(sequence_id)):
        os.makedirs('data/{}'.format(sequence_id))

    header = {'Authorization' : 'OAuth {}'.format(access_token)}
    url = 'https://graph.mapillary.com/image_ids?sequence_id={}'.format(sequence_id)
    r = requests.get(url, headers=header)
    data = r.json()

    image_ids = data['data']
    img_num = len(image_ids)
    urls = []
    print(img_num)
    print('getting urls')
    for x in range(0, img_num):
        image_id = image_ids[x]['id']
        req_url = 'https://graph.mapillary.com/{}?fields=thumb_original_url,altitude,camera_type,captured_at,compass_angle,geometry,exif_orientation'.format(image_id)
        r = requests.get(req_url, headers=header)
        data = r.json()
        print('getting url {} of {}'.format(x, img_num))
        #print(data['geometry']['coordinates'][1], data['geometry']['coordinates'][0])
        urls.append(data)

    print('downloading.. this process will take a while. please wait')
    for i,url in enumerate(urls):
        path = 'data/{}/{}.jpg'.format(sequence_id, datetime.utcfromtimestamp(int(url['captured_at'])/1000).strftime('%Y-%m-%d_%HH%Mmn%S.%f'))
        download(url['thumb_original_url'],path, url)
