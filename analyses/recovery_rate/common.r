
classify <- function(value) {
    return(signif(value, 1))
}

records <- read.delim('coverage.dat', header=TRUE)
records$InventorySize <- sapply(records$TotalInventory, classify)
records$InventorySize <- as.factor(records$InventorySize)

