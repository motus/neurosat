
library(ggplot2)
library(scales)

setwd("C:/Users/sergiym/devel/neurosat/")

data <- read.csv("neurosat-solve-stats.csv")
data$sat_good <- data$sat_sol / (data$sat_sol + data$sat_unsol + data$sat_invalid)

png("neurosat-solve-stats.png", width=800, height=480, res=160)

ggplot(data=data, aes(x=n_iter, y=sat_good)) +
  geom_line(size=0.8) +
  geom_point(size=2) +
  geom_text(data=data[data$n_iter == 16,],
            label=paste(round(data$sat_good[data$n_iter == 16], 4) * 100, "%", sep=""),
            nudge_y=0.055, nudge_x=4) +
  scale_x_continuous("Number of iterations", breaks=data$n_iter, limits=c(1,64)) +
  scale_y_continuous("SAT problems solved", labels=scales::percent, limits=c(0,1)) +
  theme_bw()

dev.off()


data <- read.csv("neurosat-stats-experiment-1.csv")

png("neurosat-stats-experiment-1.png", width=800, height=480, res=160)

ggplot(data=data, aes(x=factor(n_vars), y=sat_good_pct/100)) +
  geom_col() +
  geom_text(data=data,
            label=paste(round(data$sat_good_pct, 2), "%", sep=""),
            nudge_y=0.055) +
  scale_x_discrete("Number of variables") +
  scale_y_continuous("SAT problems solved", labels=scales::percent, limits=c(0,1)) +
  theme_bw()

dev.off()

