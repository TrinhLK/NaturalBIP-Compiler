#!/usr/bin/env python
import sys
import os
import os.path
import json
mango_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))+ '/include/')
sys.path.append(mango_dir)
import PyBool_public_interface as Bool
import dhorn2bip as bipgen

# -------------------------------------
# Load data
with open('gen-data/system_infor.json', 'r') as fp:
	system_info = json.load(fp)

print ("\nsystem_info: " + str(system_info))
print ("\nconfigurations: " + str(system_info['configuration']))
print ("\npredicates: " + str(system_info['constraints']))
print ("\nactions: " + str(system_info['actions']))
list_actions = [elm[0] for elm in system_info['actions']]
list_constraints = [elm[0] for elm in system_info['constraints']]

print ("\nlist_actions: " + str(list_actions))
print ("\nlist_constraints: " + str(list_constraints))
allowed_interactions = {}
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
	print (L)
	for i in L["Clauses"]:
		if isinstance(i,list):
			list_key_rev.append(i[::-1])
		else:
			list_key_rev.append(L["Clauses"][::-1])
	# print ("list_key_rev: " + str(list_key_rev))
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
			text = text.replace("~", "")
		self.text = text
		self.params = [text[0:text.find("_")]]
		self.name = text[text.find("_")+1:]
		# self.name = text[0:text.find("_")]
		# params_text = text[text.find("_")+1:]
		# self.params = params_text.split("_")
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
		res += " | ".join(list_txt_neg)
		
		if list_txt_pos != []:
			if list_txt_neg != []: res += " | "
			res += " | ".join(list_txt_pos)
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
def merge_two_pos_list_OUTDATED(l_atom_1, l_atom_2):
	result = []
	l_atom_1_text = [elm[0].text for elm in l_atom_1]
	l_atom_2_text = [elm[0].text for elm in l_atom_2]
	# print (str(l_atom_1_text) + "\t" + str(l_atom_2_text))
	merged_list_text = l_atom_1_text + l_atom_2_text
	merged_list_text = list(set(merged_list_text))
	# print (merged_list_text)
	merged_list = l_atom_1 + l_atom_2
	dict_pos = {}

	for elm_text in merged_list_text:
		for elm in merged_list:
			if elm[0].text == elm_text:
				dict_pos[elm_text] = elm
	# print ("new post list: " + str(merged_list_text) + "\t len(dict_pos): " + str(list(dict_pos.keys())))
	result = list(dict_pos.values())

	# if l_atom_1 == []:
	# 	return l_atom_2
	# else:
	# 	if l_atom_2 == []:
	# 		return l_atom_1
	# 	for i in l_atom_1:
	# 		temp_list = []
	# 		if isinstance(i, list):
	# 			for i_el in i:
	# 				temp_list.append(i_el)
	# 		else:
	# 			temp_list.append(i)
	#
	# 		for j in l_atom_2:
	# 			temp_list_j = []
	# 			if isinstance(j, list):
	# 				for j_el in j:
	# 					temp_list_j.append(j_el)
	# 			else:
	# 				temp_list_j.append(j)
	#
	# 			result.append(temp_list + temp_list_j)
	#
	return result

def merge_two_pos_list(l_atom_1, l_atom_2):
	l_atom_1_text = []
	l_atom_2_text = []
	merged_list = []
	result = []

	for i in l_atom_1:
		if isinstance(i, list):
			for elm in i:
				# print ("TEST TEXT:" + elm.text)
				merged_list.append(elm)
			i_text = [elm.text for elm in i]
			l_atom_1_text.append(i_text)
			
	l_atom_2_text = [elm[0].text for elm in l_atom_2]
	for elm in l_atom_2:
		merged_list.append(elm[0])

	# print ("merged_list:" + str(merged_list))
	merged_list = list(set(merged_list))
	merged_list_str = []
	for elm in merged_list:
		# print ("check type: " + str(type(elm)) + "\tvalue: " + elm.showInfor())
		merged_list_str.append(elm.showInfor())
		# sub_merged_list = []
		# if isinstance(elm, list):
		# 	for elm_i in elm:
		# 		sub_merged_list.append(elm_i.showInfor())
		# else:
		# 	merged_list_str.append(elm.showInfor())
		# print ("value: " + elm.showInfor())
	# merged_list_str = [elm.showInfor() for elm in merged_list]
	# print ("merged_list_str:" + str(merged_list_str))

	merged_list_text = merge_two_pos_list_text(l_atom_1_text, l_atom_2_text)
	# print ("merged_list_text:" + str(merged_list_text))
	for text_list in merged_list_text:
		sub_rs = []
		for elm_text in text_list:
			for elm in merged_list:
				if elm.text == elm_text:
					sub_rs.append(elm)
					break
		result.append(sub_rs)
	return result

