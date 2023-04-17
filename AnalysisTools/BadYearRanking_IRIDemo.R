###############################################################################

# IRI Farmer Bad Year Ranking Algorithm

# By Max Mauerman

# Objective: Generate a probabalistic ranking of years from worst to best from
# data on respondents' pairwise comparison of years. (Bradley-Terry algorithm)

# Uses data on coldness of NYC winters from IRI seminar 5/5/20

# Participants were IRI staff and research scientists

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

responses <- read_xlsx("Seminar data.xlsx")
responses <- responses[,-1]
responses <- cbind(responses,
            win1=rep(0,nrow(responses)),win2=rep(0,nrow(responses)),
            tie=rep(0,nrow(responses)),
            win1_adj=rep(0,nrow(responses)),win2_adj=rep(0,nrow(responses)))
responses <-
  responses %>%
    rename_at(1:4,~c("user","year1","year2","response"))

## Summary table of response frequency and DKs
response_summary <- responses %>%
    group_by(year1, year2) %>%
      count(response)

responses <- responses[ which(responses$response != "?"),] # drop DKs 

for (x in 1:nrow(responses)) {
  
  if (responses[x,4] == responses[x,2]){
    responses[x,5] <- 1
    responses[x,8] <- 1
  }
  
  if (responses[x,4] == responses[x,3]){
    responses[x,6] <- 1
    responses[x,9] <- 1
  }
  
  if (responses[x,4] == "="){
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

weather <- read_xlsx("nyc winters.xlsx",sheet = "winters_cleaned_subset") 

weather <-
  weather %>%
  rename_at(1:5,~c("year","frg","lga","teb","avg"))
  
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
                       frg[year] + lga[year] + teb[year],
                     id = "year",
                     data = data)

summary(model_weather)

model_order <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                     formula = ~ year + first,
                     id = "year",
                     data = data)

summary(model_order)


model <- model_weather

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

#png("bt_ranking.png", width=600, height=600)
ranks_plot <- dwplot(plot,dot_args=list(size=2),whisker_args=list(size=.3))+theme_bw()+
  xlab("Estimated Ranking of NYC Winter Severity")+
  theme(text = element_text(size=20),legend.title = element_blank())
print(ranks_plot)
#dev.off()