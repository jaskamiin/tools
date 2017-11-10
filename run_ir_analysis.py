from analyze import *
import sys

table = genDefUse(sys.argv[1])
table = genInOut(table)
pvars =  getProgVars(table)

print_Table(table)
