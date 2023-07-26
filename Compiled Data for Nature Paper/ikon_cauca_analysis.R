

### This file produces analysis of the Cauca, Colombia iKON pilot data (nNv '21 and Jun '22)
### for the paper "Innovative Rural Community Contributions to Historical Climate Data".

### The data itself is available through the Supplementary Material section of the paper.

### written by Max Mauerman (mmauerman@iri.columbia.edu)

library(ggplot2)
library(dplyr)
library(readxl)
library(BradleyTerry2)
library(dotwhisker)
library(tidyr)
library(lubridate)
library(gtools)
library(ggtext)
library(glue)

setwd("") ## change as needed

## load and clean data

data <- read.csv("Cauca_Deployment_withids.csv")
data_followup <- read.csv("cauca fcc data.csv")

data$survey_round <- 1
data_followup$survey_round <- 2

data_followup <- data_followup %>% dplyr::select(-X) %>% rename_at(c(1:2),~c("userid","time_stamp")) %>%
                      relocate(time_stamp)
    
data <- rbind(data,data_followup)

data$survey_round <- factor(data$survey_round,labels=c("Nov 2021","Jun 2022"))
  
data <- data %>% mutate(configs = recode(configs,"g|1" = "1","1|g" = "1", "2|g" = "2", "g|3" = "3", "3|g" = "3", "g|4a" = "4a"))

script_labs <- c("Vanilla","Mem Trig","Mem Trig + Focus","Mem Trig + Focus + Short Endpoints","Mem Trig + Focus + Long Endpoints","Vanilla (No Gamification)")
script_vals <- c("1","2","3","4a","4b","ng")

data$configs <- factor(data$configs,levels=script_vals,labels=script_labs)

gender_labs <- c("Female","Male","No Answer")
names(gender_labs) <- c(1:3)

colnames(data)[16] <- 'n_active' ## renaming for ease of use 

data$time_stamp <- as.POSIXct(data$time_stamp)

data$responsetime[data$responsetime == "None"] <- NA
data$responsetime[data$responsetime == "NULL"] <- NA
data$responsetime <- hms(substring(data$responsetime,4))
data$responsetime <- as.numeric(seconds(data$responsetime))

data <- data %>%
  mutate_at(c("points","matchsat","matchwea","matchneighbour","matchneighbour_real","neighbouranswered","neighbouranswered_real"),
            ~ as.numeric(ifelse(.x == "None",0,.x))) %>%
  group_by(userid) %>%
  mutate(score = sum(points,na.rm=T)) %>%
  ungroup()


data <- data %>% 
  rowwise() %>%
  mutate(unique_pair = paste(min(year1,year2),max(year1,year2),sep=",")) %>%
  ungroup() %>%
  group_by(userid,unique_pair) %>%
  mutate(inconsistent = ifelse(n() > 1 & length(unique(answer)) == 1,1,0)) %>%
  mutate(inconsistent = ifelse(year1 == year2,NA,inconsistent)) %>%
  ungroup()

data <- data %>%
  mutate(matchneighbour_real = matchneighbour_real / neighbouranswered_real)

# filter by days when game was active

data <- data %>%
  filter(survey_round == "Jun 2022" | time_stamp >= as.POSIXct("2021-11-26 00:30:00") & time_stamp <= as.POSIXct("2021-11-29 23:59:59"))

# indicator variable for top performers
# NB: as of 9/9/22, changed this to calculate over pooled data, not by round!

data <- data %>% group_by(userid) %>%
  mutate(mean_points = mean(points,na.rm=T), inconsistency = mean(inconsistent,na.rm=T)) %>%
  ungroup() %>%
  #group_by(survey_round) %>%
  mutate(top_performer = ifelse(mean_points >= quantile(mean_points,0.75,na.rm=T) & inconsistency <= quantile(inconsistency,0.25,na.rm=T),1,0)) %>%
  ungroup() 
  #mutate(top_performer = ifelse(survey_round == "Jun 2022",NA,top_performer))
  

# lists of worst years from various sources

known_bad_years <- c(2014,2013,2008,2009,2011) ## taken from IRI 2017 CafeSeugro project
badyears_farmer <- c(2000,2005,2011,2010,2002)
badyears_sat <- c(2010,2007,2016,2003,2015)
badyears_station <- c(2005,2016,2019,2008,2010)

badyears <- known_bad_years ## chose which you want here

## set up sensor data

sensor <- read.csv("colombia_pilot_data_sat.csv")

sat <- sensor %>%
  filter(source_type == "Satellite") %>%
  select(c(2:3)) %>%
  rename(c("sat" = "value"))

station <- sensor %>%
  filter(source_type == "Weather Station") %>%
  select(c(2:3)) %>%
  rename(c("station" = "value"))

## quick t-test of total time and score per comp between rounds

data_ttest <- data %>% group_by(survey_round,userid) %>% 
  summarise(tot_time = sum(responsetime,na.rm = T), avg_score = mean(points,na.rm = T)) %>%
  ungroup()

t.test(data_ttest$tot_time[data_ttest$survey_round == "Nov 2021"], 
       data_ttest$tot_time[data_ttest$survey_round == "Jun 2022"])

t.test(data_ttest$avg_score[data_ttest$survey_round == "Nov 2021"], 
       data_ttest$avg_score[data_ttest$survey_round == "Jun 2022"])

data_ttest_cleaned <- data_ttest %>% filter(tot_time < quantile(tot_time,0.9))

t.test(data_ttest_cleaned$tot_time[data_ttest_cleaned$survey_round == "Nov 2021"], 
       data_ttest_cleaned$tot_time[data_ttest_cleaned$survey_round == "Jun 2022"])


## summary stats

# volume of responses over time

n_player_time <- data %>%
  group_by(survey_round,time_stamp) %>%
  summarise(n_responses = n()) %>%
  mutate(n_responses = cumsum(n_responses))

desc_responses <- ggplot(n_player_time,aes(x=time_stamp,y=n_responses)) +
  geom_line() +
  theme_bw() +
  scale_x_datetime(date_breaks = "6 hours", date_labels = "%d-%H h", 
               date_minor_breaks = "1 hour") +
  facet_wrap(~survey_round,scales="free_x",ncol=1) +
  theme(axis.text.x = element_text(angle=90)) +
  ggtitle("Cumulative number of responses over time")

