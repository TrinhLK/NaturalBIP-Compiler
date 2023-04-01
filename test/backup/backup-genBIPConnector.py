import json

system_info = {}
with open('system_infor.json', 'r') as fp:
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
    triggers = list(map(list, set(map(tuple, map(set, triggers)))))
    print("triggers: " + str(triggers))
    print("remains: " + str(remains))

    if triggers == []:
        # result_str += "("
        for synch_set in remains:
            result_str += "(" + ")-(".join(synch_set) + ")\n"
        # result_str += "\n"
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
    remains_check_independence = []
    remains_independence = []
    for elm in remains:
      remains_check_independence.append(True)
    for trig in triggers:
        elements_denpendOn_trig = []
        for i in range(len(remains)):
          is_sub_set = set(trig).issubset(set(remains[i]))
          if is_sub_set:
            elements_denpendOn_trig.append(remains[i])
            remains_check_independence[i] = False
        # for elm in remains:
        #     is_sub_set = set(trig).issubset(set(elm))
        #     if is_sub_set:
        #         elements_denpendOn_trig.append(elm)
        elements_denpendOn_trig = get_list_remain(elements_denpendOn_trig,triggers)
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
    print("\n-- normal_result_str: (each line is an independent connector)\n" + str(result_str))
    for i in range(len(remains_check_independence)):
      if remains_check_independence[i] == True:
        remains_independence.append(remains[i])
    print("\n-- remains_independence:" + str(remains_independence))
    if remains_independence != [] and triggers != []:
      result_str = "[" + result_str + "]`"
      for independent_elm in remains_independence:
        result_str += "-[(" + ")-(".join(independent_elm) + ")]`"
    print("\n-- final_result_str:\n" + str(result_str))
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
    print("\n--final connector: " + result)
    return result


# --------------- TEST --------------------------
rendervous = [['m'], ['m', 'p', 'q', 'r'], ['m', 'x', 'y']]
print("rendervous:" + str(rendervous))
get_connector(rendervous)
print("-----------------------")

rendervous_1 = [['p', 'q'], ['p', 'q', 'r'], ['p', 'q', 't']]
print("rendervous-1:" + str(rendervous_1))
get_connector(rendervous_1)
print("-----------------------")

rendervous_2 = [['a', 'b'], ['b', 'c'], ['c']]
print("rendervous_2:" + str(rendervous_2))
get_connector(rendervous_2)
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
list_ = [["A"], ["B"], ["A","B"], ["B","A"], ["A","B","C"], ["B", "A", "C"]]
list_ = list(map(list, set(map(tuple, map(set, list_)))))
print (list_)

print("\n14.--------------")
tracker_peer_14 = [
                  ['p', 'q'],
                  ['r', 't']]
print("tracker_peer_14: " + str(tracker_peer_14))
get_connector(tracker_peer_14)

print("\n15.--------------")
tracker_peer_14 = [
                  ['p'],
                  ['r']]
print("tracker_peer_15: " + str(tracker_peer_14))
get_connector(tracker_peer_14)

# tracker_peer_5 = [[['TP03speakptt_broadcast'], ['TP03listenptt_broadcast'],
#                    ['p1_listen'], ['TP03speakptt_broadcast', 'p_speak']],
#                   [['TP03speakptt_broadcast'], ['TP03listenptt_broadcast'],
#                    ['p_listen', 'TP03listenptt_broadcast', 'p1_listen'],
#                    ['TP03speakptt_broadcast', 'p_speak']],
#                   [['TP03listenptt_broadcast'], ['p1_listen'],
#                    ['TP03speakptt_broadcast']],
#                   [['TP03listenptt_broadcast'],
#                    ['p_listen', 'TP03listenptt_broadcast', 'p1_listen'],
#                    ['TP03speakptt_broadcast']],
#                   [['TP03listenptt_broadcast'],
#                    ['TP03listenptt_broadcast', 'p_listen', 'p1_listen'],
#                    ['TP03speakptt_broadcast'], ['p1_listen']],
#                   [['TP03listenptt_broadcast'], ['p_listen'],
#                    ['TP03speakptt_broadcast'],
#                    ['p_listen', 'TP03listenptt_broadcast', 'p1_listen']]]
# print("tracker_peer_5: " + str(tracker_peer_5))
# tmp_connector = get_connector(tracker_peer_5)
# replace_ins_by_class(tmp_connector)
# print("\n13.--------------")
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
