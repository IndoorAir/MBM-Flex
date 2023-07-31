## R script to plot output of MBM-Flex
## ----------------------------------------

## directory with all outputs of the model run
main.output <- "20230727_191734_TestSerial"

## ----------------------------------------

#setwd(main.output)

output.files <- list.files("extracted_outputs/")

nroom <- length(output.files) - 1

## output files of each room
output.list <- list()
for (n in 1:nroom) {
  fname <- paste0(main.output, sprintf("_room%02d",n), ".csv")
  out.df <- read.csv(paste0("extracted_outputs/", fname), header=TRUE)
  output.list[[n]] <- out.df
}

## output file: outdoor concentrations
fname <- paste0(main.output, "_outdoor.csv")
outdoor <- read.csv(paste0("extracted_outputs/", fname), header=TRUE)

## WHO air quality guidelines (2021)
who.df <- data.frame(PM25=c(5,15), PM10=c(15,45), O3=c(60,100),
                     NO2=c(10,25), SO2=c(40), CO=c(4))

## TODO: convert WHO guidelines from ug/m3

## ----------------------------------------

## get list of variables to plot from ROOM 1
room1 <- output.list[[1]]
vars.list <- names(room1)

## make plots
## pdf file saved in directory `main.output`
pdf("mbmflex.pdf", paper="a4r", width=0, height=0)

for (i in 2:length(vars.list)) {
  vars <- vars.list[i]
  plot(room1[,1], room1[,i], type="l", main="", xlab="Time", ylab=vars)
  for (n in 2:nroom) {
    room <- output.list[[n]]
    lines(room[,1], room[,i])
  }
  ## plot outdoor concentrations (if available)
  vars.out <- paste0(vars, "OUT")
  if(vars.out %in% names(outdoor)) {
    lines(outdoor[,1], outdoor[,which(names(outdoor)==vars.out)])
  }
  ## plot WHO guidelines (if available)
  if (vars %in% names(who.df)) {
    abline(who.df[which(names(who.df)==vars)])
  }
}
dev.off()

#setwd("../")
