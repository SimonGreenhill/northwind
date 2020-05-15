library(mgcv)

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




plotModels <- function(results, title, xlab="x", ylab="y", xlim=c(0, max(p.best))) {
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
        xlim = xlim, ylim = c(0, 100),
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

