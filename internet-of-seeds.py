import os
import shutil
import json
import datetime
import picamera
import pandas as pd
import numpy as np
import PIL
from PIL import Image, ImageFont, ImageDraw
import flotilla
from sparkblocks import spark

config_f = 'config.json'
with open(config_f) as f:
  config = json.load(f)

## Captures an image and copies to latest.jpg. Needs to be passed a datetime
## object for the timestamped image, t.
def capture_image(t, config=config):
  ts = t.strftime('%Y-%m-%d-%H-%M')
  cam = picamera.PiCamera()
  cam.resolution = (3280, 2464)
  cam.hflip = True
  cam.vflip = True
  if config['ir'] == 1:
    filename = 'data/image-' + t.strftime('%Y-%m-%d-%H-%M') + '_ir.jpg'
    cam.capture(filename, quality=100)
    shutil.copy2(filename, 'data/latest_ir.jpg')
  else:
    filename = 'data/image-' + t.strftime('%Y-%m-%d-%H-%M') + '.jpg'
    cam.capture(filename, quality=100)
    shutil.copy2(filename, 'data/latest.jpg')
  return filename

## Captures an NDVI image from the Raspberry Pi NoIR camera that shows
## green vegetative growth in the plants.
def ndvi_process(img):
  img = img.convert('RGB')
  data = np.array(img).astype('float64')
  num = data[:,:,0] - data[:,:,1]
  denom = data[:,:,0] + data[:,:,1]
  num += 0.01
  denom += 0.01
  data[:,:,1] = (num / denom)
  low_vals = data < 128
  data[low_vals] = 0
  g = data[:,:,0].copy()
  r = data[:,:,1].copy()
  data[:,:,0] = r
  data[:,:,1] = g
  data = np.uint8(data)
  ndvi_img = Image.fromarray(data)
  ndvi_img.save('data/latest_ir.jpg')
  return ndvi_img

## Overlays the timestamp and sensor values on the latest captured image. Needs
## to be passed a datetime object and the dictionary of sensor values.
def timestamp_image(t, sensor_vals, sparks, watermark=False, config=config):
  ts_read = t.strftime('%H:%M, %a. %d %b %Y')
  if config['ir'] == 1:
    img = Image.open('data/latest_ir.jpg')
  else:
    img = Image.open('data/latest.jpg')
  img = img.resize((1438, 1080))
  if config['ir'] == 1:
    img = ndvi_process(img)
    filename = 'data/latest_ir_ts.jpg'
  else:
    filename = 'data/latest_ts.jpg'
  if watermark == True:
    wm = Image.open('data/watermark.png')
  img.paste(wm, (0, 996), wm)
  draw = ImageDraw.Draw(img)
  font = ImageFont.truetype('data/Roboto-Regular.ttf', 36)
  if config['ir'] == 1:
    draw.text((10, 10), ts_read, (255, 255, 255), font=font)
  else:
    spark_font = ImageFont.truetype('data/arial-unicode-ms.ttf', 16)
    draw.text((10, 10), ts_read, (255, 255, 255), font=font)
    draw.text((10, 50), 'Temp: {0:.2f}'.format(sensor_vals['temperature']), (255, 255, 255), font=font)
    draw.text((10, 90), 'Press: {0:.2f}'.format(sensor_vals['pressure']), (255, 255, 255), font=font)
    draw.text((10, 130), 'Light: {0:.2f}'.format(sensor_vals['light']), (255, 255, 255), font=font)
    draw.text((10, 170), 'RGB: ' + ','.join([str(int(i)) for i in sensor_vals['colour']]), (255, 255, 255), font=font)
    for i in range(len(sparks)):
      draw.text((10, 225 + i * 25), sparks[i], (255, 255, 255), font=spark_font)
  img.save(filename)
  return filename

## Reads the Flotilla sensor values and stores them in a dictionary.
def read_sensors():
  client = flotilla.Client()
  while not client.ready:
    pass
  motion = client.first(flotilla.Motion)
  light = client.first(flotilla.Light)
  colour = client.first(flotilla.Colour)
  weather = client.first(flotilla.Weather)
  vals = {}
  vals['motion'] = (motion.x, motion.y, motion.z)
  vals['light'] = light.lux
  r = int(colour.red/float(colour.clear)*255)
  g = int(colour.green/float(colour.clear)*255)
  b = int(colour.blue/float(colour.clear)*255)
  vals['colour'] = (r, g, b)
  vals['temperature'] = weather.temperature
  vals['pressure'] = weather.pressure / 10.0
  client.stop()
  return vals

## Bins the row and compresses the data by a factor equal to the bin size.
def compress(data, bin=2):
  compressed = ((data + data.shift(-1)) / bin)[::bin]
  compressed = compressed.tolist()
  return compressed

## Creates sparklines in Unicode blocks for last 24 hrs of data.
def sparklines(data):
  df = pd.read_csv(data, sep='\t')
  last_day = df[-144:]
  temps = last_day['temp']
  press = last_day['press']
  light = last_day['light']
  sl_temps = spark(compress(temps, bin=4))
  sl_press = spark(compress(press, bin=4))
  sl_light = spark(compress(light, bin=4))
  return (sl_temps, sl_press, sl_light)

## Writes the sensor values to a tab-separated text file.
def log_values(t, sensor_vals):
  filename = 'data/internet-of-seeds.log'
  ts = t.strftime('%Y-%m-%d-%H-%M')
  sensor_str = '%s\t%.2f\t%.2f\t%i\t%i\t%i\t%i\n' % (ts, sensor_vals['temperature'], sensor_vals['pressure'], sensor_vals['light'], sensor_vals['colour'][0], sensor_vals['colour'][1], sensor_vals['colour'][2])
  if not os.path.isfile(filename):
    out = open(filename, 'a')
    out.write('time\ttemp\tpress\tlight\tred\tgreen\tblue\n')
    out.write(sensor_str)
  else:
    out = open(filename, 'a')
    out.write(sensor_str)
  out.close()

## Run the functions.

t = datetime.datetime.now()
img = capture_image(t)
if config['ir'] == 1:
  sensor_vals = None
  sparks = None
  latest = timestamp_image(t, sensor_vals, sparks, watermark=True)
else:
  sensor_vals = read_sensors()
  data = 'data/internet-of-seeds.log'
  sparks = sparklines(data)
  latest = timestamp_image(t, sensor_vals, sparks, watermark=True)
  log_values(t, sensor_vals)
