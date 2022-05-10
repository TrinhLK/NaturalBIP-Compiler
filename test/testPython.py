import re
import json
import itertools
import HandlingData as hd
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

	# replace synchronized with --> <=>
	input_requirement = re.sub(r' synchronize[d|s]*\swith ', " <=> ", input_requirement)

	return input_requirement
# END ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
# PRE-PROCESSING: From input_string, return [standardized input, list_class_instance_string, dict_class_instance]
def get_standardized_requirement (input_requirement, ontology):
	result = []
	print ("\n\n---- original input_req: " + input_requirement)
	# ----- standardize spacing in the text
	input_requirement = standardize_input_requirement(input_requirement)
	print ("\n\n---- new input_req: " + input_requirement)

	# -----  get class-instance information
	# print ("\n-- class-instance:\n")
	criteria_class_instance = r'((any|every| all|a|one|some)\s([^\s]+)\s([^\s]+)(\,[\s]*|\ssuch that[\s]*|\swhere|\,\sin which\,[\s]*|\:[\s]*))'

	list_class_instance = search_from_input(input_requirement, criteria_class_instance)
	# print (list_class_instance)

	list_class_instance_string = [element[0] for element in list_class_instance]
	dict_class_instances = dict()
	for element in list_class_instance:
		try:
			dict_class_instances[element[2]].append(element[3])
		except:
			dict_class_instances[element[2]] = [element[3]]

	# print ("dict_class_instances: " + str(dict_class_instances))
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
			# print (keys)
			# print (ontology[keys])
			for state in ontology[keys]:
				# print (state + "\t\t\t" + search_state)
				# ontology[keys][state]
				if state == search_state:
					result.append(ontology[keys][state])
					# print ("\n--check ontology: " + str(ontology[keys][state]))
	if len(result) > 0:
		return result[0]
	return result
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
		if get_actions == []:
			print ("Error: " + stateName + " doesn't exist")
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
	# print ("\n-- actions:\n")
	criteria_action = r'(([^\s|\(|\,]+[\s]*)(execute[\s]+|executes[\s]+|shall[\s]+)([\~]*[\w]+))[\)|\.|\;|\,]*'
	list_action = search_from_input(input_requirement, criteria_action)
	# print (list_action)
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
	# print (temp_dict_action)

	return temp_dict_action
# END ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
# QUANTIFIERS: Class-Instance
def update_list_class_ins(list_replacement, dict_class_ins):
    for replacement in list_replacement:
        for key, values in dict_class_ins.items():
            if replacement[0] in values:
                dict_class_ins[key].append(replacement[1])
    return dict_class_ins
# END ------------------------------------ ------------------------------------


