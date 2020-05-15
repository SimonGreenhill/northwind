library(ggplot2)
library(mgcv)

options(scipen = 5)
source('lib.R')

# Set maximum knots to be low so we don't overfit given the small size of the data.
max_knots <- 8

records <- read.delim('coverage.dat', header=TRUE)

completed <- NULL

pdf('predict-gamm-individual.pdf')
par(mfrow = c(2, 2))
for (lang in unique(records$Language)) {

    d <- records[records$Language == lang,]
    d <- d[d$TranscriptLength > 0,]  # remove zero
    # and because our raw data is scanning the transcript in percentage blocks
    # we get runs of rows where the Observed number of phonemes is the same,
    # e.g. see the run of 14 below:
    #           Language        Position PPercent OPercent Observed
    #           Zurich German        5        1    5.455        3
    #           Zurich German       11        2   14.545        8
    #           Zurich German       16        3   16.364        9
    #           Zurich German       21        4   16.364        9
    #           Zurich German       26        5   16.364        9
    #           Zurich German       32        6   21.818       12
    #           Zurich German       37        7   25.455       14
    #           Zurich German       42        8   25.455       14
    #           Zurich German       48        9   25.455       14
    #           Zurich German       53       10   25.455       14
    #           Zurich German       58       11   25.455       14
    #           Zurich German       63       12   25.455       14
    #
    # ... these runs will interfere with the GAM, especially if they're near
    # the end of the sequence (where they will make the tail of the curve flatter)
    # and hence make inflate the time for recovery of the full phoneme inventory.
    d <- d[!duplicated(d$Observed), ]  # remove duplicate observations

    
    cat(sprintf("Calculating %s using k=%s", lang, max_knots), sep="\n")
    
    res <- fitModels(d, ks = c(0:max_knots))
    warnings()  # print any warnings

    plotModels(res, lang, xlab = "TranscriptLength", ylab = "Percent Observed")
    warnings()  # print any warnings

    # add some extra data to res$df
    res$df$Language <- d$Language[[1]]
    res$df$Family <- d$Family[[1]]
    res$df$TotalInventory <- d$TotalInventory[[1]]

    if (is.null(completed)) {
        completed <- res$df
    } else {
        completed <- rbind(completed, res$df)
    }
    
}
dev.off()

warnings()

p <- ggplot(completed[completed$Best,], aes(x = TotalInventory, y = RecoveryLength))
p <- p + geom_point() + geom_smooth(method = "gam", method.args = list(k = 20))
p <- p + scale_y_log10()
p <- p + xlab("Number of Phonemes in Inventory")
p <- p + ylab("Necessary Transcript Length")
p <- p + theme_classic()

ggsave('predict-gamm-combined.pdf', p)


p <- ggplot(completed[completed$k==0,], aes(x = TotalInventory, y = RecoveryLength))
p <- p + geom_point() + geom_smooth(method = "gam", method.args = list(k = 20))
p <- p + scale_y_log10()
p <- p + xlab("Number of Phonemes in Inventory")
p <- p + ylab("Necessary Transcript Length")
p <- p + theme_classic()
ggsave('predict-lm-combined.pdf', p)



p <- ggplot(completed[completed$Best,], aes(RecoveryLength))
p <- p + geom_histogram()
p <- p + scale_x_log10()
p <- p + theme_classic()
ggsave('predict-gamm-histogram.pdf', p)


p <- ggplot(completed[completed$k==0,], aes(RecoveryLength))
p <- p + geom_histogram()
p <- p + scale_x_log10()
p <- p + theme_classic()
ggsave('predict-lm-histogram.pdf', p)



sink("summary_of_best_estimates.txt")
cat("GAMM:\n")
summary(completed[completed$Best,]$RecoveryLength)
sd(completed[completed$Best,]$RecoveryLength)
cat("\n\n")
cat("LM:\n")
summary(completed[completed$k==0,]$RecoveryLength)
sd(completed[completed$k==0,]$RecoveryLength)
sink()


write.table(
    completed, file = "predict-gamm.dat",
    quote = FALSE, row.names = FALSE, sep = "\t"
)
