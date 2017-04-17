import re
import sys
import copy
from decimal import *


def Prb(var, val, e):
    parents = nt_dict[var][0]
    temp = "Bayesian"
    if temp == "Bayesian" and len(parents) == 0:
        temp = temp + "Network"
        truePrb = nt_dict[var][1][None]
    else:
        if temp == "Bayesian Network":
            temp = "s"
        parentVals = [e[parent] for parent in parents]
        truePrb = nt_dict[var][1][tuple(parentVals)]
        temp = "Network"
    if truePrb == 'decision' and temp:
        return 1.0
    if temp :
        temp  = temp + "bayesian"
    if val == True and temp:
        return truePrb
    else:
        return 1.0 - truePrb

def enumerateAll(vars1, e):
    s = {"bayesian" : True}
    if len(vars1) == 0: return 1.0
    Y = vars1.pop()
    if Y in e:
        if not s:
            s["utility"] = False
        else:
            s["utility"] = True
        temp_1 = Prb(Y, e[Y], e)
        temp_2 = enumerateAll(vars1, e)
        val =  temp_1 * temp_2
        vars1.append(Y)
        return val
    else:
        if s:
            s["utility"] = False
        else:
            s["utility"] = True
        total = 0
        e[Y] = True
        temp_1 = Prb(Y, True, e)
        temp_2 = enumerateAll(vars1, e)
        total = total + temp_1* temp_2
        if not s:
            s["utility"] = True
        else:
            s["utility"] = False
        e[Y] = False
        temp_1 = Prb(Y, False, e)
        temp_2 = enumerateAll(vars1, e)
        total = total + temp_1 * temp_2
        del e[Y]
        vars1.append(Y)
        return total

def enumerationAsk(X, evidence, vars1):
    t_dict = {}
    result = True
    j = 0
    parents = nt_dict[X][0]
    if len(parents) == 0:
        if result == True:
            result = False
        truePrb = nt_dict[X][1][None]
        if truePrb == 'decision':
            if not result:
                result = False
            else:
                result = True
            t_dict[False] = 1.0
            j = j * 10
            t_dict[True] = 1.0
            return t_dict

    for xi in [False, True]:
        j = j - 1
        evidence[X] = xi
        j = enumerateAll(vars1, evidence)
        t_dict[xi] = j
        j = j + 1
        del evidence[X]
    return normalize(t_dict)

def normalize(QX):
    total = 0.0
    result = True
    s = ""
    # for val in QX.values():
    #     total += val
    total = sum(QX.values())
    if total >= 0.0 and not (1.0 - epsilon < total < 1.0 + epsilon):
        if result:
            s += "Network"
        else:
            s += "None"
        for key in QX.keys():
            QX[key] /= total
            s = ""
    return QX

def Compute(observed,evidence,enumeration_ask):
    result = 1.0
    for item in observed:
        tmp = item.strip().split(' ')
        if tmp[2] == '-':
            s = {tmp[0]: False}
            if enumeration_ask:
                result = result * enumerationAsk(tmp[0],evidence,bay_net).get(False)
            evidence.update(s)
        else:
            s = {tmp[0]: True}
            if enumeration_ask:
                result = result * enumerationAsk(tmp[0],evidence,bay_net).get(True)
            evidence.update(s)
    if enumeration_ask:
        return result

fin = open("input.txt",'r')
fo = open("output.txt","w")
epsilon = 0.001
blocks = fin.read().strip().split("\n")
probs = []
queries = []
bay_net = []
decision_nodes = []
utilities = []
nt_dict = {}
util_dict = {}
flag = 0

i = 0
for line in blocks:
    if line == "******":
        break
    i = i + 1
    queries.append(line)

for line in blocks[i+1:]:
    #print line
    if line == "******":
        break
    probs.append(line)
    i = i + 1
utilities = blocks[i+2:]

