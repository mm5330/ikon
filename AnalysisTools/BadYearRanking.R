###############################################################################

# IRI Farmer Bad Year Ranking Algorithm

# By Max Mauerman

# Objective: Generate a probabalistic ranking of years from worst to best from
# data on farmers' pairwise comparison of years. (Bradley-Terry algorithm)

##############################################################################

## Setup

setwd("/Users/mmauerman/Documents/IRI - KON")
library(readxl)
library(devtools, quietly=TRUE)
library(qwraps2)
library(pls)
library(DescTools)
library(rrcov)
library(rmarkdown)
library(car)
library(relaimpo)
library(dplyr)
library(tidyverse)
library(magrittr)
library(BradleyTerry2)
install_github("vqv/ggbiplot")
source_gist("https://gist.github.com/dfalster/5589956")
options(qwraps2_markup = "markdown")
set.seed(1000)

## Generate random data for testing (in future, will use actual data)

# Raw pairwise comparison data

gender <- sample(x = 0:1, size = 1000, replace = T)
"2001.2002" <- sample(x = 0:1, size = 1000, replace = T)
"2001.2003" <- sample(x = 0:1, size = 1000, replace = T)
"2001.2004" <- sample(x = 0:1, size = 1000, replace = T)
"2001.2005" <- sample(x = 0:1, size = 1000, replace = T)
"2002.2003" <- sample(x = 0:1, size = 1000, replace = T)
"2002.2004" <- sample(x = 0:1, size = 1000, replace = T)
"2002.2005" <- sample(x = 0:1, size = 1000, replace = T)
"2003.2004" <- sample(x = 0:1, size = 1000, replace = T)
"2003.2005" <- sample(x = 0:1, size = 1000, replace = T)
"2004.2005" <- sample(x = 0:1, size = 1000, replace = T)

pairwise <- data.frame(gender, "2001.2002" = get('2001.2002'), "2001.2003" = get('2001.2003'), "2001.2004" = get('2001.2004'), "2001.2005" = get('2001.2005'),
                       "2002.2003" = get('2002.2003'), "2002.2004" = get('2002.2004'), "2002.2005" = get('2002.2005'),
                       "2003.2004" = get('2003.2004'), "2003.2005" = get('2003.2005'),
                       "2004.2005" = get('2004.2005'),
                       check.names = F)
pairwise$id <- 1:nrow(pairwise)

# Yearly covariates

year <- c(2001:2005)
precip <- sample(x = 0:100, size = 5)

yearly.cov <- data.frame(year,precip)

## Reshape data

# Individual preferences

range <- c(2001:2005)
combs.prefs <- choose(length(range),2) * nrow(pairwise)
counts.prefs <- data.frame(matrix(NA, nrow = combs.prefs, ncol = 4))
counts.prefs <- 
  counts.prefs %>%
  rename_at(1:4,~c("year1","year2","win1","win2"))

z <- 1
for (w in 1:nrow(pairwise)) {
  for (x in range) {
    for (y in range[range != x])
      if (x < y) { 
        
        counts.prefs$year1[z] <- x
        counts.prefs$year2[z] <- y
        counts.prefs$id[z] <- w
        
        z <- (z + 1)
        
      }
    else {}
  }
}

for (w in 1:nrow(pairwise)) {
  for (x in range) {
    for (y in range[range != x])
      if (x < y) { 
        var <- paste(x,y,sep=".")
        a <- pairwise[w,var]
        b <- ifelse((pairwise[w,var] == 1),0,1)
        counts.prefs$win1[match(counts.prefs$year1, x) & match(counts.prefs$year2, y) & match(counts.prefs$id, w)] <- a
        counts.prefs$win2[match(counts.prefs$year1, x) & match(counts.prefs$year2, y) & match(counts.prefs$id, w)] <- b
      }
    else {}
  }
}


counts.prefs$year1_fac <- factor(counts.prefs$year1, 
                             labels = unique(c(counts.prefs$year1, counts.prefs$year2)),
                             levels = unique(c(counts.prefs$year1, counts.prefs$year2)))

counts.prefs$year2_fac <- factor(counts.prefs$year2,
                             labels = unique(c(counts.prefs$year1, counts.prefs$year2)),
                             levels = unique(c(counts.prefs$year1, counts.prefs$year2)))

# Individual covariates

indiv.cov <- data.frame(gender = pairwise[,1], id = pairwise[,12])

## Bind dataframes to list

data.counts <- list(counts = counts.prefs,indiv.cov = indiv.cov,yearly.cov = yearly.cov)
data.prefs <- list(preferences = counts.prefs,indiv.cov = indiv.cov,yearly.cov = yearly.cov)

## Estimate Bradley-Terry model

model <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac, 
             formula = ~ .. + 
             year[..] +
             gender[id] * precip[..],
             data = data.prefs)
model

## Extract estimated ability scores and rank them

ranks <- BTabilities(model)
ranks_ordered <- data.frame(ranks)
ranks_ordered <- ranks_ordered[order(ranks_ordered$ability),]
ranks_ordered

## Plot confidence intervals 

ranks.qv <- qvcalc(ranks)
plot(ranks.qv) 