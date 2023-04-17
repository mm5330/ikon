###############################################################################

# IRI Farmer Bad Year Ranking Algorithm

# By Max Mauerman

# Objective: Generate a probabalistic ranking of years from worst to best from
# data on respondents' pairwise comparison of years. (Bradley-Terry algorithm)

# Uses data on severity of northern Bangladesh floods 11/23/20

# Participants were NGO staff 

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
install_github("vqv/ggbiplot")
source_gist("https://gist.github.com/dfalster/5589956")
options(qwraps2_markup = "markdown")
set.seed(1000)

## Load and clean data

responses <- read.csv("BD seminar votes.csv")
responses <- responses[,-1]
responses <- cbind(responses,
            win1=rep(0,nrow(responses)),win2=rep(0,nrow(responses)),
            tie=rep(0,nrow(responses)),
            win1_adj=rep(0,nrow(responses)),win2_adj=rep(0,nrow(responses)))
responses <-
  responses %>%
    rename_at(1:4,~c("year1","year2","response","user"))

# drop test answers

responses <- responses %>%
  filter(user > 5)

## Summary table of response frequency and DKs
response_summary <- responses %>%
    group_by(year1, year2) %>%
      count(response)

responses <- responses[ which(responses$response != "?"),] # drop DKs 

for (x in 1:nrow(responses)) {
  
  if (responses[x,3] == responses[x,1]){
    responses[x,5] <- 1
    responses[x,8] <- 1
  }
  
  if (responses[x,3] == responses[x,2]){
    responses[x,6] <- 1
    responses[x,9] <- 1
  }
  
  if (responses[x,3] == "="){
    responses[x,7] <- 1
    responses[x,8] <- 0.5
    responses[x,9] <- 0.5
  }
  
}

responses$year1_fac <- factor(responses$year1, 
                              labels = unique(c(responses$year1, responses$year2)),
                              levels = unique(c(responses$year1, responses$year2)))

responses$year2_fac <- factor(responses$year2,
                              labels = unique(c(responses$year1, responses$year2)),
                              levels = unique(c(responses$year1, responses$year2)))


## Load weather station data 

weather <- read.csv("bangladesh_data_forkon_rajshahi.csv") 
weather <- weather[,-1]
  
## Bind dataframes to list

responses$year1_fac <- data.frame(year = responses$year1_fac, first = 1)
responses$year2_fac <- data.frame(year = responses$year2_fac, first = 0)

data <- list(responses = responses, weather = weather)

## Estimate Bradley-Terry model

model_vanilla <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
             formula = ~ year,
             id = "year",
              data = data)
  
summary(model_vanilla)

model_ties <- BTm(outcome = cbind(win1_adj,win2_adj), player1 = year1_fac, player2 = year2_fac,
                     formula = ~ year,
                     id = "year",
                     data = data)

summary(model_ties)

model_weather <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                     formula = ~ (1|year) +
                       pmw[year] + str[year],
                     id = "year",
                     data = data)

summary(model_weather)

model_order <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                     formula = ~ year + first,
                     id = "year",
                     data = data)

summary(model_order)


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
plot$estimate <- plot$estimate - min(plot$estimate)
plot$std.error <- plot$std.error / max(plot$estimate)
plot$estimate <- plot$estimate / max(plot$estimate)

plot_order <- plot$term[order(plot$estimate)]

plot_sat <- weather %>%
  gather(key="model",value="estimate",-year) %>%
    rename_at(1,~c("term"))
plot_sat$estimate <- plot_sat$estimate / max(plot_sat$estimate)

plot_sat$std.error <- NA
plot_sat <- plot_sat[c(1,3,4,2)]

plot_combined <- rbind(plot,plot_sat)
plot_combined$term <- factor(plot_combined$term,levels=plot_order)

ranks_plot <- dwplot(plot_combined,dot_args=list(size=2),whisker_args=list(size=.3)) +
  theme_bw()+
  xlab("Estimated Ranking of Bangladesh Flood Severity")+
  theme(text = element_text(size=25),legend.title = element_blank())
print(ranks_plot)

# Rank-rank correlation test

spearman <- plot_combined %>%
  select(-std.error) %>%
  spread(model,estimate)

spearman$term <- as.numeric(paste(spearman$term))
spearman <- spearman[order(spearman$term),]

cor.test(x=spearman$`B-T Score`, y=spearman$pmw, method = 'spearman')
cor.test(x=spearman$`B-T Score`, y=spearman$str, method = 'spearman')
cor.test(x=spearman$pmw, y=spearman$str, method = 'spearman')