# ------------------------------------ ------------------------------------
# CONDITION:
def get_conditions_of_requirement (req_name, standardized_input, temp_dict_action):
	# print ("\n-- condition:\n")
	new_sample = standardized_input[0]
	list_class_instance = standardized_input[1]
	list_class_instance_string = [element[0] for element in list_class_instance]
	dict_class_ins = {}
	# print ("\t--list_class_instance: ")
	# print (list_class_instance)
	for element in list_class_instance:
		try:
			dict_class_ins[element[2]].append(element[3])
		except:
			dict_class_ins[element[2]] = [element[3]]

	# print (dict_class_ins)
	for element in list_class_instance_string:
		new_sample = new_sample.replace(element, "")
	for element in temp_dict_action.keys():
		new_sample = new_sample.replace(element, "")
	for element in keywords:
		new_sample = new_sample.replace(element, "")
	for element in patterns:
		new_sample = new_sample.replace(element, "")

	x = re.split(r'[\s]and|[\s]or', new_sample)
	# print ("spliting: " + str(x))
	list_condition = []
	for element in x:
		if element != '':
			list_of_tuples = re.findall(r'\.*\,*\s*(.+)', element)
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
					# print ("temp_cdt: " + str(temp_cdt))
					list_condition.append(temp_cdt)

	# Find variable for skolemization
	list_replacement = []
	for cdt in list_condition:
		if check_dependent_instance(req_name, cdt[1], list_class_instance) != []:
			list_replacement.append(check_dependent_instance(req_name, cdt[1], list_class_instance))
	print ("replacement: " + str(list_replacement))
	dict_class_ins = update_list_class_ins(list_replacement, dict_class_ins)

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


	# convert from {cond text: cond_var} to {cond text: [cond_var, {cond_name: [cond_params]}]
	# ---
	new_dict_conditions = {}
	for text,cond in dict_conditions.items():
		cond_params = []
		cond_name = ""
		words = cond.split("_")
		tmp_words = words
		tmp_dict = {}
		for word in words:
			for ins_name in dict_class_ins.values():
				if word in ins_name:
					cond_params.append(word)
					tmp_words.remove(word)
		tmp_dict["_".join(tmp_words)] = cond_params
		new_dict_conditions[text] = [dict_conditions[text]]
		new_dict_conditions[text].append(tmp_dict)
	# print ("new dict_conditions: " + str(new_dict_conditions))
	dict_conditions = new_dict_conditions
	# ---
	# print ("temp_dict_action: " + str(temp_dict_action))

	
	# Replace variable
	new_content = standardized_input[0]
	# remove actions
	# for act_i in temp_dict_action:
	for key, value in temp_dict_action.items():
		new_content = new_content.replace(key, value)

	# remove conditions
	for key, value in dict_conditions.items():
		new_content = new_content.replace(key, value[0])

	# remove quantifiers
	for element in list_class_instance_string:
		new_content = new_content.replace(element, " ")
	# remove keywords
	for element in keywords:
		new_content = new_content.replace(element, " ")
	new_content = re.sub(r'while\s|While\s', "if ", new_content)
	new_content = re.sub(r'\s+', " ", new_content.strip())
	# new_content.replace("while ", "if ")
	# print ("\n-- Function get new req: " + new_content)

	# convert from {action text: action_var} to {cond text: [cond_var, {cond_name: [cond_params]}]
	# ---
	new_dict_actions = {}
	for text,act in temp_dict_action.items():
		act_params = []
		act_name = ""
		act=act.replace("~", "")
		words = act.split("_")
		tmp_words = words
		tmp_dict = {}
		for word in words:
			for ins_name in dict_class_ins.values():
				if word in ins_name:
					act_params.append(word)
					tmp_words.remove(word)
		tmp_dict["_".join(tmp_words)] = act_params
		new_dict_actions[text] = [temp_dict_action[text]]
		new_dict_actions[text].append(tmp_dict)
	# print ("new dict_actions: " + str(new_dict_actions))
	temp_dict_action = new_dict_actions
	# ---

	output = []
	output.append(temp_dict_action)
	output.append(dict_conditions)
	output.append(new_content)
	output.append(dict_class_ins)

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
# ------------------------------------
def get_effect_list (test_str):
	effects = []
	list_either_or = re.findall(r'\(.*or.*\)', test_str)
	dict_either_or = {}
	# print(list_either_or)
	for i in range(len(list_either_or)):
		dict_either_or['either_or_' + str(i)] = list_either_or[i]
	for key, value in dict_either_or.items():
		test_str = test_str.replace(value, key)

	or_clause = test_str.split(" or ")
	for clause in or_clause:
		for key, value in dict_either_or.items():
			clause = clause.replace(key, value)
		tmp = clause.split(" and ")
		effects.append(tmp)
	return effects
# END ------------------------------------

# ------------------------------------
# PATTERNS: 
# 	Check complex patterns: if, while, after
def handle_complex_patterns (updated_requirement, ontology):
	# print ("\n-- patterns:\n")
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

	# print ("\t*\tcause: " + cause + "\t\t---\t\tremain effect: " + str(effect))
	# print ("\t* list parentheses: " + str(list_effect_parentheses))
	# print ("\t* producted list: " + str(disjunction_of_effect_clause))

	# From disjunction of effect clause, cause and ontology, gen final Boolean encoder
	boolean_form_string = get_Boolean_formulas_form(disjunction_of_effect_clause, cause, ontology)[0]
	# print ("\n(" + boolean_form_string + ")")
	return "(" + boolean_form_string + ")"
	# return temp_dict_action
# END ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
# PATTERNS: 
# 	Check complex patterns: if, while, after
# def handle_compound_patterns (updated_requirement, ontology):
# 	# print ("\n-- patterns:\n")
# 	requirement_string = updated_requirement[2]
# 	cause = ''
# 	effect = []
# 	list_effect_parentheses = []

