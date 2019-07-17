## setup logging
#import logging
#logging.basicConfig(level = logging.INFO)## import the package
import os
import pyrealsense as pyrs
from pyrealsense.constants import rs_option
import cv2
import numpy as np
import pdb
import pandas as pd
def convert_z16_to_bgr(frame):
  '''Performs depth histogram normalization
  This raw Python implementation is slow. See here for a fast implementation using Cython:
  https://github.com/pupil-labs/pupil/blob/master/pupil_src/shared_modules/cython_methods/ methods.pyx
  '''
  hist = np.histogram(frame, bins=0x10000)[0]
  hist = np.cumsum(hist)
  hist -= hist[0]
  rgb_frame = np.empty(frame.shape[:2] + (3,), dtype=np.uint8)
  zeros = frame == 0
  non_zeros = frame != 0
  #print hist[0xFFFF]
  f = hist[frame[non_zeros]] * 255 / (hist[0xFFFF])
  rgb_frame[non_zeros, 0] = 255 - f
  rgb_frame[non_zeros, 1] = 255 - f
  rgb_frame[non_zeros, 2] = 255 - f
  
  #0,1,2 = b,g,r
  rgb_frame[zeros, 0] = 20
  rgb_frame[zeros, 1] = 5
  rgb_frame[zeros, 2] = 0
  
  #pdb.set_trace()
  '''
  rgb_frame[zeros, 0] = 232
  rgb_frame[zeros, 1] = 112
  rgb_frame[zeros, 2] = 100
  '''
  return rgb_frame


fname = raw_input("project name: ")
try:
  if not(os.path.isdir(fname)):
    os.makedirs(os.path.join('./test/%s'%fname))
except OSError as e:
  if e.errno !=- errno.EEXIST:
    print "Failed to create directory"
    raise


## main codecolor_stream = pyrs.stream.ColorStream(fps=60)
depth_stream = pyrs.stream.DepthStream(fps=60)
## start the service - also available as context manager
serv = pyrs.Service()## create a device from device id and streams of interest
#cam = serv.Device(device_id = 0, streams = [color_stream, depth_stream])
cam = serv.Device(device_id = 0, streams = [pyrs.stream.ColorStream(fps = 60), depth_stream])
## retrieve 60 frames of data
n = 0
a = 0
print "a: turn on/off continuously capture"
print "c: capture now(except a is on)"
print "q: quit"
while True:
  n+=1
  try:
    cam.wait_for_frames()
    c = cam.color
    c = cv2.cvtColor(c, cv2.COLOR_RGB2BGR)
#    d = cam.depth * cam.depth_scale * 1000
#    d = cv2.applyColorMap(d.astype(np.uint8), cv2.COLORMAP_RAINBOW)
    rawd = cam.depth
    d = convert_z16_to_bgr(rawd)
    cd = np.concatenate((c, d), axis=1)
    if a ==1:
        cv2.imwrite('./test/%s/cimage%s.jpg'%(fname, n), c)
        cv2.imwrite('./test/%s/dimage%s.jpg'%(fname, n), d)
    cv2.imshow('', cd)
    key = cv2.waitKey(1) &0xFF
    if key == ord('a'):
      if a==1:
        a = 0
        print "turn off continuously capture"
      else:
        a = 1
        print "turn on continuously capture"
    if key == ord('c'):
      print "capture!"
      cv2.imwrite('./test/%s/cimage%s.jpg'%(fname, n), c)
      cv2.imwrite('./test/%s/dimage%s.jpg'%(fname, n), d)
      pd.DataFrame(rawd).to_csv('./test/%s/rawd%s.csv'%(fname, n), header=None, index = None)
    if key == ord('q'):
      print "closing..."
      break;
  except:
    print('internal error')
    break;## stop camera and service
cam.stop()
serv.stop()
