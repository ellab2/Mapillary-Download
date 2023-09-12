import requests
import json
import os
import asyncio
import argparse
from datetime import datetime
import writer
from model import PictureType

def parse_args(argv =None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--sequence_id', type=str, help='The mapillary sequence id to download')
    parser.add_argument('--access_token', type=str, help='Your mapillary access token')
    parser.add_argument('--image_count', type=int, default=None, help='How many images you want to download')

    global args
    args = parser.parse_args(argv)

def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)
    return wrapped

#@background
def download(url, fn, metadata=None):
    r = requests.get(url, stream=True)
    image = write_exif(r.content, metadata)
    with open(str(fn), "wb") as f:
        f.write(image)

def write_exif(picture, img_metadata):
    '''
    Write exif metadata
    '''
    #{'thumb_original_url': 'https://scontent-cdg4-2.xx.fbcdn.net/m1/v/t6/An9Zy2SrH9vXJIF01QkBODyUbg7XSKfwL48UwHyvihSwvECGjVbG0vSw9uhxe2-Dq-k2eUcigb83buO6zo-7eVbykfp5aQIe1kgd-MJr66nU_H-o_mwBLZXgVbj5I_5WX-C9c6FxJruHkV962F228O0?ccb=10-5&oh=00_AfDOKD869DxL-4ZNCbVo8Rn29vsc0JyjMAU2ctx4aAFVMQ&oe=65256C25&_nc_sid=201bca',
    #  'captured_at': 1603459736644, 'geometry': {'type': 'Point', 'coordinates': [2.5174596904057, 48.777089857534]}, 'id': '485924785946693'}
    
    picture = writer.writePictureMetadata(picture, img_metadata)
    picture = writer.add_altitude(picture, img_metadata)
    picture = writer.add_direction(picture, img_metadata)

    return picture

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
    img_num = args.image_count if args.image_count is not None else len(image_ids)
    urls = []
    print(img_num)
    print('getting urls')
    for x in range(0, img_num):
    #for x in range(0, 5):        
        image_id = image_ids[x]['id']
        req_url = 'https://graph.mapillary.com/{}?fields=thumb_original_url,altitude,camera_type,captured_at,compass_angle,geometry,exif_orientation'.format(image_id)
        r = requests.get(req_url, headers=header)
        data = r.json()
        print('getting url {} of {}'.format(x, img_num))
        #print(data)
        urls.append(data)

    print('downloading.. this process will take a while. please wait')
    for i,url in enumerate(urls):
        date_time_image_filename = datetime.utcfromtimestamp(int(url['captured_at'])/1000).strftime('%Y-%m-%d_%HH%Mmn%S.%f')
        path = 'data/{}/{}.jpg'.format(sequence_id, date_time_image_filename)
        img_metadata = writer.PictureMetadata(
                capture_time = datetime.utcfromtimestamp(int(url['captured_at'])/1000),
                longitude = url['geometry']['coordinates'][0],
                latitude = url['geometry']['coordinates'][1],
                picture_type = PictureType("equirectangular") if url['camera_type'] == 'spherical' else None,
                direction = url['compass_angle'],
                altitude = url['altitude'],
        )
        download(url['thumb_original_url'],path, img_metadata)
