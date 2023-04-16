
### This file generates the rankings of historical precipitation in Cauca, Colombia
### used for the paper "Innovative Rural Community Contributions to Historical Climate Data".

## setup and load data

library(here)
library(tidyverse)
library(sf)
library(leaflet)
library(ggthemes)
library(shinythemes)
library(htmltools)
library(shiny)
library(RColorBrewer)
library(knitr)
library(ggplot2)
library(png)  
library(stringr)
library(htmltools)
library(tidyr)
library(ggplot2)
#library(rowr)
library(grid)
library(gridExtra)
library(data.table)
library(ggplot2)
library(dplyr)
library(reshape2)
library(reshape)
library(readxl)
library(DT)
library(readr)
library(ggridges)

setwd("/Users/mmauerman/Documents/IRI - KON/Colombia data")

chirps <- read.csv("scenarios/Cauca/CHIRPSDK.csv")
noaa <- read.csv("scenarios/Cauca/NOAA.daily.csv")

# list of years we need to do this for...can be any number
years.list <-  c(2021)

dekad.df <- read.csv("/Users/mmauerman/Documents/IRI - Zambia reinsurance/DekadStartDay.csv") %>%
  mutate(decad.check = Decad)

DecadsDays <- function(year.index)
  # Function to join the decads to the days in a year 
  # year.index: just the year you want to do this for
  # NOTES: there is a hardcoding step for the last decad
{
  
  temp.func.df <- data.frame(
    day = as.Date(format(seq(as.Date(paste0(year.index,"/1/1")), as.Date(paste0(year.index,"/12/31")), "day")))) %>% 
    rowid_to_column(., var = "day.num") %>%  # creating a day number for our daily dates
    left_join(., dekad.df, by = c("day.num" = "StartDayN")) %>%  # joining our IRI dekad ref file
    mutate(prev_val = (Decad), next_val = (Decad),  # creating the two variables that guide the fill statement
           year = format(day, "%Y"),   # popping out year so we know which year we are talking about
           decad.name = ifelse(prev_val == next_val, day, NA)) %>%  # grabbing a decad name in date format
    fill(prev_val, .direction = "down") %>%  # 
    fill(next_val, .direction = "up") %>%
    mutate(Decad = ifelse(prev_val == next_val, prev_val, prev_val),
           Decad = ifelse(is.na(Decad), 36, Decad)) %>%  # hard coding the last part, b/c it breaks the down up approach in fill
    dplyr::select(-prev_val, -next_val, -EndDayN, -decad.check)
  
}

# output from lapply
days.decad.df <- lapply(years.list, DecadsDays) %>% 
  bind_rows() %>% # binding the items in the list
  mutate(
    decad.name = as.Date(decad.name, origin = "1970-01-01"))

# just ref name of the decades to join back to summarized files
decad.name.df <- days.decad.df %>% 
  distinct(Decad, year, decad.name) %>% 
  drop_na()

## visualize climatology vs key bad years

chirps_clim <- rowMeans(chirps[,2:ncol(chirps)],na.rm=T)
chirps_clim <- as.data.frame(cbind(chirps_clim,chirps[,1]))
colnames(chirps_clim) <- c("chirps","dek")
chirps_clim <- left_join(chirps_clim,decad.name.df,by=c("dek"="Decad"))

top_flood_years <- c(2008,2011,2018)

chirps_topyears <- chirps %>%
  select(contains(as.character(top_flood_years)))
chirps_topyears <- as.data.frame(cbind(chirps_topyears,chirps[,1]))
colnames(chirps_topyears) <- c(top_flood_years,"dek") 
chirps_topyears <- left_join(chirps_topyears,decad.name.df,by=c("dek"="Decad"))
chirps_topyears <- gather(chirps_topyears,key="year",value="chirps",c(1:length(top_flood_years)))

chirps_clim_plot <- ggplot(data=chirps_clim,aes(x=decad.name,y=chirps)) +
  geom_line(size=1) +
  geom_line(data=chirps_topyears,aes(x=decad.name,y=chirps,group=year,color=year),inherit.aes = FALSE) +
  theme_bw() +
  labs(group='year') +
  ylab("CHRIPS rainfall") +
  xlab("Timing") +
  theme(legend.position = "top",
        text=element_text(size=20),
        legend.text = element_text(size=15))
