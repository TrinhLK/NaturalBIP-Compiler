import re
import json
import itertools

keywords = [": ", ".", "there is ", "there are ", "For ", "for "]
patterns = ["if ", "If ", "While ", "while ", "After ", " after ", "Before ", "before "]

sample_2 = "Req_01: \"For any Tracker    t, if t execute broadcast, there is a Peer p such that p is registered to t and p shall either speak or listen and all Peer p1 where p1 is registerd to t and p1 is different with p and p1 shall not speak.\""

req_name = sample_2[0:sample_2.index(":")]
req_content = re.findall(r'\"(.+)\"',sample_2)[0]

# ------------------------------------ ------------------------------------
# PRE-PROCESSING: the input text
def standardize_input_requirement(input_requirement):
	# remove redundant spaces
	input_requirement = re.sub(" +", " ", input_requirement)

	# replace not execute act --> execute ~act
	input_requirement = re.sub(" not execute ", " execute ~", input_requirement)
	input_requirement = re.sub(" not executes ", " execute ~", input_requirement)

	# replace shall not act --> shall ~act
	input_requirement = re.sub(" shall not ", " shall ~", input_requirement)

	# replace x shall either A or B --> (x shall ~A or x shall ~B)
	list_of_tuples = re.findall(r'(\s([^\s]+)\sshall either ([^\s]+) or ([^\s|\,]+))', input_requirement)
	print (list_of_tuples)
	for tuple_i in list_of_tuples:
		new_content = " (" + tuple_i[1] + " shall ~" + tuple_i[2] + " or " + tuple_i[1] + " shall ~" + tuple_i[3] + ")"
		input_requirement = re.sub(tuple_i[0], new_content, input_requirement)

	return input_requirement
# END ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
# PRE-PROCESSING: From input_string, return [standardized input, list_class_instance_string, dict_class_instance]
def get_standardized_requirement (input_requirement, ontology):
	result = []
	# ----- standardize spacing in the text
	input_requirement = standardize_input_requirement(input_requirement)
	print ("\n\n---- new input_req: " + input_requirement)

	# -----  get class-instance information
	print ("\n-- class-instance:\n")
	criteria_class_instance = r'((any|every| all|a|one|some)\s([^\s]+)\s([^\s]+)(\,[\s]*|\ssuch that[\s]*|\swhere|\,\sin which\,[\s]*|\:[\s]*))'

	list_class_instance = search_from_input(input_requirement, criteria_class_instance)
	print (list_class_instance)

	list_class_instance_string = [element[0] for element in list_class_instance]
	dict_class_instances = dict()
	for element in list_class_instance:
		try:
			dict_class_instances[element[2]].append(element[3])
		except:
			dict_class_instances[element[2]] = [element[3]]

	print ("dict_class_instances: " + str(dict_class_instances))
	# ----- replace state by actions
	input_requirement = replace_state_by_actions(input_requirement, ontology, dict_class_instances)
	result.append(input_requirement)
	result.append(list_class_instance)
	result.append(dict_class_instances)

	return result
# END ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
# SKOLEMIZATION:
# 	Find all result from a string following a given pattern
# 	Save them into a list
def check_dependent_instance(req_name, condition_string, list_values):
	result = []
	req_name = re.sub(r'\_|\-', "", req_name)
	list_words_in_string = condition_string.split("_")

	the_first_var = ''
	for elm in list_values:
		if list_words_in_string[0] == elm[3]:
			the_first_var = elm[0]
	if the_first_var == '':
		return result
	# print ("checking: " + list_words_in_string[0] + "\t\t" + elm[3])
	# print ("the_first_var: " + str(the_first_var))
	the_first = [elm for elm in list_values if list_words_in_string[0] == elm[3]][0]
	the_second = [elm for elm in list_values if list_words_in_string[len(list_words_in_string)-1] == elm[3]][0]

	if the_first[1].strip() in ['a', 'some', 'one'] and the_second[1].strip() in ['every', 'any', 'all'] and list_values.index(the_first) > list_values.index(the_second):
		result = [the_first[3]]
		result.append(req_name + the_second[3] + the_first[3])
	if the_second[1].strip() in ['a', 'some', 'one'] and the_first[1].strip() in ['every', 'any', 'all'] and list_values.index(the_first) < list_values.index(the_second):
		result = [the_second[3]]
		result.append(req_name + the_first[3] + the_second[3] + the_second[3])
	
	return result