# 	if any(keyword_pattern in updated_requirement for keyword_pattern in patterns):
# 		print ("yesssss")
# END ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
# PATTERNS: 
# 	From the updated_requirement, check the pattern: if, while, after
def handle_pattern (updated_requirement, ontology):
	# print ("\n-- patterns:\n")
	if not any(keyword_pattern in updated_requirement[2] for keyword_pattern in patterns):
		boolean_form_string = updated_requirement[2]
		boolean_form_string = boolean_form_string.replace(" or ", " | ")
		boolean_form_string = boolean_form_string.replace(" and ", " & ")
	else:
		boolean_form_string = handle_complex_patterns(updated_requirement, ontology)
	# print ("\n(" + boolean_form_string + ")")
	return boolean_form_string
	# return temp_dict_action
# END ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
# ERROR HANDLING:
def error_handling(data, updated_requirement):
	detailed_info = data['Detail']
	requirement_actions = updated_requirement[0]
	requirement_class_ins = updated_requirement[3]
	no_error = True
	print ("detailed_info: " + str(detailed_info))
	for req_act_text, req_act_value in requirement_actions.items():
		text = re.findall(r'\~*(\w+)\_(\w+)', req_act_value[0])[0]
		req_ins = text[0]
		req_action = text[1]
		# print (f"req_ins: {req_ins}\t\treq_act: {req_action}")
		req_class = ""
		for key, val in requirement_class_ins.items():
			if req_ins in val:
				req_class = key

		if not (req_action in detailed_info[req_class][1]):
			print ("ERROR: " + req_class + " doesn't have action: " + req_action)
			no_error = False
		# else:
		# 	print ("ok day")
	if no_error: print ("OK - No error.\n")
# END ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
# ERROR HANDLING:
def generate_booleanFunctions_and_dataTransfer(data, updated_requirement):
	detailed_info = data['Detail']
	requirement_conditions = updated_requirement[1]
	# print (requirement_conditions)
	requirement_class_ins = updated_requirement[3]
	list_dataTransfer = []
	list_booleanFunctions = []

	# get each condition with <name> and <list_params>
	for condition_info in requirement_conditions.values():
		dict_conditions_infor = condition_info[1]
		# print ("condition: " + str(dict_conditions_infor))

		for name, params in dict_conditions_infor.items():
			# Get class_name from instance_name
			class_params = []
			for param in params:
				for key, val in requirement_class_ins.items():
					if param in val:
						class_params.append(key)
			flag_has_bool_func = False
			function_string = "In " + class_params[0] + ".java:\n\t@Guard(name=\"" + name + "\")\n\tpublic boolean " + name + "("

			# Data transfer: if more than one param and they are in different class ==> data transfer
			# Boolean functions/Guards: if more than one param and they are in different class ==> parameters
			if len(class_params) > 1:
				list_boolfuncs_params = []
				for class_param_i in class_params[1:]:
					if class_param_i != class_params[0]:
						# Data transfer
						list_dataTransfer.append("data(" + class_param_i + ".class,\"" + class_param_i + "2" + class_params[0] + "_data\").to(" + class_params[0] + ".class,\"" + class_param_i + "2" + class_params[0] + "_data\");")

						# Boolean functions/Guards
						flag_has_bool_func = True
						list_boolfuncs_params.append("@Data(name=\"" + class_param_i + "2" + class_params[0] + "_data\") " + class_param_i + " " + class_param_i + "_ins")
				function_string += ", ".join(list_boolfuncs_params)

			function_string +=  ") {}"
			if flag_has_bool_func == False: function_string = ""
			if function_string != "" : list_booleanFunctions.append(function_string)

		list_dataTransfer = list(set(list_dataTransfer))
		list_booleanFunctions = list(set(list_booleanFunctions))

	dict_result = {}
	dict_result["conditions"] = list_booleanFunctions
	dict_result["data_transfer"] = list_dataTransfer
	# print (dict_result)
	return dict_result
	
# END ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
# Analyze requirements to get components: quantifiers, elements, condition
print ("-------------------")

