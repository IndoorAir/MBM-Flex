## R script to plot the output of MBM-Flex
##
## NB: execute from the MBM-Flex directory
## ----------------------------------------
library(ggplot2)
library(scales)

## set directory of model run outputs
main.output <- "20230727_191734_TestSerial"
setwd(main.output)

## set filename of pdf file for plots
pdfname <- "mbmflex_output.pdf"

## ----------------------------------------
output.dir <- "extracted_outputs/"
output.files <- list.files(output.dir)

# number of rooms
nroom <- length(output.files) - 1

## import model output: indoor values in each room
indoor.df <- data.frame()
for (n in 1:nroom) {
  fname <- paste0(main.output, sprintf("_room%02d",n), ".csv")
  ind.df <- read.csv(paste0(output.dir, fname), header=TRUE)
  ind.df$ROOM <- paste0("R", n)
  indoor.df <- rbind(indoor.df, ind.df)
}

## import model output: outdoor values
fname <- paste0(main.output, "_outdoor.csv")
outdoor.df <- read.csv(paste0(output.dir, fname), header=TRUE)

## ----------------------------------------
## WHO air quality guidelines (2021)
## https://www.who.int/publications/i/item/9789240034228

## units in ug/m3
who.aer <- data.frame(PM25=c(5,15), PM10=c(15,45))
who.gas <- data.frame(O3=c(60,100), NO2=c(10,25), SO2=c(40), CO=c(4000))

# convert to molecule cm-3 assuming standard temperature and pressure
# according to WHO guidelines 1 ppb = 2 ug/m3
who.df <- cbind(who.aer, (who.gas*0.5*2.46e10))

## ----------------------------------------

## plot model output and save to pdf file
pdf(paste0(output.dir, pdfname), paper="a4r", width=0, height=0)

room.list <- unique(indoor.df$ROOM)
vars.list <- names(indoor.df)
for (i in 2:(length(vars.list)-1)) {
  vars <- vars.list[i]
  p <- ggplot(data=indoor.df, aes(x=Time, y=.data[[vars]], color=ROOM, name="")) +
    geom_line(linewidth=2) + labs(color=guide_legend(title=""))
  ## plot ambient concentrations (if available)
  vars.out <- paste0(vars, "OUT")
  if(vars.out %in% names(outdoor.df)) {
    p <- p + geom_line(data=outdoor.df, aes(x=Time, y=.data[[vars.out]], color="black"),
                       linewidth=2, linetype="dashed") +
      scale_color_manual(values=c("black", hue_pal()(nroom)), labels=c("Ambient",unique(room.list)))
  }
  ## plot WHO guidelines (if available)
  if (vars %in% names(who.df)) {
    guidel <- who.df[[which(names(who.df)==vars)]]
    p <- p + geom_hline(yintercept=guidel, linetype="dotted", color="black")
  }
  print(p)
}
dev.off()

## return to MBM-Flex directory
setwd("../")
