library(ape)
library(caper)
library(grid)
library(gridExtra)
library(ggplot2)

tree <- read.nexus('../../data/glottolog/glottolog.trees')
tree <- compute.brlen(tree, method="Grafen")

dat <- read.delim('../statistics/statistics.dat', header=TRUE)
rr <- read.delim('../recovery_rate/predict-gamm.dat', header=TRUE)

dat <- merge(dat, rr)
dat$LogLength <- log(dat$Length)

d <- comparative.data(
    phy=multi2di(tree),
    data=dat,
    vcv=TRUE, names.col=Label, na.omit = FALSE, warn.dropped = TRUE
)

stopifnot(d$dropped$tips == 0)
stopifnot(d$dropped$unmatched.rows == 0)

fitAvsIL <- pgls(Unobserved ~ InventoryLength, data=d, lambda='ML')
sink('fit_Unobserved_vs_InventoryLength.txt', split=TRUE)
summary(fitAvsIL)
sink()

fitAvsTL <- pgls(Unobserved ~ TranscriptLength, data=d, lambda='ML')
sink('fit_Unobserved_vs_TranscriptLength.txt', split=TRUE)
summary(fitAvsTL)
sink()

fitAvsLogTL <- pgls(Unobserved ~ log(TranscriptLength), data=d, lambda='ML')
sink('fit_Unobserved_vs_logTranscriptLength.txt', split=TRUE)
summary(fitAvsTL)
sink()



p1 <- ggplot(dat, aes(x=InventoryLength, y=Unobserved))
p1 <- p1 + geom_point()
p1 <- p1 + geom_abline(
    intercept = coef(fitAvsIL)[1],
    slope = coef(fitAvsIL)[2],
    col='darkorange',
    size=1.2
)
p1 <- p1 + ggtitle("a. Unobserved vs. Inventory Size")
p1 <- p1 + xlab('Inventory Size')
p1 <- p1 + theme_classic() + guides(colour="none")


p2 <- ggplot(dat, aes(x=TranscriptLength, y=Unobserved))
p2 <- p2 + geom_point()
p2 <- p2 + geom_abline(
    intercept = coef(fitAvsTL)[1],
    slope = coef(fitAvsTL)[2],
    col='orange',
    linetype=2,  # not signif
    size=1.2,
    alpha=0.6  # not signif
)
p2 <- p2 + ggtitle("b. Unobserved vs. Transcript Size")
p2 <- p2 + xlab('Transcript Size')
p2 <- p2 + theme_classic()


pdf('correlations.pdf')
grid.arrange(p1, p2)
x <- dev.off()
