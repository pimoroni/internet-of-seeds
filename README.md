## Internet of Seeds

![Plants side](plants_side.jpg)

This is the code that runs our [Internet of Seeds](http://blog.pimoroni.com/the-internet-of-seeds/)
project, that consists of an [IKEA VÄXER hydroponics system](http://www.ikea.com/gb/en/catalog/products/S29158684/)
equipped with a Raspberry Pi Zero and camera, Flotilla dock, and weather, light,
colour and motion modules.

Read more about how we set it up [here](http://blog.pimoroni.com/the-internet-of-seeds/)
on our blog.

## Pre-requisites

You'll need to install the python-picamera, pandas, tweepy, sparkblocks and flotilla libraries.

```
sudo apt-get install python-picamera python-pandas
sudo pip install tweepy
sudo pip install py-sparkblocks
git clone https://github.com/pimoroni/flotilla-python
cd flotilla-python/library
sudo python setup.py install
```

We've used [Roboto](https://www.fontsquirrel.com/fonts/roboto) as the font for our 
timestamping and sensor data overlay. You'll also
need [Arial Unicode MS](http://www.myfontfree.com/arial-unicode-ms-myfontfreecom126f36926.htm)
for the sparklines

To use tweepy to tweet, you'll need to set up a new app on the
[Twitter developer site](https://dev.twitter.com/). It's free to do. You'll
then need to add your own consumer and access keys and secrets in a config.json 
file. See [config.example.json](config.example.json) as an example.

The paths in the shell scripts assume that this repo is in your home directory.

We'd also suggest using a large micro SD card, preferably 64GB, since you'll
be capturing a lot of images.

## Using the scripts

We chose to use cron to run the two Python scripts via a couple of shell
scripts.

You can do the following to run the image capture/data logging script every 10
minutes and the tweeting script 4 times daily, at 00:05, 06:05, 12:05 and 18:05.

After typing `crontab -e`, add the following lines to the bottom.

```
*/10 * * * * sh /home/pi/internet-of-seeds/internet-of-seeds.sh >> /home/pi/internet-of-seeds/data/cron.log
05 00,06,12,18 * * * /home/pi/internet-of-seeds/internet-of-seeds-tweet.sh >> /home/pi/internet-of-seeds/data/cron.log
```

This also logs all of the standard output to a file named `cron.log` in the
data directory.
