from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
from os import listdir
from os.path import isfile, join
from PIL import Image
import sys
import time
import numpy as np
import io
import pandas as pd
from datetime import datetime
import re
import cv2

subscription_key = "8135a06dd85445d7bade0a45be5007b2"
endpoint = "https://smartjourney-week9.cognitiveservices.azure.com/"

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

base_path = "/home/mathieuhoude/source/SmartJourneyWeek9/frames/"
frames = [f for f in listdir(base_path) if isfile(join(base_path, f))]

def format_date(string):
    string = string.replace(" ", "")
    match = re.match('^[0-9]{3}\-[0-9]{2}\-[0-9]{2}$', string) #Some image being cropped, we accept string that would have only 3 digits for the year
    if match != None:
        return "2" + string

    match = re.match('^[0-9]{4}\-[0-9]{2}\-[0-9]{1}$', string)
    if match != None:
        return string + "1"
    match = re.match('^[0-9]{4}\-[0-9]{2}\-[0-9]{2}$', string)
    if match != None:
        return string
    else:
        return ""

def format_frame(string):
    string = string.replace(" ", "")
    match = re.match('^(£|F|E)[0-9]{0,3}\.?$', string)
    if match != None:
        return string[1:] if len(string) > 1 else "0"
    match = re.match('^(£|F|E)?[0-9]{1,3}\.?$', string)
    if match != None:
        return string
    else:
        return "0"
def is_date(string):
    string = string.replace(" ", "")
    match = re.match('^[0-9]{3}\-[0-9]{2}\-[0-9]{2,3}$', string) #Some image being cropped, we accept string that would have only 3 digits for the year
    if match != None:
        return True

    match = re.match('^[0-9]{4}\-[0-9]{2}\-[0-9]{2,3}$', string)
    if match != None:
        return True
    else:
        return False

def is_frame(string):
    string = string.replace(" ", "")
    match = re.match('^(£|F|E)[0-9]{0,3}\.?$', string)
    if match != None:
        return True
    match = re.match('^(£|F|E)?[0-9]{1,3}\.?$', string)
    if match != None:
        return True
    else:
        return False
def get_box(line):
    offset = 20
    if line.bounding_box[0] < line.bounding_box[4]:
        x_left = line.bounding_box[0] - offset
        x_right = line.bounding_box[4] + offset
    else:
        x_left = line.bounding_box[4] - offset
        x_right = line.bounding_box[0] + offset
    if line.bounding_box[1] < line.bounding_box[5]:
        y_left = line.bounding_box[1] - offset
        y_right = line.bounding_box[5] + offset
    else:
        y_left = line.bounding_box[5] - offset
        y_right = line.bounding_box[1] + offset
    return (x_left, y_left, x_right, y_right)

