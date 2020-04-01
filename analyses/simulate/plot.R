#!/usr/bin/env Rscript
library(ggplot2)
library(ggridges)
library(ggrepel)
library(dplyr)
library(patchwork)

options(encoding = "UTF-8")
options(scipen=1000000)

COLORS <- c("darkorange", "steelblue", "slategrey")


plot_ridge <- function(full, colors=COLORS, legend=TRUE) {
    p <- ggplot(full, aes(y = Language, x = Length, color = Type))
    p <- p + stat_density_ridges(
        data = full[full$Type == 'Simulated',],
        quantile_lines = FALSE,
        rel_min_height = 0.02, scale=0.9
    )
    p <- p + geom_point(data = full[full$Type != 'Simulated',])
    p <- p + scale_x_log10(limits = c(10, 10000000))
    p <- p + theme_classic()
    # turn off y axis line to cut down chart junk
    p <- p + theme(
        axis.line.y = element_blank(),
        axis.ticks.y = element_blank()
    )

    p <- p + scale_color_manual(
        values = colors,
        guide = guide_legend(
            override.aes = aes(fill = NA, linetype = 0, size=2)
        )
    )

    # do I want a legend or not?
    if (legend == TRUE) {
        p <- p + theme(
            legend.justification = c(1, -1),
            legend.position = c(1, 0)
        )
    } else {
        p <- p + theme(legend.position="none")
    }
    p <- p + ylab("")
    p
}

plot_correlation <- function(data, x, y) {
    r <- cor.test(data[[x]], data[[y]], method="spearman")
    title <- sprintf(
        '%s vs %s (rho=%0.2f, p=%0.3f)', x, y, r$estimate, r$p.value
    )
    p <- ggplot(data, aes_string(x = x, y = y))
    p <- p + geom_point()
    p <- p + geom_smooth(method = "lm")
    p <- p + scale_x_log10(limits = c(10, 10000000))
    p <- p + scale_y_log10(limits = c(10, 10000000))
    p <- p + ggtitle(title)
    p <- p + theme_classic()
    p
}



df <- read.delim("results.txt", header=TRUE)

pred <- read.delim("../recovery_rate/predict-gamm.dat", header=TRUE, stringsAsFactors=FALSE)
pred$Replicate <- 0
pred$Type <- pred$Model
pred$Length <- pred$RecoveryLength

stopifnot(nrow(pred[pred$Model == 'LM', ]) == 158)
stopifnot(nrow(pred[pred$Model == 'GAM', ]) == 158)



# get labels with diacritics
labels <- read.delim('../statistics/statistics.dat', header=TRUE, stringsAsFactors=FALSE)
rownames(labels) <- labels$Language
pred$Language <- labels[pred$Language,]$FullLanguage
df$Language <- labels[df$Language,]$FullLanguage



full <- rbind(df, pred[c("Language", "Replicate", "Length", "Type")])
full$Type <- factor(full$Type, levels=c("GAM", "LM", "Simulated"))
# set ordering to be by the length under the LM estimate.
lm.estimates <- full[full$Type == 'LM',]
olevels <- lm.estimates[order(lm.estimates$Length), 'Language']
full$Language <- factor(full$Language, levels=rev(olevels))


# histograms
p <- ggplot(full, aes(x=Length, fill=Type, group=Type))
p <- p + geom_histogram()
p <- p + facet_grid(Type~., scales="free")
p <- p + theme_classic() + guides(fill = FALSE)
p <- p + scale_fill_manual(values=COLORS)
p <- p + ylab("")
p <- p + scale_x_log10()

ggsave('histogram.pdf', p)


# scatter plot comparison
p <- ggplot(full, aes(y=Language, x=Length, group=Type, color=Type))
p <- p + geom_point(alpha=0.9, size=0.8)
p <- p + scale_color_manual(values=COLORS)
p <- p + theme_classic()
p <- p + ylab("")
p <- p + scale_x_log10()

ggsave('comparison.png', p, width=8, height=18)


# ridge plot
p <- plot_ridge(full)

# PNG means that we keep the unicode characters in the language labels.
ggsave('comparison-ridges.png', p, height=20, dpi=300)

s1 <- levels(full$Language)[1: 79]
s2 <- levels(full$Language)[80: length(levels(full$Language))]

