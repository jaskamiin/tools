from analyze import *
import sys

table = genDefUse(sys.argv[1])
table = genInOut(table)
print_Table(table)