# def merge_two_pos_list_text(l_atom_1_text, l_atom_2_text):
# 	merged_list_text = []
# 	print ("l_atom_1_text: " + str(l_atom_1_text))
# 	print ("l_atom_2_text: " + str(l_atom_2_text))
# 	if l_atom_1_text == []:
# 		return l_atom_2_text
# 	else:
# 		if l_atom_2_text == []:
# 			return l_atom_1_text
# 		for i in l_atom_1_text:
# 			temp_list = []
# 			if isinstance(i, list):
# 				temp_list = i
# 				for y in l_atom_2_text:
# 					temp_list.append(y)
# 				merged_list_text.append(temp_list)
# 				# print ("check: " + str(merged_list_text))
# 			else:
# 				temp_list = [[i_el, y] for i_el in l_atom_1_text for y in l_atom_2_text]
# 				merged_list_text = temp_list
	
# 	print ("merged_list_text: " + str(merged_list_text))
# 	return merged_list_text
def merge_two_pos_list_text(l_atom_1_text, l_atom_2_text):
    # temp_list = [[i_el, y] for i_el in l_atom_1_text for y in l_atom_2_text]
	temp_list = []
	if l_atom_1_text == []:
		return l_atom_1_text
	else:
		if l_atom_2_text == []:
			return l_atom_2_text
		for elm_1 in l_atom_1_text:
			if isinstance(elm_1, list):
		# print ("fg")
				for elm_2 in l_atom_2_text:
					new_value = elm_1
					new_value.append(elm_2)
					new_value = list(set(new_value))
					temp_list.append(new_value)
			else:
				for elm_2 in l_atom_2_text:
					new_value = []
					new_value.append(elm_1)
					new_value.append(elm_2)
					new_value = list(set(new_value))
					temp_list.append(new_value)
    # print ("before: " + str(temp_list))
		l = list(map(list, set(map(tuple, map(set, temp_list)))))
    # print ("after: " + str(l))
		return l
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
		print ("k_i: " + str(k_i) + "\tv_i: " + str(v_i))
		for elem_v_i in v_i:
			# tmp = Atomic_Element(elem_v_i + "_" + k_i)
			tmp = Atomic_Element(k_i + "_" + elem_v_i)
			result.append([tmp])
	print ("result type: " + str(type(result)) + "\t result: " + str(result))
	return result

def create_addtional_positive_clause(elem_list, config):
	my_dict = convert_list_elem_to_dict(elem_list)
	my_dict = create_dict_of_instances_actions(my_dict,config)
	result = convert_dict_to_list_pos(my_dict)
	return result
# END -------------------------------------------------------------------

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

