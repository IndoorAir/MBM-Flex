## ---------------------------------------------------------------------
## R script
## ---------------------------------------------------------------------

exposure_metrics <- function(data.df, adults, children, outname) {

  ## number of timesteps
  tstep <- nrow(data.df)

  ## number of people in the room
  n.occupants <- adults + children

  ## ----------------------------------------
  ## WHO air quality guidelines (2021)
  ## https://www.who.int/publications/i/item/9789240034228

  ## units in ug/m3
  who.aer <- data.frame(PM25=c(5,15), PM10=c(15,45))
  who.gas <- data.frame(O3=c(60,100), NO2=c(10,25), SO2=c(NA,40), CO=c(NA,4000))
  ## ----------------------------------------

  ## open output file
  sink(outname)

  ## calculate metrics for each variable
  cat("Exposure metrics from the MBM-Flex model calculations")
  cat("\n=====================================================\n\n")
  for (i in 2:ncol(data.df)) {
    var.name <- names(data.df)[i]

    ## convert gas phase species to ug/m3 assuming standard temperature
    ## and pressure -- according to WHO guidelines 1 ppb = 2 ug/m3
    if (var.name != "tspx") {
      var.df <- data.df[[i]]*2/2.46e10
    }

    ## select when there are people in the room
    occup.df <- var.df[which(n.occupants > 0)]

    ## average and maximum concentrations
    cat(var.name, "\n\n")
    cat("Mean concentration:", round(mean(var.df), digits=2), "ug/m3\n")
    cat("Mean concentration in occupied room:", round(mean(occup.df), digits=2), "ug/m3\n")
    cat("Max concentration: ", round(max(var.df), digits=2), "ug/m3\n")
    cat("Max concentration in occupied room: ", round(max(occup.df), digits=2), "ug/m3\n")

    ## fractional time when concentrations exceed the WHO guidelines
    if (var.name %in% names(who.df)) {
      who.gl <- who.df[[which(names(who.df)==var.name)]]
      x1 <- 100*length(which(var.df > who.gl[1]))/tstep
      y1 <- 100*length(which(var.df > who.gl[2]))/tstep
      x2 <- 100*length(which(occup.df > who.gl[1]))/tstep
      y2 <- 100*length(which(occup.df > who.gl[2]))/tstep
      
      cat("\n")
      if (var.name == "O3") {
        cat("Time exceeding WHO guidelines (Peak season):", round(x1, digits=1), "%\n")
        cat("Time exceeding WHO guidelines (8-hour):", round(y1, digits=1), "%\n")
        cat("Time exceeding WHO guidelines (Peak season) in occupied room:", round(x2, digits=1), "%\n")
        cat("Time exceeding WHO guidelines (8-hour) in occupied room:", round(y2, digits=1), "%\n")
      } else {
        cat("Time exceeding WHO guidelines (Annual):", round(x1, digits=1), "%\n")
        cat("Time exceeding WHO guidelines (24-hour):", round(y1, digits=1), "%\n")
        cat("Time exceeding WHO guidelines (Annual) in occupied room:", round(x2, digits=1), "%\n")
        cat("Time exceeding WHO guidelines (24-hour) in occupied room:", round(y2, digits=1), "%\n")
      }
    }

    cat("\n-----------------------------------------------------------------------\n\n")
  }

  ## close output file
  sink()
}


exposure_metrics(indoor.df[c("Time","O3","NO2","HONO","HNO3")], indoor.df["adults"], indoor.df["children"], "metrics.txt")
