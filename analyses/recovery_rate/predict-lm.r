library(ggplot2)
source('common.r')

make_fig <- function(x, y, prediction, percent, title) {
    plot(
        x, y,
        ylim=c(0, 100),
        xlim=c(0, max(p) + 10),
        pch=19, col="#333333",
        main=title
    )
    lines(prediction, percent, col="orange", lwd=2)
}

records$LogTL <- log(records$TranscriptLength + 1)

percent <- seq(0, 100, 1)

pdf('predict-lm-individual.pdf')
completed = data.frame(Language=c(), Length=c(), TotalInventory=c())
for (lang in levels(records$Language)) {
    d <- records[records$Language == lang,]
    m <- lm(LogTL ~ OPercent, data = d)
    p <- predict(m, data.frame(OPercent = percent))

    make_fig(d$LogTL, d$OPercent, p, percent, lang)

    completed <- rbind(completed,
        data.frame(
            Language=lang,
            Length=exp(p[100]),
            TotalInventory=d$TotalInventory[[1]]
        )
    )
}
dev.off()

options(scipen=5)

p <- ggplot(completed, aes(x=TotalInventory, y=Length))
p <- p + geom_point() + geom_smooth(method="lm")
p <- p + scale_y_log10()
p <- p + xlab("Number of Phonemes in Inventory")
p <- p + ylab("Necessary Transcript Length")
p <- p + theme_bw()

pdf('predict-lm-combined.pdf')
print(p)
dev.off()

completed <- completed[order(completed$Length),]
write.table(completed, file="predict-lm.dat", quote=FALSE, row.names=FALSE, sep="\t")
