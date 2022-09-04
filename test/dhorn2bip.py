import json
import re
system_info = {}
with open('gen-data/system_infor.json', 'r') as fp:
		system_info = json.load(fp)

def get_connector(connector):
    triggers = []
    remains = []
    # result = []
    result_str = ""

    # In the case of standalone port
    for elm in connector:
        if len(elm) == 1:
            # triggers.append([elm])
            triggers.append(elm)
        else:
            remains.append(elm)

    if get_intersect(remains) != []:
        if triggers != []:
            for trig in triggers:
                if list(set(trig) & set(get_intersect(remains))) == []:
                    triggers.append(get_intersect(remains))
        else:
            triggers.append(get_intersect(remains))

    # print ("test insect: " + str(get_intersect(remains)))
    # In the case of compact ports
    # if triggers == []:
    #   triggers = get_intersect(remains)
    # print("len(triggers) - 1: " + str(len(triggers) - 1))

    # for trig in triggers:
    #   if len(trig) > 1:
    #     result_str += "[(" + ")-(".join(trig) + ")]`-"
    #   else:
    #     result_str += "(" + trig[0] + ")`-"
    print("triggers: " + str(triggers))
    print("remains: " + str(remains))

    if triggers == []:
        # result_str += "("
        for synch_set in remains:
            result_str += "(" + ")-(".join(synch_set) + ")\n"
            print ("sub synch_set: " + result_str)
        # result_str += ")"
    else:
        for i in range(len(triggers) - 1):
            if len(triggers[i]) > 1:
                result_str += "[(" + ")-(".join(triggers[i]) + ")]`-"
            else:
                result_str += "(" + triggers[i][0] + ")`-"

        if len(triggers[len(triggers) - 1]) > 1:
            result_str += "[(" + ")-(".join(
                triggers[len(triggers) - 1]) + ")]`"
        else:
            result_str += "(" + triggers[len(triggers) - 1][0] + ")`"

    # for trig in triggers:
    #   result.append([trig])
    # Lay ra tung remain set cho moi bien trig
    idx = 0
    for trig in triggers:
        elements_denpendOn_trig = []
        for elm in remains:
            is_sub_set = set(trig).issubset(set(elm))
            if is_sub_set:
                elements_denpendOn_trig.append(elm)
        elements_denpendOn_trig = get_list_remain(elements_denpendOn_trig,
                                                  triggers)
        # print("-- after trig: " + str(trig) + "\t elements: " + str(elements_denpendOn_trig))
        # if elements_denpendOn_trig != []: result_str += "-"
        if is_a_connector(elements_denpendOn_trig):
            print("----- recursive on: " + str(elements_denpendOn_trig))
            # result.append(get_connector(elements_denpendOn_trig))
            result_str += "-[" + get_connector(elements_denpendOn_trig) + "]"
            # if idx < len(triggers) - 1: result_str += "-"
            # result = get_connector(elements_denpendOn_trig)
        else:
            # result.append(elements_denpendOn_trig)
            synch_string = []
            for synch_list in elements_denpendOn_trig:
                synch_list_str = ""
                if len(synch_list) > 1: synch_list_str += "["
                synch_list_str += "(" + ")-(".join(synch_list) + ")"
                if len(synch_list) > 1: synch_list_str += "]"
                synch_string.append(synch_list_str)
            # synch_string = list(set(synch_string))
            if not ("-".join(synch_string) in result_str):
                result_str += "-" + "-".join(synch_string)
        idx += 1
    # print ("\n--result:\n" + str(result))
    print("\n--result_str:" + str(result_str))
    return result_str


#If the input set has no standalone element
def get_intersect(no_standalone_set):
    result = []
    if (len(no_standalone_set) > 1):
        for elm_i in no_standalone_set:
            isTrigger = True
            for elm_j in no_standalone_set:
                if elm_i != elm_j:
                    if set(elm_i).issubset(set(elm_j)) == False:
                        isTrigger = False
                        break
            # if isTrigger: result.append(elm_i)
            if isTrigger: result = elm_i

    return result


def is_a_connector(remain):
    rs = False
    # remain = removeUnion(remain)
    for i in range(len(remain)):
        for j in range(i + 1, len(remain)):
            # print("check intersect:" + str(list(set(remain[i]) & set(remain[j]))))
            if list(set(remain[i]) & set(remain[j])) != []:
                rs = True
                break
            # for elm_j in remain:
            #   print ("check intersect:" + str(set(elm_i) & set(elm_j)))
            #   if elm_i != elm_j and set(elm_i) & set(elm_j) != {}:
            #       rs = True
    return rs