# Generate additional postive clause
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

	# print ("test list ports:\nbefore")
	# for elem_i in temp:
	# 	print (elem_i)
	temp = list(dict.fromkeys(temp))
	# print ("test list ports:\nafter")
	# test_rs = []
	for elem_i in temp:
		atom_elem = Atomic_Element(elem_i)
		# print (elem_i)
		result.append([atom_elem])
		# test_rs.append([elem_i])
	# print (result)
	for clause_i in list_cnf_clauses:
		clause_i.printer()
	# result_1 = create_addtional_positive_clause(result, config)
	# my_dict = convert_list_elem_to_dict(result)
	# print (my_dict)
	# print ("-----")
	# my_dict = add_ports_to_all_instances(my_dict)
	# print (my_dict)
	# print ("-----")
	# result = convert_dict_to_list_pos(my_dict)
	return result
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
				# print ("neg_i: " + str(list_MyClause[i].get_neg_list_str()))
				# print ("neg_j: " + str(list_MyClause[j].get_neg_list_str()))
				# print("pos_i: " + str(list_MyClause[i].get_pos_list_str()))
				# print("pos_j: " + str(list_MyClause[j].get_pos_list_str()))
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
	if cl2.neg == []:
		if hasattr(cl1, "neg"):
			for cl1_neg_j in cl1.neg:
				list_tmp = []
				tmp_clause = CNF_Clauses()
				tmp_clause.neg = []
				tmp_clause.pos = [elm for elm in cl2.pos]

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
				tmp_clause.neg = []
				tmp_clause.pos = [elm for elm in cl2.pos]
				list_tmp.append(tmp_clause)

				rs.append(list_tmp)
		# for cl1_neg_j in cl1.neg:
		# 	list_tmp = []
		# 	tmp_clause = CNF_Clauses()
		# 	tmp_clause.neg = []
		# 	tmp_clause.pos = [elm for elm in cl2.pos]

		# 	subtmp_clause = CNF_Clauses()
		# 	subtmp_clause.neg = cl1_neg_j
		# 	subtmp_clause.pos = cl1.pos

		# 	list_tmp.append(subtmp_clause)
		# 	list_tmp.append(tmp_clause)
		# 	rs.append(list_tmp)
	else:
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
	# print ("list_cls: " + str(list_cls))
	if len(list_cls) > 1:

		res_cls = list_cls[0]
		for i in range(1, len(list_cls)):
			res_cls = combination_of_2_clauses(res_cls, list_cls[i])
	if len(list_cls) == 1:
		cls_0 = list_cls[0]
		for neg_i in cls_0.neg:
			tmp_cls = CNF_Clauses()
			tmp_cls.neg = neg_i
			tmp_cls.pos = cls_0.pos
			res_cls.append([tmp_cls])
	print ("\n--- 4. Generate list of dual-Horn clause")
	print_dual_Horn(res_cls)
	return res_cls

def saturate_dual_horn(dual_horn, list_ports):
	res = []
	# additional_clause = CNF_Clauses()
	# additional_clause.neg = []
	# additional_clause.pos = list_ports

	# tmp_additional_clause = CNF_Clause()
	# print ("Print list port: ")
	list_port_str = []
	

	for port in list_ports:
		# print (port[0].showInfor())
		list_port_str.append(port[0].showInfor())	

	for dual_horn_set in dual_horn:
		tmp_additional_str = []
		if isinstance(dual_horn_set,list):
			for dh_clause in dual_horn_set:
				if dh_clause.pos != []:
					for neg_elm in dh_clause.neg:
						if neg_elm.showInfor() in list_port_str:
							tmp_additional_str.append(neg_elm.showInfor())
					for pos_set in dh_clause.pos:
						for pos_elm in pos_set:
							if pos_elm.showInfor() in list_port_str:
								tmp_additional_str.append(pos_elm.showInfor())
		else:
			for neg_elm in dual_horn_set.neg:
				if neg_elm.showInfor() in list_port_str:
					tmp_additional_str.append(neg_elm.showInfor())
			for pos_set in dual_horn_set.pos:
				for pos_elm in pos_set:
					if pos_elm.showInfor() in list_port_str:
						tmp_additional_str.append(pos_elm.showInfor())
		print ("additional_clause_str: " + str(tmp_additional_str))
		# print ("--- additional_clause_str: " + str(list(set(tmp_additional_str))))
		tmp_additional_str = list(set(tmp_additional_str))

		tmp_additional = []
		for elm in tmp_additional_str:
			new_elm = Atomic_Element(elm)
			tmp_additional.append([new_elm])
		# for elm in tmp_additional:
		# 	print ("tmp_additional_elm: " + elm[0].showInfor())
		shouldAddMoreClause = True
		if isinstance(dual_horn_set,list):
			for dh_clause in dual_horn_set:
				if dh_clause.neg == []:
					dh_clause.pos = tmp_additional
					shouldAddMoreClause = False
		
		if shouldAddMoreClause == True:
			additional_clause_1 = CNF_Clauses()
			additional_clause_1.neg = []
			additional_clause_1.pos = tmp_additional
			# additional_clause_1.printer()
			dual_horn_set.append(additional_clause_1)
		# else:
		# 	additional_clause_1 = CNF_Clauses()
		# 	additional_clause_1.neg = []
		# 	additional_clause_1.pos = tmp_additional
		# 	# additional_clause_1.printer()
		# 	dual_horn_set.append(additional_clause_1)

	# for elem in dual_horn:
	# 	# print ("*** \t\t\tCHECK TYPE: " + str(type(elem)))
	# 	elem.append(additional_clause)
	# 	# print ("check addional_clause: " + str(len(additional_clause.pos)))
	return dual_horn

