#!/usr/bin/env python
import sys
import os.path
import json
mango_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))+ '/include/')
sys.path.append(mango_dir)
import PyBool_public_interface as Bool

# -------------------------------------
# Load data
with open('gen-data/system_info_tracker_peer.json', 'r') as fp:
	system_info = json.load(fp)

print ("\nsystem_info: " + str(system_info))
print ("\nconfigurations: " + str(system_info['configuration']))
print ("\npredicates: " + str(system_info['constraints']))
print ("\nactions: " + str(system_info['actions']))
list_actions = [elm[0] for elm in system_info['actions']]
list_constraints = [elm[0] for elm in system_info['constraints']]

print ("\nlist_actions: " + str(list_actions))
print ("\nlist_actions: " + str(list_constraints))

# -------------------------------------

def is_predicate(elem, list_preds):
	for i in list_preds:
		if i == elem:
			return True
	return False

def list_cnf_clauses_raw(L):
	my_dict = dict(L["map"])
	# reverse clause to move all neg in front
	list_key_rev = []
	for i in L["Clauses"]:
		list_key_rev.append(i[::-1])

	# replace int by string
	list_cnf_clauses = []
	for i in list_key_rev:
		temp_list = []
		for j in i:
			
			if j < 0:
				j1 = abs(j)
				temp_val = "~" + list(my_dict.keys())[list(my_dict.values()).index(j1)]
				temp_list.append(temp_val)
			else:
				# print(list(my_dict.keys())[list(my_dict.values()).index(j)])
				temp_val = list(my_dict.keys())[list(my_dict.values()).index(j)]
				temp_list.append(temp_val)
		list_cnf_clauses.append(temp_list)
	print ("\n--- 1. Convert dictionary to list of strings")
	print (str(list_cnf_clauses))
	return list_cnf_clauses

###
# -----------------------------------------------------------------------
# Class for a clause, which includes:
#	- a list of neg
#	- a list of pos
#	- bool to check that used or not
# -----------------------------------------------------------------------
###
class Atomic_Element:
	text = ""
	name = ""
	params = []
	isNeg = False
	isPred = False

	def __init__(self, text):
		
		if "~" in text:
			self.isNeg = True
			text = text[text.find("~")+1:]
		self.params = [text[0:text.find("_")]]
		self.name = []

		self.text = text
		self.name = text[0:text.find("_")]
		params_text = text[text.find("_")+1:]
		self.params = params_text.split("_")
		self.isPred = False

	def showInfor(self):
		return self.text + ""

