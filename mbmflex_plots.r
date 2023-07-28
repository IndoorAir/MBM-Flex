#

dir <- "20230727_191734_TestSerial"

setwd(dir)   # folder with all outputs of the model run
nroom <- 3    # number of rooms

df <- read.csv(paste("extracted_outputs/", dir, "_room01.csv", sep=""))

print(head(df))

setwd("../")