def get_list_remain(remain, trigger):
    new_remain = []
    for elm in remain:
        for trig in trigger:
            is_sub_set = set(trig).issubset(set(elm))
            if is_sub_set:
                elm = [x for x in elm if x not in trig]

        if elm != [] and not (elm in new_remain):
            new_remain.append(elm)

    remain = [x for x in new_remain]
    remain = removeUnion(remain)
    return remain


# Remove the trigger element to get synchron
def removeUnion(allowedInteractions):
    if len(allowedInteractions) > 1:
        # case: [q, r, qr] should remove qr
        union = allowedInteractions[0]
        for i in range(1, len(allowedInteractions)):
            union = list(set(union + allowedInteractions[i]))
        # print ("union: " + str(union))
        pivot_set = []
        tmp_set = []
        for i in allowedInteractions:
            if set(union) == set(i):
                pivot_set = i
            else:
                tmp_set.append(i)

        # print ("pivot_set: " + str(pivot_set))
        # print ("tmp_set: " + str(tmp_set))
        # case: [r, rt] shouldn't be remove
        if len(tmp_set) > 1:
            temp_union = tmp_set[0]
            for i in range(1, len(tmp_set)):
                temp_union = list(set(temp_union + tmp_set[i]))
            if set(temp_union) == set(pivot_set):
                allowedInteractions.remove(pivot_set)
        # print ("removed union: " + str(allowedInteractions))
    return allowedInteractions

def replace_ins_by_class(connector_str):
    result = connector_str
    for subject in system_info['configuration'].keys():
        instances = system_info['configuration'][subject]
        for ins in instances:
            if ("(" + ins + "_") in result:
                result = result.replace("(" + ins + "_", "(" + subject + ".")
    print ("\n--final connector: " + result)
    return result

def replace_ins_by_class_in_sets(set_of_interactions):
    result = []
    for each_set in set_of_interactions:
        new_each_set = []
        for conjunct_set in each_set: 
            new_conjunct_set = []
            for elem in conjunct_set:
                elem = "(" + elem
                for subject in system_info['configuration'].keys():
                    instances = system_info['configuration'][subject]
                    for ins in instances:
                        if ("(" + ins + "_") in elem:
                            # print (elem)
                            elem = elem.replace("(" + ins + "_", subject + ".")
                            # print ("  --> " + elem)
                            new_conjunct_set.append(elem)
            new_each_set.append(new_conjunct_set)
        tmp_new_each_set = list(map(list, set(map(tuple, map(set, new_each_set)))))
        result.append(tmp_new_each_set)
            # print (new_conjunct_set)
    print (str(result))
    return result

# def replace_ins_by_class_1(set_of_interactions):
#     result = []
#     for set_i in set_of_interactions:
#         new_set = []
#         for interactions in set_i:
#             new_interactions = []
#             for elm_i in interactions:
#                 new_elm = "(" + elm_i
#                 # print ("elm_i: " + elm_i)
#                 for subject in system_info['configuration'].keys():
#                     instances = system_info['configuration'][subject]
#                     # print ("instances: " + str(instances))
#                     for ins in instances:
#                         # print (ins + "\t" + subject + "\t" + new_elm)
#                         if ("(" + ins + "_") in new_elm:
#                             new_elm = new_elm.replace("(" + ins + "_", subject + ".")
#                             new_interactions.append(new_elm)
#             new_set.append(new_interactions)
#         result.append(new_set)
    # print ("F:new_positive_clauses: " + str(result))
    # result = connector_str
    # for subject in system_info['configuration'].keys():
    #     instances = system_info['configuration'][subject]
    #     for ins in instances:
    #         if ("(" + ins + "_") in result:
    #             result = result.replace("(" + ins + "_", "(" + subject + ".")
    # print ("\n--final connector: " + result)
    # return result
# --------------- TEST --------------------------
rendervous = [['p', 'q', 'r']]
print("rendervous:" + str(rendervous))
get_connector(rendervous)