png("desc_responses.png", width=500,height=600)
desc_responses
dev.off()

# responses per player

n_responses <- data %>%
  group_by(survey_round,userid) %>%
  summarise(n_responses = n(), top_performer = max(top_performer))

desc_responses_perplayer <- ggplot(n_responses,aes(x=n_responses, fill = factor(top_performer))) +
  geom_histogram(bins=15) +
  facet_wrap(~survey_round,scales="free_x") +
  theme_bw() +
  ggtitle("Distribution of number of responses per player")

png("desc_responses_perplayer.png", width=1600,height=400)
desc_responses_perplayer
dev.off()

# number of players per treatment arm

desc_treat <- ggplot(data %>% group_by(survey_round,userid) %>% filter(row_number() == n())) +
  geom_bar(aes(x=configs,fill = factor(top_performer))) +
  #scale_x_discrete(labels = script_labs,breaks=c(1:6)) +
  facet_wrap(~survey_round,scales="free_x") +
  theme_bw() +
  ggtitle("Number of players in each attention treatment arm") +
  theme(axis.text.x = element_text(angle=90))

png("desc_treat.png", width=1600,height=400)
desc_treat
dev.off()

desc_treat_rewards <- ggplot(data %>% group_by(survey_round,userid) %>% summarise(config_reward = max(config_reward), top_performer = max(top_performer))) +
  geom_bar(aes(x=config_reward,fill = factor(top_performer))) +
  facet_wrap(~survey_round) +
  theme_bw() +
  ggtitle("Number of players in each reward treatment arm") +
  theme(axis.text.x = element_text(angle=90))

png("desc_treat_rewards.png", width=8160,height=400)
desc_treat_rewards
dev.off()

# demographics

desc_age <- ggplot(data %>% group_by(survey_round,userid) %>% summarise(age = max(age), top_performer = max(top_performer))) +
  geom_histogram(aes(x=age,fill=factor(top_performer)),bins=15) +
  facet_wrap(~survey_round) +
  theme_bw() +
  ggtitle("Distribution of player age")

png("desc_age.png", width=1600,height=400)
desc_age
dev.off()

desc_gender <- ggplot(data %>% group_by(survey_round,userid) %>% summarise(gender= max(gender), top_performer = max(top_performer))) +
  geom_bar(aes(x=gender,fill=factor(top_performer))) +
  scale_x_continuous(labels = gender_labs,breaks=c(1:3)) +
  facet_wrap(~survey_round) +
  theme_bw() +
  ggtitle("Number of players by gender") +
  theme(axis.text.x = element_text(angle=90))

png("desc_gender.png", width=1600,height=400)
desc_gender
dev.off()

# sharing

desc_sharing<- ggplot(data %>% group_by(survey_round,userid) %>% summarise(inviteaccepted=max(inviteaccepted))) +
  geom_bar(aes(x=inviteaccepted)) +
  facet_wrap(~survey_round) +
  theme_bw() +
  ggtitle("Number of accepted invitations") +
  theme(axis.text.x = element_text(angle=90))

png("desc_sharing.png", width=850,height=400)
desc_sharing
dev.off()

## treatment arm comparisons 

# total score

data_totscore <- data %>%
  group_by(survey_round,configs) %>%
  summarise(mean = mean(score,na.rm=T),
            sd = sd(score,na.rm = T))