###
# -----------------------------------------------------------------------
# Class for a clause, which includes:
#	- a list of neg
#	- a list of pos
#	- bool to check that used or not
# -----------------------------------------------------------------------
###
class CNF_Clauses:
	neg = []	#elements can be an atom or a list of atoms
	pos = []	#elements can be an atom or a list of atoms
	rm = False

	def __init__(self):
		self.neg = []
		self.pos = []
		rm = False

	def add_neg(self, negEl):
		self.neg.append(negEl)

	def add_pos(self, posEl):
		self.pos.append(posEl)

	def print_macro(self):
		res = ""
		if isinstance(self.neg, list):
			neg_i_str = [(element.text) for element in self.neg]
			tmp_neg = " & ".join(neg_i_str)
		else:
			tmp_neg = self.neg.text
		tmp_pos = []
		for i in self.pos:
			if isinstance(i, list):
				pos_i_str = [(element.text) for element in i]
				tmp_pos_i = " & ".join(pos_i_str)
				tmp_pos.append(tmp_pos_i)
			else:
				tmp_pos.append(i.text)
		pos_str = " | ".join(tmp_pos)
		if pos_str != "":
			res = "~(" + tmp_neg + ") | " + pos_str
		else:
			res = "~(" + tmp_neg + ")"
		print (res)

	def printer(self):
		# print ("\n---printing clause---")
		res = ""

		list_txt_neg = []
		for neg_i in self.neg:
			# print (type(i))
			if isinstance(neg_i, list):
				# print ("check type: " + str(type(neg_i)))
				i_elm_str = []
				for element in neg_i:
					if isinstance(element, list) == False:
						i_elm_str.append(element.text)
				# i_elm_str = [element.text for element in neg_i]
				tmp = " & ".join(i_elm_str)
				list_txt_neg.append("~(" + tmp + ")")
			else:
				list_txt_neg.append("~" + neg_i.text)

		list_txt_pos = []
		for i in self.pos:
			if isinstance(i, list):
				i_elm_str = [element.text for element in i]
				tmp = " & ".join(i_elm_str)
				list_txt_pos.append(tmp)
			else:
			# print (str(type(i)) + " " + str(i.text))
				list_txt_pos.append(i.text)
		res += " | ".join(list_txt_neg) + " | " + " | ".join(list_txt_pos)
		# res += ", " + str(self.rm)
		print ("(" + res + ")")

	def get_neg_list_str(self):
		res = []
		for i in self.neg:
			if isinstance(i, list):
				temp_res = []
				for i_el in i:
					if isinstance(i_el, list) == False:
						temp_res.append(i_el.text)
				res.append(temp_res)
			else:
				res.append(i.text)
		return res

	def get_pos_list_str(self):
		res = []
		for i in self.pos:
			if isinstance(i, list):
				temp_res = []
				for i_el in i:
					temp_res.append(i_el.text)
				res.append(temp_res)
			else:
				res.append(i.text)
		return res
# check if two lists are equal
def compareList(l1,l2):
   l1.sort()
   l2.sort()
   return (l1 == l2)

# make a conjunction between elements of two lists
def merge_two_pos_list(l_atom_1, l_atom_2):
	result = []
	if l_atom_1 == []:
		return l_atom_2
	else:
		if l_atom_2 == []:
			return l_atom_1
		for i in l_atom_1:
			temp_list = []
			if isinstance(i, list):
				for i_el in i:
					temp_list.append(i_el)
			else:
				temp_list.append(i)


			for j in l_atom_2:
				temp_list_j = []
				if isinstance(j, list):
					for j_el in j:
						temp_list_j.append(j_el)
				else:
					temp_list_j.append(j)
					
				result.append(temp_list + temp_list_j)
		
	return result

###
# -----------------------------------------------------------------------
### get list of positive ports
# -----------------------------
# add data to list of instances of CNF_Clauses Class
def convert_list_elem_to_dict(elem_list):
	result = {}
	for elem_i in elem_list:
		# print (type(elem_i[0]))
		dicts_key = elem_i[0].params[0]
		
		if dicts_key in result.keys():
			continue

		dicts_value = []
		dicts_value.append(elem_i[0].name)
		for elem_j in elem_list:
			if elem_j[0] != elem_i[0]:
				j_keys = elem_j[0].params[0]
				if j_keys == dicts_key:
					dicts_value.append(elem_j[0].name)
		result[dicts_key] = dicts_value
	return result

def create_dict_of_instances_actions(elem_dict, config):
	new_elem_dict = {}
	for elem_k, elem_v in elem_dict.items():
		for config_k, config_v in config.items():
			if elem_k in config_v:
				print (config_k)
				if config_k in new_elem_dict.keys():
					new_elem_dict[config_k] = list(set(elem_v) | set(new_elem_dict[config_k]))
				else:
					new_elem_dict[config_k] = elem_v
	result = {}
	for elem_k, elem_v in new_elem_dict.items():
		for config_k, config_v in config.items():
			if config_k == elem_k:
				for value_i in config_v:
					result[value_i] = elem_v
	return result

def convert_dict_to_list_pos(my_dict):
	result = []
	for k_i, v_i in my_dict.items():
		for elem_v_i in v_i:
			tmp = Atomic_Element(elem_v_i + "_" + k_i)
			result.append([tmp])
	return result