print("\n1.--------------")
broadcast_1 = [['p'], ['p', 'q'], ['p', 'r'], ['p', 'q', 'r']]
print("broadcast_1: " + str(broadcast_1))
get_connector(broadcast_1)

print("\n2.--------------")
broadcast_2 = [['p'], ['q'], ['p', 'q'], ['p', 'r'], ['q', 'r'],
               ['p', 'q', 'r']]
print("broadcast_2: " + str(broadcast_2))
get_connector(broadcast_2)

print("\n3.--------------")
broadcast_4 = [['p', 'q'], ['p', 'q', 'r'], ['p', 'q', 't'],
               ['p', 'q', 'r', 't']]
print("broadcast_3: " + str(broadcast_4))
get_connector(broadcast_4)

print("\n4.--------------")
broadcast_3 = [['p', 'q'], ['r'], ['p', 'q', 'r'], ['p', 'q', 'r', 't']]
print("broadcast_4: " + str(broadcast_3))
get_connector(broadcast_3)

print("\n5.--------------")
causality_chain = [['p'], ['p', 'q'], ['p', 'q', 'r']]
print("causality_chain: " + str(causality_chain))
get_connector(causality_chain)

# print("\n5.--------------")
# causality_chain_1 = [['p'], ['p', 'q'], ['p', 'q', 'r'], ['t'], ['t', 'p'],
#                      ['t', 'p', 'q'], ['p', 'q', 'r', 't'], ['p', 's'],
#                      ['p', 'q', 's'], ['p', 'q', 'r', 's'], ['t', 's'],
#                      ['p', 't', 's'], ['p', 't', 'q', 's'],
#                      ['p', 'q', 'r', 't', 's']]
# print("causality_chain_1: " + str(causality_chain_1))
# get_connector(causality_chain_1)

print("\n6.--------------")
causality_chain_2 = [['p'], ['p', 'q'], ['p', 'q', 'r'], ['p', 'q', 'r', 't']]
print("causality_chain_2: " + str(causality_chain_2))
get_connector(causality_chain_2)

print("\n6.1.--------------")
causality_chain_3 = [['p'], ['p', 'q'], ['p', 'q', 'r', 't']]
print("causality_chain_3: " + str(causality_chain_3))
get_connector(causality_chain_3)

# print("\n7.--------------")
# broadcast_5 = [['p'], ['p', 'q'], ['t'], ['t', 'p'], ['t', 'p', 'q'],
#                      ['p', 's'], ['p', 'q', 's'], ['t', 's'], ['t', 'p', 's'],
#                      ['t', 'p', 'q', 's']]
# print("broadcast_5: " + str(broadcast_5))
# get_connector(broadcast_5)

print("\n7.--------------")
atomic_broadcast = [['p'], ['p', 'q', 'r']]
print("atomic_broadcast: " + str(atomic_broadcast))
get_connector(atomic_broadcast)

# print("\n9.--------------")
# tracker_peer = [['T1.broadcast'], ['T1.broadcast', 'P.speak'], ['T2.broadcast'], ['T2.broadcast', 'P.listen', 'P1.listen'], ['T2.broadcast', 'P.listen', 'P1.listen']]
# print("tracker_peer: " + str(tracker_peer))
# get_connector(tracker_peer)

# print("\n10.--------------")
# tracker_peer_1 = [['T1.broadcast'], ['T2.broadcast'], ['T2.broadcast', 'P.listen', 'P1.listen'], ['T2.broadcast', 'P.listen', 'P1.listen']]
# print("tracker_peer: " + str(tracker_peer_1))
# get_connector(tracker_peer_1)

print("\n8.--------------")
tracker_peer = [['Tracker.broadcast'], ['Tracker.broadcast'],
                ['Tracker.broadcast', 'Peer.speak', 'Peer.listen'],
                ['Tracker.broadcast', 'Peer.listen', 'Peer.listen'],
                ['Tracker.broadcast', 'Peer.listen'],
                ['Tracker.broadcast', 'Peer.speak']]
print("tracker_peer: " + str(tracker_peer))
get_connector(tracker_peer)

print("\n9.--------------")
# tracker_peer_1 = [['Tracker.broadcast'], ['Tracker.broadcast'], ['Tracker.broadcast', 'Peer.speak', 'Peer.listen'], ['Tracker.broadcast', 'Peer.listen']]
tracker_peer_1 = [['p'], ['p'], ['p', 'r', 'q'], ['p', 'q']]
print("tracker_peer_1: " + str(tracker_peer_1))
get_connector(tracker_peer_1)

