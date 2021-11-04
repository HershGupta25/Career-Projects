library(readr)
library(dplyr)
library(tidyverse)

setwd("/Users/HerschelGupta/Downloads");
shots <- read_csv("shots_data.csv");

shot_bins <- shots %>% 
         mutate(shottype = case_when(
          (abs(x) > 22 & y <= 7.8) ~ "Corner 3",
          ((x^2 + y^2)^.5 > 23.75) ~ "Non Corner 3",
          TRUE ~ "Two Point")) 

summary <- shot_bins %>%
            group_by(team, shottype) %>%
            summarize(made = sum(fgmade),n=n()) %>%
            mutate("eFG%" = round(if_else(grepl("3",shottype), 
                                       (made*1.5)/n,made/n),3),
                   "Shot %" = round(n/sum(n),3))