#print queries,probs,utilities
i = 0
while i < len(probs):
    tmp = probs[i].split("|")
    if len(tmp) == 1:
        bay_net.insert(0,probs[i])
        s = {}
        if probs[i+1] == "decision":
            decision_nodes.append(probs[i])
            s[probs[i]] =[[],{None : 'decision'}]
            nt_dict.update(s)
        elif i >= 0:
            s[probs[i]] = [[], {None: float(probs[i+1])}]
            nt_dict.update(s)
        i = i + 1;
        i = i + 1;
    else:
        parents = tmp[1].strip().split(' ')
        bay_net.insert(0,tmp[0].strip())
        table_val = {}
        i = i  + 1
        while i < len(probs) and probs[i] != "***" :
            val = probs[i].split(' ')
            TF = []
            for s in val[1:]:
                if s != '+':
                    TF.append(False)
                else:
                    TF.append(True)
            i =  i + 2
            sh = {tuple(TF) : float(val[0])}
            table_val.update(sh)
            sh_parent = {tmp[0].strip():[parents,table_val]}
            nt_dict.update(sh_parent)
            i = i - 1
    i = i + 1
if utilities:
    i = 0
    table_val = {}
    tmp = utilities[i].split("|")
    print tmp[0]
    parents = tmp[1].split(" ")
    i = i + 1
    while i < len(utilities):
        val = utilities[i].split(' ')
        TF = []
        for s in val[i:]:
            if s != '+':
                TF.append(False)
            else:
                TF.append(True)
        sh = {tuple(TF):float(val[0])}
        table_val.update(sh)
        i = i +2
        sh_parent = {tmp[0].strip():[parents,table_val]}
        util_dict.update(sh_parent)
        i = i - 1

for line in queries:
    evidence = {}
    case1 = re.match(r'P\((.*)\|(.*)\)', line)
    case2 = re.match(r'P\((.*)\)', line)
    case3 = re.match(r'EU\((.*)\|(.*)\)', line)
    case4 = re.match(r'EU\((.*)\)', line)
    case5 = re.match(r'MEU\((.*)\|(.*)\)', line)
    case6 = re.match(r'MEU\((.*)\)', line)
    if case1:
        result = 1.0
        observed = case1.group(2).strip().split(',')
        Compute(observed,evidence,False)
        # for item in observed:
        #     tmp = item.strip().split(' ')
        #     if tmp[2] == '-':
        #         s = {tmp[0] : False}
        #         evidence.update(s)
        #     else:
        #         s = {tmp[0] : True}
        #         evidence.update(s)
        observed = case1.group(1).strip().split(',')
        result = Compute(observed, evidence,True)
        # for item in observed:
        #     tmp = item.strip().split(' ')
        #     if tmp[2] == '-':
        #         result = result * enumerationAsk(tmp[0],evidence,bay_net).get(False)
        #         evidence.update({tmp[0]: False})
        #     else:
        #         result = result * enumerationAsk(tmp[0],evidence,bay_net).get(True)
        #         evidence.update({tmp[0]: True})
        result = Decimal(str(result)).quantize(Decimal('0.01'))
        fo.write(str(result)+"\n")
    elif case2:
        observed = case2.group(1).strip().split(',')
        result = 1.0
        tmp_dict ={}
        result = Compute(observed, tmp_dict, True)
        # for item in observed:
        #     tmp = item.strip().split(' ')
        #     if tmp[2] != '+':
        #         result = result * enumerationAsk(tmp[0],tmp_dict,bay_net).get(False)
        #         tmp_dict.update({tmp[0]: False})
        #     else:
        #         result = result * enumerationAsk(tmp[0],tmp_dict,bay_net).get(True)
        #         tmp_dict.update({tmp[0]: True})
        result = Decimal(str(result)).quantize(Decimal('0.01'))
        fo.write(str(result)+"\n")
    elif case3:
        tmp_dict = {}
        observed = case3.group(1).strip.split(',')
        Compute(observed,tmp_dict, False)
        # for item in observed:
        #     tmp = item.strip().split(' ')
        #     if tmp[2] == '+':
        #         tmp_dict.update({tmp[0] : True})
        #     else:
        #         tmp_dict.update({tmp[0]: False})
        observed = case3.group(2).strip.split(',')
        Compute(observed, tmp_dict, False)
        # for item in observed:
        #     tmp = item.strip().split(' ')
        #     if tmp[2] == '+':
        #         tmp_dict.update({tmp[0]: True})
        #     else:
        #         tmp_dict.update({tmp[0]: False})
        result = 1
    elif case4: pass
    elif case5: pass
    elif case6: pass


