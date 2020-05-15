library(ape)
library(caper)
library(ggplot2)
library(dplyr)

options(encoding = "UTF-8")
options(scipen = 1000000)

COLORS <- c("darkorange", "steelblue", "darkgray")

tree <- read.nexus('../../data/glottolog/glottolog.trees')
tree <- multi2di(compute.brlen(tree, method="Grafen"))

dat <- read.delim('../statistics/statistics.dat', header=TRUE, stringsAsFactors=FALSE)

# load LM and GAM models
rr <- read.delim('../recovery_rate/predict-gamm.dat', header=TRUE, stringsAsFactors=FALSE)

# prune to remove non-best GAMS
rr.lm <- rr[rr$Model == 'LM', ]
# sort by k and then remove the duplicates:
rr.gam <- rr[rr$Model == 'GAM', ]
rr.gam <- rr.gam[order(rr.gam$k), ]
rr.gam <- rr.gam %>% distinct(Language, .keep_all = TRUE)

rr <- rbind(rr.gam, rr.lm)

# load simulation results
sim <- read.delim('../simulate/results.txt', header=TRUE, stringsAsFactors=FALSE)
# just get average
sim <- sim %>% group_by(Language) %>%
    dplyr::summarize(RecoveryLength = median(Length, na.rm=TRUE))
sim$Model <- 'Simulation'


# remove unneeded columns
rr <- rr[, c("Language", "Model", "RecoveryLength")]
dat <- dat[, c("Label", "Language", "Family", "InventoryLength", "TranscriptLength")]
sim <- sim[, c("Language", "Model", "RecoveryLength")]

dat <- merge(dat, rbind(rr, sim))
print(head(dat))

# PGLS
d.lm <- comparative.data(
    phy=tree,
    data=dat[dat$Model == 'LM', ],
    vcv=TRUE, names.col=Label, na.omit = FALSE, warn.dropped = TRUE
)

d.gam <- comparative.data(
    phy=tree,
    data=dat[dat$Model == 'GAM', ],
    vcv=TRUE, names.col=Label, na.omit = FALSE, warn.dropped = TRUE
)

d.sim <- comparative.data(
    phy=tree,
    data=dat[dat$Model == 'Simulation', ],
    vcv=TRUE, names.col=Label, na.omit = FALSE, warn.dropped = TRUE
)

# did we lose any tips?
stopifnot(d.lm$dropped$tips == 0)
stopifnot(d.lm$dropped$unmatched.rows == 0)
stopifnot(d.gam$dropped$tips == 0)
stopifnot(d.gam$dropped$unmatched.rows == 0)
stopifnot(d.sim$dropped$tips == 0)
stopifnot(d.sim$dropped$unmatched.rows == 0)


fitRL.lm <- pgls(log10(RecoveryLength) ~ InventoryLength, data=d.lm, lambda='ML')
fitRL.gam <- pgls(log10(RecoveryLength) ~ InventoryLength, data=d.gam, lambda='ML')
fitRL.sim <- pgls(log10(RecoveryLength) ~ InventoryLength, data=d.sim, lambda='ML')



sink('fit_InventoryLength_vs_LogRecoveryLength.txt', split=TRUE)

cat("\nApproach: LM\n")
summary(fitRL.lm)

cat('\n===========================================\n')

cat("\nApproach: GAM\n")
summary(fitRL.gam)

cat('\n===========================================\n')

cat("\nApproach: Simulation\n")
summary(fitRL.sim)

cat('\n===========================================\n')

sink()


# plot

p <- ggplot(dat, aes(x=InventoryLength, y=RecoveryLength, group=Model, color=Model))
p <- p + geom_point()
p <- p + geom_abline(
    intercept = coef(fitRL.lm)[1],
    slope = coef(fitRL.lm)[2],
    col='darkorange',
    size=1.2
)
p <- p + geom_abline(
    intercept = coef(fitRL.gam)[1],
    slope = coef(fitRL.gam)[2],
    col='steelblue',
    size=1.2
)
p <- p + geom_abline(
    intercept = coef(fitRL.sim)[1],
    slope = coef(fitRL.sim)[2],
    col='darkgray',
    size=1.2
)
p <- p + scale_color_manual('Approach', values=COLORS)
p <- p + xlab("Number of Phonemes in Inventory")
p <- p + ylab("Recovery Length (log)")
p <- p + scale_y_log10()
p <- p + theme_classic()
p <- p + theme(
    #legend.justification = c(1, -1),
    legend.position = c(0.85, 0.15)
)
ggsave('recovery.pdf', p)