# -----------------------------
# 1. From each dualHorn set
# 	add related element to the non-negative clause
# 2. Get the union of non-negative clauses
# return
def generate_atomic_interactions(dual_horn, list_ports):
	res = []
	set_of_interactions = []
	list_port_str = []

	# Get strings of all list ports
	for port in list_ports:
		list_port_str.append(port[0].showInfor())	
	i = 0
	for dual_horn_set in dual_horn:
		positive_clause_str = []
		set_of_atomic_interactions = []
		positive_clause = []

		for dual_horn_clause in dual_horn_set:
			if dual_horn_clause.neg == []:
				tmp_positive_clause_str = dual_horn_clause.get_pos_list_str()
				for elm in tmp_positive_clause_str:
					positive_clause_str.append(elm[0])
				print ("positive_clause_str: " + str(positive_clause_str))
		positive_clause_str = list(set(positive_clause_str))
		for elm in positive_clause_str:
			checked = False
			conjunction_of_elm = ""
			for dual_horn_clause in dual_horn_set:

				atomic_interactions = []
				# print ("Neg_clause: " + str(dual_horn_clause.get_neg_list_str()))
				# print ("Post_clause: " + str(dual_horn_clause.get_pos_list_str()))

				if dual_horn_clause.neg != [] and dual_horn_clause.get_pos_list_str() != []:
					neg_action = ""
					for neg_elem in dual_horn_clause.get_neg_list_str():
						if neg_elem in list_port_str:
							neg_action = neg_elem
							# atomic_interactions.append(neg_elem)

					if neg_action == elm:
						atomic_interactions.append(neg_action)
						for pos_clause in dual_horn_clause.get_pos_list_str():
							if isinstance(pos_clause, list):
								for pos_elem in pos_clause:
									if pos_elem in list_port_str:
										atomic_interactions.append(pos_elem)
							else:
								if pos_clause in list_port_str:
									atomic_interactions.append(pos_clause)
						# conjunction_of_elm = "&".join(atomic_interactions)

						canAdd = True
						for positive_clause_elm in positive_clause:
							if list(set(positive_clause_elm) - set(atomic_interactions)) == [] and list(set(atomic_interactions) - set(positive_clause_elm)) == []:
								canAdd = False
								break
						if canAdd == True:	
							atomic_interactions = list(set(atomic_interactions))
							positive_clause.append(atomic_interactions)
						checked = True
			if checked == False: positive_clause.append([elm])
			# print ("conjunction_of_elm: " + str(conjunction_of_elm))
			# positive_clause = list(map(lambda x: x.replace(elm, conjunction_of_elm), positive_clause))
		print ("positive_clause_" + str(i) + " = " + str(positive_clause))
		set_of_interactions.append(positive_clause)

		for positive_clause_elm in positive_clause:
			if res == []: 
				positive_clause_elm = list(set(positive_clause_elm))
				res.append(positive_clause_elm)
			else:
				canAdd = True
				for elm in res:
					if list(set(elm) - set(positive_clause_elm)) == [] and list(set(positive_clause_elm) - set(elm)) == []:
						canAdd = False
						break
				if canAdd == True:	
					positive_clause_elm = list(set(positive_clause_elm))
					res.append(positive_clause_elm)
		i = i+1
	print ("Unionset =  " + str(res))
	print ("set_of_interactions =  " + str(set_of_interactions) + "\nlen = " + str(len(set_of_interactions)))
	new_set_of_interactions = []

	for elm_i in set_of_interactions:
	    if elm_i not in new_set_of_interactions and elm_i != []:
	        new_set_of_interactions.append(elm_i)
	print ("new set_of_interactions =  " + str(new_set_of_interactions) + "\nlen = " + str(len(new_set_of_interactions)))
	return new_set_of_interactions
			# canAdd = True
			# for positive_clause_elm in positive_clause:
			# 	if list(set(positive_clause_elm) - set(atomic_interactions)) == []:
			# 		canAdd = False
			# 		break
			# if canAdd == True:	positive_clause.append(atomic_interactions)

			
		# print ("POSitive clause: " + str(positive_clause))

