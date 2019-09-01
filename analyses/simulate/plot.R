#!/usr/bin/env Rscript
library(ggplot2)
library(ggridges)
options(encoding = "UTF-8")

options(scipen=1000000)

df <- read.delim("results.txt", header=TRUE)

pred <- read.delim("../recovery_rate/predict-gamm.dat", header=TRUE)
pred$Replicate <- 0
pred$Type <- "Modelled"

# get labels with diacritics
labels <- read.delim('../statistics/statistics.dat', header=TRUE)
rownames(labels) <- labels$Language
pred$Language <- labels[pred$Language,]$FullLanguage
df$Language <- labels[df$Language,]$FullLanguage



full <- rbind(df, pred[c("Language", "Replicate", "Length", "Type")])
full$Type <- factor(full$Type, levels=c("Modelled", "Simulated"))

full$Language <- factor(full$Language, levels=pred$Language[order(pred$Length)])



p <- ggplot(df, aes(x=Length)) + geom_histogram()
p <- p + theme_classic() + guides(color=FALSE)
p <- p + ylab("")
p <- p + scale_x_log10()

ggsave('histogram.pdf', p)






p <- ggplot(full, aes(y=Language, x=Length, group=Type, color=Type))
p <- p + geom_point(alpha=0.9, size=0.8)
p <- p + scale_color_manual(values=c("darkorange", "lightgray"))
p <- p + theme_classic() + guides(color=FALSE)
p <- p + ylab("")
p <- p + scale_x_log10()

ggsave('comparison.png', p, width=8, height=18)





p <- ggplot(full, aes(y=Language, x=Length))
p <- p + stat_density_ridges(quantile_lines=FALSE, rel_min_height = 0.02, scale=0.9)
p <- p + geom_point(
    data=full[full$Type == 'Modelled',],
    aes(x=Length, y=Language, color="darkorange")
)
p <- p + theme_classic() + guides(color=FALSE)
p <- p + ylab("")
p <- p + scale_x_log10()


ggsave('comparison-ridges.png', p, width=8, height=18)


# Correlation

sim <- aggregate(df$Length, list(df$Language), median)
mdl <- pred
rownames(mdl) <- mdl$Language
mdl <- mdl[as.character(sim$Group.1),]

lengths <- data.frame(Simulated=sim$x, Modelled=mdl$Length)


sink("correlation.txt")
cor.test(lengths$Simulated, lengths$Modelled, method="spearman")
sink()

p <- ggplot(lengths, aes(x=Simulated, y=Modelled))
p <- p + geom_point()
p <- p + theme_classic()
p <- p + scale_x_log10() + scale_y_log10()

ggsave('comparison-correlations.pdf', p)


sink("summary.txt")
print(paste("Median:", median(df$Length)))
print(paste("SD:", sd(df$Length)))
sink()

