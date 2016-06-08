from gurobipy import *
from xlrd import open_workbook
import pandas
import re
import ast

## change evenings and courses from 0-indexed to starting at 1 to comply w/ data

# import course info
refWB = open_workbook("reference.xlsx")
refWS = refWB.sheet_by_index(0)

# number of courses needing prelims
nCourses = refWS.nrows-1

# Enrollment total for each course
E = [int(refWS.row_values(i)[2]) for i in range(1,refWS.nrows) if refWS.row_values(i)[2]]
# number of Prelims given in each course
nPrelims = [int(refWS.row_values(i)[3]) for i in range(1,refWS.nrows) if refWS.row_values(i)[3]]
# set building
S= [i+1 for i in xrange(len(nPrelims)) if nPrelims[i] == 1]
P= [i+1 for i in xrange(len(nPrelims)) if nPrelims[i] == 2]
T= [i+1 for i in xrange(len(nPrelims)) if nPrelims[i] == 3]

# import student overlap matrix
O = pandas.read_excel("overlap.xlsx").values

# number of available evenings
nEvenings = 21

f = open('fallPatterns.txt')

configs = dict()
numLines = 0
for line in f:
    courseIndex = line.split()[0]
    courseIndex = int(courseIndex)
    patterns= re.split('[0-9]+\t[0-9]+\t', line)[1].split()

    patternDict= dict()
    for p in xrange(len(patterns)):
        patternDict[p]= ast.literal_eval(patterns[p])
        
    configs[courseIndex]= patternDict

f.close()
        
sConfigsByEvening = {e:{i:[k for k in configs[i].keys() if e == configs[i][k]] for i in S} for e in xrange(1,nEvenings+1)}
pConfigsByEvening = {e:{i:[k for k in configs[i].keys() if e in configs[i][k]] for i in P} for e in xrange(1,nEvenings+1)}
tConfigsByEvening = {e:{i:[k for k in configs[i].keys() if e in configs[i][k]] for i in T} for e in xrange(1,nEvenings+1)}

configsByEvening = dict()
for e in xrange(1,nEvenings+1):
    eveningDict = dict(sConfigsByEvening[e].items() + pConfigsByEvening[e].items() + tConfigsByEvening[e].items())
    configsByEvening[e] = eveningDict




#########################################################
################### Build Model #########################

# create model
m = Model("EveningPrelims")

# create decision variables
x = []
for i in range(nCourses):
	x.append([])
	x[i] = []
	for k in range(len(configs[i+1].keys())):
		x[i].append([])
		x[i][k] = []

y = []
for i in range(nCourses):
	y.append([])
	y[i] = []
	for j in range(nCourses):
		y[i].append([])
		y[i][j] = []
		for e in range(nEvenings):
			y[i][j].append([])
			y[i][j][e] = []

# add decision variables to the model 
for i in range(nCourses):
	for k in range(len(configs[i+1].keys())):
		x[i][k] = m.addVar(vtype = GRB.BINARY, name = "x.{}.{}".format(i+1,k+1))

for i in range(nCourses):
	for j in range(nCourses):
		for e in range(nEvenings):
				y[i][j][e] = m.addVar(vtype = GRB.BINARY, name = "y.{}.{}.{}".format(i+1,j+1,e+1))



# update model to include new variables
m.update()

# add objective function
m.setObjective(quicksum(O[i,j]*y[i][j][e] for i in range(nCourses-1) for j in range(i+1,nCourses) for e in range(nEvenings)), GRB.MINIMIZE)

# Constraint 1
for i in range(nCourses):
	m.addConstr(quicksum(x[i][k] for k in configs[i+1].keys()) == 1, "Constraint 1.{}".format(i+1))

# Constraint 2
nightlyCapacity = 4000
for e in range(1,nEvenings+1):
    m.addConstr(quicksum(E[i-1]*x[i-1][k] for i in configsByEvening[e].keys() for k in configsByEvening[e][i]) <= nightlyCapacity,"Constraint 2.{}".format(e))


m.optimize()

