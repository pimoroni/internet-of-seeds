import os
import shutil
import datetime
import picamera
import PIL
from PIL import Image, ImageFont, ImageDraw
import flotilla

## Captures an image and copies to latest.jpg. Needs to be passed a datetime
## object for the timestamped filename, t.
def capture_image(t):
  ts = t.strftime('%Y-%m-%d-%H-%M')
  cam = picamera.PiCamera()
  cam.resolution = (3280, 2464)
  cam.hflip = True
  cam.vflip = True
  filename = '/home/pi/internet-of-seeds/image-' + t.strftime('%Y-%m-%d-%H-%M') + '.jpg'
  cam.capture(filename, quality=100)
  shutil.copy2(filename, '/home/pi/internet-of-seeds/latest.jpg')
  return filename

## Converts the dictionary of sensor values to a nicely formatted string.
def sensor_vals_as_string(sensor_vals):
  sensor_str = 'Temp: %.2f C, Press: %.2f hPa, Light: %i lux, RGB: %i,%i,%i.' % (sensor_vals['temperature'], sensor_vals['pressure'], sensor_vals['light'], sensor_vals['colour'][0], sensor_vals['colour'][1], sensor_vals['colour'][2])
  return sensor_str

## Overlays the timestamp and sensor values on the latest captured image. Needs
## to be passed a datetime object and the dictionary of sensor values.
def timestamp_image(t, sensor_vals):
  ts_read = t.strftime('%H:%M, %a. %d %b %Y')
  sensor_str = sensor_vals_as_string(sensor_vals)
  img = Image.open('/home/pi/internet-of-seeds/latest.jpg')
  # wm = Image.open('/home/pi/watermark.png')
  img = img.resize((1438, 1080))
  # img.paste(wm, (0, 996), wm)
  draw = ImageDraw.Draw(img)
  font = ImageFont.truetype('/home/pi/roboto/Roboto-Regular.ttf', 36)
  draw.text((10, 10), ts_read, (255, 255, 255), font=font)
  draw.text((10, 46), sensor_str, (255, 255, 255), font=font)
  filename = '/home/pi/internet-of-seeds/latest_ts.jpg'
  img.save(filename)
  return filename

## Reads the Flotilla sensor values, stores them in a dictionary.
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

## Writes the sensor values to a tab-separated text file.
def log_values(t, sensor_vals):
  filename = '/home/pi/internet-of-seeds/internet-of-seeds.log'
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
sensor_vals = read_sensors()
latest = timestamp_image(t, sensor_vals)
log_values(t, sensor_vals)