def create_addtional_positive_clause(elem_list, config):
	my_dict = convert_list_elem_to_dict(elem_list)
	my_dict = create_dict_of_instances_actions(my_dict,config)
	result = convert_dict_to_list_pos(my_dict)
	return result

def get_list_cnf_clauses (list_cnf_clauses):

	list_MyClause = []
	# print (len(list_cnf_clauses))

	for clauses in list_cnf_clauses:
		# print ("clauses: " + str(clauses))
		clause = CNF_Clauses()
		for elem in clauses:
			if "~" in elem:
				atom_neg = Atomic_Element(elem)
				clause.add_neg([atom_neg])
			else:
				atom_pos = Atomic_Element(elem)
				clause.add_pos([atom_pos])
		list_MyClause.append(clause)
	return list_MyClause

def get_all_port_elements(list_cnf_clauses, list_preds, config):
	result = []
	temp = []
	for clause_i in list_cnf_clauses:
		for neg_elem in clause_i.neg:
			if is_predicate(neg_elem[0].text, list_preds) == False:
				temp.append(neg_elem[0].text)
		for pos_elem in clause_i.pos:
			if is_predicate(pos_elem[0].text, list_preds) == False:
				temp.append(pos_elem[0].text)

	print ("test list ports:\nbefore")
	for elem_i in temp:
		print (elem_i)
	temp = list(dict.fromkeys(temp))
	print ("test list ports:\nafter")
	# test_rs = []
	for elem_i in temp:
		atom_elem = Atomic_Element(elem_i)
		print (elem_i)
		result.append([atom_elem])
		# test_rs.append([elem_i])
	print (result)

	result_1 = create_addtional_positive_clause(result, config)
	# my_dict = convert_list_elem_to_dict(result)
	# print (my_dict)
	# print ("-----")
	# my_dict = add_ports_to_all_instances(my_dict)
	# print (my_dict)
	# print ("-----")
	# result = convert_dict_to_list_pos(my_dict)
	return result_1
	# print (test_rs)
# ----------------------------- TEST

def get_list_str(neg_OR_pos_list):
	res = []
	for i in neg_OR_pos_list:
		if isinstance(i, list):
			temp_res = []
			for i_el in i:
				if isinstance(i_el, list) == False:
					temp_res.append(i_el.text)
			res.append(temp_res)
		else:
			res.append(i.text)
	return res


# -----------------------------
# If the some clauses have the same negative list, make a conjunction of their positive list
# synthesis all clauses have the same negative list
def synthesis_cnf_clauses(list_MyClause):
	combine_same_neg = []

	for i in range(len(list_MyClause)):
		
		if list_MyClause[i].rm == True:
			continue
		temp = CNF_Clauses()
		for j in range(i+1,len(list_MyClause)):

			if (compareList(list_MyClause[i].get_neg_list_str(), list_MyClause[j].get_neg_list_str())):
				temp.neg = list_MyClause[i].neg
				list_MyClause[i].pos = merge_two_pos_list(list_MyClause[i].pos, list_MyClause[j].pos)
				list_MyClause[j].rm = True
				temp.pos = list_MyClause[i].pos
				combine_same_neg.append(temp)
				list_MyClause[i].rm = True

	for i in range(len(list_MyClause)):
		if list_MyClause[i].rm == False:
			combine_same_neg.append(list_MyClause[i])

	combine_same_neg = list(dict.fromkeys(combine_same_neg))
	print ("\n--- 2. Conjunct positive parts of clauses have the same negative part")
	for clause_i in combine_same_neg:
		clause_i.printer()
	return combine_same_neg

