import json
from pprint import pprint
import urllib.request



# id_list=[]
# data = json.load(open('PMtask_Relations_TrainingSet.json'))


# print(data["documents"][0])

# # for id in data["documents"]:
# #     id_list.append(id['id'])



# result = []
# count = 1
# for id in id_list:
#   print(count)
#   count+=1
#   url = "https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/Gene/"+id+"/json/"
#   sock = urllib.request.urlopen(url) 
#   htmlSource = sock.read  ()                            
#   sock.close()
#   result.append(htmlSource)

def compare(orifile, toolfile):
    ori = []
    for x in orifile['passages']:
        for i in x['annotations']:
            ori.append(i['locations'][0]['offset'])
    ori.sort()
    print(ori)
    tool = []
    for x in toolfile["denotations"]:
        tool.append(x['span']['begin'])
    tool.sort()
    print(tool)

    pter1 = 0
    pter2 = 0
    cnt = 0
    while pter1 < len(ori) and pter2 < len(tool):
        # print(pter1, pter2)
        if ori[pter1] < tool[pter2]:
            pter1 += 1
        elif ori[pter1] > tool[pter2]:
            pter2 += 1
        else:
            cnt += 1
            pter1 += 1
            pter2 += 1
    print('compared:', cnt)
    print('original:', len(ori))
    print('ratio:', float(cnt)/len(ori))
    return (cnt, len(ori))

ori = object()
cnt = 0
sum = 0
with open('PMtask_Relations_TrainingSet.json','r') as orifile:
    ori = json.load(orifile)
    for compo in ori['documents']:
        result = []
        try:
            url = "https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/Gene/"+ compo['id']+"/json/"
            sock = urllib.request.urlopen(url) 
            htmlSource = sock.read()                    
            sock.close()
            # print(htmlSource)
            toolfile = json.loads(htmlSource.decode('utf-8'))
            if len(toolfile['denotations']) == 0:
                continue
            print('paperID:', compo['id'])
            c, s = compare(compo, toolfile)
            cnt += c
            sum += s
        except Exception as e:
            print(str(e))
print(cnt, sum, cnt/sum)

