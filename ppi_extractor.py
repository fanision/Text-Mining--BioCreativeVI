from xml.dom import minidom
import csv
import collections
from pycorenlp import StanfordCoreNLP
import pickle

#xmldoc = minidom.parse('AIMED-unified-format.xml')


###################
#construct relation dict
###################

relation_word_list=[]
with open("/Users/fanision/Desktop/Thesis_Research/corpora/PPIFinder_Supplementary_Data/Supplementary_Data_1_deleted.csv","r",encoding = "utf8") as f:
	reader = csv.reader(f)
	for line in reader:
		a=line[1].split(",")
		for i in a:
			relation_word_list.append(i.strip())




#the function to construct protein entity:index dict
def entity_index_dict(sent,xml):
	# itemlist = xml.getElementsByTagName('sentence')
	# for sentence in itemlist:
	# 	if sentence.attributes["id"].value.split(".")[2]==sent:
	# 		sen = sentence.attributes['text'].value

	dict = {}
	itemlist = xml.getElementsByTagName('entity')
	for entity in itemlist:
		if entity.attributes["id"].value.split(".")[2]==sent:
			dict[entity.attributes["id"].value]=int(entity.attributes["charOffset"].value.split('-')[0])
	return dict
#{AIMed.d29.s244.e0:79;AIMed.d29.s244.e0:90}
#entity id: starting position


def REL_locator(sent, xml):
	dict={}
	itemlist = xml.getElementsByTagName('sentence')
	for sentence in itemlist:
		if sentence.attributes["id"].value.split(".")[2]==sent:
			sen = sentence.attributes['text'].value
	nlp = StanfordCoreNLP('http://localhost:9000')
	text = (sen)

	output = nlp.annotate(text, properties={'annotators': 'tokenize,ssplit,pos,depparse,parse','outputFormat': 'json'})
	for i in output['sentences'][0]['tokens']:
		if "N" in i["pos"] or "V" in i["pos"]:
			if i["word"] in relation_word_list:
				dict[i["word"]]=[]
				dict[i["word"]].append(i["characterOffsetBegin"])
				dict[i["word"]].append(i["pos"])
	return dict
#{'binding': [110, 'NN']}



def PPI_generator(p_entity_dict,REL_dict):
	final_dict = {}
	ans_dict={}
	protein_list=[]
	d = collections.OrderedDict(sorted(p_entity_dict.items()))
	for key,value in d.items():
		protein_list.append(key)
	print("This group has"+str(len(protein_list))+" protein entities")
	if len(protein_list)>2:
		# for i in range(len(protein_list)-1):
		# 	pair = ""
		# 	next = i+1
		# 	while d[protein_list[next]] == d[protein_list[i]]and next!=len(protein_list)-1:
		# 		next+=1
		# 	if d[protein_list[next]] != d[protein_list[i]]:
		# 		pair+=protein_list[i]
		# 		pair+=";"
		# 		pair+=protein_list[next]
		# 		ans_dict[pair]=[]
		# 	else: continue
		for i in range(len(protein_list)):
			for m in range(i+1,len(protein_list)):
				if p_entity_dict[protein_list[i]]!=p_entity_dict[protein_list[m]]:
					pair = protein_list[i]+";"+protein_list[m]
					ans_dict[pair]=[]

	else:
		pair = ""
		pair+=protein_list[0]
		pair+=";"
		pair+=protein_list[1]
		ans_dict[pair]=[]

	if REL_dict == {}:
		for key,value in ans_dict.items():
			final_dict[key] = []
			final_dict[key].append(4)
			#feature index '1', pos of REL. because there is no REL, pad '1' here
			final_dict[key].append(0)
			#feature index '2', the number of protein entites
			final_dict[key].append(len(protein_list))

	else:
		for key,value in REL_dict.items():
			index = value[0]
			pos = value[1]
			for k,v in ans_dict.items():
				ppi = k.split(";")
				#feature index '0', the position of REL compared to PPs
				if index<p_entity_dict[ppi[0]]:
					final_dict[k+";"+key]=[]
					final_dict[k+";"+key].append(1)
					#feature index '1', pos of REL, N=0, V=1
					if pos[0]=="N":
						final_dict[k+";"+key].append(0)
					else:
						final_dict[k+";"+key].append(1)
					#feature index '2', the number of protein entites
					final_dict[k+";"+key].append(len(protein_list))
				elif index>p_entity_dict[ppi[0]] and index<p_entity_dict[ppi[1]]:
					final_dict[k+";"+key]=[]
					final_dict[k+";"+key].append(2)
					#feature index '1', pos of REL, N=0, V=1
					if pos[0]=="N":
						final_dict[k+";"+key].append(0)
					else:
						final_dict[k+";"+key].append(1)
					#feature index '2', the number of protein entites
					final_dict[k+";"+key].append(len(protein_list))
				else:
					final_dict[k+";"+key]=[]
					final_dict[k+";"+key].append(3)
					#feature index '1', pos of REL, N=0, V=1
					if pos[0]=="N":
						final_dict[k+";"+key].append(0)
					else:
						final_dict[k+";"+key].append(1)
					#feature index '2', the number of protein entites
					final_dict[k+";"+key].append(len(protein_list))
	return final_dict
