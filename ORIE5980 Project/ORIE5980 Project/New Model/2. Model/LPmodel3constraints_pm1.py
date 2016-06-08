from gurobipy import *
from xlrd import open_workbook
import pandas
import re
import ast
import math

## change evenings and courses from 0-indexed to starting at 1 to comply w/ data

# import course info
refWB = open_workbook("referenceSpring.xlsx")
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
O = pandas.read_excel("overlapSpring.xlsx").values

# number of available evenings
nEvenings = 21


def pm(pattern,window):

    if len(pattern)==1:
        patternOp = range(pattern[0]-window, pattern[0]+window+1)
    elif len(pattern)==2:
        pool = [range(pattern[i]-window, pattern[i]+window+1) for i in xrange(len(pattern))]
        patternOp = [(a,b) for a,b in zip(pool[0],pool[1])]
        patternOp = [(a,b) for (a,b) in patternOp if a and b in range(1,nEvenings+1)]
    else:
        pool = [range(pattern[i]-window, pattern[i]+window+1) for i in xrange(len(pattern))]
        patternOp = [(a,b,c) for a,b,c in zip(pool[0],pool[1],pool[2])]
        patternOp = [(a,b,c) for (a,b,c) in patternOp if a and b and c in range(1,nEvenings+1)]

    patternDict= dict()
    for p in xrange(len(patternOp)):
        patternDict[p]= patternOp[p]
        
    return patternDict

f = open('input2015Spring.txt')

configs = dict()
for line in f:
    courseIndex = int(line.split()[0])
    prelimsConfig = int(line.split()[1])
    pattern = []
    for i in xrange(len(line.split())-2):
        pattern.append(int(line.split()[i+2]))
    configs[courseIndex]= pm(pattern,1)

f.close()


sConfigsByEvening = {e:{i:[k for k in configs[i].keys() if e == configs[i][k]] for i in S} for e in xrange(1,nEvenings+1)}
pConfigsByEvening = {e:{i:[k for k in configs[i].keys() if e in configs[i][k]] for i in P} for e in xrange(1,nEvenings+1)}
tConfigsByEvening = {e:{i:[k for k in configs[i].keys() if e in configs[i][k]] for i in T} for e in xrange(1,nEvenings+1)}

configsByEvening = dict()
for e in xrange(1,nEvenings+1):
    eveningDict = dict(sConfigsByEvening[e].items() + pConfigsByEvening[e].items() + tConfigsByEvening[e].items())
    configsByEvening[e] = eveningDict

	
coursesByEvening = {e:[i for i in configsByEvening[e].keys() if len(configsByEvening[e][i]) > 0] for e in range(1,nEvenings+1)}


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
		x[i][k] = m.addVar(vtype = GRB.BINARY, name = "x.{}.{}".format(i+1,k))

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

# Constraint 3
for e in xrange(1,nEvenings+1):
    coursesWithConfigOnThisEvening = coursesByEvening[e]
    n = len(coursesWithConfigOnThisEvening)
    for i in xrange(n-1):
        c1 = coursesWithConfigOnThisEvening[i]
        for j in xrange(i+1,n):
            c2 = coursesWithConfigOnThisEvening[j]
            for k1 in configsByEvening[e][c1]:
                for k2 in configsByEvening[e][c2]:
                	m.addConstr(quicksum([x[c1-1][k1], x[c2-1][k2], -1*y[c1-1][c2-1][e-1]]) <= 1, "Constraint 3.{}.{}.{}.{}.{}".format(e,c1+1,k1+1,c2+1,k2+1))

m.optimize()


#### for output
solutionList = []
for var in m.getVars():
	if var.X == 1 and var.VarName[0] == 'x':
		solutionList.append(var)

for var in solutionList:
	print var.VarName
			
schedule = {i:[] for i in xrange(1,nEvenings+1)}
for var in solutionList:
	courseIndex = int(var.VarName.split(".")[1])
	chosenConfigNumber = int(var.VarName.rsplit(".",1)[1])
	chosenConfig= configs[courseIndex][chosenConfigNumber]
	tupleOrNah = isinstance(chosenConfig, tuple)   # true => tuple
	if tupleOrNah:
		for e in chosenConfig:
			schedule[e].append(courseIndex)
	else:
		schedule[e].append(courseIndex)


conflictsPerCourse = {i:0 for i in configs.keys()}
for evening in schedule.keys():
	print evening, ": ", schedule[evening]
	n = len(schedule[evening])
	for i in xrange(n-1):
		c1 = schedule[evening][i]
		for j in xrange(i+1,n):
			c2 = schedule[evening][j]
			conflictsBetweenTheseTwo = O[c1-1,c2-1]
			conflictsPerCourse[c1] += conflictsBetweenTheseTwo
			conflictsPerCourse[c2] += conflictsBetweenTheseTwo


for key in conflictsPerCourse.keys():
	print key, conflictsPerCourse[key]
