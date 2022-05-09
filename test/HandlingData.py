import re  #regular expression
import json

# ------------------------------------------------------------------------------------

# 1. Get data of components from the model (.xml file): Class-functions-FSM
# 2. Get constraints from the requirements (which not appears in the model)
# ------------------------------------------------------------------------------------

dsl_requirement_file = "input/inputDSL.txt" # "inputHeroku.txt" "inputDSL.txt"
xml_model_file = "input/mlamp.xml"	# "monitorswitch.xml" "mlamp.xml"
dict_class_instances = dict()	# Class data

#---------------------------------------------
# Read file line by line
def readInput(input):
	f = open(input,"r")
	lines = f.readlines()
	result = ""

	for line in lines:
		result += line

	return result

#---------------------------------------------
# 1. Read XML File
# 		Save data structure: className - {state: list-of-coming-actions} into list

#-----
# The structure of each element in the model
class ElementInfo:
	def __init__(self, _className, _dict_stt_act):
		self.className = _className
		self.dict_stt_act = _dict_stt_act

	def eprintInfor(self):
		print (self.className + ":\n\t" + str(self.dict_stt_act))

#------------------------- -------------------------
# Read xml file
def readXML(xmlFile):
	f = open(xmlFile,"r")
	lines = f.readlines()
	result = ""
	className = ""
	flagStarting = False
	dict_stt_act = {}
	listClassInfo = []
	dictClassInfor = dict()
	list_actions = []
	list_states = []
	tmp_detail = {}
	# dict_detail = {}

	# dict_req = dict()
	tmp_req = dict()
	for line in lines:

		# ---
		if "<class name" in line:
			nameStr = line[line.index("name=")+6:]
			name = nameStr[0 : nameStr.index('"')]
			# print (name)
			className = name

		if "<transition" in line:
			sttStr = line[line.index("to=")+4:]
			stt = sttStr[0 : sttStr.index('"')]
			actionStr = line[line.index("action=")+8:]
			action = actionStr[0: actionStr.index('"')]
			try:
				dict_stt_act[stt].append(action)
			except:
				dict_stt_act[stt] = [action]

		if "<action" in line:
			action_name = line[line.index("name=")+6:line.rindex("\"")]
			list_actions.append(action_name)

		if "<place" in line:
			stateStr = line[line.index("name=")+6:]
			state_name = stateStr[0:stateStr.index('"')]
			list_states.append(state_name)


		if "</class>" in line:
			for key in dict_stt_act.keys():
				new_value = (list(set(dict_stt_act[key])))
				dict_stt_act[key] = new_value
			tmp = ElementInfo(className, dict_stt_act)
			listClassInfo.append(tmp)
			print (list_states)
			print (list_actions)
			tmp_detail[className] = [list_states]
			tmp_detail[className].append(list_actions)
			className = ""
			dict_stt_act = {}
			list_states = []
			list_actions = []

		# ---  requirements
		if "<annotations name=\"Specification\">" in line:
			flagStarting = True
		if "<annotation id=" in line and flagStarting == True:
			
			reqNameStr = line[line.index("id=")+4:]
			req_name = reqNameStr[0 : reqNameStr.index('"')]
			# req_name = req_name.replace("-","_")
			req_name = re.sub(r'-|\s', "_", req_name)
			req_content = re.findall(r'\>(.*)\<', line)[0]
			# print ("req_name: " + req_name + "\treq_content: " + req_content)
			tmp_req[req_name] = req_content
			# try:
			# 	dictClassInfor["Specification"].append(tmp_req)
			# except:
			# 	dictClassInfor["Specification"] = [tmp_req]
		if "</annotations>" in line:
			flagStarting = False
		# result += line
		# print (line)

	tmp_class = {}
	for elm in listClassInfo:
		elm.eprintInfor()
		tmp_class[elm.className] = elm.dict_stt_act

	dictClassInfor["Class"] = tmp_class
	dictClassInfor["Specification"] = tmp_req
	dictClassInfor["Detail"] = tmp_detail

	# return result
	return dictClassInfor
# END ------------------------- -------------------------

#------------------------- -------------------------
# Read xml file
def get_requirements(xmlFile):
	f = open(xmlFile,"r")
	lines = f.readlines()
	result = ""
	flagStarting = False
	dict_req = dict()
	for line in lines:
		if "<annotations name=\"Specification\">" in line:
			flagStarting = True
		if "<annotation id=" in line and flagStarting == True:
			tmp_req = dict()
			reqNameStr = line[line.index("id=")+4:]
			req_name = reqNameStr[0 : reqNameStr.index('"')]
			# req_name = req_name.replace("-","_")
			req_name = re.sub(r'-|\s', "_", req_name)
			req_content = re.findall(r'\>(.*)\<', line)[0]
			# print ("req_name: " + req_name + "\treq_content: " + req_content)
			tmp_req[req_name] = req_content
			try:
				dict_req["Specification"].append(tmp_req)
			except:
				dict_req["Specification"] = [tmp_req]
		if "</annotations>" in line:
			flagStarting = False

	# print (dict_req)

# END ------------------------- -------------------------

# dict_class_instances = readXML(xml_model_file)
# print (dict_class_instances)
# # print (dict_class_instances)
# get_requirements(xml_model_file)

# with open('gen-data/data.json', 'w') as fp:
#     json.dump(dict_class_instances, fp)

# with open('gen-data/data.json', 'r') as fp:
#     data = json.load(fp)

# print("\n\n --- Ontology ---")
# print(data)
# print("\n\n --- Class info ---")
# print(data['Specification'])