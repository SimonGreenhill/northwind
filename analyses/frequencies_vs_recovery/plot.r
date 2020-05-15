library(ggplot2)
library(ggrepel)
library(viridis)
library(patchwork)

df <- read.delim('results.dat', header=TRUE)

# 1. Rank = how common it is cross-linguistically (= rank in Phoible)
# 2. Ni = number of illustrations listing the phoneme in inventory
# 3. Nt = number of illustrations attesting the phoneme in NWS text
# 4. C = Nt/Ni (i.e. type capture rate) = the proportion of languages with phoneme
#    P that have P observed in the illustration.
# 5. R = rank in JIPA texts by phoneme frequency (summed over all languages).
# 6. AverageFirstObservationPercent = the average time to the first observation
#   of Phoneme P


# Remove anything where we do not have the phoneme in the JIPA article
df <- df[df$Ni > 0, ]

# convert NI to Rank for consistency
df$RankNI <- rank(df$Ni, ties="average")


cor.test(df$AverageFirstObservationPercent, df$Rank, method="spearman")

cor.test(df$AverageFirstObservationPercent, df$Ni, method="spearman")

#-----------------

p <- ggplot(df, aes(x=AverageFirstObservationPercent, y=Rank, color=Rank))
p <- p + geom_point()
p <- p + theme_classic()
#p <- p + xlab("Average percentage of NWS text elapsed before first observation of phoneme")
p <- p + ylab("Global Ranking of Phoneme (Phoible)")
p <- p + scale_color_continuous('Type Capture Rate', type = "viridis")
p <- p + guides(color="none")

# Time to first observation vs. x-ling freq (in JIPA Ni)
q <- ggplot(df, aes(x=AverageFirstObservationPercent, y=Ni, color=Rank))
q <- q + geom_point()
q <- q + theme_classic()
#q <- q + xlab("Average percentage of NWS text elapsed before first observation of phoneme")
q <- q + ylab("Number of languages with Phoneme (JIPA)")
q <- q + scale_color_continuous('Global Ranking', type = "viridis")
q <- q + theme(
    legend.direction = "horizontal",
    legend.position=c(0.95, 0.95),
    legend.justification=c(1, 1)
)


p <- p + geom_point(data=df[df$AverageFirstObservationPercent==100,], color="tomato")
q <- q + geom_point(data=df[df$AverageFirstObservationPercent==100,], color="tomato")

p <- p + xlab("") + ggtitle("a. Global Ranking vs. First Observation")
q <- q + xlab("") + ggtitle("b. JIPA Frequency vs. First Observation")

#p <- p + geom_smooth(method="lm", color="steelblue")
#q <- q + geom_smooth(method="lm", color="steelblue")

pq <- p + q + plot_annotation(tag_levels = 'a')
pq <- pq / grid::textGrob(  # HACK
    'Average percentage of NWS text elapsed before first observation of phoneme',
    just = "centre"
)
pq <- pq + plot_layout(heights = unit(c(11, 0.5), c('null', 'cm')))

ggsave('firstobs.pdf', pq, height=6, width=10)


rare <- df[df$Rank >= 200, ]

p <- ggplot(rare, aes(x=AverageFirstObservationPercent, y=Rank, label=Phoneme, color=Rank))
p <- p + geom_point() + geom_text_repel()
p <- p + ylab("Number of languages with Phoneme (Phoible)")
p <- p + xlab("Average percentage of NWS text elapsed before first observation of phoneme")
p <- p + scale_color_continuous('', type = "viridis")
p <- p + theme_classic()
p <- p + guides(color="none")

ggsave("rare-1.png", p)



p <- ggplot(rare, aes(x = AverageFirstObservationPercent, y = 1, label = Phoneme, color=Rank))
p <- p + geom_point()
p <- p + geom_text_repel(
    nudge_y      = 0.05,
    direction    = "x",
    vjust        = 0,
    segment.size = 0.1
)
p <- p + scale_color_continuous('', type = "viridis")
p <- p + ylab("Average percentage of NWS text elapsed before first observation of phoneme")
p <- p + theme_classic()
p <- p + theme(
    axis.line.y  = element_blank(),
    axis.ticks.y = element_blank(),
    axis.text.y = element_blank(),
    axis.title.y = element_blank()
)


ggsave("rare-2.png", p)
