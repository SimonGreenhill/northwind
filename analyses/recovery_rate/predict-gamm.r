library(ggplot2)
library(mgcv)
source('common.r')

make_fig <- function(x, y, predicted_lm, predicted_gam, percent, title) {
    plot(
        x, y,
        ylim=c(0, 100),
        xlim=c(0, max(p) + 10),
        pch=19, cex=0.6,
        col="#333333",
        main=title
    )
    lines(predicted_lm, percent, col="red")
    lines(predicted_gam, percent, col="blue")
}


percent <- seq(0, 100, 1)

pdf('predict-gamm-individual.pdf')
completed = data.frame(Language=c(), Length=c(), TotalInventory=c(), ChiSig=c(), RSq=c())
for (lang in levels(records$Language)) {
    print(paste("Calculating ", lang))
    d <- records[records$Language == lang,]
    d <- d[d$TranscriptLength > 0,]

    # equivalent to lm
    m <- gam(TranscriptLength ~ OPercent, data=d, method="ML", family=Gamma(link=log))
    mg <- gam(TranscriptLength ~ s(OPercent, k=5), data=d, method="ML", family=Gamma(link=log))

    a <- anova(m, mg, test="Chisq")

    p <- predict(m, data.frame(OPercent=percent), family=Gamma(link=log))
    pg <- predict(mg, data.frame(OPercent=percent), family=Gamma(link=log))

    make_fig(log(d$TranscriptLength), d$OPercent, p, pg, percent, lang)

    completed <- rbind(completed,
        data.frame(
            Language=lang,
            Length=exp(pg[100]),
            TotalInventory=d$TotalInventory[[1]],
            ChiSig=a$`Pr(>Chi)`[[2]],
            RSq=summary(mg)$r.sq
        )
    )
}
dev.off()

options(scipen=5)

p <- ggplot(completed, aes(x=TotalInventory, y=Length))
p <- p + geom_point() + geom_smooth(method="gam", method.args=list(k=5))
p <- p + scale_y_log10()
p <- p + xlab("Number of Phonemes in Inventory")
p <- p + ylab("Necessary Transcript Length")
p <- p + theme_classic()

pdf('predict-gamm-combined.pdf')
print(p)
dev.off()

completed <- completed[order(completed$Length),]
write.table(completed, file="predict-gamm.dat", quote=FALSE, row.names=FALSE, sep="\t")

