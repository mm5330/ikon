###############################################################################

# IRI Madagascar 2020 Data Analysis

# By Max Mauerman

# Compares farmer bad year ranking measured two ways:

# 1. Direct ranking exercise

# 2. Pairwise comparisons (estimated via Bradley-Terry algorithm)

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
library(ggplot2)
library(dotwhisker)
set.seed(1000)

## Load and clean data

mad <- read_xlsx("Madagascar data.xlsx")

keep <- c("Region","District","Commune","Village/s","What was the worst year?","2nd worst","3rd worst","4th worst","5th worst","6th worst","7th worst","8th worst","Pair 1 year 1","Pair 1 year 2","Which year was drier:\n\n1. ${pair_1_y1}\n2. ${pair_1_y2}","Pair 2 year 1","Pair 2 year 2","Which year was drier:\n\n1. ${pair_2_y1}\n2. ${pair_2_y2}","Pair 3 year 1","Pair 3 year 2","Which year was drier:\n\n1. ${pair_3_y1}\n2. ${pair_3_y2}")
data = subset(mad,select = keep) 
data <- 
  data %>%
    rename_at(1:21,~c("region","district","commune","village","ranking_1","ranking_2","ranking_3","ranking_4","ranking_5","ranking_6","ranking_7","ranking_8","pair_1_y1","pair_1_y2","pair_1","pair_2_y1","pair_2_y2","pair_2","pair_3_y1","pair_3_y2","pair_3"))

## Aggregate ranked data

for(x in 1:8) {


name <- paste("ranking_",x,sep="")
var <- paste("data$ranking_",x,sep="")
rank <- rep(x,nrow(data))

assign(name,data.frame(eval(parse(text=var)),rank))
  
} 

## NOTE: per team discussion 8/18, only using first four ranks

ranking <- rbind(ranking_1,ranking_2,ranking_3,ranking_4)
ranking <-
  ranking %>%
    rename_at(1:2,~c("year","rank"))

ranking <- 
    ranking %>%
      group_by(year) %>%
        summarise(sd = sd(rank, na.rm = T), rank = mean(rank, na.rm = T))

ranking$year <- as.numeric(as.character(ranking$year))
years <- data.frame(year = seq(from = 1983, to = 2019, by = 1), rank = NA)
ranking <- left_join(years,ranking,by = "year")
ranking <- ranking %>% 
  transmute(year = year, rank = ifelse(is.na(rank.y), rank.x, rank.y), sd = sd)

## Plot 

ranking$model <- "Focus Group"
ranking <- ranking %>%
  rename_at(1:3,~c("term","estimate","std.error"))

ranking <- ranking[!is.na(ranking$estimate),]
ranking$estimate <- 4 - (ranking$estimate - 1)
ranking <- ranking[order(ranking$estimate),]

ranking_plot <- dwplot(ranking,dot_args=list(size=2),whisker_args=list(size=.3))+theme_bw()+
  xlab("Estimated Focus Group Bad Year Ranking")+
  theme(text = element_text(size=15),legend.title = element_blank())
print(ranking_plot)

## Generate Bradley-Terry ranking from pairwise data

for (x in 1:3) {
  
name <- paste("pairwise_",x,sep="")
y1 <- paste("data$pair_",x,"_y1",sep="")
y2 <- paste("data$pair_",x,"_y2",sep="")
win <- paste("data$pair_",x,sep="")

assign(name,data.frame(eval(parse(text=y1)), eval(parse(text=y2)), eval(parse(text=win))))
  
}

pairwise <- rbind(pairwise_1,pairwise_2,pairwise_3)
pairwise <- pairwise %>%
  rename_at(1:3,~c("y1","y2","win"))

pairwise$win1 <- 0
pairwise$win1[pairwise$win == "Year 1"] <- 1

pairwise$win2 <- 0
pairwise$win2[pairwise$win == "Year 2"] <- 1

pairwise$y1 <- as.numeric(as.character(pairwise$y1))
pairwise$y2 <- as.numeric(as.character(pairwise$y2))

pairwise$year1_fac <- factor(pairwise$y1, 
                              labels = unique(c(pairwise$y1, pairwise$y2)),
                              levels = unique(c(pairwise$y1, pairwise$y2)))

pairwise$year2_fac <- factor(pairwise$y2,
                              labels = unique(c(pairwise$y1, pairwise$y2)),
                              levels = unique(c(pairwise$y1, pairwise$y2)))


model_vanilla <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                     formula = ~ year,
                     id = "year",
                     data = pairwise)

summary(model_vanilla)

model <- model_vanilla

## Extract estimated ability scores and rank them

ranks <- BTabilities(model)
ranks_ordered <- data.frame(ranks)
ranks_ordered <- ranks_ordered[order(ranks_ordered$ability),]
ranks_ordered

## Plot confidence intervals 

ranks.qv <- qvcalc(ranks)

term <- rownames(ranks.qv[["covmat"]])
estimate <- ranks.qv[["qvframe"]][["estimate"]]
std.error <- ranks.qv[["qvframe"]][["quasiSE"]]
model <- c("B-T Score")
plot <- data.frame(term,estimate,std.error,model)
plot <- plot[order(plot$estimate),]

bt_plot <- dwplot(plot,dot_args=list(size=2),whisker_args=list(size=.3))+theme_bw()+
  xlab("Estimated B-T Bad Year Ranking")+
  theme(text = element_text(size=20),legend.title = element_blank())
print(bt_plot)

## Combine graphs

# Rescale vars

rank_max <- max(ranking$estimate)
ranking$estimate <- ranking$estimate / rank_max
ranking$std.error <- ranking$std.error / rank_max

bt_max <- max(plot$estimate)
plot$estimate <- plot$estimate / bt_max
plot$std.error <- plot$std.error / bt_max

plot_combined <- rbind(ranking,plot)
plot_combined <- plot_combined[order(plot_combined$estimate),]

comb_plot <- dwplot(plot_combined,dot_args=list(size=2),whisker_args=list(size=.3))+theme_bw()+
  xlab("Estimated Bad Year Ranking")+
  theme(text = element_text(size=15),legend.title = element_blank())
print(comb_plot)