#----------------- ----------------- ----------------- -----------------
def generate_atomic_interactions_1(dual_horn, list_ports):
	res = []
	set_of_interactions = []
	list_port_str = []

	# Get strings of all list ports
	for port in list_ports:
		list_port_str.append(port[0].showInfor())	
	i = 0
	for dual_horn_set in dual_horn:
		positive_clause_str = []
		set_of_atomic_interactions = []
		positive_clause = []

		m_tmp_positive_clause_str = []
		for dual_horn_clause in dual_horn_set:
			if dual_horn_clause.neg == []:
				tmp_positive_clause_str = dual_horn_clause.get_pos_list_str()
				for elm in tmp_positive_clause_str:
					positive_clause_str.append(elm[0])
				print ("positive_clause_str: " + str(positive_clause_str))
			else:
				tmp_positive_clause_str = dual_horn_clause.get_pos_list_str()
				print ("tmp_positive_clause_str: " + str(tmp_positive_clause_str))
				if tmp_positive_clause_str != []:
					m_tmp_positive_clause_str = m_tmp_positive_clause_str + tmp_positive_clause_str
		print ("m_tmp_positive_clause_str: " + str(m_tmp_positive_clause_str))

		for elm_idx in range(len(positive_clause_str)):
			for tmp_pos_elm in m_tmp_positive_clause_str:
				if positive_clause_str[elm_idx] in tmp_pos_elm:
					positive_clause_str[elm_idx] = tmp_pos_elm
					break
		print ("new_positive_clause_str: " + str(positive_clause_str))
		
		for elm in range(len(positive_clause_str)):
			# atomic_interactions = []
			for dual_horn_clause in dual_horn_set:
				
				if dual_horn_clause.neg != [] and dual_horn_clause.get_pos_list_str() != []:

					# Get neg_action, ignore neg_conditions
					neg_action = ""
					for neg_elem in dual_horn_clause.get_neg_list_str():
						if neg_elem in list_port_str:
							neg_action = neg_elem

					if len(positive_clause_str[elm]) == 1 and neg_action == positive_clause_str[elm][0]:
						for pos_cls_elm in dual_horn_clause.get_pos_list_str():
							tmp_atomic_interactions = pos_cls_elm + dual_horn_clause.get_neg_list_str()
							print ("check 1: " + neg_action + " \t " + str(tmp_atomic_interactions))
							positive_clause_str[elm] = tmp_atomic_interactions
					if neg_action == positive_clause_str[elm]:
						for pos_cls_elm in dual_horn_clause.get_pos_list_str():
							tmp_atomic_interactions = pos_cls_elm + dual_horn_clause.get_neg_list_str()
							print ("check 2: " + neg_action + " \t " + str(tmp_atomic_interactions))
							positive_clause_str[elm] = tmp_atomic_interactions
				# atomic_interactions = list(map(list, set(map(tuple, map(set, atomic_interactions)))))
		print ("positive_clause_str: " + str(positive_clause_str))
		positive_clause_str = list(map(list, set(map(tuple, map(set, positive_clause_str)))))
		print ("updated_positive_clause_str: " + str(positive_clause_str))
		# positive_clause_str = list(set(positive_clause_str))
		# for elm in positive_clause_str:
		# 	checked = False
		# 	conjunction_of_elm = ""
		# 	for dual_horn_clause in dual_horn_set:

		# 		atomic_interactions = []
		# 		# print ("Neg_clause: " + str(dual_horn_clause.get_neg_list_str()))
		# 		# print ("Post_clause: " + str(dual_horn_clause.get_pos_list_str()))

		# 		if dual_horn_clause.neg != [] and dual_horn_clause.get_pos_list_str() != []:
		# 			neg_action = ""
		# 			for neg_elem in dual_horn_clause.get_neg_list_str():
		# 				if neg_elem in list_port_str:
		# 					neg_action = neg_elem
		# 					# atomic_interactions.append(neg_elem)

		# 			if neg_action == elm:
		# 				atomic_interactions.append(neg_action)
		# 				for pos_clause in dual_horn_clause.get_pos_list_str():
		# 					if isinstance(pos_clause, list):
		# 						for pos_elem in pos_clause:
		# 							if pos_elem in list_port_str:
		# 								atomic_interactions.append(pos_elem)
		# 					else:
		# 						if pos_clause in list_port_str:
		# 							atomic_interactions.append(pos_clause)
		# 				# conjunction_of_elm = "&".join(atomic_interactions)

		# 				canAdd = True
		# 				for positive_clause_elm in positive_clause:
		# 					if list(set(positive_clause_elm) - set(atomic_interactions)) == [] and list(set(atomic_interactions) - set(positive_clause_elm)) == []:
		# 						canAdd = False
		# 						break
		# 				if canAdd == True:	
		# 					atomic_interactions = list(set(atomic_interactions))
		# 					positive_clause.append(atomic_interactions)
		# 				checked = True
		# 	if checked == False: positive_clause.append([elm])
		# 	# print ("conjunction_of_elm: " + str(conjunction_of_elm))
		# 	# positive_clause = list(map(lambda x: x.replace(elm, conjunction_of_elm), positive_clause))
		# print ("positive_clause_" + str(i) + " = " + str(positive_clause))
		set_of_interactions.append(positive_clause_str)

		for positive_clause_elm in positive_clause_str:
			if res == []: 
				positive_clause_elm = list(set(positive_clause_elm))
				res.append(positive_clause_elm)
			else:
				canAdd = True
				for elm in res:
					if list(set(elm) - set(positive_clause_elm)) == [] and list(set(positive_clause_elm) - set(elm)) == []:
						canAdd = False
						break
				if canAdd == True:	
					positive_clause_elm = list(set(positive_clause_elm))
					res.append(positive_clause_elm)
		i = i+1
	print ("Unionset =  " + str(res))
	print ("set_of_interactions =  " + str(set_of_interactions) + "\nlen = " + str(len(set_of_interactions)))
	new_set_of_interactions = []

	for elm_i in set_of_interactions:
	    if elm_i not in new_set_of_interactions and elm_i != []:
	        new_set_of_interactions.append(elm_i)
	print ("new set_of_interactions =  " + str(new_set_of_interactions) + "\nlen = " + str(len(new_set_of_interactions)))
	return new_set_of_interactions


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
		# remove_elements_in_pos_clause_1(a_clause)
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
	elements_to_be_removed = []
	for clause_i in a_dual_horn_clause:
		if clause_i.pos == []:
			tmp_neg_str_j = [elem.text for elem in clause_i.neg if elem.isPred == False]
			elements_to_be_removed = list(set(elements_to_be_removed + tmp_neg_str_j))
	# print ("\nelements_to_be_removed: " + str(elements_to_be_removed))	

	for clause_i in a_dual_horn_clause:
		# if clause_i.pos == []: continue
		list_pos_str = []
		list_pos_atom = []
		for pos_j in clause_i.pos:
			if isinstance(pos_j,list):
				tmp_pos_j = [elem.text for elem in pos_j if elem.isPred == False]
				list_pos_str.append(tmp_pos_j)
			else:
				if pos_j.isPred == False:
					list_pos_str.append([pos_j.text])
		# print ("list_pos_str: " + str(list_pos_str))

		new_list_pos_str = []
		for pos_j in list_pos_str:
			new_pos_j = []
			for elm_str in pos_j:
				if elm_str not in elements_to_be_removed:
					new_pos_j.append(elm_str)
			new_list_pos_str.append(new_pos_j)

		# print ("new_list_pos_str: " + str(new_list_pos_str))
		for pos_j in new_list_pos_str:
			pos_j_atom = []
			if pos_j != []:
				for elm_str in pos_j:
					elm_atom = Atomic_Element(elm_str)
					pos_j_atom.append(elm_atom)

			if pos_j_atom != []:
				list_pos_atom.append(pos_j_atom)
		new_clause = CNF_Clauses()
		new_clause.neg = clause_i.neg
		new_clause.pos = list_pos_atom
		result.append(new_clause)
	return result

