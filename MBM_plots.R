## R script to plot output of MBM-Flex
## ----------------------------------------

## folder with all outputs of the model run
main.output <- "20230727_191734_TestSerial"

## ----------------------------------------

setwd(main.output)

output.files <- list.files("extracted_outputs")

nroom <- length(output.files) - 1

list.out <- list()
for (n in 1:nroom) {
  fname <- paste0(main.output, sprintf("_room%02d",n), ".csv")
  df <- read.csv(paste0("extracted_outputs/", fname), header=TRUE)
  list.out[[n]] <- df
}

fname <- paste0(main.output, "_outdoor.csv")
df <- read.csv(paste0("extracted_outputs/", fname), header=TRUE)

## ----------------------------------------

## make plots



setwd("../")
