## R script to plot the output of MBM-Flex
##
## NB: execute from the MBM-Flex directory
## ----------------------------------------
library(ggplot2)
library(scales)

## set directory of model run outputs
main.output <- "20230818_122533_TestSerial"
setwd(main.output)

## set filename of pdf file for plots
pdfname <- "mbmflex_output.pdf"

## ----------------------------------------
output.dir <- "extracted_outputs/"
output.files <- list.files(output.dir, pattern=".csv")

# number of rooms
nroom <- length(output.files) - 1

## import model output: indoor values in each room
indoor.df <- data.frame()
for (n in 1:nroom) {
  fname <- paste0(main.output, sprintf("_room%02d",n), ".csv")
  ind.df <- read.csv(paste0(output.dir, fname), header=TRUE)
  ind.df$ROOM <- paste("Room", n, sep=" ")
  indoor.df <- rbind(indoor.df, ind.df)
}

## import model output: outdoor values
fname <- paste0(main.output, "_outdoor.csv")
outdoor.df <- read.csv(paste0(output.dir, fname), header=TRUE)

## time in hours
indoor.df$Time <- indoor.df$Time/3600
outdoor.df$Time <- outdoor.df$Time/3600

## ----------------------------------------
## WHO air quality guidelines (2021)
## https://www.who.int/publications/i/item/9789240034228

## units in ug/m3
who.aer <- data.frame(PM25=c(5,15), PM10=c(15,45))
who.gas <- data.frame(O3=c(60,100), NO2=c(10,25), SO2=c(NA,40), CO=c(NA,4000))

# convert to molecule cm-3 assuming standard temperature and pressure
# according to WHO guidelines 1 ppb = 2 ug/m3
who.df <- cbind(who.aer, (who.gas*0.5*2.46e10))
who.df$avg.time <- c("Annual", "24-hours")

## ----------------------------------------

## plot model output and save to pdf file
pdf(paste0(output.dir, pdfname), paper="a4r", width=0, height=0)

## list of rooms and variables to plot
room.list <- unique(indoor.df$ROOM)
vars.list <- names(indoor.df)

## plot indoor variables in each room
for (i in 2:(length(vars.list)-1)) {
  vars <- vars.list[i]
  gp <- ggplot(data=indoor.df, aes(x=Time, y=.data[[vars]], color=ROOM, name="")) +
               geom_line(linewidth=2) + labs(color=guide_legend(title=""))
  gp.col <- hue_pal()(nroom)
  gp.lab <- unique(room.list)
  ## plot outdoor concentrations (if available)
  vars.out <- paste0(vars, "OUT")
  if(vars.out %in% names(outdoor.df)) {
    gp <- gp + geom_line(data=outdoor.df, aes(x=Time, y=.data[[vars.out]], color="black"), linewidth=2)
    gp.col <- c("black", gp.col)
    gp.lab <- c("Outdoors", gp.lab)
  }

  ## plot WHO guidelines (if available)
  if (vars %in% names(who.df)) {
    who.gl <- who.df[[which(names(who.df)==vars)]]
    gp <- gp + geom_hline(yintercept=who.gl[1], linewidth=1, linetype="dotted", color="black")
    gp <- gp + geom_hline(yintercept=who.gl[2], linewidth=1, linetype="dotted", color="black")
    if (vars == "O3") {
      gp <- gp + geom_text(aes(x=1, y=who.gl[1], label="WHO guideline\nPeak season", color="black")) +
            geom_text(aes(x=1, y=who.gl[2], label="WHO guideline\n8-hour", color="black"))
    } else {
      gp <- gp + geom_text(aes(x=1, y=who.gl[1], label="WHO guideline\nAnnual", color="black")) +
            geom_text(aes(x=1, y=who.gl[2], label="WHO guideline\n24-hour", color="black"))
    }
  }
  gp.legend <- scale_color_manual(values=gp.col, labels=gp.lab)
  gp <- gp + gp.legend + theme(axis.text=element_text(size=12),
                               axis.title.x=element_text(size=12, vjust=-2),
                               axis.title.y=element_text(size=12, vjust=2),
                               legend.text=element_text(size=14))
  print(gp)
}
dev.off()

## return to MBM-Flex directory
cat("\n*** Plots saved to", paste0(main.output,"/",output.dir,pdfname), "***\n")
setwd("../")
