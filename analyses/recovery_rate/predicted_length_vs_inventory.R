library(ape)
library(caper)
library(ggplot2)
options(scipen=1000000)

df <- read.delim('predict-gamm.dat', header=TRUE)
labels <- read.delim('../statistics/statistics.dat', header=TRUE)


tree <- read.nexus('../../data/glottolog/glottolog.trees')
tree <- compute.brlen(tree, method="Grafen")

# make labels match...
df <- merge(df, labels, by="Language")


print("REMOVE OUTLIERS")
df <- df[df$Length <= 100000, ]  # removing outliers
tree <- drop.tip(tree, setdiff(tree$tip.label, df$Label))

cd <- comparative.data(
    phy=multi2di(tree),
    data=df,
    vcv=TRUE,
    names.col=Label,
    na.omit = FALSE,
    warn.dropped = TRUE
)
stopifnot(cd$dropped$tips == 0)
stopifnot(cd$dropped$unmatched.rows == 0)

sink("predicted_length_vs_inventory.txt")


cat('\n===========================================\n')
cat("LM:: Estimated Length vs Inventory\n")

m <- lm(Length~TotalInventory, data=df)
summary(m)


cat('\n===========================================\n')
cat("LM:: Log(Estimated Length) vs Inventory\n")
m <- lm(log(Length)~TotalInventory, data=df)
summary(m)

cat('\n===========================================\n')
cat("PGLS:: Estimated Length vs Inventory\n")

fit <- pgls(Length ~ TotalInventory, data=cd, lambda='ML', )
summary(fit)
par(mfrow=c(2,2))
pdf("pgls-length-vs-inventory.pdf")
plot(fit)
x <- dev.off()


cat('\n===========================================\n')
cat("PGLS:: Log(Estimated Length) vs Inventory **** \n")
fit.log <- pgls(log(Length) ~ TotalInventory, data=cd, lambda='ML')
summary(fit.log)
pdf("pgls-loglength-vs-inventory.pdf")
plot(fit.log)
x <- dev.off()

cat('\n===========================================\n')
cat("PGLS:: Log(Estimated Length) vs Log(Inventory)\n")
fit.loglog <- pgls(log(Length) ~ log(TotalInventory), data=cd, lambda='ML')
summary(fit.loglog)
pdf("pgls-loglength-vs-loginventory.pdf")
plot(fit.loglog)
x <- dev.off()


sink()

# DECISION:
# Log transformed Length is better as it makes the Q-Q plot track the line closer
# and the residuals are less clustered.
#
# Log(Length) and log(TotalInventory) is less preferred
#   - brings back the tails in the Q-Q
#   - no natural reason for log of inventory
#   - substantially lower R2
#
#  Decided to use Log(Length) ~ TotalInventory as best model.



predicted <- data.frame(
    TotalInventory=df$TotalInventory,
    Length=exp(predict(fit.log))
)

predicted <- data.frame(
    TotalInventory=1:100,
    LogLength=predict(fit.log, data.frame(TotalInventory=1:100), interval='prediction'),
    Length=exp(predict(fit.log, data.frame(TotalInventory=1:100), interval='prediction'))
)

p <- ggplot(df, aes(x=TotalInventory, y=Length))
p <- p + geom_point()
p <- p + geom_line(data=predicted, col='darkorange', size=1.2)
p <- p + scale_y_log10()
p <- p + xlab('Inventory Size') + ylab("Predicted Transcript Length Needed for Full Recovery")
p <- p + theme_classic() + guides(colour="none")

ggsave("predicted_length_vs_inventory.pdf", p)
ggsave("predicted_length_vs_inventory.png", p)

sink("predicted_length_vs_inventory.log")
for (i in 1:100) {
    x = predicted[i+1,]$Length - predicted[i,]$Length
    print(paste(i, x))
}
sink()
