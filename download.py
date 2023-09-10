import requests
import json
import os
import asyncio
import argparse

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

@background
def download(url, fn):
  r = requests.get(url, stream=True)
  with open(str(fn), "wb") as f:
    f.write(r.content)

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
        req_url = 'https://graph.mapillary.com/{}?fields=thumb_original_url'.format(image_id)
        r = requests.get(req_url, headers=header)
        data = r.json()
        print('getting url {} of {}'.format(x, img_num))
        urls.append(data['thumb_original_url'])

    print('downloading.. this process will take a while. please wait')
    for i,url in enumerate(urls):
        path = 'data/{}/{}.jpg'.format(sequence_id, i)
        download(url,path)
