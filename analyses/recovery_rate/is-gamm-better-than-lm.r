#!/usr/bin/env Rscript

t <- read.table('predict-gamm.dat', sep="\t", header=TRUE)

cat("how many chi-sq tests are significant?\n")
cat(sprintf(
    "%d of %d",
    nrow(t[t$ChiSig <= 0.05,]),
    nrow(t)
))
cat("\n\n")

cat("which tests are not significant?\n")
print(t[t$ChiSig > 0.05,])
cat("\n\n")

cat("Minimum: ")
print(min(t$ChiSig))
cat("\n")

cat("Maximum: ")
print(max(t$ChiSig))
print(max(t[t$ChiSig <= 0.05,]$ChiSig))
cat("\n")