# -----------------------------
# collect ports with corresponding predicates
# If the negative list has more than one elements, check their type:
# 	- If it's a predicate, collect it with relevant ports
# 	- If there is no relevant port, consider again the skolemized formulae
def collect_neg_with_conditions(synthesis_cnf, given_list_preds):

	for clause_i in synthesis_cnf:
		list_neg = clause_i.neg
		for neg_elem in list_neg:
			neg_elem[0].isPred = is_predicate(neg_elem[0].text, given_list_preds)

		if len(list_neg) > 1:
			list_of_neg = []
			for i in range(len(list_neg)):
				if isinstance(list_neg[i][0], list):
					continue
				if list_neg[i][0].isPred:
					continue
				new_neg_i = []
				#new_neg_i.append(list_neg[i].text)
				new_neg_i.append(list_neg[i][0])

				for j in range(i+1, len(list_neg)):
					if list_neg[j][0].isPred == False:
						continue
					else: # i is not pred, j is pred
						# some params of i appear in j
						# if len(set(list_neg[i][0].params) & set(list_neg[j][0].params)):
						# 	# new_neg_i.append(list_neg[j].text)
						# 	new_neg_i.append(list_neg[j][0])
						# if the first param of i == the first param of j
						if list_neg[i][0].params[0] == list_neg[j][0].params[0]:
							new_neg_i.append(list_neg[j][0])
				list_of_neg.append(new_neg_i)

			clause_i.neg = list_of_neg

	print ("\n--- 3. collect ports in the negative list with predicates (if exists)")
	for clause_i in synthesis_cnf:
		clause_i.printer()
	return synthesis_cnf

# -----------------------------
#Input: 2 clauses
#Output: all combination from neg_lists <-> list of list of clauses
def combination_of_2_clauses(cl1, cl2):
	rs = []
	for cl2_neg_i in cl2.neg:
		if hasattr(cl1, "neg"):
			for cl1_neg_j in cl1.neg:
				list_tmp = []
				tmp_clause = CNF_Clauses()
				tmp_clause.neg = cl2_neg_i
				tmp_clause.pos = cl2.pos

				# for sub_elm in cl1_neg_j:
				subtmp_clause = CNF_Clauses()
				subtmp_clause.neg = cl1_neg_j
				subtmp_clause.pos = cl1.pos

				list_tmp.append(subtmp_clause)

				list_tmp.append(tmp_clause)
				rs.append(list_tmp)
		else: #cl1 is a previous combination
			for combined_cl1_i in cl1:
				list_tmp = []
				for combined_cl1_i_j in combined_cl1_i:
					list_tmp.append(combined_cl1_i_j)
				tmp_clause = CNF_Clauses()
				tmp_clause.neg = cl2_neg_i
				tmp_clause.pos = cl2.pos
				list_tmp.append(tmp_clause)

				rs.append(list_tmp)
	return rs

def mk_dualHorn(list_cls):
	res_cls = []
	if len(list_cls) > 1:

		res_cls = list_cls[0]
		for i in range(1, len(list_cls)):
			res_cls = combination_of_2_clauses(res_cls, list_cls[i])
	else:
		cls_0 = list_cls[0]
		for neg_i in cls_0.neg:
			tmp_cls = CNF_Clauses()
			tmp_cls.neg = neg_i
			tmp_cls.pos = cls_0.pos
			res_cls.append(tmp_cls)
	print ("\n--- 4. Generate list of dual-Horn clause")
	return res_cls

def saturate_dual_horn(dual_horn, list_ports):
	res = []
	additional_clause = CNF_Clauses()
	additional_clause.neg = []
	additional_clause.pos = list_ports
	print ("get list port: ")
	for port in list_ports:
		print (port[0].showInfor())
	for elem in dual_horn:
		elem.append(additional_clause)
		# print ("check addional_clause: " + str(len(additional_clause.pos)))
	return dual_horn

