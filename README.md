# mapillary_download
Simple code to download images in one or several mapillary sequences. 

## How to use
change the access token with your access token and the sequence ids with the ids of the sequences you want to download
```Shell
python download.py "MLY|xxxx|xxxxxxx" --sequence_ids xxxxxxxxxxx xxxxxxxxxxx
```

## Available arguments
```Shell
python download.py -h
usage: download.py [-h] [--sequence_ids [SEQUENCE_IDS ...]] [--image_ids [IMAGE_IDS ...]] [--destination DESTINATION]
                   [--image_limit IMAGE_LIMIT] [--overwrite]
                   access_token

positional arguments:
  access_token          Your mapillary access token

optional arguments:
  -h, --help            show this help message and exit
  --sequence_ids [SEQUENCE_IDS ...]
                        The mapillary sequence id(s) to download
  --image_ids [IMAGE_IDS ...]
                        The mapillary image id(s) to get their sequence id(s)
  --destination DESTINATION
                        Path destination for the images
  --image_limit IMAGE_LIMIT
                        How many images you want to download
  --overwrite           overwrite existing images
```

## How to get my access token
 - Go to https://www.mapillary.com/dashboard/developers
 - Click on "Registrer Application", enter the needed informations, enable the application to "Read" data, then click on register :

    ![register application](./doc/snapshot_mapillary_register_application.jpg)
 - When this registration is done, click on "view" in the token column. This is you access token : 
 
    ![token](./doc/snapshot_mapillary_token.jpg)

## How to get my sequence id

 - Go to https://mapillary.com/app
 - Click on one of the picture of the sequence you want to download
 - Click on the "image option" button (right panel)
 - Click on "advanced" then click on the sequence id to copy it in the clipboard

    ![snapshot](./doc/snapshot_mapillary_sequence.jpg)