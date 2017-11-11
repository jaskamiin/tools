from copy import deepcopy

def spawnTable(fn):
    with open(fn, 'r') as f:
        stmts = [[t.strip() for t in l.split(',')] for l in f.readlines()]
    table = {
        'I{}'.format(i+1):{
            'statement':stmts[i],
            'def':[],
            'use':[],
            'in':[],
            'out':[],
            'pred':[],
            'succ':[]
        } for i in range(len(stmts))
    }
    return (table,stmts)

def isnumber(s):
    if s.find('-') == 0:
        s = s[1:]
    d = s.find('.')
    if d > -1:
        s = s[:d]+s[d+1:]
    return s.isdigit()

def islabel(s):
    return len(s) == 1 and len(s[0]) and s[0][-1] == ':'

def genDefUse(fn):
    #Load IR code file and build empty table:
    table,stmts = spawnTable(fn)

    #Load def and use columns:
    pa_arith = ['add','sub','mult','div']
    branches = ['breq','brneq','brgt','brgeq','brlt','brleq','goto']

    for i in range(len(stmts)):
        instr='I{}'.format(i+1)
        s = stmts[i]
        op = s[0]
        if islabel(s):
            continue
        if op == 'assign':
            table[instr]['def'].append(s[1])
            if not isnumber(s[2]):
                table[instr]['use'].append(s[2])
        if op in pa_arith:
            table[instr]['def'].append(s[-1])
            for a in [s[1],s[2]]:
                if not isnumber(a):
                    table[instr]['use'].append(a)
        if op in branches:
            labelidx = 1 if op == 'goto' else -1
            table[instr]['jumps'] = {}
            table[instr]['jumps']['pb'] = 'I{}'.format(stmts.index([s[labelidx]+':'])+2)
            if op != 'goto':
                for a in [s[1],s[2]]:
                    if not isnumber(a):
                        table[instr]['use'].append(a)
                for j in range(i+1, len(stmts)):
                    s2 = stmts[j]
                    if len(s2) > 1 and len(s2[0]) and s2[0][-1] != ':':
                        table[instr]['jumps']['ft'] = 'I{}'.format(j+1)
                        break

        table[instr]['use']=list(set(table[instr]['use']))
        table[instr]['def']=list(set(table[instr]['def']))

        #create succ[I]
        if i+2 <= len(stmts) and op != 'goto':
            j = 2
            while islabel(table['I{}'.format(i+j)]['statement']):
                j += 1
            table[instr]['succ'].append('I{}'.format(i+j))
        if 'jumps' in table[instr].keys():
            v=table[instr]['jumps'].values()
            table[instr]['succ'].extend(v)
        #create pred[I] by reversing succ[I]
        for p in table[instr]['succ']:
            table[p]['pred'].append(instr)
        #make sure values in pred/succ only appear once
        table[instr]['succ']=list(set(table[instr]['succ']))
        table[instr]['pred']=list(set(table[instr]['pred']))
    return table


def genOut(table,instr):
    I = table[instr]
    out = deepcopy(I['out'])
    for s in I['succ']:
        succ = table[s]
        for sp in succ['in']:
            out.append(sp)
    return list(set(out))
    
def genIn(table,instr):
    I = table[instr]
    _in = deepcopy(I['in'])
    _def = set(I['def'])
    _use = set(I['use'])
    _out = set(I['out'])
    _in.extend(list(_use | (_out - _def)))
    return _in
    
def genInOut(table):
    order = list(reversed(['I{}'.format(i+1) for i in range(len(table))]))
    change = True
    for X in range(200):
        table_state = table.copy()
        for ld in sorted(table.items(),key=lambda i:order.index(i[0])):
            instr = ld[0]
            table[instr]['out'] = genOut(table,instr)
            table[instr]['in'] = genIn(table,instr)
            table[instr]['out'] = list(set(table[instr]['out']))
            table[instr]['in'] = list(set(table[instr]['in']))
        if table_state == table:
            change = False
    return table

	
def getProgVars(table):
    _vars = []
    order = ['I{}'.format(i+1) for i in range(len(table))]
    for ld in sorted(table.items(),key=lambda i:order.index(i[0])):
        _vars.extend(ld[1]['def'])
    _vars=list(set(_vars))
    return _vars


def getLiveRanges(table):
    _vars = getProgVars(table)

    

# print table
def print_Table(table,stmt=True):
    pstr = '{: <10}{: <30}{: <10}{: <10}{: <20}{: <20}{: <15}{: <15}'
    prows=['','Statement' if stmt else '' ,'Def','Use','In','Out','pred','succ' ]
    print pstr.format(*prows)
    print '-' * 120
    order = ['I{}'.format(i+1) for i in range(len(table))]
    for ld in sorted(table.items(),key=lambda i:order.index(i[0])):
        _stm='{}'.format(', '.join(ld[1]['statement']))
        _def='({})'.format(','.join(ld[1]['def']))
        _use='({})'.format(','.join(ld[1]['use']))
        _in ='({})'.format(','.join(ld[1]['in']))
        _out='({})'.format(','.join(ld[1]['out']))
        _prd='({})'.format(','.join(ld[1]['pred']))
        _suc='({})'.format(','.join(ld[1]['succ']))
        prows = [ld[0],_stm if stmt else '',_def,_use,_in,_out,_prd,_suc]
        print pstr.format(*prows)

	