print(chirps_clim_plot)


## aggregate by seasonal sum

# two seasonals in colombia, so aggregating over both than taking min

chirps_early <- colSums(chirps[c(4:15),-1])
chirps_late <- colSums(chirps[c(24:30),-1])
chirps_min <- apply(cbind(chirps_early,chirps_late),1,min)
chirps_max <- apply(cbind(chirps_early,chirps_late),1,max)

chirps_aggregate <- data_frame("chirps" = chirps_min, "year" = names(chirps_min))
chirps_aggregate$year <- gsub("X", "", chirps_aggregate$year)

chirps_aggregate_excess <- data_frame("chirps" = chirps_max, "year" = names(chirps_max))
chirps_aggregate_excess$year <- gsub("X", "", chirps_aggregate_excess$year)

## visualize frequency distribution of seasonal sum over years

chirps_hist_plot <- ggplot(data=chirps_aggregate,aes(x=scale(chirps))) +
    geom_histogram(binwidth = 0.25) +
    geom_text(aes(y=5,label=year,color="red"),position=position_jitter(seed=1,width=0.1,height=2)) +
    theme_bw() +
    xlab("Aggregate CHIRPS, standardized") +
    theme(legend.position = "none")
print(chirps_hist_plot)

chirps_hist_plot_excess <- ggplot(data=chirps_aggregate_excess,aes(x=scale(chirps))) +
  geom_histogram(binwidth = 0.25) +
  geom_text(aes(y=5,label=year,color="red"),position=position_jitter(seed=1,width=0.1,height=2)) +
  theme_bw() +
  xlab("Aggregate CHIRPS, standardized (max)") +
  theme(legend.position = "none")
print(chirps_hist_plot_excess)

## do the same for NOAA station data

noaa_clim <- rowMeans(noaa[,2:ncol(noaa)],na.rm=T)
noaa_clim <- as.data.frame(cbind(noaa_clim,noaa[,1]))
colnames(noaa_clim) <- c("noaa","day")

noaa_topyears <- noaa %>%
  select(contains(as.character(top_flood_years)))
noaa_topyears <- as.data.frame(cbind(noaa_topyears,noaa[,1]))
colnames(noaa_topyears) <- c(top_flood_years,"day") 
noaa_topyears <- gather(noaa_topyears,key="year",value="noaa",c(1:length(top_flood_years)))

# change day to date variable

noaa_clim$date <- as.Date(paste0(noaa_clim$day,"-2020"),"%d-%b-%Y")
noaa_topyears$date <- as.Date(paste0(noaa_topyears$day,"-2020"),"%d-%b-%Y")

noaa_clim_plot <- ggplot(data=noaa_clim,aes(x=date,y=as.numeric(noaa))) +
  geom_line(size=1) +
  geom_line(data=noaa_topyears,aes(x=date,y=as.numeric(noaa),group=year,color=year),inherit.aes = FALSE) +
  theme_bw() +
  labs(group='year') +
  ylab("NOAA station rainfall") +
  xlab("Timing") +
  theme(legend.position = "top",
        text=element_text(size=20),
        legend.text = element_text(size=15))
print(noaa_clim_plot)


## aggregate by seasonal sum

# two seasonals in colombia, so aggregating over both than taking min

noaa_early <- colSums(noaa[c(32:150),-1])
noaa_late <- colSums(noaa[c(244:304),-1])
noaa_min <- apply(cbind(noaa_early,noaa_late),1,min)
noaa_max <- apply(cbind(noaa_early,noaa_late),1,max)

noaa_aggregate <- data_frame("noaa" = noaa_min, "year" = names(noaa_min))
noaa_aggregate$year <- gsub("X", "", noaa_aggregate$year)

noaa_aggregate_excess <- data_frame("noaa" = noaa_max, "year" = names(noaa_max))
noaa_aggregate_excess$year <- gsub("X", "", noaa_aggregate_excess$year)

## visualize frequency distribution of seasonal sum over years

noaa_hist_plot <- ggplot(data=noaa_aggregate,aes(x=scale(noaa))) +
  geom_histogram(binwidth = 0.25) +
  geom_text(aes(y=5,label=year,color="red"),position=position_jitter(seed=1,width=0.1,height=2)) +
  theme_bw() +
  xlab("Aggregate noaa, standardized") +
  theme(legend.position = "none")
