library(ggplot2)
library(mgcv)
library(itsadug)
source('common.r')

records <- itsadug::start_event(records, column="OPercent", event=c("Language"))

m.OP <- bam(TranscriptLength ~ OPercent,
    data=records, method="ML", link=Gamma(link=log))

m.OPF <- bam(TranscriptLength ~ OPercent
    + s(Family, bs="re")
    data=records, method="ML", link=Gamma(link=log)
)

m.OPFL <- bam(TranscriptLength ~ OPercent
    + s(Family, bs="re")
    + s(Language, bs="re"),
    data=records, method="ML", link=Gamma(link=log)
)

m.OPFLTI <- bam(TranscriptLength ~ OPercent
    + s(Family, bs="re")
    + s(Language, bs="re")
    + s(TotalInventory, bs="re"),
    data=records, method="ML", link=Gamma(link=log)
)

m.OPFLTI.ar <- bam(TranscriptLength ~ OPercent
    + s(Family, bs="re")
    + s(Language, bs="re")
    + s(TotalInventory, bs="re"),
    data=records, method="ML", link=Gamma(link=log),
    rho=acf_resid(m.OPFLTI)[2]
)


m.OPFLTIF <- bam(TranscriptLength ~ OPercent
    + s(Family, bs="re")
    + s(Language, bs="re")
    + s(TotalInventory, bs="re")
    + s(TotalInventory, Family, bs="re"),
    data=records, method="ML", link=Gamma(link=log)
)


m.OPFLTIF.ar <- bam(TranscriptLength ~ OPercent
    + s(Family, bs="re")
    + s(Language, bs="re")
    + s(TotalInventory, bs="re")
    + s(TotalInventory, Family, bs="re"),
    data=records, method="ML", link=Gamma(link=log),
    rho=acf_resid(m.OPFLTIF)[2]
)



anova(m.OP, m.OPF, m.OPFL, m.OPFLTI, m.OPFLTIF, test="Chisq")

# OPFL is best
m.OPFL.ar <- bam(TranscriptLength ~ OPercent
    + s(Family, bs="re")
    + s(Language, bs="re"),
    data=records, method="ML", link=Gamma(link=log),
    rho=acf_resid(m.OPFL)[2]

)

anova(m.OPFL, m.OPFL.ar, test="Chisq")


pred <- predict(m6.ar,
    data.frame(
        OPercent=seq(0, 100, 1),
        Family=rep('Austronesian', 101),
        TotalInventory=rep(NA, 101),
        TranscriptLength=rep(NA, 101)
    )
)

p <- ggplot(dat, aes(x=TotalInventory, y=TranscriptLength))
p <- p + geom_point() + geom_smooth(method="gam", data=pred)
p <- p + scale_y_log10()
p <- p + xlab("Number of Phonemes in Inventory")
p <- p + ylab("Necessary Transcript Length")
p <- p + theme_classic()


