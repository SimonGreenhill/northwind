#!/usr/bin/env Rscript
library(ggplot2)
library(ggridges)
library(ggrepel)
library(dplyr)
library(patchwork)
library(viridis)

options(encoding = "UTF-8")
options(scipen=1000000)

COLORS <- c("steelblue", "darkorange", "slategrey")


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

# filter the GAM results to the correct knots
pred <- pred[pred$k %in% c(0, 8), ]

stopifnot(nrow(pred[pred$Model == 'LM', ]) == 158)
stopifnot(nrow(pred[pred$Model == 'GAM', ]) == 158)



# get labels with diacritics
labels <- read.delim('../statistics/statistics.dat', header=TRUE, stringsAsFactors=FALSE)
rownames(labels) <- labels$Language
pred$Language <- labels[pred$Language,]$FullLanguage
df$Language <- labels[df$Language,]$FullLanguage



full <- rbind(df, pred[c("Language", "Replicate", "Length", "Type")])
full$Type <- factor(full$Type, levels=c("LM", "GAM", "Simulated"))
# set ordering to be by the length under the LM estimate.
lm.estimates <- full[full$Type == 'LM',]
olevels <- lm.estimates[order(lm.estimates$Length), 'Language']
full$Language <- factor(full$Language, levels=rev(olevels))



# histograms
p.lm <- ggplot(full[full$Type=='LM', ], aes(x=Length)) +
    geom_histogram(fill=COLORS[[1]]) +
    theme_classic() +
    ylab("Number") + xlab("") +
    scale_x_log10(limits=c(10, 100000000)) +
    ggtitle("a. LM")

p.gam <- ggplot(full[full$Type=='GAM', ], aes(x=Length)) +
    geom_histogram(fill=COLORS[[2]]) +
    theme_classic() +
    ylab("Number") + xlab("") +
    scale_x_log10(limits=c(10, 100000000)) +
    ggtitle("b. GAM")

p.sim <- ggplot(full[full$Type=='Simulated', ], aes(x=Length)) +
    geom_histogram(fill=COLORS[[3]]) +
    theme_classic() +
    ylab("Number") + xlab("Number of tokens required for complete recovery") +
    scale_x_log10(limits=c(10, 100000000)) +
    ggtitle("c. Simulations")

p <- p.lm / p.gam / p.sim

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
# I do not know *why* scale_color_manual in here is losing the level ordering
# and messing up the colors, which is why we have the manual ordering here to
# ensure that GAM is orange like the other plots.
p <- plot_ridge(full, colors=c(COLORS[[2]], COLORS[[1]], COLORS[[3]]))

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


# simulation only ridgeplot
full.sim <- merge(
    full[full$Type == 'Simulated', ],
    pred[pred$Model=='LM', c("Language", "TotalInventory")],
    by = "Language"
)

full.sim$Language <- factor(
    full.sim$Language,
    levels = unique(full.sim$Language[order(full.sim$TotalInventory)])
)

upper <- quantile(full.sim$Length, probs=c(0.95))

p <- ggplot(full.sim, aes(
    y = Language, x = Length, color = TotalInventory, fill = TotalInventory
))
p <- p + geom_vline(xintercept = median(full.sim$Length))
p <- p + geom_vline(xintercept = upper)
p <- p + stat_density_ridges(quantile_lines = FALSE, rel_min_height = 0.05, scale = 0.9)
p <- p + scale_x_log10(limits = c(50, 100000))
p <- p + scale_fill_viridis("Phonemes") + scale_color_viridis()
p <- p + guides(color="none")
p <- p + theme_classic()
p <- p + theme(
    legend.position = c(0, 1),
    legend.justification = c(0, 1)
)

# turn off y axis line to cut down chart junk
p <- p + theme(
    axis.line.y = element_blank(),
    axis.ticks.y = element_blank()
)
p <- p + ylab("") + xlab("Number of tokens required for full recovery")

# PNG means that we keep the unicode characters in the language labels.
ggsave('comparison-ridges-simonly.png', p, height = 18, width = 10, dpi = 300)



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

# worst case scenario...
p <- ggplot(full[full$Type=='Simulated', ], aes(x=Length, group=Type, fill=Type))
p <- p + geom_histogram()
#p <- p + geom_vline(xintercept=median(full[full$Type=='Simulated', 'Length']))
#p <- p + geom_vline(xintercept=twosd)
#p <- p + facet_grid(Type~., scales="free")
p <- p + scale_fill_manual(values=c("slategray"))
p <- p + theme_classic()
p <- p + guides(fill="none")
p <- p + ylab("Number of Simulations")
p <- p + xlab("Estimated Amount of Text Needed for Full Recovery")
p <- p + scale_x_log10()

ggsave("simulated-overall.pdf", p, height=8, width=8)

sink("simulated-overall.log")

cat(paste("Median:", median(full[full$Type=='Simulated', "Length"]), "\n"))
cat(paste("Min:", min(full[full$Type=='Simulated', "Length"]), "\n"))
cat(paste("Max:", max(full[full$Type=='Simulated', "Length"]), "\n"))
cat(paste("SD:", sd(full[full$Type=='Simulated', "Length"]), "\n"))

twosd <- mean(full[full$Type=='Simulated', "Length"]) + 2 * sd(full[full$Type=='Simulated', "Length"])

cat(paste("95%:", twosd, "\n"))

sink()

# worst case scenarios
# top 10 worst
f <- full[full$Type == 'Simulated', ]
f <- f[order(f$Length), ]

head(f, 5)

tail(f, 10)



# 95 %
qtiles <- c(0.5, 0.95, 0.99, 1.0)
print("Qtile LM")
quantile(full[full$Type == 'LM', 'Length'], probs=qtiles)

print("Qtile GAM")
quantile(full[full$Type == 'GAM', 'Length'], probs=qtiles)

print("Qtile Simulation")
quantile(full[full$Type == 'Simulated', 'Length'], probs=qtiles)

print("Qtile OVERALL")
quantile(full$Length, probs=qtiles)
