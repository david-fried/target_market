from flask import Flask, render_template, request, send_from_directory
import cv2
import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, BatchNormalization, Flatten
import numpy as np
import matplotlib.pyplot as plt
from skimage.transform import resize
#For API CALL ADDRESS SUBMIT
import urllib.request
import json
# Import google_streetview for the api module
import os
import google_streetview.api
import time
import glob
#import streetview
import itertools
from config import gkey

### ADDRESS INPUT ###
###########returns model predictions from user address input###########
def address_form(model, submit_address, FORM_COUNT):
    global ln

    #API CALL FOR USER ADDRESS SUBMIT IN FORM
    input_address = []
    # address_count = 0

    # submit_address = request.form["address"]
    input_address.append(submit_address)
    
    time.sleep(1)

    address = np.array(input_address)

    np.savetxt("static/data/user_address_submit.txt", address, fmt='%5s')

    time.sleep(1)

    #this is the first part of the streetview, url up to the address, this url will return a 600x600px image
    pre="https://maps.googleapis.com/maps/api/streetview?size=600x600&location="
    
    #this is the second part of the streetview url, the text variable below, includes the path to a text file containing one address per line
    #the addresses in this text file will complete the URL needed to return a streetview image and provide the filename of each streetview image
    text="static/data/user_address_submit.txt"
    
    #this is the third part of the url, needed after the address
    suf=f"&key={gkey}&fov=60"
    
    #this is the directory that will store the streetview images
    dir=r"static/images/address_submit/"
    
    #checks if the dir variable (output path) above exists and creates it if it does not
    if not os.path.exists(dir):
        os.makedirs(dir)
    
    #opens the address list text file (from the 'text' variable defined above) in read mode ("r")
    with open(text,"r") as text_file:
        #the variable 'lines' below creates a list of each address line in the source 'text' file
        address_choice = text_file.readline().strip('\n')

        ln = address_choice.replace(" " , "+")
        
        # creates the url that will be passed to the url reader, this creates the full, valid, url that will return a google streetview image for each address in the address text file
        URL = pre+ln+suf
        
            #creates the filename needed to save each address's streetview image locally
        filename = os.path.join(dir, "_" + str(ln)+".jpg")
        
        #final step, fetches and saves the streetview image for each address using the url created in the previous steps
        urllib.request.urlretrieve(URL, filename)
        
        time.sleep(1)

        renamed_image = f"static/images/address_submit/{FORM_COUNT}.jpg"

        if os.path.exists(renamed_image):
            os.remove(renamed_image)
        os.rename(filename, renamed_image)
        
    # prepare image for model prediction by first resizing to be consistent with the model
    image = plt.imread(f'static/images/address_submit/{FORM_COUNT}.jpg')
    resized_image = resize(image, (400,400,3))
    
    # preds = model.predict(np.array([resized_image]))
    data = {}
    predictions = model.predict(np.array([resized_image]))[0]
    predictions = list(predictions)
    best_guess_value = max(predictions)
    best_guess_index = predictions.index(best_guess_value)
    classifications = {0: 'Brick', 1: 'Siding', 2: 'Unknown'}
    best_guess_category = classifications[best_guess_index]

    if best_guess_value >= 0.5:
        data['Best_guess'] = f'The classification of this property type is: {best_guess_category}.'
    else:
        data['Best_guess'] = 'The classification of this property type is: Unknown.'

    for i, prediction in enumerate(predictions):
        data[classifications[i]] = f'{classifications[i]}: {round(100*prediction,0)}%'
    print(data)

    FORM_COUNT += 1
    
    return (data, FORM_COUNT)



### IMAGE INPUT ###
###########returns model predictions from user image upload###########

def image_form(model, request_files, COUNT):

    new_image = f'static/images/upload_images/{COUNT}.jpg' 

    request_files.save(new_image)
    image = plt.imread(new_image)
    resized_image = resize(image, (400,400,3))
    data = {}
    predictions = model.predict(np.array([resized_image]))[0]
    predictions = list(predictions)
    best_guess_index = predictions.index(max(predictions))
    classifications = {0: 'Brick', 1: 'Siding', 2: 'Unknown'}
    best_guess_category = classifications[best_guess_index]
    data['Best_guess'] = f'The model has identified {best_guess_category}.'
    for i, prediction in enumerate(predictions):
        data[classifications[i]] = f'{classifications[i]}: {round(100*prediction,0)}%'
    
    COUNT += 1

    return (data, COUNT)


