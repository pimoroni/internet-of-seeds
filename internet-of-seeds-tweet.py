import json
import tweepy
import datetime

with open(config_f) as f:
  config = json.load(f)

## Function to tweet sensor values and a timestamped image. Needs to be passed
## status (timestamp and sensor values pulled from data log) and the latest
## image filename.
def tweet_pic(status, latest, config=config):
  ckey = config['tweepy']['ckey']
  csecret = config['tweepy']['csecret']
  akey = config['tweepy']['akey']
  asecret = config['tweepy']['asecret']
  auth = tweepy.OAuthHandler(ckey, csecret)
  auth.set_access_token(akey, asecret)
  api = tweepy.API(auth)
  api.update_with_media(latest, status=status)

## Set the latest image filename, grab the last line from the data log.
if config['ir'] == 1:
  latest = 'data/latest_ir_ts.jpg'
  t = datetime.datetime.now()
  ts = t.strftime('%Y-%m-%d-%H-%M')
  status = ts + '.'
else:
  latest = 'data/latest_ts.jpg'
  fn = 'data/internet-of-seeds.log'

  with open(fn) as f:
    for l in f.readlines():
      pass

  sensor_vals = l.rstrip().split('\t')
  status = '%s: Temp: %s C, Press: %s hPa, Light: %s lux, RGB: %s,%s,%s.' % tuple(sensor_vals)

tweet_pic(status, latest)