# END ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
# QUANTIFIERS, STATE, ACTION:
# 	Find all result from a string following a given pattern
# 	Save them into a list
def search_from_input(input_string, criteria):
	list_of_tuples = re.findall(criteria, input_string)
	result = []
	for element in list_of_tuples:
		# print (element)
		new_elem = []
		for x in element:
			if x != '':
				new_elem.append(x)
		result.append(new_elem)
	return result
# END ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
# STATE: 
# 	From "A is in state_s": get all transitions come in state_s
def get_list_actions_from_state(ontology, className, search_state):
	# print ("\n --- Check get list actions come to a state")
	# print ("className: " + className + "\t\tsearch_state: " + search_state)
	result = []
	for keys in ontology.keys():
		if keys == className:
			print (keys)
			print (ontology[keys])
			for state in ontology[keys]:
				# print (state + "\t\t\t" + search_state)
				# ontology[keys][state]
				if state == search_state:
					result.append(ontology[keys][state])
					print ("\n--check ontology: " + str(ontology[keys][state]))
	return result[0]
# END ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
# STATE: 
# 	replace "A is in state_s" by "(A shall act_1 or ... or A shall act_n)" in the requirement
# 	remove \sin\s because ex: m is deploy IN vm
def replace_state_by_actions(requirement, ontology, dict_class_instances):
	state_string = re.findall(r'((\s[^\s]+)(\sis in\s)([^\s]+)\s(state)*)', requirement)
	# print ("\n--- state_string: " + str(state_string))
	get_className = ''
	for tuple_i in state_string:
		variable = tuple_i[1].strip()
		# print ("Variable: " + variable)
		for key, value in dict_class_instances.items():
			for instances in value:
				if instances == variable:
					# print ("Class: " + key + " of " + instances)
					get_className = key
		# get list action
		stateName = tuple_i[3].strip()
		# print ("tuple_i: " + str(tuple_i))
		get_actions = get_list_actions_from_state(ontology, get_className, stateName)
		list_action = []
		for action in get_actions:
			list_action.append(tuple_i[1].strip() + " shall " + action)
		action_string = " or ".join(list_action)
		# print ('action_string: ' + action_string)
		requirement = requirement.replace(tuple_i[0], " (" + action_string + ")")
	return requirement
# END ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
# ACTIONS: From input_string, return [standardized input, list_class_instance_string, dict_class_instance]
def get_dictionary_of_actions (input_requirement, ontology):
	print ("\n-- actions:\n")
	criteria_action = r'(([^\s|\(|\,]+[\s]*)(execute[\s]+|executes[\s]+|shall[\s]+)([\~]*[\w]+))[\)|\.|\;|\,]*'
	list_action = search_from_input(input_requirement, criteria_action)
	print (list_action)
	temp_dict_action = dict()
	for element in list_action:
		temp_element = [element[0]]
		element[3] = re.sub(r"\.|\;|\)|\(|\,|\s", "", element[3])
		element[1] = re.sub(r"\.|\;|\)|\(|\,|\s", "", element[1])
		new_action = ""
		if "~" in element[3]:
			new_action = "~" + element[1] + "_" + re.sub(r"\~", "", element[3])
		else:
			new_action = element[1] + "_" + element[3]
		temp_element.append(new_action)
		temp_dict_action[element[0]] = new_action
	print (temp_dict_action)

	return temp_dict_action
