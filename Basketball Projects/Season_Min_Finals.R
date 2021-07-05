library(dplyr)
library(ggplot2)
library(nbastatR)
library(purrr)
library(ggthemes)

finals_season_mins = function(season,teamone,teamtwo) {
  
  game_logs <- game_logs(seasons = season,result_types = "player",season_types = "Regular Season")
  players <- bref_players_stats(seasons = season,only_totals = FALSE)
  
  finals_opening_rosters <- game_logs %>% 
                            filter((slugTeam == teamone | slugTeam == teamtwo ) & numberGameTeamSeason == 1) %>% 
                            arrange(slugTeam) %>%
                            select(yearSeason,slugTeam,namePlayer)
    if (season == 2012) {
      totalMin <- 48*5*66
    } else {
      totalMin <- 19680
    }
  season_min <- players %>% 
                filter(slugTeamBREF %in% finals_opening_rosters$slugTeam & namePlayer %in% finals_opening_rosters$namePlayer) %>%
                mutate(`Finals Team & Year` = stringr::str_c(slugTeamBREF,yearSeason, sep = " - ")) %>%
                group_by(`Finals Team & Year`) %>%
                summarize(`% of Season Minutes`= (sum(minutes)/totalMin)*100)
                 
  season_min
}

season_mins = function(season) {
  game_logs <- game_logs(seasons = season,result_types = "player",season_types = "Regular Season")
  players <- bref_players_stats(seasons = season,only_totals = FALSE)
  opening_rosters <- game_logs %>% 
                            filter(numberGameTeamSeason == 1) %>% 
                            arrange(slugTeam) %>%
                            select(yearSeason,slugTeam,namePlayer)
  
  if (season == 2012) {
    totalMin <- 48*5*66
  } else {
    totalMin <- 19680
  }
  season_min <- players %>% 
                filter(namePlayer %in% opening_rosters$namePlayer & !slugTeamBREF %in% "TOT") %>%
                mutate(`Team & Year` = stringr::str_c(slugTeamBREF,yearSeason, sep = " - ")) %>%
                group_by(`Team & Year`) %>%
                summarize(`% of Season Minutes`= (sum(minutes)/totalMin)*100)
  
  season_min
}

years <- c(2000:2019)
champs <- c("LAL","LAL","LAL","SAS","DET","SAS","MIA","SAS","BOS","LAL","LAL","DAL","MIA","MIA","SAS","GSW","CLE","GSW","GSW","TOR")
runnup <- c("IND","PHI","NJN","NJN","LAL","DET","DAL","CLE","LAL","ORL","BOS","MIA","OKC","SAS","MIA","CLE","GSW","CLE","CLE","GSW")

finals_teams <- pmap_dfr(list(years,champs,runnup),finals_season_mins)
finals_teams_upd <- finals_teams %>% arrange(desc(`% of Season Minutes`)) %>% mutate(`Finals Team & Year` = factor(`Finals Team & Year`,`Finals Team & Year`))

champs_yrs <- stringr::str_c(champs,years,sep = " - ")
ggplot(finals_teams_upd, aes(x = `Finals Team & Year`,y = `% of Season Minutes`)) +
         geom_point(color=ifelse(finals_teams_upd$`Finals Team & Year` %in% champs_yrs, "goldenrod2", "grey"), 
                    size=ifelse(finals_teams_upd$`Finals Team & Year` %in% champs_yrs, 3, 1) ) +
         geom_segment( aes(x=`Finals Team & Year`, xend=`Finals Team & Year`, y=0, yend=`% of Season Minutes`),
                       color=ifelse(finals_teams_upd$`Finals Team & Year` %in% champs_yrs, "goldenrod2", "grey"), 
                       size=ifelse(finals_teams_upd$`Finals Team & Year` %in% champs_yrs, 1.3, 0.7)) +
         coord_flip() +
         ggtitle("How important is continuity?") +
         theme_wsj()

teams_mins <- map_dfr(years,season_mins)
teams_min_upd <- teams_mins %>% arrange(desc(`% of Season Minutes`)) %>% 
                 mutate(`Team & Year` = factor(`Team & Year`,`Team & Year`)) %>%
                 head(40)

ggplot(teams_min_upd, aes(x = `Team & Year`,y = `% of Season Minutes`)) +
  geom_point(color=ifelse(teams_min_upd$`Team & Year` %in% champs_yrs, "goldenrod2", "grey"), 
             size=ifelse(teams_min_upd$`Team & Year` %in% champs_yrs, 3, 1) ) +
  geom_segment( aes(x=`Team & Year`, xend=`Team & Year`, y=0, yend=`% of Season Minutes`),
                color=ifelse(teams_min_upd$`Team & Year` %in% champs_yrs, "goldenrod2", "grey"), 
                size=ifelse(teams_min_upd$`Team & Year` %in% champs_yrs, 1.3, 0.7)) +
  coord_flip() +
  ggtitle("How important is continuity?") +
  theme_wsj()
  
  
