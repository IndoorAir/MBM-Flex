#

main.output <- "20230727_191734_TestSerial"

setwd(main.output)   # folder with all outputs of the model run

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

setwd("../")