# END ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
# CONDITION:
def get_conditions_of_requirement (req_name, standardized_input, temp_dict_action):
	print ("\n-- condition:\n")
	new_sample = standardized_input[0]
	list_class_instance = standardized_input[1]
	list_class_instance_string = [element[0] for element in list_class_instance]
	# print (temp_dict_action)
	for element in list_class_instance_string:
		new_sample = new_sample.replace(element, "")
	for element in temp_dict_action.keys():
		new_sample = new_sample.replace(element, "")
	for element in keywords:
		new_sample = new_sample.replace(element, "")
	for element in patterns:
		new_sample = new_sample.replace(element, "")

	x = re.split(r'[\s]and|[\s]or', new_sample)
	list_condition = []
	for element in x:
		if element != '':
			list_of_tuples = re.findall(r'\s(.+)', element)
			# print ("\n list tuples: ")
			# print (list_of_tuples)
			for tuple_i in list_of_tuples:
				tuple_i = tuple_i.strip()
				tuple_i = tuple_i.replace(",", "").strip()
				tuple_i = tuple_i.replace(" ", "_")
				if "_" in tuple_i:
					old_one = tuple_i.replace("_", " ")
					temp_cdt = [old_one]
					temp_cdt.append(tuple_i.strip())
					list_condition.append(temp_cdt)

	# Find variable for skolemization
	list_replacement = []
	for cdt in list_condition:
		if check_dependent_instance(req_name, cdt[1], list_class_instance) != []:
			list_replacement.append(check_dependent_instance(req_name, cdt[1], list_class_instance))
	print ("replacement: " + str(list_replacement))

	# Replace variable in actions
	for key in temp_dict_action:
		content = temp_dict_action[key]
		for replacement in list_replacement:
			if replacement[0]+"_" in content:
				content = content.replace(replacement[0]+"_", replacement[1]+"_")
		temp_dict_action[key] = content

	# Replace variable in condition
	dict_conditions = dict()
	for cdt in list_condition:
		variables = cdt[1].split("_")
		for replacement in list_replacement:
			if variables[0] == replacement[0]:
				variables[0] = replacement[1]
			if variables[len(variables)-1] == replacement[0]:
				variables[len(variables)-1] = replacement[1]
		new_one = "_".join(variables)
		dict_conditions[cdt[0]] = new_one

	output = []
	output.append(temp_dict_action)
	output.append(dict_conditions)

	# Replace variable
	new_content = standardized_input[0]
	for dict_i in output:
		for key, value in dict_i.items():
			new_content = new_content.replace(key, value)
	for element in list_class_instance_string:
		new_content = new_content.replace(element, "")
	for element in keywords:
		new_content = new_content.replace(element, "")
	new_content = re.sub(r'while\s|While\s', "if ", new_content)
	# new_content.replace("while ", "if ")
	# print ("\n-- Function get new req: " + new_content)
	output.append(new_content)

	# output = [dict_action, dict_condition, paraphased_requirement]
	return output
# END ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
# PATTERNS: analyze pattern
# ------------------------------------ ------------------------------------
def get_all_actions_from_ontology (ontology):
	# print ("\n--- ---")
	result = []
	list_values = ontology.values()
	for element in list_values:
		# print (element)
		for list_val in element.values():
			result = result + list_val
	# print (list_values)
	# print (list(set(result)))
	return list(set(result))

# ------------------------------------ ------------------------------------
# PATTERNS: 
# 	
def get_Boolean_formulas_form(disjunction_of_effect_clause, cause, ontology):
	result = []
	# get all actions
	list_actions = get_all_actions_from_ontology(ontology)
	for a_clause in disjunction_of_effect_clause:
		can_interact_element = []
		list_interacting_clause = []

		for element in a_clause:
			for action in list_actions:
				# element = element.strip()
				if (element.strip().endswith("_" + action) or ("_" + action + "_") in element.strip()) and not ("~" in element):
					# print (element + ":\t OK")
					can_interact_element.append(element)

		# print ("can_interact_element: " + str(can_interact_element))

		for interacting_element_i in can_interact_element:
			interacting_clause = "(" + interacting_element_i.strip() + " => ("
			cause_list = []
			for interacting_element_j in a_clause:
				if interacting_element_i != interacting_element_j:
					cause_list.append(interacting_element_j.strip())
					# interacting_clause += "and " + interacting_element_j
			# interacting_clause += " and " + cause + ")"
			cause_list.append(cause.strip())

			list_interacting_clause.append(interacting_clause + " & ".join(cause_list) + "))")
		result.append(list_interacting_clause)

	# print (result)
	result_str = []
	for disjunction_clause in result:
		conjunction_string = " & ".join(disjunction_clause)
		result_str.append(conjunction_string)
		
	# print ([" or ".join(result_str)])
	new_result = [" | ".join(result_str)]
	new_result.append(result)
	
	return new_result
# ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
# PATTERNS: 
# 	From the updated_requirement, check the pattern: if, while, after
def handle_pattern (updated_requirement, ontology):
	print ("\n-- patterns:\n")
	requirement_string = updated_requirement[2]
	cause = ''
	effect = []
	list_effect_parentheses = []

	# ---- ---- ----
	# Get Cause and list of Effect
	# --- patterns If and After
	if "if " in requirement_string or "If " in requirement_string or "after " in requirement_string or "After " in requirement_string:
		# list_clauses = requirement_string.split("if ")
		list_clauses = re.split(r'If\s|if\s|After\s|after\s', requirement_string)
		# print ("list_1: " + list_clauses[1])

		# Get Effect and Cause
		if list_clauses[0] != '':
			cause = list_clauses[1]
			effect = re.split(r'[\s]and|[\s]or', list_clauses[0])
			# effect = list_clauses[0].split("and|or")
		else:
			sub_list_clause = list_clauses[1].split(", ")
			cause = sub_list_clause[0]
			effect = sub_list_clause[1].split("and")

	# --- pattern Before
	if "before " in requirement_string or "Before " in requirement_string:
		list_clauses = re.split(r'Before\s|before\s', requirement_string)

		# Get Before and MAIN
		# A before B 
		if list_clauses[0] != '':
			cause = list_clauses[1]
			effect = re.split(r'[\s]and|[\s]or', list_clauses[0])
		# Before A, B
		else:
			sub_list_clause = list_clauses[1].split(", ")
			cause = sub_list_clause[0]
			effect = sub_list_clause[1].split("and")

	# ---- ---- ----
	# In effect clause, get all elements have "(" and "or" keywords
	# Save them into list_effect_parentheses
	new_effect = []
	if len(effect) > 0:
		# print ("size: " + str(len(effect)) + "\teffect: " + str(effect))

		for element in effect:
			# print ("effect's element: " + str(element))
			if "(" in element and "or" in element:
				list_effect_parentheses.append(element)
			else:
				new_effect.append(element)
	effect = new_effect
	disjunction_of_effect_clause = []
	list_af = []
	for parentheses in list_effect_parentheses:
		content = parentheses[parentheses.index("(")+1:parentheses.index(")")]
		# print ("content: " + content)
		content_element = content.split("or")
		list_af.append(content_element)
	# print ("list_af: " + str(list_af))

	# ---- ---- ----
	# Get all combinations of or_clause
	product_list = itertools.product(*list_af)
	for element in product_list:
		disjunction_of_effect_clause.append(list(element)+effect)

	print ("\t*\tcause: " + cause + "\t\t---\t\tremain effect: " + str(effect))
	print ("\t* list parentheses: " + str(list_effect_parentheses))
	print ("\t* producted list: " + str(disjunction_of_effect_clause))

	# From disjunction of effect clause, cause and ontology, gen final Boolean encoder
	boolean_form_string = get_Boolean_formulas_form(disjunction_of_effect_clause, cause, ontology)[0]
	# print ("\n(" + boolean_form_string + ")")
	return "(" + boolean_form_string + ")"
	# return temp_dict_action
# END ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
# Analyze requirements to get components: quantifiers, elements, condition
print ("-------------------")
def analyze_requirement(req_name, input_requirement, ontology):

	standardized_input = get_standardized_requirement(input_requirement, ontology)
	input_requirement = standardized_input[0]
	list_class_instance = standardized_input[1]
	dict_class_instances = standardized_input[2]
	list_class_instance_string = [element[0] for element in list_class_instance]

	# Actions
	temp_dict_action = get_dictionary_of_actions(input_requirement, ontology)

	# Conditions
	updated_requirement = get_conditions_of_requirement(req_name, standardized_input, temp_dict_action)
	print ("\n-- updated req: " + updated_requirement[2])

	handle_pattern(updated_requirement, ontology)
	print (req_name + " = " + handle_pattern(updated_requirement, ontology))
# END ------------------------------------ ------------------------------------

print ("------------------- sample 2")
ontology = dict()
with open('gen-data/data.json', 'r') as fp:
    ontology = json.load(fp)
print (ontology)
analyze_requirement(req_name, req_content, ontology)
print ("------------------- end sample 2")

print ("------------------- sample 3")
# sample_3 = "Req_02: \"For any MySQL m, there are a VirtualMachine vm, a VirtualMachine vm1 such that m shall undeploy while vm is in Inactive state and m is deployed in vm and vm1 is in Active state.\""
sample_3 = "Req_02: \"For any MySQL m, there are a VirtualMachine vm, a VirtualMachine vm1 such that if m shall undeploy, vm is in Inactive state and m is deployed in vm and vm1 is in Active state and Reg_05.\""

req_name_3 = sample_3[0:sample_3.index(":")]
req_content_3 = re.findall(r'\"(.+)\"',sample_3)[0]
analyze_requirement(req_name_3, req_content_3, ontology)
print ("------------------- end sample 3")

