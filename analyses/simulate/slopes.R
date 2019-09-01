#!/usr/bin/env Rscript
library(ggplot2)

df <- read.delim("slopes.dat", header=FALSE, sep=":")

b <- df[df$V2 >= -1,]


print(paste("Median:", median(df$V2)))
print(paste("SD:", sd(df$V2)))
print(paste("N:", nrow(df)))
print(paste("Below:", nrow(b)))



pdf("slopes.pdf")
p <- ggplot(df, aes(V2)) + geom_histogram()
p <- p + theme_classic()
print(p)
x <- dev.off()
