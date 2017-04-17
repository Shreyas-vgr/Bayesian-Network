import re
import sys
import copy
from decimal import *

def normalize(QX):
    tot = 0.0
    for val in QX.values():
        tot += val
    if not (1.0 - epsilon < tot < 1.0 + epsilon):
        for key in QX.keys():
            QX[key] /= tot
    return QX
def Prb(var, val, e):
    parents = prob_dict[var][0]
    if len(parents) == 0:
        truePrb = prob_dict[var][1][None]
    else:
        parentVals = [e[parent] for parent in parents]
        truePrb = prob_dict[var][1][tuple(parentVals)]
    if truePrb == 'decision':
        return 1.0
    if val == True:
        return truePrb
    else:
        return 1.0 - truePrb
def enumerationAsk(X, e, vars1):
    QX = {}
    parents = prob_dict[X][0]
    if len(parents) == 0:
        truePrb = prob_dict[X][1][None]
        if truePrb == 'decision':
            QX[False] = 1.0
            QX[True] = 1.0
            return QX

    for xi in [False, True]:
        e[X] = xi
        QX[xi] = enumerateAll(vars1, e)
        del e[X]
    return normalize(QX)
def enumerateAll(vars1, e):
    if len(vars1) == 0: return 1.0
    Y = vars1.pop()
    if Y in e:
        val = Prb(Y, e[Y], e) * enumerateAll(vars1, e)
        vars1.append(Y)
        return val
    else:
        total = 0
        e[Y] = True
        total += Prb(Y, True, e) * enumerateAll(vars1, e)
        e[Y] = False
        total += Prb(Y, False, e) * enumerateAll(vars1, e)
        del e[Y]
        vars1.append(Y)
        return total

def Compute(observed,evidence,enumeration_ask):
    for item in observed:
        tmp = item.strip().split(',')
        if tmp[2] == '-':
            s = {tmp[0]: False}
            evidence.update(s)
            if enumeration_ask:
                return enumerationAsk().get(False)
        else:
            s = {tmp[0]: True}
            evidence.update(s)
            if enumeration_ask:
                return enumerationAsk().get(True)


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
        bay_net.append(probs[i])
        if probs[i+1] == "decision":
            decision_nodes.append(probs[i])
            nt_dict.update({probs[i]:[[],{None : 'decision'}]})
        else:
            nt_dict.update({probs[i]:[[],{None : float(probs[i+1])}]})
        i = i + 1;
        i = i + 1;
    else:
        parents = tmp[1].strip().split(' ')
        bay_net.append(tmp[0].strip())
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
            table_val.update({tuple(TF): float(val[0])})
            nt_dict.update({tmp[0].strip():[parents,table_val]})
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
        table_val.update({tuple(TF):float(val[0])})
        util_dict.update({tmp[0].strip():[parents,table_val]})
        i = i + 2
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
        result = 1
        observed = match.group(1).strip().split(',')
        Compute(observed,evidence,False)
        # for item in observed:
        #     tmp = item.strip().split(',')
        #     if tmp[2] == '-':
        #         s = {tmp[0] : False}
        #         evidence.update(s)
        #     else:
        #         s = {tmp[0] : True}
        #         evidence.update(s)
        observed = match.group(2).strip().split(',')
        result = Compute(observed, evidence,True)
        # for item in observed:
        #     tmp = item.strip().split(',')
        #     if tmp[2] == '-':
        #         result = result * enumerationAsk().get(False)
        #         evidence.update({tmp[0]: False})
        #     else:
        #         result = result * enumerationAsk().get(True)
        #         evidence.update({tmp[0]: True})
        result = result.quantize(Decimal('0.1'))
        fo.write(str(result))
    elif case2:
        observed = case2.group(1).strip().split(',')
        result = 1
        tmp_dict ={}
        result = Compute(observed, tmp_dict, True)
        # for item in observed:
        #     tmp = item.strip().split(',')
        #     if tmp[2] != '+':
        #         result = result * enumerationAsk().get(False)
        #         tmp_dict.update({tmp[0]: False})
        #     else:
        #         result = result * enumerationAsk().get(True)
        #         tmp_dict.update({tmp[0]: True})
        result = result.quantize(Decimal('0.1'))
        fo.write(str(result))
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
    elif case4:
    elif case5:
    elif case6:


