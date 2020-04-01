library(ggplot2)
library(mgcv)

options(scipen = 5)

# fits all models including:
# 0: a linear model
# 1-N: GAMs with varying knots (specified by vector given in `ks`)
#
# `ks` specifies which models to run. It should probably include 0, up to the
# number of knots. If you specify more knots than the available degrees of
# freedom then mgcv will generate errors. Therefore you probably want to set
# the max value in `ks` to the number of unique values in your data column e.g.
# > ks=0:length(unique(d$OPercent))
#
# Returns a list of:
#  1. df -- a data frame of results
#  2. models -- a list of fitted model objects
#  3. x  -- the x axis values
#  4. y -- the y axis values

fitModels <- function(d, ks=0:2, method="REML") {
    percent <- seq(0, 100, 1)

    models <- list()
    df <- data.frame(
        Model = NULL, k = NULL, RecoveryLength = NULL, RSQ = NULL,
        ResidDF = NULL, ChiSQ = NULL, EDF = NULL, AIC = NULL
    )

    for (k in ks) {
        # equiv to lm
        if (k == 0) {
            m <- mgcv::gam(
                TranscriptLength ~ OPercent,
                data = d, method = method, family = poisson(link = log),
                select = TRUE
            )
        } else {
            m <- mgcv::gam(
                TranscriptLength ~ s(OPercent, k = k),
                data = d, method = method, family = poisson(link = log),
                select = TRUE
            )
        }

        p <- predict(m, data.frame(OPercent = percent), family = poisson(link = log))
        summ <- summary.gam(m)
        models[[as.character(k)]] <- m

        df <- rbind(df, data.frame(
            Model = ifelse(k == 0, 'LM', 'GAM'),
            k = k,
            RecoveryLength = exp(p[[100]]),
            RSQ = summ$r.sq,
            ResidDF = summ$residual.df,
            ChiSQ = ifelse(k == 0, NA, summ$chi.sq),
            EDF = ifelse(k == 0, NA, summ$edf),
            AIC = AIC(m)
        ))
    }
    # flag best model
    df$Best <- df$AIC == min(df$AIC, na.rm = TRUE)
    list(df = df, models = models, x = log(d$TranscriptLength), y = d$OPercent)
}




plotModels <- function(results, title, xlab="x", ylab="y") {
    percent <- seq(0, 100, 1)

    # find best model
    best <- as.character(results$df[results$df$Best, 'k'][[1]])
    p.best <- predict(
        results$models[[best]],
        data.frame(OPercent = percent),
        family = poisson(link = log)
    )
    p.lm <- predict(
        results$models[['0']],
        data.frame(OPercent = percent),
        family = poisson(link = log)
    )

    plot(
        results$x, results$y,
        xlab = xlab, ylab = ylab,
        xlim = c(0, max(p.best)), ylim = c(0, 100),
        pch = 19, cex = 0.6, col = "#333333",
        main = sprintf(
            "%s
            GLM=%0.0f, GAM=%0.0f",
            title,
            results$df[results$df$k == '0', 'RecoveryLength'],
            results$df[results$df$k == best, 'RecoveryLength']
        )
    )

    for (r in names(results$models)) {
        p <- predict(
            results$models[[r]],
            data.frame(OPercent = percent),
            family = poisson(link = log)
        )
        color <- ifelse(r == '0', 'black', 'lightblue')
        lines(p, percent, col = color)
    }

    # over plot best fitting model and lm
    lines(p.best, percent, col = 'tomato')
    lines(p.lm, percent, col = 'black')
    # and over plot the real data points so they're not hidden
    points(results$x, results$y, pch = 19, cex = 0.6, col = "#333333")
}



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

    
    # Set maximum knots to be low so we don't overfit given the small size of the data.
    max_knots <- 3
    cat(sprintf("Calculating %s using k=%s", lang, max_knots), sep="\n")
    
    res <- fitModels(d, ks = c(0, max_knots))
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