print(noaa_hist_plot)

noaa_hist_plot_excess <- ggplot(data=noaa_aggregate_excess,aes(x=scale(noaa))) +
  geom_histogram(binwidth = 0.25) +
  geom_text(aes(y=5,label=year,color="red"),position=position_jitter(seed=1,width=0.1,height=2)) +
  theme_bw() +
  xlab("Aggregate noaa, standardized (max)") +
  theme(legend.position = "none")
print(noaa_hist_plot_excess)


## generate cleaned, ranked version for use in iKON

chirps_late_filtered <- data.frame(chirps_late,names(chirps_late)) %>%
  rename_at(1:2,~c("value","year")) %>%
  filter(!is.na(value)) %>%
  mutate(year = gsub("X", "", year)) %>%
  filter(year >= 2000) %>%
  mutate(value = scale(value))

# old version
# chirps_late_filtered$value <- cut_interval(chirps_late_filtered$value,length=0.5,ordered_result=TRUE)

# new version - 10 regular intervals
chirps_late_filtered$value <- cut(chirps_late_filtered$value,breaks=10,ordered_result=TRUE)

chirps_late_filtered$value <- as.numeric(chirps_late_filtered$value)
chirps_late_filtered$source_name <- "CHIRPS"
chirps_late_filtered$source_type <- "Satellite"

noaa_late_filtered <- data.frame(noaa_late,names(noaa_late)) %>%
  rename_at(1:2,~c("value","year")) %>%
  filter(!is.na(value)) %>%
  mutate(year = gsub("X", "", year)) %>%
  filter(year >= 2000 & year < 2021) %>%
  mutate(value = scale(value))

# old version
# noaa_late_filtered$value <- cut_interval(noaa_late_filtered$value,length=0.5,ordered_result=TRUE)

# new version - 10 regular intervals
noaa_late_filtered$value <- cut(noaa_late_filtered$value,breaks=10,ordered_result=TRUE)

noaa_late_filtered$value <- as.numeric(noaa_late_filtered$value)
noaa_late_filtered$source_name <- "NOAA"
noaa_late_filtered$source_type <- "Weather Station"

## just curious

cor.test(x=noaa_late_filtered$value, y=chirps_late_filtered$value, method = 'spearman')
plot(noaa_late_filtered$value,chirps_late_filtered$value)
abline(a=0, b=1, lty="dotted")

stats::qqplot(noaa_late_filtered$value, chirps_late_filtered$value)
abline(a=0, b=1, lty="dotted")


## save

colombia_pilot_data_sat <- rbind(noaa_late_filtered,chirps_late_filtered)

write.csv(colombia_pilot_data_sat,"colombia_pilot_data_sat.csv")

## generate fake user data

set.seed(9)

# score

user_ids <- sapply(1:10,function(x) paste0("fakeuser",x))
user_scores <- sapply(1:10,function(x) runif(1,min=100,max=1000))
user_scores <- round(user_scores,digits=0)

colombia_pilot_data_users <- cbind(user_ids,user_scores)
colnames(colombia_pilot_data_users) <- c("user_id","score")

# responses

rand_response <- function(user,years,n) {
  
  responses <- list()
  
  for (x in c(1:n)) {
    
    rand1 <- runif(1,min=1,max=length(years)) 
    year1 <- years[rand1]
    
    years2 <- years[!years %in% year1]
    rand2 <- runif(1,min=1,max=length(years2)) 
    year2 <- years2[rand2]
    
    resp <- round(runif(1,min=1,max=3),digits=0)
    
    response <- c(year1,year2,resp)
    responses[[x]] <- response
    
  }
  
  responses <- simplify2array(responses)
  responses <- t(responses)
  responses <- cbind(responses,rep(as.character(user),nrow(responses)))
  colnames(responses) <- c("year1","year2","answer","user_id")
  responses <- as.data.frame(responses)
  
  responses
}

years_unique <- unique(colombia_pilot_data_sat$year) 
rand_responses_all <- lapply(user_ids,  function(y) rand_response(user=y,years=years_unique,n=10))

library(plyr)
rand_responses_all <- ldply(rand_responses_all,rbind)

## save

write.csv(colombia_pilot_data_users,"colombia_pilot_data_score.csv")
write.csv(rand_responses_all,"colombia_pilot_data_responses.csv")