def remove_elements_in_pos_clause_1(a_dual_horn_clause):
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
# def generate_dual_Horn(L, given_list_preds):
# 	# 1. get raw data of the CNF
# 	list_cnf_clauses = list_cnf_clauses_raw(L)
# 	# convert it into list of CNF_Clauses
# 	list_MyClause = get_list_cnf_clauses (list_cnf_clauses)
#
# 	list_all_ports = get_all_port_elements(list_MyClause, given_list_preds)
#
# 	# 2. synthesis clauses which have the same negative list
# 	synthesis_cnf = synthesis_cnf_clauses(list_MyClause)
# 	# 3. collect predicates with ports in negative clause
# 	synthesis_cnf = collect_neg_with_conditions(synthesis_cnf, given_list_preds)
# 	# generate dual-Horn
# 	gen_dual_Horn = mk_dualHorn(synthesis_cnf)
# 	print ("\nBefore saturating")
# 	print_dual_Horn(gen_dual_Horn)
#
# 	dh = saturate_dual_horn(gen_dual_Horn, list_all_ports)
# 	print ("\nAfter saturating")
# 	print_dual_Horn(dh)
#
# 	return gen_dual_Horn

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


def gen_JavaBIP_Macro_code(req_file):
	# config = {"Peer":["p", "p1"], "Tracker":["P1p", "P3p"], "Route":["r", "r1"], "Monitor":["m"]}
	# config = dsl2skol.new_dict_class_instance
	# data = {}
	system_info = {}
	# with open('gen-data/data_tracker_peer.json', 'r') as fp:
	# 	data = json.load(fp)
	with open('gen-data/system_infor.json', 'r') as fp:
		system_info = json.load(fp)

	config = system_info['configuration']
	list_actions = [elm[0] for elm in system_info['actions']]
	list_constraints = [elm[0] for elm in system_info['constraints']]


	L = get_cnf_list(req_file)
	# print("\n-----\n")
	# print(L)

	list_tracker_peer_preds = [elm[0] for elm in system_info['constraints']]

	# 1. get raw data of the CNF
	list_cnf_clauses = list_cnf_clauses_raw(L)
	list_MyClause = get_list_cnf_clauses(list_cnf_clauses)
	# print (list_cnf_clauses)
	list_all_ports = get_all_port_elements(list_MyClause, list_tracker_peer_preds, config)

	# 2. synthesis clauses which have the same negative list
	synthesis_cnf = synthesis_cnf_clauses(list_MyClause)

	# 3. collect predicates with ports in negative clause
	synthesis_cnf = collect_neg_with_conditions(synthesis_cnf, list_tracker_peer_preds)

	# generate dual-Horn
	dual_horn_clause = mk_dualHorn(synthesis_cnf)
	# print ("*** \t\t\tCHECK TYPE INPUT: " + str(type(dual_horn_clause)))
	# dh = saturate_dual_horn(dual_horn_clause, list_all_ports)


	absorbed_dual_horn_clause = absorb_dual_Horn(dual_horn_clause)
	print ("--- 5. absorbed dual-Horn clause")
	print_dual_Horn(absorbed_dual_horn_clause)
	print ("--- 5.1 added pos clauses")
	absorbed_dual_horn_clause = saturate_dual_horn(absorbed_dual_horn_clause, list_all_ports)
	print_dual_Horn(absorbed_dual_horn_clause)

	print ("--- 6. set of atomic interactions")
	# print_dual_Horn(absorbed_dual_horn_clause)
	# generate_atomic_interactions(absorbed_dual_horn_clause, list_all_ports)
	# print ("---- generate_atomic_interactions_1 ----")
	# generate_atomic_interactions_1(absorbed_dual_horn_clause, list_all_ports)
	# print ("---- END generate_atomic_interactions_1 ----")

	# allowed_interactions[req_file] = generate_atomic_interactions(absorbed_dual_horn_clause, list_all_ports)
	allowed_interactions[req_file] = generate_atomic_interactions_1(absorbed_dual_horn_clause, list_all_ports)

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
						tmp_pos = []
						for pos_i in i:
							if isPred(list_tracker_peer_preds, pos_i.text) == False:
								tmp_pos.append(pos_i.text)
						pos_str.append(tmp_pos)
					else:
						# if isPred(list_tracker_peer_preds, i.text) == False: pos_str.append(i.text)
						if isPred(list_tracker_peer_preds, i.text) == False: pos_str.append([i.text])
				# pos_str = [i.text for i in sub_elm.pos if i[0].isPred == False]
				# print ("pos_str: " + str(pos_str))
				if sub_elm.neg != []:
					list_neg = []
					list_neg.append(sub_elm.neg[0].text)
					# print ("list_neg: " + str(list_neg))
					tmp_neg = replace_instances_by_class(list_neg, config)
					# print ("tmp_neg: " + str(tmp_neg))
					for pos_elm_list in pos_str:
						tmp_post = replace_instances_by_class(pos_elm_list, config)
						if len(tmp_neg) > 0:
							if tmp_neg[0] in tmp_post:
								tmp_post.remove(tmp_neg[0])
							tmp_post = list(set(tmp_post))
							require_list.append("port(" + tmp_neg[0] + ").requires(" + ", ".join(tmp_post) + ");\n")
					# tmp_post = replace_instances_by_class(pos_str, config)
					# if len(tmp_neg) > 0:
					# 	if tmp_neg[0] in tmp_post:
					# 		tmp_post.remove(tmp_neg[0])
					# 	tmp_post = list(set(tmp_post))
					# 	require_list.append("port(" + tmp_neg[0] + ").requires(" + ", ".join(tmp_post) + ");\n")
				else:  # accept_list of each dual horn clause
					# Replace instance_name by class_name before extending it
					tmp_list = []
					for pos_elm_list in pos_str:
						tmp_pos_list = replace_instances_by_class(pos_elm_list, config)
						tmp_list.append(tmp_pos_list[0])
					# tmp_list = replace_instances_by_class(pos_str, config)
					# if accept_list == [] or len(tmp_list) > len(accept_list):
					# 	accept_list = tmp_list
					# else:
					# 	for tmp_elm in tmp_list:
					# 		if tmp_elm not in accept_list:
					# 			accept_list.append(tmp_elm)
					intersect_list = list(set(tmp_list) & set(accept_list))
					accept_list = accept_list + tmp_list
					accept_list = [i for i in accept_list if not i in intersect_list or intersect_list.remove(i)]
					# if accept_list == []:
					# 	accept_list = tmp_list
					# else:
					# 	intersect_list = list(set(tmp_list) & set(accept_list))
					# 	accept_list = accept_list + tmp_list
					# 	accept_list = [i for i in accept_list if not i in intersect_list or intersect_list.remove(i)]


	# print ("\n\n ***** accept_list: " + str(accept_list))
	n_accepts_list = []
	dict_accept = {}
	for i in range(len(accept_list)):
		rhs = []
		for j in range(len(accept_list)):
			if i != j:
				rhs.append(accept_list[j])
		dict_accept[accept_list[i]] = list(set(rhs))

	for k, v in dict_accept.items():
		n_accepts_list.append('port(' + k + ').accepts(' + ', '.join(v) + ');\n')
	n_require_list = list(set(require_list))
	for req in n_require_list:
		result += req
	for acc in n_accepts_list:
		result += acc
	return result


