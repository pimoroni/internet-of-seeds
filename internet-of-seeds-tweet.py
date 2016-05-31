import tweepy

## Function to tweet sensor values and a timestamped image. Needs to be passed
## status (timestamp and sensor values pulled from data log) and the latest
## image filename.
def tweet_pic(status, latest):
  ckey = ''
  csecret = ''
  akey = ''
  asecret = ''
  auth = tweepy.OAuthHandler(ckey, csecret)
  auth.set_access_token(akey, asecret)
  api = tweepy.API(auth)
  api.update_with_media(latest, status=status)

## Set the latest image filename, grab the last line from the data log.

latest = '/home/pi/internet-of-seeds/latest_ts.jpg'

fn = '/home/pi/internet-of-seeds/internet-of-seeds.log'
with open(fn) as f:
  for l in f.readlines():
    pass

## Format the sensor values nicely for tweeting, run the tweet_pic function.

sensor_vals = l.rstrip().split('\t')
status = '%s: Temp: %s C, Press: %s hPa, Light: %s lux, RGB: %s,%s,%s.' % tuple(sensor_vals)
tweet_pic(status, latest)