print("\n10.--------------")
tracker_peer_2 = [['Tracker.broadcast'],
                  ['Tracker.broadcast', 'Peer.listen', 'Peer.listen'],
                  ['Tracker.broadcast', 'Peer.speak']]
print("tracker_peer_2: " + str(tracker_peer_2))
get_connector(tracker_peer_2)

print("\n11.--------------")
tracker_peer_3 = [['Tracker.broadcast'],
                  ['Tracker.broadcast', 'Peer1.listen', 'Peer2.listen'],
                  ['Tracker.broadcast', 'Peer3.listen'],
                  ['Tracker.broadcast', 'Peer4.speak']]
print("tracker_peer_3: " + str(tracker_peer_3))
get_connector(tracker_peer_3)

print("\n12.--------------")
tracker_peer_4 = [['Tracker.broadcast'],
                  ['Tracker.broadcast', 'Peer1.listen', 'Peer2.listen'],
                  ['Tracker.broadcast', 'Peer2.listen', 'Peer1.listen'],
                  ['Tracker.broadcast', 'Peer3.listen']]
print("tracker_peer_4: " + str(tracker_peer_4))
get_connector(tracker_peer_4)

print("\n13.--------------")
tracker_peer_5 = [['p_speak', 'TP03speakptt_broadcast'], ['TP03speakptt_broadcast'], ['TP03listenptt_broadcast'], ['p1_listen', 'TP03listenptt_broadcast'], ['p_listen', 'TP03listenptt_broadcast']]
print("tracker_peer_5: " + str(tracker_peer_5))
tmp_connector = get_connector(tracker_peer_5)
replace_ins_by_class(tmp_connector)
print("\n14.--------------")
# positive_clauses = [[['p_listen', 'TP03listenptt_broadcast'], ['p1_listen', 'TP03listenptt_broadcast'], ['TP03listenptt_broadcast']], [['p_speak', 'TP03speakptt_broadcast'], ['TP03speakptt_broadcast'], ['p1_listen', 'TP03listenptt_broadcast'], ['TP03listenptt_broadcast']], [['p1_listen', 'TP03listenptt_broadcast'], ['TP03listenptt_broadcast']]]

positive_clauses = [[['p_register', 't_log'], ['TP012ptt_log', 'p_unregister'], ['p_unregister', 't_log']]]
# positive_clauses_1 = [[['Tracker.broadcast'], ['Tracker.broadcast', 'Peer.listen'], ['Tracker.broadcast', 'Peer.speak']], [['Tracker.broadcast'], ['Tracker.broadcast', 'Peer.listen']], [['Tracker.broadcast'], ['Tracker.broadcast', 'Peer.listen']]]




# positive_clauses = [[['TP03speakptt_broadcast'], ['p1_listen'], ['TP03speakptt_broadcast', 'p_speak'], ['TP03listenptt_broadcast']], [['TP03speakptt_broadcast'], ['p1_listen', 'TP03listenptt_broadcast'], ['TP03speakptt_broadcast', 'p_speak'], ['TP03listenptt_broadcast']], [['TP03speakptt_broadcast'], ['p1_listen'], ['p1_speak'], ['TP03listenptt_broadcast']], [['TP03speakptt_broadcast'], ['p1_listen', 'TP03listenptt_broadcast'], ['p1_speak'], ['TP03listenptt_broadcast']], [['p1_listen'], ['p_listen', 'TP03listenptt_broadcast'], ['TP03speakptt_broadcast'], ['TP03listenptt_broadcast']], [['p1_listen', 'TP03listenptt_broadcast'], ['p_listen'], ['TP03speakptt_broadcast'], ['TP03listenptt_broadcast']], [['TP03listenptt_broadcast'], ['p1_speak'], ['p1_listen'], ['p_listen', 'TP03listenptt_broadcast'], ['TP03speakptt_broadcast']], [['TP03listenptt_broadcast'], ['p1_speak'], ['p1_listen', 'TP03listenptt_broadcast'], ['p_listen'], ['TP03speakptt_broadcast']]]
list_connectors = []
for positive_clause_i in positive_clauses:
    tmp_connector_i = get_connector(positive_clause_i)
    # print (tmp_connector_i)
    list_connectors.append(replace_ins_by_class(tmp_connector_i))