#{'AIMed.d29.s244.e0;AIMed.d29.s244.e1;binding': [2], 
#'AIMed.d29.s244.e1;AIMed.d29.s244.e3;binding': [1], 
#'AIMed.d29.s244.e2;AIMed.d29.s244.e3;binding': [1], 
#'AIMed.d29.s244.e3;AIMed.d29.s244.e4;binding': [1], 
#'AIMed.d29.s244.e4;AIMed.d29.s244.e5;binding': [1]}


def protein_entity_distance(sen,generator_dict,entity_dict):
	for key, value in generator_dict.items():
		a=key.split(";")
		e1=entity_dict[a[0]]
		e2=entity_dict[a[1]]
		distance = sen[e1:e2].count(" ")
		value.append(distance)
	return generator_dict


def protein_REL_distance(b,sen,entity_dict,rel_dict):
	for key,value in b.items():
		p1 = int(entity_dict[key.split(";")[0]])
		p2 = int(entity_dict[key.split(";")[1]])
		if value[0]==4:
			value.append(0)
			value.append(0)
		if value[0]==1:
			rel = int(rel_dict[key.split(";")[2]][0])	
			value.append(sen[rel:p1].count(" "))
			value.append(sen[rel:p2].count(" "))
		if value[0]==2:
			rel = int(rel_dict[key.split(";")[2]][0])	
			value.append(sen[p1:rel].count(" "))
			value.append(sen[rel:p2].count(" "))
		if value[0]==3:
			rel = int(rel_dict[key.split(";")[2]][0])	
			value.append(sen[p1:rel].count(" "))
			value.append(sen[p2:rel].count(" "))
	return b
		




def negation_position(b,sen,entity_dict,rel_dict):
	switch = 0
	l = sen.split(" ")
	for i in l:
		if i=="no" or i=="not" or i=="neither" or i=="nor":
			print(i)
			m = {}
			m[sen.index(i)] = 'neg'
			for key,value in b.items():
				m[int(entity_dict[key.split(";")[0]])] = 'p1'
				m[int(entity_dict[key.split(";")[1]])] = 'p2'
				if value[0]==4:
					d = collections.OrderedDict(sorted(m.items()))
					w=[]
					for key,v in d.items():
						w.append(v)
					try:
						str=w[w.index("neg")+1]
						value.append(1)
						value.append(num_determiner(str))
					except IndexError:
						value.append(0)
						value.append(0)
				else:
					m[rel_dict[key.split(";")[2]][0]]="rel"
					d = collections.OrderedDict(sorted(m.items()))
					w=[]
					for key,v in d.items():
						w.append(v)
					try:
						str=w[w.index("neg")+1]
						value.append(1)
						value.append(num_determiner(str))
					except IndexError:
						value.append(0)
						value.append(0)
			switch =1
			break
	if switch ==1:
		return b
	else:
		for key,value in b.items():
				value.append(0)
				value.append(0)
		return b

def num_determiner(str):
	if str=="rel":
		return 1
	if str=="p1":
		return 2
	if str=="p2":
		return 3

def interacting_determiner(b,record):
	for key,value in b.items():
		l=key.split(";")
		pair =l[0]+";"+l[1]
		if pair in record:
			value.append(1)
		else:
			value.append(0)
	return b





data_for_training=[]

xmldoc_AIMED = minidom.parse('output.xml')

# itemlist = xmldoc_AIMED.getElementsByTagName('entity')
# cnt = 0
# for i in itemlist:
# 	if cnt > 1000:
# 		break
# 	cnt += 1
# 	print(i.attributes['id'].value)