# -----------------------------
# absorb the dual-horn clause
# Convert all atom in neg to list atom (list of 1 element)
# absorb
def absorb_dual_Horn(dual_horn_clause_list):
	# Convert negative list from a list of Atom to list of list Atom
	result = []
	for a_clause in dual_horn_clause_list:
		for sub_clause in a_clause:
			if isinstance(sub_clause.neg, list) == False:
				sub_clause.neg = [sub_clause.neg]
		a_clause = absorb_remove_imply_false(a_clause)
		a_clause = remove_elements_in_pos_clause(a_clause)
		result.append(a_clause)
	print ("absorb the dual horn")
	return result

# remove clauses have negtive part is in neg => false
def absorb_remove_imply_false(dual_horn_clause):
	result = []
	for i in range(len(dual_horn_clause)):
		can_be_kept = True
    	
		if dual_horn_clause[i].pos == []:
			result.append(dual_horn_clause[i])
			continue

		tmp_neg_str = [elem.text for elem in dual_horn_clause[i].neg if elem.isPred == False]

		for j in range(len(dual_horn_clause)):
			if dual_horn_clause[j].pos == [] and i != j:
				tmp_neg_str_j = [elem.text for elem in dual_horn_clause[j].neg if elem.isPred == False]
				# print (str(j) + ": " + str(tmp_neg_str_j))
				if (len(set(tmp_neg_str) & set(tmp_neg_str_j)) > 0):
					can_be_kept = False
					break
		
		if can_be_kept:
			result.append(dual_horn_clause[i])

	return result

def remove_elements_in_pos_clause(a_dual_horn_clause):
	result = []
	for i in range(len(a_dual_horn_clause)-1):
		result.append(a_dual_horn_clause[i])

	last_clause = a_dual_horn_clause[-1]
	new_last_clause = CNF_Clauses()

	if last_clause.neg == []:
		
		list_pos = [elem[0] for elem in last_clause.pos]

		# ---------------------------
		# remove elements if ~elements | false
		# print ("\ni clauses before: " + str(accepts_string))
		new_list_pos = []
		for pos_i in list_pos:
			keep = True
			for j in range(len(a_dual_horn_clause) - 1):
				if a_dual_horn_clause[j].pos == []:
					tmp_neg_str_j = [elem.text for elem in a_dual_horn_clause[j].neg if elem.isPred == False]
					if tmp_neg_str_j[0] == pos_i.text:
						keep = False
						break
			if keep == True:
				new_list_pos.append(pos_i)
		
		new_last_clause.pos = new_list_pos
		result.append(new_last_clause)

	return result

def absorb_a_dual_Horn_clause_1(dual_horn_clause):
	pos_clause = dual_horn_clause[-1]
	# make sure this is the pos clause
	if pos_clause.neg == []:
		print ("gg")

