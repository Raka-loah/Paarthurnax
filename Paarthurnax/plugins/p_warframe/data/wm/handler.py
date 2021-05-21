import os
import json
import re
from functools import reduce

def readFile (path) :
  with open(os.path.join(os.path.dirname(os.path.abspath(__file__))  ,path) , 'r', encoding='utf-8') as file:
    return json.loads(file.read())

toListItem  = lambda item: "\"{name}\":\"{url}\"".format(name = item["item_name"], url = item["url_name"])
mergeToJSONFormat = lambda acc, cur: acc + "," + cur
mergeJSONItems = lambda arr: "{" + reduce(mergeToJSONFormat, arr) + "}"

filterItems =lambda reg ,arr: filter((lambda item: re.search(reg, item) != None), arr)

def convertToRegobj (rules) : 
  regObj = []
  for (key,value) in rules.items():
    regObj.append({'reg': key, 'rep': value})
  return regObj

def writeFile (datas, path):
  with open(os.path.join(os.pardir, path), 'w') as ot:
    ot.write(mergeJSONItems(datas))

def output (): 
  wmCantRaw = readFile('wmCant.json')
  wmEnRaw = readFile('wmEN.json')
  wmCnRaw = readFile('wmCN.json')
  regObj = convertToRegobj(wmCantRaw)
  wmcn = reduce(mergeToJSONFormat, map(toListItem , wmCnRaw["items"]))
  wmen = reduce(mergeToJSONFormat, map(toListItem , wmEnRaw["items"]))
  wcant =reduce(mergeToJSONFormat, map(lambda regObj : reduce(mergeToJSONFormat,map(lambda item: item.replace(regObj['reg'], regObj['rep']),filterItems( regObj['reg'], map(toListItem , wmCnRaw["items"])))), regObj))
  writeFile([wmcn, wmen, wcant],'wmNew.json')