plot_totscore <- ggplot(data_totscore,aes(x=configs,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  #scale_x_discrete(labels = script_labs) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("Total Score") +
  ggtitle("Total Score by Attention Treatment Arm") +
  theme_bw()

png("plot_totscore.png", width=1600,height=400)
plot_totscore
dev.off()

data_totscore_rewards <- data %>%
  group_by(survey_round,config_reward) %>%
  summarise(mean = mean(score,na.rm=T),
            sd = sd(score,na.rm = T))

plot_totscore_rewards <- ggplot(data_totscore_rewards,aes(x=config_reward,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("Total Score") +
  ggtitle("Total Score by Reward Treatment Arm") +
  theme_bw()

png("plot_totscore_rewards.png", width=1600,height=400)
plot_totscore_rewards
dev.off()

# average score

data_avgscore <- data %>%
  # filter(year1 %in% badyears | year2 %in% badyears) %>% ## comment out if you don't want to subset to worst years
  group_by(survey_round,configs) %>%
  summarise(mean = mean(points,na.rm=T),
            sd = sd(points,na.rm = T))

plot_avgscore <- ggplot(data_avgscore,aes(x=configs,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  #scale_x_discrete(labels = script_labs) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("Average Score") +
  ggtitle("Average Per-Comparison Score by Attention Treatment Arm") +
  theme_bw()

png("plot_avgscore.png", width=1600,height=400)
plot_avgscore
dev.off()

data_avgscore_rewards <- data %>%
  # filter(year1 %in% badyears | year2 %in% badyears) %>% ## comment out if you don't want to subset to worst years
  group_by(survey_round,config_reward) %>%
  summarise(mean = mean(points,na.rm=T),
            sd = sd(points,na.rm = T))

plot_avgscore_rewards <- ggplot(data_avgscore_rewards,aes(x=config_reward,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("Average Score") +
  ggtitle("Average Per-Comparison Score by Reward Treatment Arm") +
  theme_bw()

png("plot_avgscore_rewards.png", width=1600,height=400)
plot_avgscore_rewards
dev.off()

# average time per comparison

data_avgtime_clean <- data %>%
  filter(responsetime <= quantile(responsetime,probs=0.9,na.rm=T)) %>%
  group_by(survey_round,configs) %>%
  summarise(mean = mean(responsetime,na.rm=T),
            sd = sd(responsetime,na.rm = T))

plot_avgtime_clean <- ggplot(data_avgtime_clean,aes(x=configs,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  #scale_x_discrete(labels = script_labs) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("Time Per Comparison (seconds)") +
  ggtitle("Average Time Per Comparison by Attention Treatment Arm (outliers cleaned)") +
  theme_bw()

png("plot_avgtime_clean.png", width=1600,height=400)
plot_avgtime_clean
dev.off()

data_avgtime_clean_rewards <- data %>%
  filter(responsetime <= quantile(responsetime,probs=0.9,na.rm=T)) %>%
  group_by(survey_round,config_reward) %>%
  summarise(mean = mean(responsetime,na.rm=T),
            sd = sd(responsetime,na.rm = T))

plot_avgtime_clean_rewards <- ggplot(data_avgtime_clean_rewards,aes(x=config_reward,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("Time Per Comparison (seconds)") +
  ggtitle("Average Time Per Comparison by Reward Treatment Arm (outliers cleaned)") +
  theme_bw()

png("plot_avgtime_clean_rewards.png", width=1600,height=400)
plot_avgtime_clean_rewards
dev.off()

# total time spent

data_tottime_clean <- data %>%
  filter(responsetime <= quantile(responsetime,probs=0.9,na.rm=T)) %>%
  group_by(survey_round,userid) %>%
  summarise(tot_time = sum(responsetime,na.rm=T),configs = configs) %>%
  group_by(survey_round,configs) %>%
  summarise(mean = mean(tot_time,na.rm=T),
            sd = sd(tot_time,na.rm = T))

plot_tottime_clean <- ggplot(data_tottime_clean,aes(x=configs,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  #scale_x_discrete(labels = script_labs) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("Total Time Spent (days)") +
  ggtitle("Total Time Spent by Attention Treatment Arm (outliers cleaned)") +
  theme_bw()

png("plot_tottime_clean.png", width=1600,height=400)
plot_tottime_clean
dev.off()

data_tottime_clean_rewards <- data %>%
  filter(responsetime <= quantile(responsetime,probs=0.9,na.rm=T)) %>%
  group_by(survey_round,userid) %>%
  summarise(tot_time = sum(responsetime,na.rm=T),config_reward = max(config_reward)) %>%
  group_by(survey_round,config_reward) %>%
  summarise(mean = mean(tot_time,na.rm=T),
            sd = sd(tot_time,na.rm = T))

plot_tottime_clean_rewards <- ggplot(data_tottime_clean_rewards,aes(x=config_reward,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("Total Time Spent (days)") +
  ggtitle("Total Time Spent by Rewards Treatment Arm (outliers cleaned)") +
  theme_bw()

png("plot_tottime_clean_rewards.png", width=1600,height=400)
plot_tottime_clean_rewards
dev.off()


# sensor data matching %

data_avgmatch_sens <- data %>%
  # filter(year1 %in% badyears | year2 %in% badyears) %>% ## comment out if you don't want to subset to worst years
  group_by(survey_round,configs) %>%
  summarise(mean = mean(matchsat,na.rm=T),
            sd = sd(matchsat,na.rm = T))

plot_avgmatch_sens <- ggplot(data_avgmatch_sens,aes(x=configs,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  #scale_x_discrete(labels = script_labs) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("% Matching") +
  ggtitle("Average % Matching with Satellite Data by Attention Treatment Arm") +
  theme_bw()

png("plot_avgmatch_sense.png", width=1600,height=400)
plot_avgmatch_sens
dev.off()

data_avgmatch_sens_rewards <- data %>%
  # filter(year1 %in% badyears | year2 %in% badyears) %>% ## comment out if you don't want to subset to worst years
  group_by(survey_round,config_reward) %>%
  summarise(mean = mean(matchsat,na.rm=T),
            sd = sd(matchsat,na.rm = T))

plot_avgmatch_sens_rewards <- ggplot(data_avgmatch_sens_rewards,aes(x=config_reward,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("% Matching") +
  ggtitle("Average % Matching with Satellite Data by Reward Treatment Arm") +
  theme_bw()

png("plot_avgmatch_sense_rewards.png", width=1600,height=400)
plot_avgmatch_sens_rewards
dev.off()


# neighbor matching %

data_avgmatch_neighb <- data %>%
  # filter(year1 %in% badyears | year2 %in% badyears) %>% ## comment out if you don't want to subset to worst years
  group_by(survey_round,configs) %>%
  summarise(mean = mean(matchneighbour_real,na.rm=T),
            sd = sd(matchneighbour_real,na.rm = T))

plot_avgmatch_neighb <- ggplot(data_avgmatch_neighb,aes(x=configs,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  #scale_x_discrete(labels = script_labs) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("% Matching") +
  ggtitle("Average % Matching with Neighbors by Attention Treatment Arm") +
  theme_bw()

png("plot_avgmatch_neighb.png", width=1600,height=400)
plot_avgmatch_neighb
dev.off()


data_avgmatch_neighb_rewards <- data %>%
  # filter(year1 %in% badyears | year2 %in% badyears) %>% ## comment out if you don't want to subset to worst years
  group_by(survey_round,config_reward) %>%
  summarise(mean = mean(matchneighbour_real,na.rm=T),
            sd = sd(matchneighbour_real,na.rm = T))

plot_avgmatch_neighb_rewards <- ggplot(data_avgmatch_neighb_rewards,aes(x=config_reward,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("% Matching") +
  ggtitle("Average % Matching with Neighbors by Reward Treatment Arm") +
  theme_bw()

png("plot_avgmatch_neighb_rewards.png", width=1600,height=400)
plot_avgmatch_neighb_rewards
dev.off()

# probability of getting a year in the top 25% correct (satellites)

data_topquart_sat <- data %>%
  mutate(quart_correct = ifelse( 
    (year1 %in% badyears_sat & !year2 %in% badyears_sat & answer == 1) |
    (year2 %in% badyears_sat & !year1 %in% badyears_sat & answer == 2)
    ,1,0)) %>%
  group_by(survey_round,configs) %>%
  summarise(mean = mean(quart_correct,na.rm=T),
            sd = sd(quart_correct,na.rm = T))

plot_topquart_sat <- ggplot(data_topquart_sat,aes(x=configs,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  #scale_x_discrete(labels = script_labs) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("% Matching") +
  ggtitle("Average % Matching with Any Top Quartile Sat by Attention Treatment Arm") +
  theme_bw()

png("plot_topquart_sat.png", width=1600,height=400)
plot_topquart_sat
dev.off()

data_topquart_sat_reward <- data %>%
  mutate(quart_correct = ifelse( 
    (year1 %in% badyears_sat & !year2 %in% badyears_sat & answer == 1) |
      (year2 %in% badyears_sat & !year1 %in% badyears_sat & answer == 2)
    ,1,0)) %>%
  group_by(survey_round,config_reward) %>%
  summarise(mean = mean(quart_correct,na.rm=T),
            sd = sd(quart_correct,na.rm = T))

plot_topquart_sat_reward <- ggplot(data_topquart_sat_reward,aes(x=config_reward,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("% Matching") +
  ggtitle("Average % Matching with Any Top Quartile Sat by Reward Treatment Arm") +
  theme_bw()

png("plot_topquart_sat_reward.png", width=1600,height=400)
plot_topquart_sat_reward
dev.off()

# probability of getting a year in the top 25% correct (neighbors)

data_topquart_neighb <- data %>%
  mutate(quart_correct = ifelse( 
    (year1 %in% badyears_farmer & !year2 %in% badyears_farmer & answer == 1) |
      (year2 %in% badyears_farmer & !year1 %in% badyears_farmer & answer == 2)
    ,1,0)) %>%
  group_by(survey_round,configs) %>%
  summarise(mean = mean(quart_correct,na.rm=T),
            sd = sd(quart_correct,na.rm = T))

plot_topquart_neighb <- ggplot(data_topquart_neighb,aes(x=configs,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  #vscale_x_discrete(labels = script_labs) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("% Matching") +
  ggtitle("Average % Matching with Any Top Quartile Neighbors by Attention Treatment Arm") +
  theme_bw()

png("plot_topquart_neighb.png", width=1600,height=400)
plot_topquart_neighb
dev.off()

data_topquart_neighb_reward <- data %>%
  mutate(quart_correct = ifelse( 
    (year1 %in% badyears_sat & !year2 %in% badyears_farmer & answer == 1) |
      (year2 %in% badyears_sat & !year1 %in% badyears_farmer & answer == 2)
    ,1,0)) %>%
  group_by(survey_round,config_reward) %>%
  summarise(mean = mean(quart_correct,na.rm=T),
            sd = sd(quart_correct,na.rm = T))

plot_topquart_neighb_reward <- ggplot(data_topquart_neighb_reward,aes(x=config_reward,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("% Matching") +
  ggtitle("Average % Matching with Any Top Quartile Neighbors by Reward Treatment Arm") +
  theme_bw()

png("plot_topquart_neighb_reward.png", width=1600,height=400)
plot_topquart_neighb_reward
dev.off()

# sharing

data_sharing <- data %>%
  group_by(survey_round,userid) %>%
  summarise(inviteaccepted = max(inviteaccepted,na.rm=T),configs = configs) %>%
  group_by(survey_round,configs) %>%
  summarise(mean = mean(inviteaccepted,na.rm=T),
            sd = sd(inviteaccepted,na.rm = T))

plot_sharing <- ggplot(data_sharing,aes(x=configs,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  #vscale_x_discrete(labels = script_labs) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("Number of Accepted Invites") +
  ggtitle("Average Accepted Invites by Attention Treatment Arm") +
  theme_bw()

png("plot_sharing.png", width=1600,height=400)
plot_sharing
dev.off()

data_sharing_reward <- data %>%
  group_by(survey_round,userid) %>%
  summarise(inviteaccepted = max(inviteaccepted,na.rm=T),config_reward = max(config_reward,na.rm=T)) %>%
  group_by(survey_round,config_reward) %>%
  summarise(mean = mean(inviteaccepted,na.rm=T),
            sd = sd(inviteaccepted,na.rm = T))

plot_sharing_reward <- ggplot(data_sharing_reward,aes(x=config_reward,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("Number of Accepted Invites") +
  ggtitle("Average Accepted Invites by Reward Treatment Arm") +
  theme_bw()

png("plot_sharing_reward.png", width=1600,height=400)
plot_sharing_reward
dev.off()

# internal consistency

data_consistency <- data %>%
  group_by(survey_round,configs) %>%
  summarise(mean = mean(inconsistent,na.rm=T),
            sd = sd(inconsistent,na.rm = T))

plot_consistency <- ggplot(data_consistency,aes(x=configs,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  #scale_x_discrete(labels = script_labs) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("% Inconsistent Answers") +
  ggtitle("% Inconsistent Answers by Attention Treatment Arm") +
  theme_bw()

png("plot_consistency.png", width=1600,height=400)
plot_consistency
dev.off()

data_consistency_reward <- data %>%
  group_by(survey_round,config_reward) %>%
  summarise(mean = mean(inconsistent,na.rm=T),
            sd = sd(inconsistent,na.rm = T))

plot_consistency_reward <- ggplot(data_consistency_reward,aes(x=config_reward,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  facet_wrap(~survey_round,scales = "free_x") +
  xlab("Treatment Arm") +
  ylab("% Inconsistent Answers") +
  ggtitle("% Inconsistent Answers by Reward Treatment Arm") +
  theme_bw()

png("plot_consistency_reward.png", width=1600,height=400)
plot_consistency_reward
dev.off()

## gender comparisons 

# total score

data_totscore <- data %>%
  group_by(gender) %>%
  summarise(mean = mean(score,na.rm=T),
            sd = sd(score,na.rm = T))

gender_totscore <- ggplot(data_totscore,aes(x=gender,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  scale_x_continuous(labels = gender_labs,breaks=c(1:3)) +
  xlab("Gender") +
  ylab("Total Score") +
  ggtitle("Total Score by Gender") +
  theme_bw()

png("gender_totscore.png", width=800,height=400)
gender_totscore
dev.off()

# average score

data_avgscore <- data %>%
  group_by(gender) %>%
  summarise(mean = mean(points,na.rm=T),
            sd = sd(points,na.rm = T))

gender_avgscore <- ggplot(data_avgscore,aes(x=gender,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  scale_x_continuous(labels = gender_labs,breaks=c(1:3)) +
  xlab("Gender") +
  ylab("Average Score") +
  ggtitle("Average Per-Comparison Score by Gender") +
  theme_bw()

png("gender_avgscore.png", width=800,height=400)
gender_avgscore
dev.off()

# average time per comparison

data_avgtime_clean <- data %>%
  filter(responsetime <= quantile(responsetime,probs=0.9,na.rm=T)) %>%
  group_by(gender) %>%
  summarise(mean = mean(responsetime,na.rm=T),
            sd = sd(responsetime,na.rm = T))

gender_avgtime_clean <- ggplot(data_avgtime_clean,aes(x=gender,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  scale_x_continuous(labels = gender_labs,breaks=c(1:3)) +
  xlab("Gender") +
  ylab("Time Per Comparison (seconds)") +
  ggtitle("Average Time Per Comparison by Gender (outliers cleaned)") +
  theme_bw()

png("gender_avgtime_clean.png", width=800,height=400)
gender_avgtime_clean
dev.off()

# total time spent

data_tottime_clean <- data %>%
  filter(responsetime <= quantile(responsetime,probs=0.9,na.rm=T)) %>%
  group_by(userid) %>%
  summarise(tot_time = sum(responsetime,na.rm=T),gender = max(gender)) %>%
  group_by(gender) %>%
  summarise(mean = mean(tot_time,na.rm=T),
            sd = sd(tot_time,na.rm = T))

gender_tottime_clean <- ggplot(data_tottime_clean,aes(x=gender,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  scale_x_continuous(labels = gender_labs,breaks=c(1:3)) +
  xlab("Gender") +
  ylab("Total Time Spent (days)") +
  ggtitle("Total Time Spent by Gender (outliers cleaned)") +
  theme_bw()

png("gender_tottime_clean.png", width=800,height=400)
gender_tottime_clean
dev.off()

# sensor data matching %

data_avgmatch_sens <- data %>%
  group_by(gender) %>%
  summarise(mean = mean(matchsat,na.rm=T),
            sd = sd(matchsat,na.rm = T))

gender_avgmatch_sens <- ggplot(data_avgmatch_sens,aes(x=gender,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  scale_x_continuous(labels = gender_labs,breaks=c(1:3)) +
  xlab("Gender") +
  ylab("% Matching") +
  ggtitle("Average % Matching with Sensor Data by Gender") +
  theme_bw()

png("gender_avgmatch_sense.png", width=800,height=400)
gender_avgmatch_sens
dev.off()

# neighbor matching %

data_avgmatch_neighb <- data %>%
  group_by(gender) %>%
  summarise(mean = mean(matchneighbour_real,na.rm=T),
            sd = sd(matchneighbour_real,na.rm = T))

gender_avgmatch_neighb <- ggplot(data_avgmatch_neighb,aes(x=gender,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  scale_x_continuous(labels = gender_labs,breaks=c(1:3)) +
  xlab("Gender") +
  ylab("% Matching") +
  ggtitle("Average % Matching with Neighbors by Gender") +
  theme_bw()

png("gender_avgmatch_neighb.png", width=800,height=400)
gender_avgmatch_neighb
dev.off()


# probability of getting a year in the top 25% correct (satellites)

data_topquart_sat <- data %>%
  mutate(quart_correct = ifelse( 
    (year1 %in% badyears_sat & !year2 %in% badyears_sat & answer == 1) |
      (year2 %in% badyears_sat & !year1 %in% badyears_sat & answer == 2)
    ,1,0)) %>%
  group_by(gender) %>%
  summarise(mean = mean(quart_correct,na.rm=T),
            sd = sd(quart_correct,na.rm = T))

gender_topquart_sat <- ggplot(data_topquart_sat,aes(x=gender,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  scale_x_continuous(labels = gender_labs,breaks=c(1:3)) +
  xlab("Gender") +
  ylab("% Matching") +
  ggtitle("Average % Matching with Any Top Quartile Sat by Gender") +
  theme_bw()

png("gender_topquart_sat.png", width=800,height=400)
gender_topquart_sat
dev.off()

# probability of getting a year in the top 25% correct (neighbors)

data_topquart_neighb <- data %>%
  mutate(quart_correct = ifelse( 
    (year1 %in% badyears_sat & !year2 %in% badyears_farmer & answer == 1) |
      (year2 %in% badyears_sat & !year1 %in% badyears_farmer & answer == 2)
    ,1,0)) %>%
  group_by(gender) %>%
  summarise(mean = mean(quart_correct,na.rm=T),
            sd = sd(quart_correct,na.rm = T))

gender_topquart_neighb <- ggplot(data_topquart_neighb,aes(x=gender,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  scale_x_continuous(labels = gender_labs,breaks=c(1:3)) +
  xlab("Gender") +
  ylab("% Matching") +
  ggtitle("Average % Matching with Any Top Quartile Neighbors by Gender") +
  theme_bw()

png("gender_topquart_neighb.png", width=800,height=400)
gender_topquart_neighb
dev.off()

# sharing

data_sharing <- data %>%
  group_by(userid) %>%
  summarise(inviteaccepted = max(inviteaccepted,na.rm=T),gender = max(gender,na.rm=T)) %>%
  group_by(gender) %>%
  summarise(mean = mean(inviteaccepted,na.rm=T),
            sd = sd(inviteaccepted,na.rm = T))

gender_sharing <- ggplot(data_sharing,aes(x=gender,y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  scale_x_continuous(labels = gender_labs,breaks=c(1:3)) +
  xlab("Treatment Arm") +
  ylab("Number of Accepted Invites") +
  ggtitle("Average Accepted Invites by Gender") +
  theme_bw()

png("gender_sharing.png", width=800,height=400)
gender_sharing
dev.off()

## look at behavior of top players

# average time per comparison

data_avgtime_clean <- data %>%
  filter(responsetime <= quantile(responsetime,probs=0.9,na.rm=T)) %>%
  group_by(top_performer) %>%
  summarise(mean = mean(responsetime,na.rm=T),
            sd = sd(responsetime,na.rm = T))

topperf_avgtime_clean <- ggplot(data_avgtime_clean,aes(x=factor(top_performer),y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  xlab("Status") +
  ylab("Time Per Comparison (seconds)") +
  ggtitle("Average Time Per Comparison by Top Performer Status (outliers cleaned)") +
  theme_bw()

png("topperf_avgtime_clean.png", width=800,height=400)
topperf_avgtime_clean
dev.off()

# sharing

data_sharing <- data %>%
  group_by(survey_round,userid) %>%
  summarise(inviteaccepted = max(inviteaccepted,na.rm=T),top_performer = top_performer) %>%
  group_by(survey_round,top_performer) %>%
  summarise(mean = mean(inviteaccepted,na.rm=T),
            sd = sd(inviteaccepted,na.rm = T))

topperf_sharing <- ggplot(data_sharing,aes(x=factor(top_performer),y=mean)) +
  geom_pointrange(aes(ymin = mean - 1.65*(sd), ymax = mean + 1.65*(sd))) +
  xlab("Status") +
  ylab("Number of Accepted Invites") +
  ggtitle("Average Accepted Invites by Top Performer Status") +
  theme_bw()

png("topperf_sharing.png", width=1600,height=400)
topperf_sharing
dev.off()

## bradley-terry ranking

responses <- data %>%
  select(year1,year2,answer,userid,survey_round) %>%
  mutate(answer=ifelse(answer == 4,NA,answer))

responses <- responses %>%
  filter(!is.na(answer))

responses_temp <- responses

responses <- responses %>% select(-survey_round)

responses <- cbind(responses,
                   win1=rep(0,nrow(responses)),win2=rep(0,nrow(responses)),
                   tie=rep(0,nrow(responses)),
                   win1_adj=rep(0,nrow(responses)),win2_adj=rep(0,nrow(responses)))

for (x in 1:nrow(responses)) {
  
  if (responses[x,3] == 1){
    responses[x,5] <- 1
    responses[x,8] <- 1
  }
  
  if (responses[x,3] == 2){
    responses[x,6] <- 1
    responses[x,9] <- 1
  }
  
  if (responses[x,3] == 3){
    responses[x,7] <- 1
    responses[x,8] <- 0.5
    responses[x,9] <- 0.5
  }
  
}

responses <- cbind(responses,responses_temp$survey_round)
colnames(responses)[10] <- "survey_round"

responses$year1_fac <- factor(responses$year1, 
                              labels = unique(c(responses$year1, responses$year2)),
                              levels = unique(c(responses$year1, responses$year2)))

responses$year2_fac <- factor(responses$year2,
                              labels = unique(c(responses$year1, responses$year2)),
                              levels = unique(c(responses$year1, responses$year2)))


dk_yearly <- data %>% gather(year1:year2,key="order",value="year") %>% ## impt. to keep in mind that DKs are not very common
  group_by(survey_round,year) %>%
  mutate(chosen = ifelse(order=="year1" & answer == 1,1,0)) %>%
  mutate(chosen = ifelse(order=="year2" & answer == 2 & chosen == 0,1,chosen)) %>%
  summarise(dk_count_yearly = sum(ifelse(answer == 4,1,0)),
            win_pct = mean(chosen,na.rm=T)) %>%
  ungroup()

year_cov <- left_join(sat,station,by="year") %>%
  relocate(year,sat,station)

year_cov <- left_join(year_cov,dk_yearly,by="year")

year_cov <- year_cov %>% mutate(topquart_sat = ifelse(sat >= 7,1,0),
                                topquart_station = ifelse(station >= 7,1,0))

indiv_cov <- data %>%
  group_by(survey_round) %>%
    mutate(treat_reward_binary = ifelse(config_reward == "r1",1,0),) %>%
    mutate(treat_attn_binary = ifelse(configs == "1",1,0)) %>%
    mutate(treat_attn_factor = factor(configs)) %>%
    mutate(responsetime_clean = ifelse(responsetime < quantile(responsetime,0.9,na.rm=T),responsetime,NA)) %>%
    group_by(userid) %>%
     mutate(indiv_dk_count = sum(ifelse(answer == 4,1,0)),
            mean_points = mean(points,na.rm=T),
            tot_responses = n(),
            avg_time = mean(responsetime_clean,na.rm=T),
            inconsistency = mean(inconsistent,na.rm=T)) %>%
    ungroup() %>%
  group_by(survey_round) %>%
    mutate(avg_time = ifelse(is.nan(avg_time),mean(avg_time,na.rm=T),avg_time)) %>%
    mutate(top_quart_points = ifelse(mean_points >= quantile(mean_points,0.8),1,0)) %>%
    mutate(answer=ifelse(answer == 4,NA,answer)) %>%
    mutate(gender = ifelse(gender == 1,1,0)) %>%
    filter(!is.na(answer)) %>%
    mutate(index = c(1:n())) %>%
  ungroup() %>%
  select(index,treat_reward_binary,treat_attn_binary,treat_attn_factor,
         indiv_dk_count,mean_points,top_quart_points,tot_responses,avg_time,inconsistency,
         gender,age,responsetime_clean,top_performer,survey_round)

years_seen <- data %>%
  filter(!is.na(answer)) %>%
  group_by(survey_round) %>%
    mutate(index = c(1:n())) %>%
    gather(year1:year2,key="order",value="year") %>%
    arrange(userid,time_stamp) %>%
    group_by(userid,year) %>%
    mutate(seen = ifelse(time_stamp == min(time_stamp),0,1)) %>%
  ungroup() %>%
  group_by(survey_round,index) %>%
    summarise(seen = max(seen)) %>%
  ungroup()

responses <- responses %>% group_by(survey_round) %>% mutate(index = c(1:n())) %>% ungroup()

responses <- left_join(responses,indiv_cov,by=c("index" = "index", "survey_round" = "survey_round"))
responses <- left_join(responses,years_seen,by=c("index" = "index", "survey_round" = "survey_round"))
responses <- left_join(responses,year_cov %>% rename(c("sat_y1" = "sat", "station_y1" = "station")),by=c("year1" = "year", "survey_round" = "survey_round"))
responses <- left_join(responses,year_cov %>% filter(survey_round == "Nov 2021") %>% select(-dk_count_yearly, -survey_round, ) %>% rename(c("sat_y2" = "sat", "station_y2" = "station")),by=c("year2" = "year"))

responses <- responses %>%
  mutate(sat_y1_bin = ifelse(sat_y1 > sat_y2,1,0),
         sat_y2_bin = ifelse(sat_y1 > sat_y2,0,1),
         station_y1_bin = ifelse(station_y1 > station_y2,1,0),
         station_y2_bin = ifelse(station_y1 > station_y2,0,1))

responses$year1_fac <- data.frame(year = responses$year1_fac, first = 1, 
                                  time_spent = responses$responsetime_clean,
                                  seen_before = responses$seen,
                                  treat_reward = responses$treat_reward_binary, treat_attn_binary = responses$treat_attn_binary, treat_attn_factor = responses$treat_attn_factor,
                                  indiv_dk_count = responses$indiv_dk_count,
                                  sat_bin = responses$sat_y1_bin, station_bin = responses$station_y1_bin)
responses$year2_fac <- data.frame(year = responses$year2_fac, first = 0, 
                                  time_spent = responses$responsetime_clean,
                                  seen_before = responses$seen,
                                  treat_reward = responses$treat_reward_binary, treat_attn_binary = responses$treat_attn_binary,treat_attn_factor = responses$treat_attn_factor,
                                  indiv_dk_count = responses$indiv_dk_count,
                                  sat_bin = responses$sat_y2_bin, station_bin = responses$station_y2_bin)

responses <- responses %>% select(-dk_count_yearly)

data_bt <- list(responses = responses %>% filter(survey_round == "Nov 2021"), yearly.cov = year_cov)

data_bt_r2 <- list(responses = responses %>% filter(survey_round == "Jun 2022"), yearly.cov = year_cov)

data_bt_pooled <- list(responses = responses, yearly.cov = year_cov)

data_bt_highperf <- list(responses = responses %>%
                           filter(top_performer == 1)
                           , yearly.cov = year_cov)

data_bt_lowperf <- list(responses = responses %>%
                           filter(top_performer == 0)
                         , yearly.cov = year_cov)

model_vanilla <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                     formula = ~ year,
                     id = "year",
                     data = data_bt)

summary(model_vanilla)

model_vanilla_pooled <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                     formula = ~ year,
                     id = "year",
                     data = data_bt_pooled)

summary(model_vanilla_pooled)


model_highperf <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                     formula = ~ year,
                     id = "year",
                     data = data_bt_highperf)

summary(model_highperf)

model_lowperf <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                      formula = ~ year,
                      id = "year",
                      data = data_bt_lowperf)

summary(model_lowperf)

model_round2 <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                      formula = ~ year,
                      id = "year",
                      data = data_bt_r2)

summary(model_round2)

model_ties <- BTm(outcome = cbind(win1_adj,win2_adj), player1 = year1_fac, player2 = year2_fac,
                  formula = ~ year,
                  id = "year",
                  data = data_bt)

summary(model_ties)

model_order <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                   formula = ~ year + first,
                   id = "year",
                   data = data_bt)

summary(model_order)

anova(model_vanilla,model_order,test="F")

model_dk_indiv <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                   formula = ~ year + year:indiv_dk_count,
                   id = "year",
                   data = data_bt)

summary(model_dk_indiv)

anova(model_vanilla,model_dk_indiv,test="F")

model_seen_indiv <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                      formula = ~ year + year:seen,
                      id = "year",
                      data = data_bt)

summary(model_seen_indiv)

anova(model_vanilla,model_seen_indiv,test="F")

model_time_indiv <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                      formula = ~ year + year:avg_time,
                      id = "year",
                      data = data_bt)

summary(model_time_indiv)

anova(model_vanilla,model_time_indiv,test="F")

model_gender_indiv <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                        formula = ~ year + year:gender,
                        id = "year",
                        data = data_bt)

summary(model_gender_indiv)

anova(model_vanilla,model_gender_indiv,test="F")

model_age_indiv <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                          formula = ~ year + year:age,
                          id = "year",
                          data = data_bt)

summary(model_age_indiv)

anova(model_vanilla,model_age_indiv,test="F")

model_totresp_indiv <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                        formula = ~ year + year:tot_responses,
                        id = "year",
                        data = data_bt)

summary(model_totresp_indiv)

anova(model_vanilla,model_totresp_indiv,test="F")

model_points <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                      formula = ~ year + year:top_quart_points,
                      id = "year",
                      data = data_bt)

summary(model_points)

anova(model_vanilla,model_points,test="F")

model_topperf <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                    formula = ~ year + year:top_performer,
                    id = "year",
                    data = data_bt)

summary(model_topperf)

anova(model_vanilla,model_topperf,test="F")


model_topperf_pooled <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                     formula = ~ year + year:top_performer,
                     id = "year",
                     data = data_bt_pooled, 
                     refcat = "2000")

summary(model_topperf_pooled)

# anova(model_vanilla,model_topperf_pooled,test="F")

model_consistency <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                    formula = ~ year + year:inconsistency,
                    id = "year",
                    data = data_bt)

summary(model_consistency)

anova(model_vanilla,model_consistency,test="F")

model_sensors  <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                   formula = ~ (1|year) + sat[year] + station[year],
                   id = "year",
                   data = data_bt)
  
summary(model_sensors)

model_sensors_worst  <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                      formula = ~ (1|year) + topquart_sat[year] + topquart_station[year],
                      id = "year",
                      data = data_bt)

summary(model_sensors_worst)


model_dk_yearly_sensors  <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                      formula = ~ (1|year) + sat[year] + station[year] + dk_count_yearly[year],
                      id = "year",
                      data = data_bt)

summary(model_dk_yearly_sensors)

model_dk_indiv_sensors  <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                                formula = ~ (1|year) + sat[year] + station[year] + 
                                                    + sat[year]:indiv_dk_count + station[year]:indiv_dk_count,
                                id = "year",
                                data = data_bt)

summary(model_dk_indiv_sensors)

model_time_sensors  <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                               formula = ~ (1|year) + sat[year] + station[year] + 
                                 + sat[year]:avg_time + station[year]:avg_time,
                               id = "year",
                               data = data_bt)

summary(model_time_sensors)

model_gender_sensors  <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                           formula = ~ (1|year) + sat[year] + station[year] + 
                             + sat[year]:gender + station[year]:gender,
                           id = "year",
                           data = data_bt)

summary(model_gender_sensors)

model_age_sensors  <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                             formula = ~ (1|year) + sat[year] + station[year] + 
                               + sat[year]:age + station[year]:age,
                             id = "year",
                             data = data_bt)

summary(model_age_sensors)

model_seen_sensors  <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                          formula = ~ (1|year) + sat[year] + station[year] + 
                            + sat[year]:seen + station[year]:seen,
                          id = "year",
                          data = data_bt)

summary(model_seen_sensors)

model_totresp_sensors  <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                           formula = ~ (1|year) + sat[year] + station[year] + 
                             + sat[year]:tot_responses + station[year]:tot_responses,
                           id = "year",
                           data = data_bt)

summary(model_totresp_sensors)

model_consistency_sensors  <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                              formula = ~ (1|year) + sat[year] + station[year] + 
                                + sat[year]:inconsistency + station[year]:inconsistency,
                              id = "year",
                              data = data_bt)

summary(model_consistency_sensors)


model_treat_rewards  <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                      formula = ~ year + year:treat_reward_binary,
                      id = "year",
                      data = data_bt)

summary(model_treat_rewards)

anova(model_vanilla,model_treat_rewards,test="F")

model_treat_rewards_sensors <-   BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                             formula = ~ (1|year) + sat[year]:treat_reward_binary + station[year]:treat_reward_binary
                             + sat[year] + station[year],
                             id = "year",
                             data = data_bt)
summary(model_treat_rewards_sensors)

model_treat_rewards_consensus <-   BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                                     formula = ~ (1|year) + win_pct[year]:treat_reward_binary +
                                     + win_pct[year],
                                     id = "year",
                                     data = data_bt)
summary(model_treat_rewards_consensus)

model_treat_attn  <- BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                            formula = ~ year + year:treat_attn_factor,
                            id = "year",
                            data = data_bt)

summary(model_treat_attn)

anova(model_vanilla,model_treat_attn,test="F")

model_treat_attn_sensors <-   BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                                     formula = ~ (1|year) + sat[year]:treat_attn_factor + station[year]:treat_attn_factor
                                     + sat[year] + station[year],
                                     id = "year",
                                     data = data_bt)
summary(model_treat_attn_sensors)

model_treat_attn_consensus <-   BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                                       formula = ~ (1|year) + win_pct[year]:treat_attn_factor +
                                         + win_pct[year],
                                       id = "year",
                                       data = data_bt)
summary(model_treat_attn_consensus)

model_topperf_sensors <-   BTm(outcome = cbind(win1,win2), player1 = year1_fac, player2 = year2_fac,
                                  formula = ~ (1|year) + sat[year]:top_performer + station[year]:top_performer
                                  + sat[year] + station[year],
                                  id = "year",
                                  data = data_bt)
summary(model_topperf_sensors)

## plot 

results_allmods <- list()
mod_names <- c("Consistent Players Only (Rounds 1+2)", "All Other Players (Rounds 1+2)")

i <- 1
for (mod in list(model_highperf,model_lowperf)) {

  
  model <- mod
  
  ## Extract estimated ability scores and rank them
  
  ranks <- BTabilities(model)
  ranks_ordered <- data.frame(ranks)
  ranks_ordered <- ranks_ordered[order(ranks_ordered$ability),]
  ranks_ordered
  
  ## Plot confidence intervals 
  
  # ranks.qv <- qvcalc(ranks)
  # term <- rownames(ranks.qv[["covmat"]])
  # estimate <- ranks.qv[["qvframe"]][["estimate"]]
  # std.error <- ranks.qv[["qvframe"]][["quasiSE"]]
  
  term <- rownames(ranks_ordered)
  estimate <- ranks_ordered$ability
  std.error <- ranks_ordered$s.e.
  
  model <- mod_names[i]
  plot <- data.frame(term,estimate,std.error,model)
  plot$estimate <- plot$estimate - min(plot$estimate)
  plot$std.error <- plot$std.error / max(plot$estimate)
  plot$estimate <- plot$estimate / max(plot$estimate)

  results_allmods[[i]] <- plot
  
  i <- i + 1

}
 
results_allmods_plot <- bind_rows(results_allmods)

plot_order <- results_allmods_plot$term[order(results_allmods_plot$estimate)]
plot_order <- unique(plot_order)
results_allmods_plot$term <- factor(results_allmods_plot$term,levels=plot_order)

highlight = function(x, list, color="black", family="") {
  ifelse(x %in% list, glue("<b style='font-family:{family}; color:{color}'>{x}</b>"), x)
}

ranks_plot <- dwplot(results_allmods_plot,dot_args=list(size=2),whisker_args=list(size=.3)) +
  theme_bw()+
  scale_y_discrete(labels = function(x) highlight(x,paste(known_bad_years,sep="|"),"orange")) +
  geom_vline(xintercept = 0.60, linetype = 2) +
  xlab("Estimated Ranking of Bad Years \n Known bad years highlighted in orange") +
  theme(legend.title = element_blank(), legend.position = 'bottom') +
  theme(axis.text.y=element_markdown())

png("bt_ranking.png", width=800,height=400)
print(ranks_plot)
dev.off()

spearman <- results_allmods_plot %>%
  select(-std.error) %>%
  spread(model,estimate)

spearman$term <- as.numeric(paste(spearman$term))

spearman <- left_join(spearman,sat,by=c("term" = "year"))
spearman <- left_join(spearman,station,by=c("term" = "year"))

cor.test(x=spearman$Vanilla, y=spearman$sat, method = 'spearman')
cor.test(x=spearman$Vanilla, y=spearman$station, method = 'spearman')

# balance tests 

balance <- data %>% 
  mutate(treat = ifelse(configs == 1,0,1),
         gender = ifelse(gender == 1,1,2)) %>%
  group_by(gender,treat) %>% 
  summarise(n = length(unique(userid))) %>%
  ungroup() %>%
  spread(key="gender",value="n")

colnames(balance) <- c("Treatment Status","# Players [Female]","# Players [Male]")
write.csv(balance,"ikon_technicafe_balance.csv",row.names=T)


