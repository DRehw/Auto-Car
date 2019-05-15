'''
Created on May 12, 2019

@author: Dave
'''
import ast
import json

def getJsonDataFromTag(jsonString, jsonTag):
    jsonObj = json.loads(jsonString)
    res=None
    for key, value in jsonObj.items():
        if key == jsonTag:
            res = ast.literal_eval(str(value))
            #print(res)
            break
    return res

def parseAADCData(aadc_data, JSONtag):
    start = aadc_data.find(JSONtag) + len(JSONtag) + 2
    ss = aadc_data[start + 1:]
    end = ss.find(':')
    ss = ss[:end]
    result = [[]]
    if end != -1 :
        end = ss.rfind(',')
        ss = ss[:end]
        result = ast.literal_eval(ss)
    return result

def parseLidarData(aadc_lidar):
    start = aadc_lidar.find("[")
    ss = aadc_lidar[start:-1]
    print(ss)
    result = ast.literal_eval(ss)
    return result