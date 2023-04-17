###############################################################################

# IRI Ethiopia 2020 Data Analysis

# By Max Mauerman

# Compares farmer bad year ranking measured two ways:

# 1. Direct ranking exercise

# 2. Pairwise comparisons (ranking estimated via Bradley-Terry algorithm)

##############################################################################

## Setup

setwd("/Users/Nick/Documents/IRI - KON")
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
library(janitor)
set.seed(1000)

## Load and clean data

eth <- read_xlsx("ethiopia data.xlsx")
eth2 <- read_xlsx("ethiopia data (oct).xlsx")

keep <- c("Region","woreda1","village1","What was the worst year?","2nd worst","3rd worst","4th worst","5th worst","6th worst","7th worst","8th worst","pair_1_y1","pair_1_y2","Which year was drier:\n\n1. ${pair_1_y1}\n2. ${pair_1_y2}","pair_2_y1","pair_2_y2","Which year was drier:\n\n1. ${pair_2_y1}\n2. ${pair_2_y2}","pair_3_y1","pair_3_y2","Which year was drier:\n\n1. ${pair_3_y1}\n2. ${pair_3_y2}")

data = subset(eth,select = keep)
data2 = subset(eth2,select = keep)
data <- rbind(data,data2)

data <- 
  data %>%
  rename_at(1:20,~c("region","woreda","village","ranking_1","ranking_2","ranking_3","ranking_4","ranking_5","ranking_6","ranking_7","ranking_8","pair_1_y1","pair_1_y2","pair_1","pair_2_y1","pair_2_y2","pair_2","pair_3_y1","pair_3_y2","pair_3"))

## Aggregate ranked data

for(x in 1:8) {
  
  
  name <- paste("ranking_",x,sep="")
  var <- paste("data$ranking_",x,sep="")
  rank <- rep(x,nrow(data))
  
  assign(name,data.frame(eval(parse(text=var)),rank))
  
} 


ranking <- rbind(ranking_1,ranking_2,ranking_3,ranking_4,ranking_5,ranking_6,ranking_7,ranking_8)
ranking <-
  ranking %>%
  rename_at(1:2,~c("year","rank"))

ranking <- 
  ranking %>%
  group_by(year) %>%
  summarise(sd = sd(rank, na.rm = T), rank = mean(rank, na.rm = T))

ranking$year <- as.numeric(as.character(ranking$year))
years <- data.frame(year = seq(from = 1983, to = 2018, by = 1), rank = NA)
ranking <- left_join(years,ranking,by = "year")
ranking <- ranking %>% 
  transmute(year = year, rank = ifelse(is.na(rank.y), rank.x, rank.y), sd = sd)

## Plot 

ranking$model <- "Focus Group"
ranking <- ranking %>%
  rename_at(1:3,~c("term","estimate","std.error"))

ranking <- ranking[!is.na(ranking$estimate),]
ranking$estimate <- 8 - (ranking$estimate - 1)
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

#add Unique ID for each village 
pairwise_1 <- cbind(pairwise_1, Unique_ID = 1:nrow(pairwise_1))
pairwise_2 <- cbind(pairwise_2, Unique_ID = 1:nrow(pairwise_2))
pairwise_3 <- cbind(pairwise_3, Unique_ID = 1:nrow(pairwise_3))

pairwise <- rbind(pairwise_1,pairwise_2,pairwise_3)
pairwise <- pairwise %>%
  rename_at(1:3,~c("y1","y2","win"))


#EM analysis with pairs
pairwise$win[pairwise$win == 'Year 1'] <- 1
pairwise$win[pairwise$win == 'Year 2'] <- 0
pairwise <- pairwise[!(pairwise$win == c("Don't know")),]
pairwise <- pairwise[!(pairwise$win == c("The two years were equal")),]
pairwise[,3] <- sapply(pairwise[,3], as.numeric)
pair_proportions <- pairwise %>%
  group_by(y1, y2) %>%
  summarise(win=(mean(win)))

#apply a unique ID for each pair
pairwise$pair_ID <- with(pairwise, {m1 = ifelse(y1 < y2, y1, y2);
                                    m2 = ifelse(y1 < y2, y2, y1);
                                    return(as.numeric(interaction(m1, m2, drop=TRUE)))})

pair_proportions$pair_ID <- with(pair_proportions, {m1 = ifelse(y1 < y2, y1, y2);
                                    m2 = ifelse(y1 < y2, y2, y1);
                                    return(as.numeric(interaction(m1, m2, drop=TRUE)))})

pairwise <- merge(pairwise, pair_proportions, by = c("pair_ID")) #kinda messy but it works