stopifnot(all(levels(full$Language) %in% c(s1, s2)))


# split the ridge plot in half
# - note the s2, s1 order as the factor levels are best-worst
p <- plot_ridge(full[full$Language %in% s2, ], legend=FALSE) +
     plot_ridge(full[full$Language %in% s1, ])

# PNG means that we keep the unicode characters in the language labels.
ggsave('comparison-ridges-split.png', p, height=10, width=16, dpi=300)





# Correlations
# convert to a wide dataframe with a median value for the simulations
wide <- full[full$Type == 'Simulated', ]
wide <- aggregate(wide$Length, list(wide$Language), median)
colnames(wide) <- c("Language", 'Simulation')

wide <- merge(wide, full[full$Type == 'LM', c("Language", "Length")])
colnames(wide)[3] <- 'LM'
wide <- merge(wide, full[full$Type == 'GAM', c("Language", "Length")])
colnames(wide)[4] <- 'GAM'


p <- plot_correlation(wide, 'LM', 'GAM') +
     plot_correlation(wide, 'LM', 'Simulation') +
     plot_correlation(wide, 'GAM', 'Simulation')

ggsave('correlations.png', p, width=18, dpi=300)


sink("summary.txt")
cat("OVERALL:\n")

for (method in c("LM", "GAM", "Simulated")) {
    cat(method, ":\n")
    d <- full[full$Type == method, ]
    s <- summary(d[, 'Length'])

    cat(sprintf(
        "%0.3f s.d=%0.3f [%0.3f-%0.3f]\n",
        s[['Median']],
        sd(d[, 'Length']),
        s[['Min.']],
        s[['Max.']]
    ))

    cat("\n")
}



cat("==========================================")
for (lang in sort(as.character(unique(full$Language)))) {
    cat(lang, ":\n")
    d <- full[full$Language == lang, ]
    s <- summary(d[d$Type == 'Simulated', 'Length'])

    cat("\tLM:       ", d[d$Type == 'LM', 'Length'], "\n")
    cat("\tGAM:      ", d[d$Type == 'GAM', 'Length'], "\n")
    cat(sprintf(
        "\tSimulated: %0.3f s.d=%0.3f [%0.3f-%0.3f]\n",
        s[['Median']],
        sd(d[d$Type == 'Simulated', 'Length']),
        s[['Min.']],
        s[['Max.']]
    ))
    cat("\n")

}


sink()




## Investigation:

stat <- read.delim('../statistics/statistics.dat', header=TRUE, stringsAsFactors=FALSE)
stat <- merge(stat, pred)

rr <- read.delim('../recovery_rate/coverage.dat', header=TRUE, stringsAsFactors=FALSE)
rr <- rr %>% group_by(Language) %>% slice(which.max(OPercent))
rr <- merge(rr, pred)


# bigger inventories take longer to recover
p <- ggplot(pred, aes(x=TotalInventory, y=RecoveryLength, color=Type, group=Type))
p <- p + geom_point() + geom_smooth()
p <- p + scale_y_log10()
p <- p + theme_classic()
ggsave('recoverylength_vs_inventory_size.pdf', p)


# length of transcript doesn't affect recovery _rate_
p <- ggplot(stat, aes(x=TranscriptLength, y=RecoveryLength, color=Type, group=Type))
p <- p + geom_point() + geom_smooth()
p <- p + scale_y_log10()
p <- p + theme_classic()
ggsave('recoverylength_vs_transcript_length.pdf', p)


# maximum observation percentage is big influence on recovery length
p <- ggplot(rr, aes(x=OPercent, y=RecoveryLength, label=Language, color=Type, group=Type))
p <- p + geom_point() + geom_smooth()
p <- p + geom_text_repel(
    data = subset(rr, RecoveryLength > 100000)
)
p <- p + scale_y_log10()
p <- p + theme_classic()
ggsave('recoverylength_vs_observed_percent.pdf', p)



p <- ggplot(rr, aes(x=OPercent, y=RecoveryLength, label=Language, color=Best, group=Type))
p <- p + geom_point()
p <- p + geom_text_repel(
    data = subset(rr, RecoveryLength > 100000)
)
p <- p + scale_y_log10()
p <- p + theme_classic()
