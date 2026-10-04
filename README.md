# epaper_display_tools
***
Project contains script to dither an image using Floyd-Steinberg error diffusion and a simple tcp client script to send commands to the esp32 interfacing with the spectra 6 color display. The Firmware for the ESP32S3 can be found bellow. 

Check out the [epaper_display_firmware Repository](https://github.com/lebrown-lb/epaper_display_firmware) for more details.


## cmd_tcp_client
> cmd_tcp_client.py

**Action Command List**

UPDATE - updates display to whatever is in the image buffer\
DEMO - displays the demo image to the display\
CLEAR - clears the display\
SLEEP - display enters low power mode

**Draw Command List**

clear - clears the image buffer to a given color\
text - writes text to the specified location in the image buffer\
rect - draws a rectangle to the image buffer\
circle - draws a circle to the image buffer\
line - draws a line to the image buffer

*For Draw Commands send just the command word and the reply will be a string describing its usage*

**Example Commands**

```bash
# Demo command usage
python ./cmd_tcp_client.py 10.0.0.115 3333 'DEMO'
```
```bash
# UPDATE command usage
python ./cmd_tcp_client.py 10.0.0.115 3333 'UPDATE'
```
```bash
# line command usage
python ./cmd_tcp_client.py 10.0.0.151 3333 'line:0,0,1599,1199,YELLOW,3x3,DOTS'
```

*Note that the correct IP and PORT needs to be specified* 

## image_dithering_upload

> image_dithering_upload.py

```bash
# script usage without IP and PORT
python ./image_dithering_upload.py input.png output.png
```
*Note when the IP and PORT are not specified the script will not upload the dithered image*

```bash
# script usage with IP and PORT
python ./image_dithering_upload.py input.png output.png 10.0.0.151 3333
```

*Note that in all the above examples arguments order must be as specified and the packages in **packages.txt** must be installed*