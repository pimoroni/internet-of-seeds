#!/bin/bash
cd /home/pi/internet-of-seeds
sudo python internet-of-seeds.py
/usr/local/bin/aws s3 cp /home/pi/internet-of-seeds/data/latest_ir_ts.jpg s3://pirate-plant-pics/latest_ir_ts.jpg --no-sign-request
