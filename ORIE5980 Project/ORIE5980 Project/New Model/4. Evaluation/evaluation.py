
f = open("s-pm1.txt")
schedule = []
for l in f.readlines():
    night = l.strip().split("\t")
    print night
    night = [int(y) for y in night]
    #print night
    schedule.append(night)
    f.close()
    

f = open("overlapSpring.txt")
overlap = []

for l in f.readlines():
    course = l.strip().split("\t")
    #print course
    course = [int(y) for y in course]
    overlap.append(course)  
    f.close()
    
count = 0
ov = []
courseConflicts = {k:0 for k in xrange(1,len(course)+1)}
for i in range(0,len(schedule)):
    if len(schedule[i]) == 1: count = count
    else:
        for j in range(0,(len(schedule[i])-1)):
            for k in range(j+1,len(schedule[i])):
                if overlap[schedule[i][j]-1][schedule[i][k]-1] != 0:
                    if i<=8:
                        print schedule[i][j],schedule[i][k],i+1,overlap[schedule[i][j]-1][schedule[i][k]-1]              
                    else:
                        print schedule[i][j],schedule[i][k],i+2,overlap[schedule[i][j]-1][schedule[i][k]-1]              

                    count = count+overlap[schedule[i][j]-1][schedule[i][k]-1]
                    
                    courseConflicts[schedule[i][j]] = courseConflicts[schedule[i][j]]+overlap[schedule[i][j]-1][schedule[i][k]-1]
                    courseConflicts[schedule[i][k]] = courseConflicts[schedule[i][k]]+overlap[schedule[i][j]-1][schedule[i][k]-1]
                      
                    #print count
#for k in courseConflicts.keys():
    #print k,courseConflicts[k]

# add the part of how many courses eliminate conflicts/reduce conflicts