#fix y1 and y2 column names
colnames(pairwise)[colnames(pairwise) %in% c("y1.x", "y2.x")] <- c("y1", "y2")
colnames(pairwise)[colnames(pairwise) %in% c("win.x")] <- c("win")

#removing rows that do not meet the threshold of .8
pairwise <- pairwise[!(pairwise$win.y > .8 & pairwise$win == 0), ]
pairwise <- pairwise[!(pairwise$win.y < .2 & pairwise$win == 1), ]

#changing win back to Year 1 and 2 to work with the rest of the code
pairwise$win[pairwise$win == '1'] <- 'Year 1'
pairwise$win[pairwise$win == '0'] <- 'Year 2'

#EM analysis 
#replacing wins with 1 and losses with 0 for each year and combing the dataframes
# y1_data <- select(pairwise, y1, win)
# y1_data$win[y1_data$win == 'Year 1'] <- 1
# y1_data$win[y1_data$win == 'Year 2'] <- 0
# y2_data <- select(pairwise, y2, win)
# y2_data$win[y2_data$win == 'Year 1'] <- 1
# y2_data$win[y2_data$win == 'Year 2'] <- 0
# names(y2_data)[1] <- 'y1'
# 
# year_data <- rbind(y1_data, y2_data)
# names(year_data)[1] <- 'year'
# year_data[,2] <- sapply(year_data[,2], as.numeric)
# year_data <- year_data[!(year_data$win == c("Don't know")),]
# year_data <- year_data[!(year_data$win == c("The two years were equal")),]
# 
# year_proportions <- year_data %>%
#   group_by(year) %>%
#   summarise(win = mean(win))


#add a column giving village's that answered 1984 wrong = 1 
#you can replace 1984 with whatever year you want to take out
#pairwise <- cbind(pairwise, wrong = length(nrow(pairwise)))
#pairwise$wrong <- ifelse((pairwise$y1 == '1984' & pairwise$win == 'Year 2') | (pairwise$y2=='1984'&pairwise$win=='Year 1'),1,0)

#giving every answer in a village a 1 if they got year 'x' wrong
#pairwise <- pairwise %>%
  #group_by(Unique_ID) %>%
  #mutate(wrong = ifelse(sum(wrong) > 0, 1, 0))

#taking out every answer for each village that got year 'x' wrong
#pairwise = pairwise[-c(which(pairwise$wrong == 1)), ]
#taking out year 'x' because a year cannot win every time with the B-T model
#pairwise <- subset(pairwise, y1!='1984')


#add a column giving village's that answered 1984 wrong = 1 (replace with whatever year you're taking out) 
#pairwise <- cbind(pairwise, wrong = length(nrow(pairwise)))
#pairwise$wrong <- ifelse(pairwise$y1 == '1984' & pairwise$win == 'Year 2',1, 0)
#add next line if any y2 == 1984 (none are in this data)
#pairwise$wrong <- ifelse(pairwise$y2=='1984'&pairwise$win=='Year 1', 1,0)

#pairwise <- pairwise %>%
#group_by(Unique_ID) %>%
#mutate(wrong, ifelse(sum(wrong) > 0, 1, 0))
#names(pairwise)[6] <- "Village_Wrong"

#takes out all villages that got 'x' year wrong (1984 in this case)
#pairwise = pairwise[-c(which(pairwise$Village_Wrong == '1')), ]
#takes out all  of 'x' year (because you cannot have one year only win with the B-T method)
pairwise <- subset(pairwise, y1!='1984')


#continuing B-T method

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

plot$estimate <- plot$estimate - min(plot$estimate) ## should have a more elegant way of doing this...
bt_max <- max(plot$estimate)
plot$estimate <- plot$estimate / bt_max
plot$std.error <- plot$std.error / bt_max

plot_combined <- rbind(ranking,plot)
plot_combined <- plot_combined[order(plot_combined$estimate),]

comb_plot <- dwplot(plot_combined,dot_args=list(size=2),whisker_args=list(size=.3))+theme_bw()+
  xlab("Estimated Bad Year Ranking")+
  theme(text = element_text(size=15),legend.title = element_blank())
print(comb_plot)

pairwise_years <- unique(plot$term)
plot_combined_trunc <- dplyr::filter(plot_combined, term %in% pairwise_years)
comb_plot_trunc <- dwplot(plot_combined_trunc,dot_args=list(size=2),whisker_args=list(size=.3))+theme_bw()+
  xlab("Estimated Bad Year Ranking (subset)")+
  theme(text = element_text(size=15),legend.title = element_blank())
print(comb_plot_trunc)