def main():
	current_path = os.getcwd() + "/gen-data/PBL_reqs/"
	system_info = {}

	with open('gen-data/system_infor.json', 'r') as fp:
		system_info = json.load(fp)

	macro_code = ""
	bip_cons = ""
	for x in os.listdir(current_path):
		if x.endswith(".txt"):
			# Prints only text file present in My Folder
			print (x + " ------------------------ -------------------------- ------------------------")
			macro_code += gen_JavaBIP_Macro_code(current_path + x) + "\n"
			print ("End " + x + " ------------------------ -------------------------- ------------------------\n\n")
			# print (gen_JavaBIP_Macro_code(current_path + x))

	data_transfer = list(set(system_info['data_transfer']))
	for dt in data_transfer:
		macro_code += dt
	print("\n------------------------ -------------------------- ------------------------")
	print (macro_code)

	print("\n------------------------")
	boolean_functions = list(set(system_info['boolean_functions']))
	for bl in boolean_functions:
		print (bl)
	print("\nBIP connectors ------------------------")
	for k,v in allowed_interactions.items():
		req_name = k[k.rindex("/")+1:k.index(".txt")]
		bip_cons += bipgen.gen_BIP_connector(req_name, v)
		bip_cons += "\n"
	print (bip_cons)
	# gen_JavaBIP_Macro_code("gen-data/PBL_reqs/Req_01.txt")
	# print (allowed_interactions)

def get_JavaBIP_style(inpStr):
	# print ("----- check input: " + inpStr)
	str_parts = inpStr.split("-")
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
		# print ("action: " + action)
		strsplit = action.split("_")
		for k,v in config.items():
			if strsplit[0] in v:
				# print ("check exist: " + strsplit[0] + " - " + k)
				tmp_action = action.replace(strsplit[0]+"_", k+"-")
				# print ("tmp_action: " + tmp_action)
				tmp_list.append(tmp_action)
	rs = [get_JavaBIP_style(tmp_elm) for tmp_elm in tmp_list]
	return rs

if __name__ == "__main__":
    main()

