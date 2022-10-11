# -*- coding: utf-8 -*-
"""Demo_Evaluation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AxkDCNDDzccybGcqRdwOsXtZt87uotZH

<a id="1"></a>
# <p style="background-color:#000000;font-family:newtimeroman;color:#fff;font-size:120%;text-align:center;border-radius:20px 80px;">Import Libraries</p>
"""

#!pip install progressbar2

#!pip install contextlib2

#!pip install shapely

# Commented out IPython magic to ensure Python compatibility.
#Clone Git Repository
#!git clone https://github.com/fizyr/keras-retinanet.git
# %cd C:/Users/Gianlu/keras-retinanet/
#!python setup.py build_ext --inplace

# Commented out IPython magic to ensure Python compatibility.
# %cd C:/Users/Gianlu/keras-retinanet/

"""**IMPORT LIBRARIES**"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
# show images inline
# %matplotlib inline

import keras
import tensorflow as tf

# import miscellaneous modules
import matplotlib.pyplot as plt
import cv2
import os
import numpy as np
import time

import ast

# import keras_retinanet
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color
from keras_retinanet import models

# import libraries to download weights
import keras_resnet
import urllib.request

# libraries to transform data
import contextlib2
import io
import IPython
import json
import pathlib
import sys

# libraries for Confusion Matrix
from shapely.geometry import Polygon,Point
import shapely
import gc

"""<a id="1"></a>
# <p style="background-color:#000000;font-family:newtimeroman;color:#fff;font-size:120%;text-align:center;border-radius:20px 80px;">Connect to the weights from the last training</p>

Weights from last training
"""

PRETRAINED_MODEL = './snapshots/resnet50_csv_10.h5'

"""<a id="1"></a>
# <p style="background-color:#000000;font-family:newtimeroman;color:#fff;font-size:120%;text-align:center;border-radius:20px 80px;">Load Data </p>
"""

def bbox_to_dict(row):
    dictionary= dict({'x_min': ast.literal_eval(row['bbox'])[0],
                  'y_min': ast.literal_eval(row['bbox'])[1],
                  'x_max': ast.literal_eval(row['bbox'])[2],
                  'y_max': ast.literal_eval(row['bbox'])[3]}
                  )
    return dictionary

def concat_name_row(row):
    concatenation=row['img_name']+str(row['Unnamed: 0'])
    return concatenation

df_test = pd.read_csv("D:/Pictures/dataset/new_images/valid.csv")

df_test=df_test.loc[df_test["class"].astype(str) != '']
#df_test['img_name'] = df_test['img_name'].apply(eval)

df_test['image_path'] = "D:/Pictures/dataset/new_images/test/" + df_test['img_name'].astype(str) 
df_extrain=df_test.explode('img_name') # Single annotation per row
df_extrain['annotations']=df_extrain.apply(lambda row: bbox_to_dict(row), axis=1)
df_extrain['img_id']=df_extrain.apply(lambda row: concat_name_row(row), axis=1)
df_extrain.reset_index(inplace=True)
df_extrain.head()

df_extrain_main=pd.DataFrame(pd.json_normalize(df_extrain['annotations']), columns=['x_min', 'y_min', 'x_max', 'y_max']).join(df_extrain)
df_extrain_main=df_extrain_main[df_extrain_main['class'].notna()]
df_extrain_main=df_extrain_main[['image_path','x_min', 'y_min', 'x_max', 'y_max','class','img_name','img_id']] 
df_extrain_main.head(10)

"""<a id="1"></a>
# <p style="background-color:#000000;font-family:newtimeroman;color:#fff;font-size:120%;text-align:center;border-radius:20px 80px;">Transfoming Data Format </p>
"""

def create_tf_example(rowss,data_df):
    """Create a tf.Example entry for a given training image."""
    full_path = os.path.join(rowss.image_path)
    with tf.io.gfile.GFile(full_path, 'rb') as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image = Image.open(encoded_jpg_io)
    if image.format != 'JPEG':
        raise ValueError('Image format not JPEG')

    height = image.size[1] # Image height
    width = image.size[0] # Image width
    #print(width,height)
    filename = f'{rowss.img_id}'.encode('utf8') # Unique id of the image.
    encoded_image_data = None # Encoded image bytes
    image_format = 'jpeg'.encode('utf8') # b'jpeg' or b'png'

    xmins = [] 
    xmaxs = [] 
    ymins = [] 
    ymaxs = [] 
    
    # Convert ---> [xmin,ymin,width,height] to [xmins,xmaxs,ymins,ymaxs]
    xmin = rowss['x_min']
    xmax = rowss['x_max']
    ymin = rowss['y_min']
    ymax = rowss['y_max']
    

    #main_data.append((rowss['image_path'],xmins,xmaxs,ymins,ymaxs))
    return rowss['image_path'],xmin,ymin,xmax,ymax

tf_example1=[]

from PIL import Image, ImageDraw
for index, row in df_extrain_main.iterrows():
            if index % 1000 == 0:
                print('Processed {0} images.'.format(index))
            image_path,xmins,ymins,xmaxs,ymaxs=create_tf_example(row,df_extrain_main)
            #print(image_path,xmins,xmaxs,ymins,ymaxs)
            df_extrain_main.loc[index,'image_path']=image_path
            df_extrain_main.loc[index,'x_min']=xmins
            df_extrain_main.loc[index,'y_min']=ymins
            df_extrain_main.loc[index,'x_max']=xmaxs
            df_extrain_main.loc[index,'y_max']=ymaxs

"""<a id="1"></a>
# <p style="background-color:#000000;font-family:newtimeroman;color:#fff;font-size:120%;text-align:center;border-radius:20px 80px;">Creating CSV for Validation </p>
"""

classes=pd.DataFrame([{'class':'Platelets','label':0},{'class':'WBC','label':1},{'class':'RBC','label':2},{'class':'FBC','label':3}])
classes.to_csv("D:/Pictures/dataset/new_images/classes.csv",index=False,header=False)  # This CSV will be use in training

df_extrain_main['class']!=''
df_extrain_main[['image_path','x_min','y_min','x_max','y_max','class']].to_csv("D:/Pictures/dataset/new_images/annotation_validation.csv",index=False,header=False)

"""### Scrit to evaluate the model"""

