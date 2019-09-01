library(ggplot2)
options(scipen=10000)

languages_to_keep <- c("Czech", "Basque (Western Low Navarrese)")

df <- NULL
for (filename in list.files('.', "*.rate$")) {
    f <- read.delim(filename, header=TRUE)
    f$Bible <- tools::file_path_sans_ext(filename)
    f$PPercent <- (f$Position / max(f$Position)) * 100
    if (is.null(df)) { df <- f } else { df <- rbind(df, f) }
}

df$Category <- 'Bible'

# merge in JIPA.
jipa <- read.delim('../recovery_rate/coverage.dat', header=TRUE)
jipa$Bible <- NA
jipa$Family <- NULL
jipa$Category <- 'North Wind'

stopifnot(colnames(jipa) == colnames(df))

df <- rbind(df, jipa[jipa$Language %in% df$Language, ])

# rename
df$Language <- droplevels(df$Language)
levels(df$Language)[levels(df$Language) == "Basque (Western Low Navarrese dialect)"] <- "Basque (Western Low Navarrese)"


p1 <- ggplot(df, aes(x=Position, y=OPercent, color=Category)
)
p1 <- p1 + geom_line(aes(group=Bible))
p1 <- p1 + facet_wrap(~Language, ncol=3)
p1 <- p1 + xlab('Number of Tokens Observed') + ylab("Percentage of Observed Phonemes")
p1 <- p1 + theme_classic()
p1 <- p1 + ylim(0, 100)
p1 <- p1 + scale_x_log10()

pdf("recovery_rate_bibles.pdf", width=8, height=8)
print(p1)
x <- dev.off()



df.ortho <- df[df$Language %in% languages_to_keep, ]

p2 <- ggplot(df.ortho, aes(x=Position, y=OPercent, color=Category)
)
p2 <- p2 + geom_line(aes(group=Bible))
p2 <- p2 + facet_wrap(~Language, ncol=3)
p2 <- p2 + xlab('Number of Tokens Observed') + ylab("Percentage of Observed Phonemes")
p2 <- p2 + theme_classic()
p2 <- p2 + ylim(0, 100)
p2 <- p2 + scale_x_log10()
p2 <- p2 + geom_dl(aes(label = Category), method = list("last.points", dl.trans(x = x - 0.6, y = y + 0.3)), cex = 0.8)
p2 <- p2 + scale_color_manual(values=c("tomato", "steelblue"))
p2 <- p2 + theme(legend.position = "none")


pdf("recovery_rate_bibles-keep.pdf", width=8, height=4)
print(p2)
x <- dev.off()


# get sizes
sizes <- aggregate(df.ortho[, c("Position")], list(df.ortho$Bible), max)

sizes.c <- sizes[startsWith(sizes$Group.1, 'ces-'),]
sizes.b <- sizes[startsWith(sizes$Group.1, 'eus-'),]