def absorb_a_dual_Horn(dual_horn_clause):
	# Absorb 
	result = absorb_remove_imply_false(dual_horn_clause)
	result = remove_elements_in_pos_clause(result)

	# # remove clauses have negtive part is in neg => false
	# for i in range(len(dual_horn_clause)):
	# 	can_be_kept = True
    	
	# 	if dual_horn_clause[i].pos == []:
	# 		result.append(dual_horn_clause[i])
	# 		continue

	# 	tmp_neg_str = [elem.text for elem in dual_horn_clause[i].neg if elem.isPred == False]

	# 	for j in range(len(dual_horn_clause)):
	# 		if dual_horn_clause[j].pos == [] and i != j:
	# 			tmp_neg_str_j = [elem.text for elem in dual_horn_clause[j].neg if elem.isPred == False]
	# 			# print (str(j) + ": " + str(tmp_neg_str_j))
	# 			if (len(set(tmp_neg_str) & set(tmp_neg_str_j)) > 0):
	# 				can_be_kept = False
	# 				break
		
	# 	if can_be_kept:
	# 		result.append(dual_horn_clause[i])

	# ---------------------------------------------------------------------
	# adjust elements in the added positive clause
	accepts_clause = result[-1]
	new_list_pos = []
	if accepts_clause.neg == []:
		
		list_pos = [elem[0] for elem in accepts_clause.pos]
		accepts_string = [elem.text for elem in list_pos]

		# ---------------------------
		# remove elements if ~elements | false
		# print ("\ni clauses before: " + str(accepts_string))
		for j in range(len(result) - 1):
			if result[j].pos == []:
				tmp_neg_str_j = [elem.text for elem in result[j].neg if elem.isPred == False]
				for pos_i in list_pos:
					if tmp_neg_str_j[0] == pos_i.text:
						list_pos.remove(pos_i)
	
		accepts_string = [pos_i.text for pos_i in list_pos]
		# print ("i clauses after remove: " + str(accepts_string))
		
		# ---------------------------
		# add A, B if ~elements | A & B 
		for pos_i in list_pos:
			should_add = True
			tmp_list = []
			for j in range(len(result) - 1):
				j_neg_str = [elem.text for elem in result[j].neg if elem.isPred == False]
				j_pos_str = [elem[0].text for elem in result[j].pos]

				if pos_i.text == j_neg_str[0]:
					# print ("bip")
					# tmp_list = []
					tmp_list.append(pos_i)
					tmp_list.extend(result[j].pos[0])
					should_add = False
			if tmp_list != []:
				# print ("check size before: " + str(len(tmp_list)))
				remove_id = []
				
				for i in range(len(tmp_list)):
					for j in range(i+1, len(tmp_list)):
						# print (str(i) + ", " + str(j) + " - " + tmp_list[j].text)
						if tmp_list[i].text == tmp_list[j].text:
							remove_id.append(j)
							break
					
				for i in range(len(remove_id)-1,-1,-1):
					tmp_list.pop(remove_id[i])

				new_list_pos.append(tmp_list)

			if should_add == True:
				new_list_pos.append(pos_i)

		# new_list_pos = list(dict.fromkeys(new_list_pos))
		# print (get_list_str(new_list_pos))

	result.pop(-1)
	new_Clause = CNF_Clauses()
	new_Clause.pos = new_list_pos
	result.append(new_Clause)
	# ---------------------------------------------------------------------
	return result

# -----------------------------
def print_dual_Horn(list_dual_horn):

	for i in range(len(list_dual_horn)):
		# print ("i: ")
		print ("\n------ " + str(i))
		if isinstance(list_dual_horn[i], list):
			for j in range(len(list_dual_horn[i])):
				# print ("----- test Rs[" + str(i) + "][" + str(j) + "]=")
				# print ("---" + str(type(list_dual_horn[i][j])))
				list_dual_horn[i][j].print_macro()
				# print ("---")
			print ("------\n")
		else:
			list_dual_horn[i].print_macro()


# -----------------------------
def get_cnf_list(file_name):

	expr = Bool.parse_std(file_name)
	expr = expr["main_expr"]
	expr = Bool.simplify(expr)
	expr = Bool.exp_cnf(expr)

	L = Bool.cnf_list(expr)
	return L

def isPred(listPred, inp):
	for pred in listPred:
		if pred in inp:
			return True
	return False

# -----------------------------
def generate_dual_Horn(L, given_list_preds):
	# 1. get raw data of the CNF
	list_cnf_clauses = list_cnf_clauses_raw(L)
	# convert it into list of CNF_Clauses
	list_MyClause = get_list_cnf_clauses (list_cnf_clauses)

	list_all_ports = get_all_port_elements(list_MyClause, given_list_preds)

	# 2. synthesis clauses which have the same negative list
	synthesis_cnf = synthesis_cnf_clauses(list_MyClause)
	# 3. collect predicates with ports in negative clause
	synthesis_cnf = collect_neg_with_conditions(synthesis_cnf, given_list_preds)
	# generate dual-Horn
	gen_dual_Horn = mk_dualHorn(synthesis_cnf)
	print ("\nBefore saturating")
	print_dual_Horn(gen_dual_Horn)

	dh = saturate_dual_horn(gen_dual_Horn, list_all_ports)
	print ("\nAfter saturating")
	print_dual_Horn(dh)

	return gen_dual_Horn

