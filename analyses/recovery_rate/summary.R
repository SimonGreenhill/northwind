df <- read.delim('predict-gamm.dat', header=TRUE)

df <- df[, c("Language", "Length", 'TotalInventory')]

cat("SUMMARY\n")
print(summary(df$Length))

cat("\nSmallest:\n")
df[order(df$Length),][1, ]

cat("\nLargest:\n")
df[order(df$Length),][nrow(df), ]

cat("\nMore than 100,000:\n")
df[df$Length > 100000, ]

cat("\nMore than 1,000,000:\n")
df[df$Length > 1000000, ]

cat("\nSummary without outliers\n")
df[df$Length < 100000, ] -> x
print(summary(x))
