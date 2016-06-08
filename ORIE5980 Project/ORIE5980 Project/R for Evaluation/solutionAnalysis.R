courses.new <- courses
newSolution <- read.csv('solution0501.txt', header = F, sep = '.')
colnames(newSolution) <- c('x', 'index', 'newConfig')
newSolution$x <- NULL
newSolution$index <- newSolution$index + 1000

for(i in 1:(dim(newSolution)[1])){
    ind <- newSolution[i,1]
    previous <- which(fallEvenings %in% courses.new[courses.new$Index == ind,7:9])
    if(newSolution[newSolution$index == ind,]$newConfig == 0){
        change <- previous - 1
    } else if(newSolution[newSolution$index == ind,]$newConfig == 2){
        change <- previous + 1
    } else {
        change <- previous
    }
    
    for(d in 1:length(change)){
        newDate <- fallEvenings[change[d]]
        courses.new[courses.new$Index == ind,6+d] <- newDate
    }
}

evenings.new <- evenings
evenings.new$courses <- sapply(1:length(eveningList),function(x){na.omit(courses.new[(courses.new$Date1 == eveningList[x]) | (courses.new$Date2 == eveningList[x]) | (courses.new$Date3 == eveningList[x]),]$Index)})
evenings.new$nCourses <- sapply(1:dim(evenings.new)[1], function(x){length(evenings.new$courses[[x]])})

evenings.new$nOnes <- sapply(1:dim(evenings.new)[1], function(x){ sum(1*(evenings.new$courses[[x]] %in% onePrelimIndex))})
evenings.new$nTwos <- sapply(1:dim(evenings.new)[1], function(x){ sum(1*(evenings.new$courses[[x]] %in% twoPrelimIndex))})
evenings.new$nThrees <- sapply(1:dim(evenings.new)[1], function(x){ sum(1*(evenings.new$courses[[x]] %in% threePrelimIndex))})
evenings.new$nStudents <- sapply(1:dim(evenings.new)[1], function(x){sum(courses[courses$Index %in% evenings.new$courses[[x]],]$nEnrolled)})


(ggplot(evenings.new[evenings.new$semester=='Fall 2014',], aes(x=date)) 
+ geom_bar(aes(y = nStudents), stat = "identity", fill = "lightgreen")
+ ggtitle("Number of Students Taking Prelims per Evening"))