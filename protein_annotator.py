from PIL import Image
import os
import numpy as np
import pylab as pl
import time
import random
import math
import csv
from collections import namedtuple
from threading import Thread
import pymysql
import urllib.request

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import queue
import threading
import time
import json
from nltk.tokenize import sent_tokenize, word_tokenize


def convone(ori, root):
    # print(sent_tokenize(ss))
    global offset
    offset += 1
    pos = []
    articalId = 0
    text = ''

    text = ori['text']
    articalId = ori['sourceid']
    for x in ori['denotations']:
        pos.append([x['span']['begin'], x['span']['end'], x['obj'][5:]])
    # print(x)
    # print(articalId)
    # print(pos)
    # print(text)
    pos.sort()
    # for x in pos:
    #     print(x[0], end='\t')
    # print()
    sentences = sent_tokenize(text)
    for x in range(len(sentences)):
        if x != 0:
            sentences[x] = ' ' + sentences[x]
        # print(len(sentences[x]), end='\t')
    # print()
    # a = ET.Element('sentence')
    # id = 'd' + articalId + ',s' +
    # c = ET.SubElement(a, 'child')
    # c.text = 'some text'
    # d = ET.SubElement(a, 'child2')
    # b = ET.Element('elem_b')
    # root = ET.Element('root')
    # root.extend((a, b))
    # tree = ET.ElementTree(root)
    # tree.write('ss/output.xml')

    senid = -1
    senlen = 0
    entid = 0
    id = ""
    isempty = True
    # print(len(sentences))
    for x in pos:

        # print('x[0] and senlen: ', x[0], senlen)
        if x[0] >= senlen:
            while x[0] >= senlen:
                if senid < 0:
                    senid += 1
                    senlen += len(sentences[senid])
                    continue

                if isempty is True:
                    root.append(ET.Element('sentence'))
                    a = root[-1]
                    id = 'x.d' + str(articalId) + '.s' + str(senid + offset)
                    a.set('id', id)
                    a.set('text', sentences[senid])
                isempty = True

                senid += 1
                senlen += len(sentences[senid])
                # print('curlen and senlen: ', len(
                #     sentences[senid]) if senid >= 0 else 0, senlen)
            # if senid >= len(sentences):
            #     continue;
            isempty = False
            entid = 0
            root.append(ET.Element('sentence'))
            a = root[-1]
            id = 'x.d' + str(articalId) + '.s' + str(senid + offset)
            a.set('id', id)
            a.set('text', sentences[senid])

            entity = ET.SubElement(a, 'entity')
            entity_id = id + '.e' + str(entid)
            entity.set('id', entity_id)
            # print('charOffset: ', str(x[0]) + '-' + str(x[1]))
            entity.set('charOffset', str(x[0]) + '-' + str(x[1]))
            entity.set('Gene', str(x[2]))
        else:
            a = root[-1]
            entid += 1

            entity = ET.SubElement(a, 'entity')
            entity_id = id + '.e' + str(entid)
            entity.set('id', entity_id)
            # print('charOffset: ', str(x[0]) + '-' + str(x[1]))
            entity.set('charOffset', str(x[0]) + '-' + str(x[1]))
            entity.set('Gene', str(x[2]))
    offset += senid


offset = 0
root = ET.Element('root')
with open('ss/PMtask_Relations_TestingSet.json', 'r') as orifile:
    ori = json.load(orifile)
    cnt = 0
    aa = 0
    for compo in ori['documents']:
        # if aa > 5:
        #     break
        # aa += 1
        result = []
        try:
            url = "https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/Gene/" + \
                compo['id'] + "/json/"
            # url = 'https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/Gene/20618438/json/'
            print(url)
            sock = urllib.request.urlopen(url)
            htmlSource = sock.read()
            sock.close()
            # print(htmlSource)
            toolfile = json.loads(htmlSource.decode('utf-8'))
            convone(toolfile, root)
        except Exception as e:
            cnt += 1
            print(str(e))
tree = ET.ElementTree(root)
tree.write('ss/output.xml')
print(cnt)