def extract_date_and_frame_number():
    results = []
    for frame in frames:
        try:
            print('-------------------------------------------')
            print("Results for: " + frame)
            result = {}
            img= Image.open(base_path + frame)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='jpeg')
            img_byte_arr = img_byte_arr.getvalue()
            original_stream = io.BytesIO(img_byte_arr)

            original_response = computervision_client.read_in_stream(original_stream, raw=True)
            # Get the operation location (URL with an ID at the end) from the response
            read_original_operation_location = original_response.headers["Operation-Location"]
            # Grab the ID from the URL
            original_operation_id = read_original_operation_location.split("/")[-1]
            # Call the "GET" API and wait for it to retrieve the results 
            while True:
                original_result = computervision_client.get_read_result(original_operation_id)
                if original_result.status not in ['notStarted', 'running']:
                    break
                time.sleep(1)

            date_box, frame_box = None, None
            for text_result in original_result.analyze_result.read_results:
                for line in text_result.lines:
                    if date_box == None:
                        date = is_date(line.text)
                        if date != False:
                            date_box = get_box(line)
                    if frame_box == None:
                        _is_frame = is_frame(line.text)
                        if _is_frame != False:
                            frame_box = get_box(line)

            date_crop = img.crop(date_box)
            img_byte_arr = io.BytesIO()
            date_crop.save(img_byte_arr, format='jpeg')
            img_byte_arr = img_byte_arr.getvalue()
            date_stream = io.BytesIO(img_byte_arr)

            frame_crop = img.crop(frame_box)
            img_byte_arr = io.BytesIO()
            frame_crop.save(img_byte_arr, format='jpeg')
            img_byte_arr = img_byte_arr.getvalue()
            frame_stream = io.BytesIO(img_byte_arr)


            # Call API with URL and raw response (allows you to get the operation location)
            # read_response = computervision_client.read(read_image_url,  raw=True)
            date_response = computervision_client.read_in_stream(date_stream, raw=True)
            frame_response = computervision_client.read_in_stream(frame_stream, raw=True)

            # Get the operation location (URL with an ID at the end) from the response
            read_date_operation_location = date_response.headers["Operation-Location"]
            # Grab the ID from the URL
            date_operation_id = read_date_operation_location.split("/")[-1]

            # Get the operation location (URL with an ID at the end) from the response
            read_frame_operation_location = frame_response.headers["Operation-Location"]
            # Grab the ID from the URL
            frame_operation_id = read_frame_operation_location.split("/")[-1]

            # Call the "GET" API and wait for it to retrieve the results 
            while True:
                date_result = computervision_client.get_read_result(date_operation_id)
                if date_result.status not in ['notStarted', 'running']:
                    break
                time.sleep(1)

            while True:
                frame_result = computervision_client.get_read_result(frame_operation_id)
                if frame_result.status not in ['notStarted', 'running']:
                    break
                time.sleep(1)

            
            result['filename'] = frame
            if date_result.status == OperationStatusCodes.succeeded:
                if len(date_result.analyze_result.read_results[0].lines) == 1:
                    date = format_date(date_result.analyze_result.read_results[0].lines[0].text)
                elif len(date_result.analyze_result.read_results[0].lines) > 1:
                    date = ''
                    for line in date_result.analyze_result.read_results[0].lines:
                        date += line.text
                    date = format_date(date)
                else:
                    date = "Invalid"
                print("Date: " + date)
                result['date'] = date

            if frame_result.status == OperationStatusCodes.succeeded:
                if len(frame_result.analyze_result.read_results[0].lines) == 1:
                    frame = format_frame(frame_result.analyze_result.read_results[0].lines[0].text)
                elif len(frame_result.analyze_result.read_results[0].lines) > 1:
                    frame = ''
                    for line in frame_result.analyze_result.read_results[0].lines:
                        frame += line.text
                    frame = format_frame(frame)
                else:
                    frame = "0"
                print("Frame: " + frame)
                result['frame'] = frame

            results.append(result)
        except:
            results.append({'filename': frame, 'date': 'Invalid', 'frame': 'Invalid'})
    df = pd.DataFrame(results)
    df.to_csv('./results.csv')
    # df["date"] = pd.to_datetime(df["date"], errors='ignore')
    # df = df.sort_values(by="date")
    # df.to_csv('./results.csv')

def build_video_from_frames():
    df = pd.read_csv('./results.csv')
    df = pd.read_csv('./results.csv', index_col=[0])
    dates = df['date'].unique()
    for date in dates:
        temp_df = df[df['date'] == date]
        temp_df = temp_df.sort_values(by='frame')
        images = []
        for _, row in temp_df.iterrows():
            img = cv2.imread(base_path + row['filename'])
            height, width, layers = img.shape 
            images.append(img)
        video = cv2.VideoWriter(date + ".avi", 0, 30, (width, height)) 
        for image in images:
            video.write(image)
        cv2.destroyAllWindows() 
        video.release()

extract_date_and_frame_number()
# build_video_from_frames()