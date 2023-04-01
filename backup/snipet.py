# Online Python compiler (interpreter) to run Python online.
# Write Python 3 code in this online editor and run it.
print("Hello world")
effects = ['p1_is_registered_to_TP02speakptt', 'p1_is_different_with_p', '~p1_speak']
cause_list = ['p_is_registered_to_TP02speakptt ', 'TP02speakptt_broadcast ', 'p_speak']

# for effect_elm in effects:
#     for cause_elm in cause_list:
#         ef_elm_action = effect_elm[effect_elm.find("_")+1:]
#         cause_elm_action = cause_elm[cause_elm.find("_")+1:]
#         if "~" in effect_elm and ef_elm_action == cause_elm_action:
#             print("swap: " + effect_elm + "\t" + cause_elm)

# for i in range(len(effects)):
#     for j in range(len(cause_list)):
#         ef_elm_action = effects[i][effects[i].find("_")+1:]
#         cause_elm_action = cause_list[j][cause_list[j].find("_")+1:]
#         if "~" in effects[i] and ef_elm_action == cause_elm_action:
#             print("swap: " + effects[i] + "\t" + cause_list[j])
#             effects[i] , cause_list[j] = cause_list[j], effects[i]

# print ("effects: " + str(effects))
# print ("cause_list: " + str(cause_list))

def swapTwoElemsFromTwoList(effects, cause_list):
    # checked = False
    for i in range(len(effects)):
        for j in range(len(cause_list)):
            ef_elm_action = effects[i][effects[i].find("_")+1:]
            cause_elm_action = cause_list[j][cause_list[j].find("_")+1:]
            if "~" in effects[i] and ef_elm_action == cause_elm_action:
                # checked = True
                print("swap: " + effects[i] + "\t" + cause_list[j])
                return [i,j]
                # effects[i] , cause_list[j] = cause_list[j], effects[i]
    # return True
    return []
            
print ("effects: " + str(effects))
print ("cause_list: " + str(cause_list))
swapped = swapTwoElemsFromTwoList(effects, cause_list)
if swapTwoElemsFromTwoList(effects,cause_list) != []:
    effects[swapped[0]] , cause_list[swapped[1]] = cause_list[swapped[1]], effects[swapped[0]]
print ("effects: " + str(effects))
print ("cause_list: " + str(cause_list))
if swapTwoElemsFromTwoList(cause_list,effects) != []:
    effects[swapped[0]] , cause_list[swapped[1]] = cause_list[swapped[1]], effects[swapped[0]]
print ("effects: " + str(effects))
print ("cause_list: " + str(cause_list))