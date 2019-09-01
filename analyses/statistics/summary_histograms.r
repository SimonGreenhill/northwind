#!/usr/bin/env Rscript
library(ggplot2)
library(gridExtra)

coverage <- read.delim('statistics.dat', header=TRUE)

# workaround https://github.com/hadley/ggplot2/issues/1565
theme_sjg <- theme_classic() + theme(
    axis.line.x = element_line(colour = 'black', size=0.5, linetype='solid'),
    axis.line.y = element_line(colour = 'black', size=0.5, linetype='solid'),
    plot.title = element_text(hjust=0)
)


pIL <- ggplot(coverage, aes(InventoryLength))
pIL <- pIL + geom_histogram(binwidth=1)
pIL <- pIL + xlab("") + ylab("Number of Languages")
pIL <- pIL + scale_x_continuous(breaks=c(0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100))


pTL <- ggplot(coverage, aes(TranscriptLength))
pTL <- pTL + geom_histogram(binwidth=25)
pTL <- pTL + scale_x_continuous(breaks=c(0, 250, 500, 750, 1000, 1250, 1500, 1750))
pTL <- pTL + xlab("") + ylab("")


pAb <- ggplot(coverage, aes(Unobserved))
pAb <- pAb + geom_histogram(binwidth=1)
pAb <- pAb + scale_x_continuous(breaks=c(0, 10, 20, 30, 40, 50))
pAb <- pAb + xlab("Number of Phonemes") + ylab("Number of Languages")

pEr <- ggplot(coverage, aes(DistinctErrors))
pEr <- pEr + geom_histogram(binwidth=1)
pEr <- pEr + scale_x_continuous(breaks=c(0, seq(1:9)))
pEr <- pEr + xlab("Number of Phonemes") + ylab("")

# labels a, b, c
pIL <- pIL + ggtitle('a. Inventory Length')  + theme_sjg
pTL <- pTL + ggtitle('b. Transcript Length') + theme_sjg
pAb <- pAb + ggtitle('c. Unobserved Phonemes') + theme_sjg
pEr <- pEr + ggtitle('d. Unexpected Phonemes') + theme_sjg

pdf('summary_histograms.pdf', width=8, height=6)
grid.arrange(pIL, pTL, pAb, pEr, ncol=2, nrow=2)
dev.off()
