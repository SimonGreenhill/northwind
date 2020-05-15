library(ggplot2)
require(gridExtra)

records <- read.delim('coverage.dat', header=TRUE)

#
# Recovery all lines
#
p1 <- ggplot(records,
    aes(x=PPercent, y=OPercent, color=TotalInventory)
)
p1 <- p1 + geom_line(aes(group=Language))
p1 <- p1 + scale_color_gradient("Inventory Size", trans="log", high="orange", low="blue")
p1 <- p1 + xlab('Transcript Percentage') + ylab("Percentage of Observed Phonemes")
p1 <- p1 + theme_classic()
p1 <- p1 + guides(color="none")

pdf("recovery_rate.pdf")
print(p1)
x <- dev.off()


#
# Recovery  - smoothed
#
p <- ggplot(records, aes(x=PPercent, y=OPercent))
p <- p + geom_smooth()
p <- p + xlab('Transcript Percentage') + ylab("Percentage of Observed Phonemes")
p <- p + xlim(0, 100) + ylim(0, 100)
p <- p + theme_classic()

pdf("recovery_rate_combined.pdf")
print(p)
x <- dev.off()



#
# Recovery -- blocked into 10s
#
records$Block <- as.factor(round(records$TotalInventory, -1))

p <- ggplot(records,
    aes(x=PPercent, y=OPercent, group=Block,
        fill=Block,
        color=Block
))
p <- p + geom_smooth()
p <- p + scale_color_brewer(palette="Set1")
p <- p + scale_fill_brewer(palette="Set1")
p <- p + xlab('Transcript Percentage') + ylab("Percentage of Observed Phonemes")
p <- p + xlim(0, 100) + ylim(0, 100)
p <- p + theme_classic()

pdf("recovery_rate_blocked.pdf")
print(p)
x <- dev.off()


p2 <- ggplot(records,
            aes(x=TranscriptLength, y=OPercent, color=TotalInventory)
)
p2 <- p2 + geom_line(aes(group=Language))
p2 <- p2 + scale_color_gradient("Inventory Size", trans="log", high="orange", low="blue")
p2 <- p2 + xlab('Transcript Length (Phonemes)')
p2 <- p2 + ylab("Percentage of Observed Phonemes")
p2 <- p2 + theme_classic()
p2 <- p2 + guides(color="none")

pdf("recovery_rate_vs_transcript_length.pdf")
print(p2)
x <- dev.off()


p1 <- p1 + ggtitle('a. Recovery Rate (Transcript Percentage)') + theme(plot.title=element_text(hjust=0))
p2 <- p2 + ggtitle('b. Recovery Rate (Transcript Length)') + theme(plot.title=element_text(hjust=0))

p1 <- p1 + geom_smooth(colour="#333333", method="loess")
p2 <- p2 + geom_smooth(colour="#333333", method="loess")

# plot 3
p3 <- p2 + scale_x_log10()
# the above will generate ggplot2 warnings from the counts at point zero:
#   Transformation introduced infinite values in continuous x-axis
p3 <- p3 + ggtitle('c. Recovery Rate (Log Transformed Transcript Length)') + theme(plot.title=element_text(hjust=0))

# force the same scale
p1 <- p1 + ylim(0, 100)
p2 <- p2 + ylim(0, 100)
p3 <- p3 + ylim(0, 100)


ggsave("combined.pdf", grid.arrange(p1, p2, p3, ncol=1))

