#!/usr/bin/env Rscript
library(dplyr)

t <- read.table('predict-gamm.dat', sep="\t", header=TRUE)

t.lm <- t[t$Model == 'LM', ]
t.gam <- t[t$Model == 'GAM', ]

# do it the long way

lm_better <- c()
for (lang in unique(t.lm$Language)) {
    if (t.lm[t.lm$Language == lang, ]$Best == TRUE) {
        cat(paste("LM better for", lang, "\n"))
        lm_better <- c(lm_better, lang)
    }
}

cat("\n\nhow many GAMs fit better than the LM using AIC?\n")
cat(sprintf(
    "%d of %d (%0.2f%%)",
    (nrow(t) - length(lm_better)),
    nrow(t),
    ((nrow(t) - length(lm_better)) / nrow(t)) * 100
))
cat("\n\n")

t.gam <- t.gam[t.gam$Language %in% lm_better == FALSE, ]
t.gam.best <- t.gam[t.gam$Best == TRUE, ]
# make sure we don't have any of the better LM's in this set:

# sort by k and then remove the duplicates:
t.gam.best <- t.gam.best[order(t.gam.best$k), ]
t.gam.best <- t.gam.best %>% distinct(Language, .keep_all = TRUE)


stopifnot(nrow(t.gam.best) + length(lm_better) == length(unique(t.lm$Language)))

cat("Minimum: ")
print(min(t.gam.best$AIC))
cat("\n")

cat("Maximum: ")
print(max(t.gam.best$AIC))
cat("\n")

cat("Median: ")
print(median(t.gam.best$AIC))
cat("\n")

cat("SD: ")
print(sd(t.gam.best$AIC))
cat("\n")