def get_synthesised_cnf(L, given_list_preds):
	list_cnf_clauses = list_cnf_clauses_raw(L)
	list_MyClause = get_list_cnf_clauses (list_cnf_clauses)
	synthesis_cnf = synthesis_cnf_clauses(list_MyClause)
	synthesis_cnf = collect_neg_with_conditions(synthesis_cnf, given_list_preds)

	return synthesis_cnf

def get_synthesised_cnf_without_neg(L):
	list_cnf_clauses = list_cnf_clauses_raw(L)
	list_MyClause = get_list_cnf_clauses (list_cnf_clauses)
	synthesis_cnf = synthesis_cnf_clauses(list_MyClause)
	return synthesis_cnf

def get_synthesised_cnf_2_steps(L):
	list_cnf_clauses = list_cnf_clauses_raw(L)
	list_MyClause = get_list_cnf_clauses (list_cnf_clauses)
	return list_MyClause

def main():
	# config = {"Peer":["p", "p1"], "Tracker":["P1p", "P3p"], "Route":["r", "r1"], "Monitor":["m"]}
	# config = dsl2skol.new_dict_class_instance
	data = {}
	system_info = {}
	with open('gen-data/data_tracker_peer.json', 'r') as fp:
		data = json.load(fp)
	with open('gen-data/system_info_tracker_peer.json', 'r') as fp:
		system_info = json.load(fp)

	config = system_info['configuration']

	print ("show config: " + str(config))
	# L = get_cnf_list(os.path.abspath(os.path.dirname(__file__)) + "/input.txt")
	L = get_cnf_list("gen-data/PBL_tracker_peer.txt")
	print ("\n-----\n")
	print (L)
	# list_tracker_peer_preds = ["isReg", "differ", "hasCapacity", "notEmpty"]
	# list_tracker_peer_preds = dsl2skol.list_conditions
	list_tracker_peer_preds = system_info['constraints']

	# 1. get raw data of the CNF
	list_cnf_clauses = list_cnf_clauses_raw(L)
	# convert it into list of CNF_Clauses
	list_MyClause = get_list_cnf_clauses (list_cnf_clauses)
	# print ("list_MyClause: ")
	# print (list_MyClause)
	list_all_ports = get_all_port_elements(list_MyClause, list_tracker_peer_preds, config)

	# 2. synthesis clauses which have the same negative list
	synthesis_cnf = synthesis_cnf_clauses(list_MyClause)

	# 3. collect predicates with ports in negative clause
	synthesis_cnf = collect_neg_with_conditions(synthesis_cnf, list_tracker_peer_preds)
	
	# generate dual-Horn
	dual_horn_clause = mk_dualHorn(synthesis_cnf)
	print ("\nBefore saturating")
	print_dual_Horn(dual_horn_clause)
	dh = saturate_dual_horn(dual_horn_clause, list_all_ports)
	# print ("list_all_ports: ")
	# print (list_all_ports)
	print ("\nAfter saturating")
	print_dual_Horn(dh)


	absorbed_dual_horn_clause = absorb_dual_Horn(dual_horn_clause)
	print_dual_Horn(absorbed_dual_horn_clause)
	# print (type(absorbed_dual_horn_clause))

	accept_list = []
	require_list = []
	result = ""
	for elem in absorbed_dual_horn_clause:
		for sub_elm in elem:
			# print (type(sub_elm))
			# print (sub_elm.neg[0].text)
			if sub_elm.pos != []:
				pos_str = []

				for i in sub_elm.pos:
					if isinstance(i, list):	
						for pos_i in i:
							if isPred(list_tracker_peer_preds, pos_i.text) == False:
								pos_str.append(pos_i.text)

					else:
						if isPred(list_tracker_peer_preds, i.text) == False: pos_str.append(i.text)				
				# pos_str = [i.text for i in sub_elm.pos if i[0].isPred == False]
				if sub_elm.neg != []:
					list_neg = []
					list_neg.append(sub_elm.neg[0].text)
					# print (list_neg)
					tmp_neg = replace_instances_by_class(list_neg, config)
					tmp_post = replace_instances_by_class(pos_str, config)
					if len(tmp_neg) > 0:
					# new_tmp_neg = [get_JavaBIP_style(tmp_elm) for tmp_elm in tmp_neg]
					# new_tmp_post = [get_JavaBIP_style(tmp_elm) for tmp_elm in tmp_post]
					# result += "port(" + tmp_neg[0] + ").requires(" + "; ".join(tmp_post) + ");\n"
						require_list.append("port(" + tmp_neg[0] + ").requires(" + "; ".join(tmp_post) + ");\n")
					# print ("port(" + tmp_neg[0] + ").requires(" + "; ".join(tmp_post) + ");")
				else: #accept_list of each dual horn clause
					# Replace instance_name by class_name before extending it
					tmp_list = replace_instances_by_class(pos_str, config)
					# for pos_elm in pos_str:
					# 	strsplit = pos_elm.split("_")
					# 	params = strsplit[1:]
					# 	for param_i in params:
					# 		for k,v in config.items():
					# 			if param_i in v:
					# 				# print ("check exist: " + param_i + " - " + k)
					# 				tmp = pos_elm.replace("_"+param_i, "_" + k)
					# 				tmp_list.append(tmp)

					# accept_list.extend(pos_str)
					# accept_list = list(set(accept_list))
					# print ("; ".join(tmp_list))
					if accept_list == []:
						accept_list = tmp_list
					else:
						for tmp_elm in tmp_list:
							if tmp_elm not in accept_list:
								accept_list.append(tmp_elm)
					print ("---\n")

	# print ("; ".join(accept_list))
	# print ("--------")
	n_accepts_list = []
	dict_accept = {}
	for i in range(len(accept_list)):
		rhs = []
		for j in range(len(accept_list)):
			if i != j:
				rhs.append(accept_list[j])
		dict_accept[accept_list[i]] = list(set(rhs))

	for k,v in dict_accept.items():
		# result += ('port(' + k + ').accepts(' + ', '.join(v) + ');\n')
		n_accepts_list.append('port(' + k + ').accepts(' + ', '.join(v) + ');\n')
	# print (dict_accept)
	n_require_list = list(set(require_list))
	for req in n_require_list:
		result += req
	for acc in n_accepts_list:
		result += acc
	print ("--------")
	print (result)