def analyze_requirement(req_name, input_requirement, data):

	result = []
	ontology = data['Class']
	standardized_input = get_standardized_requirement(input_requirement, ontology)
	input_requirement = standardized_input[0]
	list_class_instance = standardized_input[1]
	dict_class_instances = standardized_input[2]
	list_class_instance_string = [element[0] for element in list_class_instance]

	# Actions
	temp_dict_action = get_dictionary_of_actions(input_requirement, ontology)
	print ("temp_dict_action: " + str(temp_dict_action))
	# Conditions
	updated_requirement = get_conditions_of_requirement(req_name, standardized_input, temp_dict_action)
	print ("\n-- updated req: " + updated_requirement[2])
	# print (updated_requirement)
	print ("dict_action: " + str(updated_requirement[0]))

	print ("\n-- error checking: ")
	error_handling(data, updated_requirement)

	# print ("\n-- data transfer and boolean functions: ")
	artifacts = generate_booleanFunctions_and_dataTransfer(data, updated_requirement)

	handle_pattern(updated_requirement, ontology)
	# print (req_name + " = " + handle_pattern(updated_requirement, ontology))
	result = [req_name + " = " + handle_pattern(updated_requirement, ontology)]
	result.append(artifacts) #PBL inputs, boolean functions, and data transfer
	result.append(updated_requirement[3])	#Class_Instances
	result.append(list(updated_requirement[1].values())) #Conditions/Predicates
	result.append(list(updated_requirement[0].values())) #Actions

	print (result)
	return result
# END ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
def get_data_from_file(xmlFile):
	fileName = xmlFile[xmlFile.rindex('/')+1:xmlFile.rindex('.')]
	data = hd.readXML(xmlFile)
	# print (fileName)
	# try:
	# 	with open('gen-data/data_'+fileName+'.json', 'r') as fp:
	# 		data = json.load(fp)
	# except:
	# 	data = hd.readXML(xmlFile)
	# 	with open('gen-data/data_'+fileName+'.json', 'w') as fp:
	# 		json.dump(data, fp)
	return data
# END ------------------------------------ ------------------------------------

# ------------------------------------ ------------------------------------
# Generate Boolean Formulas file
def gen_Boolean_encoding(xmlFile):
	fileName = xmlFile[xmlFile.rindex('/')+1:xmlFile.rindex('.')]
	data = get_data_from_file(xmlFile)
	ontology = data['Class']
	requirements = data['Specification']

	exported_data = {}
	dict_artifacts = {}
	dict_class_ins = {}
	list_conditions = []
	list_actions = []

	result = ""
	# print (requirements)
	list_requirements = list(requirements.keys())
	list_requirements.remove("MAIN")
	# print (list_requirements)
	
	for key, value in requirements.items():
		if not "MAIN" in key:
			print ("\n\nBEGIN ---- ---- ----")
			analyzed_req = analyze_requirement(key, value, data)
			result += analyzed_req[0] + "\n"
			artifacts = analyzed_req[1]
			tmp_dict_class_ins = analyzed_req[2]
			tmp_list_conditions = analyzed_req[3]
			tmp_list_actions = analyzed_req[4]
			# print ("\n--tmp_list_actions: " + str(tmp_list_actions))
			# print (artifacts)

			for key_art in artifacts.keys():
				# if artifacts[key_art] != []:
				try:
					dict_artifacts[key_art].extend(artifacts[key_art])
				except:
					dict_artifacts[key_art] = artifacts[key_art]

			for key_class_ins in tmp_dict_class_ins.keys():
				try:
					dict_class_ins[key_class_ins].extend(tmp_dict_class_ins[key_class_ins])
					dict_class_ins[key_class_ins] = list(set(dict_class_ins[key_class_ins]))
				except:
					dict_class_ins[key_class_ins] = tmp_dict_class_ins[key_class_ins]

			try:
				list_conditions.extend(tmp_list_conditions)
			except:
				list_conditions = tmp_list_conditions

			try:
				list_actions.extend(tmp_list_actions)
			except:
				list_actions = tmp_list_actions

			print ("END ---- ---- ----\n\n")
		else:
			# new_main_content = value
			main_list = []
			new_main_content = re.sub(r'[\s]*\,[\s]*', " & ", value)
			# print ("Main_Exp: " + new_main_content)
			if ("except " or "Except ") in new_main_content:
				except_list = new_main_content[new_main_content.index("except ")+7:].split(" & ")
				main_list = list(set(list_requirements) - set(except_list))
			elif new_main_content == 'all' or new_main_content == 'All':
				main_list = list_requirements
			else:
				main_list = new_main_content.split(" & ")

			result += "Main_Exp: " + " & ".join(main_list)

	# print (dict_class_ins)
	# print (list_conditions)
	exported_data['configuration'] = dict_class_ins
	exported_data['constraints'] = list_conditions
	exported_data['actions'] = list_actions
	exported_data['boolean_functions'] = dict_artifacts['conditions']
	exported_data['data_transfer'] = dict_artifacts['data_transfer']
	exported_data['pbl_formulas'] = result
	# print (exported_data)
	# print (result)
	with open('gen-data/PBL_'+fileName+'.txt', 'w') as f:
		f.write(result)
	with open('gen-data/system_info_'+fileName+'.json', 'w') as f:
		json.dump(exported_data, f)
	# # print (fileName)
	# try:
	# 	with open('gen-data/data_'+fileName+'.json', 'r') as fp:
	# 		data = json.load(fp)
	# except:
	# 	data = hd.readXML(xmlFile)
	# 	with open('gen-data/data_'+fileName+'.json', 'w') as fp:
	# 		json.dump(data, fp)
	# return data
