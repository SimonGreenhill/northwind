library(ggplot2)
df <- read.delim('results.dat', header=TRUE)

print("PhoibleRank_vs_TextRank: ")
print(cor.test(df$Rank, df$R, method="spearman"))
p <- ggplot(df, aes(x=Rank, y=R)) + geom_point() + geom_smooth(method="lm") + theme_classic()
ggsave('PhoibleRank_vs_TextRank.pdf', p)


print("PhoibleRank_vs_CaptureRate: ")
print(cor.test(df$Rank, df$C, method="spearman"))
p <- ggplot(df, aes(x=Rank, y=C)) + geom_point() + geom_smooth(method="lm") + theme_classic()
ggsave('PhoibleRank_vs_CaptureRate.pdf', p)