#SCRIPT TO EVALUATE MODEL
!C:/Users/Gianlu/keras-retinanet/keras_retinanet/bin/evaluate.py --convert-model csv D:/Pictures/dataset/new_images/annotation.csv D:/Pictures/dataset/new_images/classes.csv {PRETRAINED_MODEL}

"""<a id="1"></a>
# <p style="background-color:#000000;font-family:newtimeroman;color:#fff;font-size:120%;text-align:center;border-radius:20px 80px;">Load Trained Model</p>
"""

model_path = os.path.join('snapshots', sorted(os.listdir('snapshots'), reverse=True)[0]) 
print(model_path)

# load retinanet model
model = models.load_model(model_path, backbone_name='resnet50')  ## Use backbone as resnet50
model = models.convert_model(model)

# load label to names mapping for visualization purposes
labels_to_names = pd.read_csv("D:/Pictures/dataset/new_images/classes.csv",header=None).T.loc[0].to_dict()

"""<a id="1"></a>
# <p style="background-color:#000000;font-family:newtimeroman;color:#fff;font-size:120%;text-align:center;border-radius:20px 80px;">Predicted vs Actual</p>
"""

THRES_SCORE = 0.4  # Set Score Threshold Value

def class_to_color(class_id):
    colors = {'Platelets':(255,0,0),'WBC':(0,255,0),'RBC':(0,0,255),'FBC':(255,255,0)}
    return colors[class_id]

def df_plot_orinal(drawOG,img_path,df):
    df=df[df['image_path']==img_path]
    for i,r in df.iterrows():
        cv2.rectangle(drawOG, (int(r['x_min']), int(r['y_min'])), (int(r['x_max']), int(r['y_max'])), (255,0,0),2)
    

def img_inference(img_path):
  image = read_image_bgr(img_path)

  # copy to draw on
  draw = image.copy()
  draw = cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)
  drawOG = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
  # preprocess image for network
  image = preprocess_image(image)
  image, scale = resize_image(image)

  # process image
  start = time.time()
  boxes, scores, labels = model.predict_on_batch(np.expand_dims(image, axis=0))
  df_plot_orinal(drawOG,img_path,df_extrain_main)
  # correct for image scale
  boxes /= scale
  # visualize detections
  for box, score, label in zip(boxes[0], scores[0], labels[0]):
      # scores are sorted so we can break
      #print(score)
      if score < THRES_SCORE:
          continue
      color = label_color(label)
      b = box.astype(int)
      draw_box(draw, b, color=color)
      caption = "{} {:.3f}%".format(labels_to_names[label], score*100) #
      draw_caption(draw, b, caption)
    
  fig = plt.figure(figsize=(20, 20))
  ax1=fig.add_subplot(1, 2, 1)
  plt.imshow(draw)
  ax2=fig.add_subplot(1, 2, 2)
  plt.imshow(drawOG)

  ax1.title.set_text('Predicted')
  ax2.title.set_text('Actual')
  plt.show()

data=df_extrain_main.sample(n=5)  #Predict on Random 5 Image
for i,r in data.iterrows():
    img_inference(r['image_path'])