# END ------------------------------------ ------------------------------------
# data = hd.readXML('input/tracker_peer.xml')
# with open('gen-data/data_'+'tracker_peer'+'.json', 'w') as fp:
# 	json.dump(data, fp)
# data = get_data_from_file('input/tracker_peer.xml')
gen_Boolean_encoding('input/tracker_peer.xml')
# print (data)
# test_str = "except Req_01, Req_04"
# new_main_content = re.sub(r'[\s]*\,[\s]*', " & ", test_str)
# except_list = new_main_content[new_main_content.index("except ")+7:].split(" & ")
# # print (except_list)
# list_requirements = ['Req_01', 'Req_02', 'Req_03', 'Req_04']
# print (list(set(list_requirements) - set(except_list)))
# data = dict()
# with open('gen-data/data.json', 'r') as fp:
#     data = json.load(fp)
# ontology = data['Class']
# print ("\n--- ontology ---")
# print (ontology)
# requirements = data['Specification']
# print ("\n--- requirements ---")
# print (requirements)

# for key, value in requirements.items():
# 	print ("\n\nBEGIN ---- ---- ----")
# 	analyze_requirement(key, value, ontology)
# 	print ("END ---- ---- ----\n\n")
# print ("------------------- sample 2")
# analyze_requirement(req_name, req_content, ontology)
# print ("------------------- end sample 2")
# if not any(keyword_pattern in "I hate it " for keyword_pattern in patterns):
# 		print ("yesssss")

# print ("------------------- sample 3")
# # sample_3 = "Req_02: \"For any MySQL m, there are a VirtualMachine vm, a VirtualMachine vm1 such that m shall undeploy while vm is in Inactive state and m is deployed in vm and vm1 is in Active state.\""
# sample_3 = "Req_02: \"For any MySQL m, there are a VirtualMachine vm, a VirtualMachine vm1 such that if m shall undeploy, vm is in Inactive state and m is deployed in vm and vm1 is in Active state and Reg_05.\""

# req_name_3 = sample_3[0:sample_3.index(":")]
# req_content_3 = re.findall(r'\"(.+)\"',sample_3)[0]
# analyze_requirement(req_name_3, req_content_3, ontology)
# print ("------------------- end sample 3")
print ("------------------- test 2")
test_str = "Req04tp_is_registered_to_t and Req04tp_speak and p1_is_registered_to_t and (x_test or y_test) and p1_is_different_with_Req04tp and ~p1_speak or Req04tp_listen"
# effects = []
# list_either_or = re.findall(r'\(.*or.*\)', test_str)
# dict_either_or = {}
# print (list_either_or)
# for i in range(len(list_either_or)):
# 	dict_either_or['either_or_'+str(i)] = list_either_or[i]
# for key, value in dict_either_or.items():
# 	test_str = test_str.replace(value, key)
# print ("dict: " + str(dict_either_or))
# print ("new_test_str: " + str(test_str))
#
# or_clause = test_str.split(" or ")
# print ("or_clause: " + str(or_clause))
# for clause in or_clause:
# 	for key, value in dict_either_or.items():
# 		clause = clause.replace(key, value)
# 	tmp = clause.split(" and ")
# 	effects.append(tmp)
#
# print (effects)
def get_effect_list (test_str):
	effects = []
	list_either_or = re.findall(r'\(.*or.*\)', test_str)
	dict_either_or = {}
	# print(list_either_or)
	for i in range(len(list_either_or)):
		dict_either_or['either_or_' + str(i)] = list_either_or[i]
	for key, value in dict_either_or.items():
		test_str = test_str.replace(value, key)

	or_clause = test_str.split(" or ")
	for clause in or_clause:
		for key, value in dict_either_or.items():
			clause = clause.replace(key, value)
		tmp = clause.split(" and ")
		effects.append(tmp)
	return effects

print (get_effect_list(test_str))
print ("------------------- end test 2")

