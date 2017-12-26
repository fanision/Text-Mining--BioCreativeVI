import json
from pprint import pprint
import urllib.request
import pickle
from xml.dom import minidom




#load Biocreative annotated data
xmldoc_BioCreative = minidom.parse('corpora/output.xml')

#load ground truth
data = json.load(open('PMtask_Relations_TrainingSet.json'))



#load predicted pairs
with open("with_sentence_id_predict_result.pickle",'rb') as f:
    predict_result = pickle.load(f)

with open("filtered_result.pickle",'rb') as f:
	filtered_result = pickle.load(f)
# print("result format: "+str(predict_result["d21775823"]))
# print("total entity number is: "+str(len(predict_result.keys())))
# total_pos_count =0
# for k,v in predict_result.items():
# 	for i in v:
# 		total_pos_count+=1
# print("there is total # pair of positive in prediction: "+str(total_pos_count))



##########add filters here to try F score##############

def mutation_finder(id):
	mutation_rec = set()
	url = "https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/Mutation/"+id+"/json/"
	sock = urllib.request.urlopen(url) 
	htmlSource = sock.read  ()                            
	sock.close()
	d=json.loads(htmlSource)
	for mutation in d["denotations"]:
		try:
			m = mutation["obj"].split("|")
			mut = m[2]+m[3]+m[4][0]
			mutation_rec.add(mut.lower())
		except IndexError:
			try:
				m = mutation["obj"].split("|")
				mut = m[1]+m[2]+m[3][0]
				mutation_rec.add(mut.lower())
			except IndexError:
				continue


	print(mutation_rec)
	return mutation_rec


#filtered_result: use mutation detection and "muta" detection; when for a document, there is no sentence
#satisfy these, get the whole original list.eg. d23446637[]
#however, in the result, there is sxxx(sentence id)
#that's the reason why need final_result
temp_result = {}
for key,value in filtered_result.items():
	if value==[]:
		temp_result[key]=predict_result[key]
	else:
		temp_result[key]=filtered_result[key]


#remove sentence id in the sentence
final_result = {}
for key,value in temp_result.items():
	final_result[key]=[]
	for i in value:
		i=list(i)
		if len(i)==1:
			a=i[0].split(".")[0]
			if a not in final_result[key]:
				final_result[key].append({a})
		else:
			a={i[0].split(".")[0],i[1].split(".")[0]}
			if a not in final_result[key]:
				final_result[key].append(a)



#real final result(ff_result), such as this situation:d20664522[{'1079475', '6249'}, {'5347'}, {'6249', '5347'}]
#because '5437' is in {'5437','6249'}, this sigle interacted one will be removed.
ff_result = {}
for key,value in final_result.items():
	ff_result[key]=[]
	temp=[]
	for i in value:
		i = list(i)
		if len(i)==2:
			ff_result[key].append(set(i))
			temp.append(i[0])
			temp.append(i[1])
	for i in value:
		i=list(i)
		if len(i)==1:
			if i[0] in temp:
				continue
			else:
				ff_result[key].append(set(i))
for key,value in ff_result.items():
	print(key)
	print(value)




total_positive = 0
for k,v in ff_result.items():
	for i in v:
		total_positive+=1
print("totoal positive is "+str(total_positive))









ground_truth={}
for i in data["documents"]:
	ground_truth[i["id"]]=[]
	for w in i["relations"]:
		ground_truth[i["id"]].append({w["infons"]["Gene1"],w["infons"]["Gene2"]})
	
print("ground_truth format"+ str(ground_truth["8922390"]))
print("below is the number of entries where protein interacts with itself")







tp_count = 0
for key,value in ff_result.items():
	gr_t=ground_truth[key[1:]]
	for v in value:
		if v in gr_t:
			tp_count+=1
print("recall is this many: "+str(tp_count))




# print("xxxxxxxxxxxxxxxxxxxx")
# article_list=[]
# for k,v in ff_result.items():
# 	article_list.append(k[1:])
# for k,v in ground_truth.items():
# 	if k not in article_list:
# 		print(k)







# filtered_result is the one with doing mutation detection and key word detection
# filtered_result={}
# itemlist = xmldoc_BioCreative.getElementsByTagName('sentence')

# for article_id,pair in predict_result.items():
# 	print(article_id)
# 	mut = mutation_finder(article_id[1:])
# 	filtered_result[article_id]=[]
# 	for i in pair:
# 		id=list(i)[0].split(".")[1][1:]
# 		for sentence in itemlist:
# 			if sentence.attributes["id"].value.split(".")[2][1:]==id:
# 				sen = sentence.attributes['text'].value.lower()
# 		for p in mut:
# 			if p in sen:
# 				filtered_result[article_id].append(i)
# 				break
# 		if "muta" in sen:
# 			if i not in filtered_result[article_id]:
# 				filtered_result[article_id].append(i)
# for u,o in filtered_result.items():
# 	print(u)
# 	print(o)
# 	break
# print("predict_result has this many doc: "+str(len(predict_result.keys())))
# print("filtered_result has this many doc: "+str(len(filtered_result.keys())))

# with open('filtered_result.pickle', 'wb') as handle:
#     pickle.dump(filtered_result,handle)











