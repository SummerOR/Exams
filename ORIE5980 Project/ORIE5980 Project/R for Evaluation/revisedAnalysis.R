library(xlsx)
library(ggplot2)
schedule <- read.xlsx("schedule.xlsx",1,stringsAsFactors = FALSE)

schedule <- schedule[schedule$Subject != 'CS 2112',]
schedule <- schedule[schedule$NetID != 'lch27',]
schedule[schedule$NetID == 'cmc27',]$Subject <- 'BSOC 2101'

evenings <- sort(unique(schedule$Prelim))
eveningList <- as.list(evenings) 
nEvenings <- length(evenings)

fallEvenings <- sort(unique(schedule[schedule$Term == "Fall 2014",]$Prelim))
springEvenings <- sort(unique(schedule[schedule$Term == "Spring 2015",]$Prelim))

evenings <- data.frame(date = sort(unique(schedule$Prelim)), semester = NA, courses = NA)
evenings[evenings$date %in% fallEvenings,]$semester <- 'Fall 2014'
evenings[evenings$date %in% springEvenings,]$semester <- 'Spring 2015'

reference.fall <- read.xlsx("fallReference.xlsx",1,stringsAsFactors = FALSE)
reference.fall <- reference.fall[-c(seq(140,195)),-1]
colnames(reference.fall) <- c('Index', 'nEnrolled', 'nPrelims', 'Title', 'Subject')
reference.fall$semester <- 'Fall 2014'
reference.fall$Index <- reference.fall$Index + 1000

reference.spring <- read.xlsx("springReference.xlsx",1,stringsAsFactors = FALSE)
reference.spring <- reference.spring[-128,]
colnames(reference.spring) <- c('Index', 'nEnrolled', 'nPrelims', 'Title', 'Subject')
reference.spring$semester <- 'Spring 2015'
reference.spring <- reference.spring[-(reference.spring$Index == 126),]
reference.spring$Index <- reference.spring$Index + 2000

courses <- rbind(reference.fall, reference.spring)


onePrelimIndex <- courses[courses$nPrelims == 1,]$Index
twoPrelimIndex <- courses[courses$nPrelims == 2,]$Index
threePrelimIndex <- courses[courses$nPrelims == 3,]$Index

courses$Date1 <- as.Date("1900-01-01")
courses$Date2 <- as.Date("1900-01-01")
courses[(courses$Index %in% onePrelimIndex),]$Date2 <- NA
courses$Date3 <- as.Date("1900-01-01")
courses[!(courses$Index %in% threePrelimIndex),]$Date3 <- NA


for(index in courses$Index){
    subject <- courses[courses$Index == index,]$Subject
    term <- courses[courses$Subject == subject,]$semester
    dates <- unique(schedule[(schedule$Subject == subject) & (schedule$Term == term), ]$Prelim)
    if(index %in% onePrelimIndex){
        courses[courses$Index == index,]$Date1 <- dates
    }else if(index %in% twoPrelimIndex){
        courses[courses$Index == index,]$Date1 <- dates[1]
        courses[courses$Index == index,]$Date2 <- dates[2]
    }else if(index %in% threePrelimIndex){
        courses[courses$Index == index,]$Date1 <- dates[1]
        courses[courses$Index == index,]$Date2 <- dates[2]
        courses[courses$Index == index,]$Date3 <- dates[3]
    }
}

evenings$courses <- sapply(1:length(eveningList),function(x){na.omit(courses[(courses$Date1 == eveningList[x]) | (courses$Date2 == eveningList[x]) | (courses$Date3 == eveningList[x]),]$Index)})
evenings$nCourses <- sapply(1:dim(evenings)[1], function(x){length(evenings$courses[[x]])})

evenings$nOnes <- sapply(1:dim(evenings)[1], function(x){ sum(1*(evenings$courses[[x]] %in% onePrelimIndex))})
evenings$nTwos <- sapply(1:dim(evenings)[1], function(x){ sum(1*(evenings$courses[[x]] %in% twoPrelimIndex))})
evenings$nThrees <- sapply(1:dim(evenings)[1], function(x){ sum(1*(evenings$courses[[x]] %in% threePrelimIndex))})
evenings$nStudents <- sapply(1:dim(evenings)[1], function(x){sum(courses[courses$Index %in% evenings$courses[[x]],]$nEnrolled)})



for(e in 1:length(eveningList)){
    if(eveningList[e] %in% fallEvenings){
        print(as.vector(evenings$courses[[e]] - 1000))
    } else {
        print(as.vector(evenings$courses[[e]] - 2000))
    }
}

conflicts.fall <- read.table("fallConflicts.txt")
conflicts.fall <- data.frame(conflicts.fall)
names(conflicts.fall) <- c("class1", "class2", "night", "nConflicts")
conflictsPerNight.fall <- sapply(1:length(fallEvenings),function(x){sum(conflicts.fall[conflicts.fall$night == x,]$nConflicts)})
evenings$conflicts <- NA
evenings[evenings$semester=='Fall 2014',]$conflicts <- conflictsPerNight.fall

conflicts.spring <- read.table("springConflicts.txt")
conflicts.spring <- data.frame(conflicts.spring)
names(conflicts.spring) <- c("class1", "class2", "night", "nConflicts")
conflictsPerNight.spring <- sapply(1:length(springEvenings),function(x){sum(conflicts.spring[conflicts.spring$night == x,]$nConflicts)})
evenings[evenings$semester=='Spring 2015',]$conflicts <- conflictsPerNight.spring


(ggplot(evenings[evenings$semester=='Fall 2014',], aes(x=date)) 
+ geom_bar(aes(y = nStudents), stat = "identity", fill = "lightgreen") 
+ geom_bar(aes(y = conflicts), stat = "identity", fill = "red") 
+ ggtitle("Number of Students Taking Prelims per Evening"))

(ggplot(evenings[evenings$semester=='Spring 2015',], aes(x=date)) 
+ geom_bar(aes(y = nStudents), stat = "identity", fill = "lightgreen") 
+ geom_bar(aes(y = conflicts), stat = "identity", fill = "red") 
+ ggtitle("Number of Students Taking Prelims per Evening"))