def get_JavaBIP_style(inpStr):
	# print ("----- check input: " + inpStr)
	str_parts = inpStr.split("_")
	return (str_parts[0] + '.class, "' + str_parts[1] + '"')
	# return (inpStr[inpStr.index("_")+1:] + '.class, "' + inpStr[0:inpStr.index("_")] + '"')

def replace_instances_by_class(list_actions, config):
	tmp_list = []
	# for pos_elm in list_actions:
	# 	strsplit = pos_elm.split("_")
	# 	params = strsplit[1:]
	# 	for param_i in params:
	# 		for k,v in config.items():
	# 			if param_i in v:
	# 				print ("check exist: " + param_i + " - " + k)
	# 				tmp = pos_elm.replace("_"+param_i, "_" + k)
	# 				tmp_list.append(tmp)
	# rs = [get_JavaBIP_style(tmp_elm) for tmp_elm in tmp_list]
	# return rs
	for action in list_actions:
		strsplit = action.split("_")
		for k,v in config.items():
			if strsplit[0] in v:
				# print ("check exist: " + strsplit[0] + " - " + k)
				tmp_action = action.replace(strsplit[0]+"_", k+"_")
				tmp_list.append(tmp_action)
	rs = [get_JavaBIP_style(tmp_elm) for tmp_elm in tmp_list]
	return rs

if __name__ == "__main__":
    main()