# print ("\nrename set_of_interactions:\n")
# replace_ins_by_class_in_sets(positive_clauses)
print ("\n\nlist_connectors: ")
for connector in list_connectors:
    print (connector)
    # trigger_list = re.findall(r'\([^\-]*\)\`', connector)
    # print (trigger_list)
    # print (list(set(trigger_list)))

# list_connectors_1 = []
# for positive_clause_i in positive_clauses_1:
#     tmp_connector_i = get_connector(positive_clause_i)
#     # print (tmp_connector_i)
#     list_connectors_1.append(tmp_connector_i)
# print ("\n\nlist_connectors_1: ")
# for connector in list_connectors_1:
#     print (connector)




# new_positive_clauses = replace_ins_by_class_1(positive_clauses)
# print ("new_positive_clauses: " + str(new_positive_clauses))

# new_list_connectors = []
# for positive_clause_i in new_positive_clauses:
#     tmp_connector_i = get_connector(positive_clause_i)
#     new_list_connectors.append(tmp_connector_i)

# print ("\n\nnew_list_connectors: ")
# for connector in new_list_connectors:
#     print (connector)
# positive_clause_0 = [['TP03speakptt_broadcast'], ['p_speak', 'TP03speakptt_broadcast'], ['TP03listenptt_broadcast']]
# positive_clause_1 = [['TP03speakptt_broadcast'], ['p_speak', 'TP03speakptt_broadcast'], ['p1_listen', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast'], ['TP03listenptt_broadcast']]
# positive_clause_2 = [['TP03speakptt_broadcast'], ['TP03listenptt_broadcast']]
# positive_clause_3 = [['TP03speakptt_broadcast'], ['p1_listen', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast'], ['TP03listenptt_broadcast']]
# positive_clause_4 = [['TP03speakptt_broadcast'], ['p_listen', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast'], ['TP03listenptt_broadcast']]
# positive_clause_5 = [['TP03speakptt_broadcast'], ['p1_listen', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast'], ['TP03listenptt_broadcast']]
# positive_clause_6 = [['TP03speakptt_broadcast'], ['p_listen', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast'], ['TP03listenptt_broadcast']]
# positive_clause_7 = [['TP03speakptt_broadcast'], ['p1_listen', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast', 'TP03listenptt_broadcast'], ['TP03listenptt_broadcast']]

# tmp_connector_0 = get_connector(positive_clause_0)
# replace_ins_by_class(tmp_connector_0)

# tmp_connector_1 = get_connector(positive_clause_1)
# replace_ins_by_class(tmp_connector_1)

# tmp_connector_2 = get_connector(positive_clause_2)
# replace_ins_by_class(tmp_connector_2)

# tmp_connector_3 = get_connector(positive_clause_3)
# replace_ins_by_class(tmp_connector_3)

# tmp_connector_4 = get_connector(positive_clause_4)
# replace_ins_by_class(tmp_connector_4)

# tmp_connector_5 = get_connector(positive_clause_5)
# replace_ins_by_class(tmp_connector_5)

# tmp_connector_6 = get_connector(positive_clause_6)
# replace_ins_by_class(tmp_connector_6)

# tmp_connector_7 = get_connector(positive_clause_7)
# replace_ins_by_class(tmp_connector_7)
# tracker_peer_2 = [['Tracker.broadcast'], ['Tracker.broadcast'], ['Tracker.broadcast', 'Peer.listen', 'Peer.listen'], ['Tracker.broadcast', 'Peer.speak', 'Peer.listen']]
# print("tracker_peer_2: " + str(tracker_peer_2))
# get_connector(tracker_peer_2)

# print("\n10.--------------")
# two_triggers = [['p'], ['p', 'q'], ['p', 'q', 'r'], ['p', 'r']]
# print("two_triggers: " + str(two_triggers))
# get_connector(two_triggers)
# (t_broadcast)`-[(TP03listen1tp_listen)-(p1_listen)]-(TP03listentp_listen)-(TP03speaktp_speak)
# print ("Configuration: " + str(list(system_info['configuration'])))
# test_str = "(t_broadcast)`-[(TP03listen1tp_listen)-(p1_listen)]-(TP03listentp_listen)-(TP03speaktp_speak)"
# print ("before test: " + test_str)