for s in range(4795):
	id = "s"+str(s)
	print(id)
	#make sure there are more than 1 protein entity in the sentence
	count = 0
	itemlist = xmldoc_AIMED.getElementsByTagName('entity')
	for entity in itemlist:
		# print(entity.attributes["id"].value.split("."))
		if entity.attributes["id"].value.split(".")[2]==id:
			count+=1
	itemlist = xmldoc_AIMED.getElementsByTagName('sentence')
	for sentence in itemlist:
		if sentence.attributes["id"].value.split(".")[2]==id:
			sen = sentence.attributes['text'].value
	itemlist = xmldoc_AIMED.getElementsByTagName('interaction')
	interaction_record=[]
	for interaction in itemlist:
		if interaction.attributes["id"].value.split(".")[2]==id:
			if interaction.attributes["e1"].value<=interaction.attributes["e2"].value:
				b=interaction.attributes["e1"].value+";"+interaction.attributes["e2"].value
				interaction_record.append(b)
			else:
				b=interaction.attributes["e2"].value+";"+interaction.attributes["e1"].value
				interaction_record.append(b)
	print(interaction_record) 
	if count>=2:
		pro=entity_index_dict(id,xmldoc_AIMED)
		w=REL_locator(id,xmldoc_AIMED)
		a=PPI_generator(pro,w)
		#feature index 3, the distance between two protein entities
		b=protein_entity_distance(sen,a,pro)
		#feature index 4,5, distance of REL to two protein entities
		#for ppi where there is no REL, both 4,5 are 0.
		b=protein_REL_distance(b,sen,pro,w)
		###############
		#feature index 6,7, negation word and its relative position
		#if none, both are 0
		b=negation_position(b,sen,pro,w)
		#########the last value in the vector is the binary value for if it is interacting
		b=interacting_determiner(b,interaction_record)
		print(b)
		data_for_training.append(b)
	else:
		print(id+" is skipped")
		continue

	


# xmldoc_AIMED = minidom.parse('bioinfer-unified-format.xml')

# for s in range(1010):
# 	id = "s"+str(s)
# 	print(id)
# 	#make sure there are more than 1 protein entity in the sentence
# 	count = 0
# 	itemlist = xmldoc_AIMED.getElementsByTagName('entity')
# 	for entity in itemlist:
# 		if entity.attributes["id"].value.split(".")[2]==id:
# 			count+=1
# 	itemlist = xmldoc_AIMED.getElementsByTagName('sentence')
# 	for sentence in itemlist:
# 		if sentence.attributes["id"].value.split(".")[2]==id:
# 			sen = sentence.attributes['text'].value
# 	itemlist = xmldoc_AIMED.getElementsByTagName('interaction')
# 	interaction_record=[]
# 	for interaction in itemlist:
# 		if interaction.attributes["id"].value.split(".")[2]==id:
# 			if interaction.attributes["e1"].value<=interaction.attributes["e2"].value:
# 				b=interaction.attributes["e1"].value+";"+interaction.attributes["e2"].value
# 				interaction_record.append(b)
# 			else:
# 				b=interaction.attributes["e2"].value+";"+interaction.attributes["e1"].value
# 				interaction_record.append(b)
# 	print(interaction_record) 
# 	if count>=2:
# 		pro=entity_index_dict(id,xmldoc_AIMED)
# 		w=REL_locator(id,xmldoc_AIMED)
# 		a=PPI_generator(pro,w)
# 		#feature index 3, the distance between two protein entities
# 		b=protein_entity_distance(sen,a,pro)
# 		#feature index 4,5, distance of REL to two protein entities
# 		#for ppi where there is no REL, both 4,5 are 0.
# 		b=protein_REL_distance(b,sen,pro,w)
# 		###############
# 		#feature index 6,7, negation word and its relative position
# 		#if none, both are 0
# 		b=negation_position(b,sen,pro,w)
# 		#########the last value in the vector is the binary value for if it is interacting
# 		b=interacting_determiner(b,interaction_record)
# 		print(b)
# 		data_for_training.append(b)
# 	else:
# 		print(id+" is skipped")
# 		continue






#pro=entity_index_dict("s244",xmldoc_AIMED)
# w=REL_locator("s1274",xmldoc_AIMED)
# PPI_generator(pro,w)



with open('bioCreative.pickle', 'wb') as handle:
	pickle.dump(data_for_training,handle)













