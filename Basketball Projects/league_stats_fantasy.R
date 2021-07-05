library(googlesheets4)
library(nbastatR)
library(dplyr)

stats <- googledrive::drive_get("SBC League Index")
# sheet_add(boise,sheet = "League Stats",.after = "Max Stats - VIS"
#                     ,gridProperties = list(
#                       rowCount = 600, columnCount = 75,
#                      frozenRowCount = 1,frozenColumnCount = 2
#                     ) )

#### LEAGUE STATS
l_stats <- bref_players_stats(seasons = 2021,tables = c("totals","advanced","per_game"),
                              widen_data = T)
curr <- read_sheet(stats,range = "League Stats!A3:B")
l_stats <- left_join(l_stats,curr,by = c("namePlayer"="Name"))


shooting <- l_stats %>% select(c("pctFG2","pctFG3","pctFT","pctTrueShooting","pctFG")) *100
shooting[shooting == 1.0 | shooting$pctTrueShooting < 2.0] <- shooting[shooting == 1.0 | shooting$pctTrueShooting < 2.0] * 100.0

collective <- l_stats %>%
          select(Team, 'Name' = namePlayer,'Pos' = groupPosition, 'Age' = agePlayer,
                 'MP' = minutesTotals,"TS%" = pctTrueShooting,'2PA/G' = fg2aPerGame,'2P%' = pctFG2,
                 '3PA/G' = fg3aPerGame,'3P%' = pctFG3,'FTA/G' = ftaPerGame,'FT%' = pctFT,
                 'ORB' = orbTotals,'DRB' = drbTotals,'AST' = astTotals,'STL' = stlTotals,'BLK' = blkTotals,
                 'PTS' = ptsTotals,'GP' = countGames,'GS' = countGamesStarted,'M/G' = minutesPerGame,
                 'FG/G' = fgmPerGame,  'FGA/G' = fgaPerGame,'3P/G' = fg3mPerGame,
                 '2P/G' = fg2mPerGame,'FT/G' = ftmPerGame,
                 'ORB/G' = orbPerGame,'DRB/G' = drbPerGame,'TRB/G' = trbPerGame,'AST/G' = astPerGame,
                 'TOV/G' = tovPerGame,'STL/G' = stlPerGame,'BLK/G' = blkPerGame,'PF/G' = pfPerGame,  'PTS/G' = ptsPerGame,
                 'FG' = fgmTotals,'FGA' = fgaTotals,'FG%' = pctFG,'3P' = fg3mTotals,'3PA' = fg3aTotals,
                  '2P' = fg2mTotals,'2PA' = fg2aTotals,'FT' = ftmTotals,'FTA' = ftaTotals,
                  'TRB' = trbTotals, 'TOV' = tovTotals,'PF' = pfTotals)
collective[c("TS%","3P%","2P%","FT%","FG%")] <- shooting[c("pctTrueShooting","pctFG3","pctFG2","pctFT","pctFG")]

avg_plyr <- collective %>% summarise_if(is.numeric,mean)
avg_plyr <- round(avg_plyr,3)

collective <- collective %>% arrange(Name) %>%
              mutate("Calc Value" = ((MP-avg_plyr$MP)/avg_plyr$MP)*.027 + ((`TS%`-avg_plyr$`TS%`)/avg_plyr$`TS%`)*.108 + ((`2P%`-avg_plyr$`2P%`)/avg_plyr$`2P%`)*.081 +
                                    ((`3P%`-avg_plyr$`3P%`)/avg_plyr$`3P%`)*.081 + ((`FT%`-avg_plyr$`FT%`)/avg_plyr$`FT%`)*.054 + ((STL-avg_plyr$STL)/avg_plyr$STL)*.081 +
                                    ((ORB-avg_plyr$ORB)/avg_plyr$ORB)*.081 + ((DRB-avg_plyr$DRB)/avg_plyr$DRB)*.081 + ((AST-avg_plyr$AST)/avg_plyr$AST)*.108 + 
                                    ((BLK-avg_plyr$BLK)/avg_plyr$BLK)*.081 + ((PTS-avg_plyr$PTS)/avg_plyr$PTS)*.162 - ((TOV-avg_plyr$TOV)/avg_plyr$TOV)*.054)

### REMEMBER TO ALWAYS ARRANGE THE GOOGLE SHEET IN ALPHABETICAL ORDER BEFORE WRITING TO IT
range_write(ss = stats,avg_plyr,sheet = "League Stats",range = "D1")
stats %>% range_write(collective,sheet = "League Stats",range = "A3")
range_autofit(stats,sheet = "League Stats")

#### ROSTER STATS
rost_stats <- collective[collective$Name %in% c("Andrew Wiggins","Ben McLemore", "Cassius Stanley","Coby White","Dorian Finney-Smith","Enes Kanter",
                                                "Giannis Antetokounmpo","Ivica Zubac","Josh Hart","Payton Pritchard","Ricky Rubio","Duncan Robinson",
                                                "Rui Hachimura","Frank Kaminsky"),] %>% 
  select(Name,Age,MP,PTS,ORB,DRB,TRB,AST,TOV,STL,BLK,PF,FG,FGA,'TS%','2P','2PA','2P%','3P','3PA','3P%','FT','FTA','FT%')


stats %>% range_write(rost_stats,sheet = "Roster Stats",range = "A2")
range_autofit(stats,sheet = "Roster Stats")


#### MORE THAN 10 MINUTES
more_ten <- collective %>% filter(`M/G` > 10)
ap_mt <- more_ten %>% summarise_if(is.numeric,mean)
ap_mt <- round(ap_mt,3)
more_ten <- more_ten %>% arrange(Name) %>%
            mutate("Calc Value" = ((MP-ap_mt$MP)/ap_mt$MP)*.027 + ((`TS%`-ap_mt$`TS%`)/ap_mt$`TS%`)*.108 + ((`2P%`-ap_mt$`2P%`)/ap_mt$`2P%`)*.081 +
                     ((`3P%`-ap_mt$`3P%`)/ap_mt$`3P%`)*.081 + ((`FT%`-ap_mt$`FT%`)/ap_mt$`FT%`)*.054 + ((STL-ap_mt$STL)/ap_mt$STL)*.081 +
                     ((ORB-ap_mt$ORB)/ap_mt$ORB)*.081 + ((DRB-ap_mt$DRB)/ap_mt$DRB)*.081 + ((AST-ap_mt$AST)/ap_mt$AST)*.108 + 
                     ((BLK-ap_mt$BLK)/ap_mt$BLK)*.081 + ((PTS-ap_mt$PTS)/ap_mt$PTS)*.162 - ((TOV-ap_mt$TOV)/ap_mt$TOV)*.054)
stats %>% range_write(ap_mt,sheet = "> 10 MPG",range = "D1")
stats %>% range_write(more_ten,sheet = "> 10 MPG",range = "A3")
range_autofit(stats,sheet = "> 10 MPG")


#### POSITION BREAKDOWN
positions <- more_ten %>% group_split(Pos)
centers <- positions[[1]]
forwards <- positions[[2]]
guards <- positions[[3]]

#### GUARDS
ap_guards <- guards %>% summarise_if(is.numeric,mean)
ap_guards <- round(ap_guards,3)
guards <- guards %>%
  mutate("Calc Value" = ((MP-ap_guards$MP)/ap_guards$MP)*.027 + ((`TS%`-ap_guards$`TS%`)/ap_guards$`TS%`)*.108 + ((`2P%`-ap_guards$`2P%`)/ap_guards$`2P%`)*.081 +
           ((`3P%`-ap_guards$`3P%`)/ap_guards$`3P%`)*.081 + ((`FT%`-ap_guards$`FT%`)/ap_guards$`FT%`)*.054 + ((STL-ap_guards$STL)/ap_guards$STL)*.081 +
           ((ORB-ap_guards$ORB)/ap_guards$ORB)*.081 + ((DRB-ap_guards$DRB)/ap_guards$DRB)*.081 + ((AST-ap_guards$AST)/ap_guards$AST)*.108 + 
           ((BLK-ap_guards$BLK)/ap_guards$BLK)*.081 + ((PTS-ap_guards$PTS)/ap_guards$PTS)*.162 - ((TOV-ap_guards$TOV)/ap_guards$TOV)*.054)
stats %>% range_write(ap_guards,sheet = "> 10 MPG: Guards",range = "D1")
stats %>% range_write(guards,sheet = "> 10 MPG: Guards",range = "A3")

#### FORWARDS
ap_forwards <- forwards %>% summarise_if(is.numeric,mean)
ap_forwards <- round(ap_forwards,3)
forwards <- forwards %>%
  mutate("Calc Value" = ((MP-ap_forwards$MP)/ap_forwards$MP)*.027 + ((`TS%`-ap_forwards$`TS%`)/ap_forwards$`TS%`)*.108 + ((`2P%`-ap_forwards$`2P%`)/ap_forwards$`2P%`)*.081 +
           ((`3P%`-ap_forwards$`3P%`)/ap_forwards$`3P%`)*.081 + ((`FT%`-ap_forwards$`FT%`)/ap_forwards$`FT%`)*.054 + ((STL-ap_forwards$STL)/ap_forwards$STL)*.081 +
           ((ORB-ap_forwards$ORB)/ap_forwards$ORB)*.081 + ((DRB-ap_forwards$DRB)/ap_forwards$DRB)*.081 + ((AST-ap_forwards$AST)/ap_forwards$AST)*.108 + 
           ((BLK-ap_forwards$BLK)/ap_forwards$BLK)*.081 + ((PTS-ap_forwards$PTS)/ap_forwards$PTS)*.162 - ((TOV-ap_forwards$TOV)/ap_forwards$TOV)*.054)
stats %>% range_write(ap_forwards,sheet = "> 10 MPG: Forwards",range = "D1")
stats %>% range_write(forwards,sheet = "> 10 MPG: Forwards",range = "A3")

#### CENTERS
ap_centers <- centers %>% summarise_if(is.numeric,mean)
ap_centers <- round(ap_centers,3)
centers <- centers %>%
  mutate("Calc Value" = ((MP-ap_centers$MP)/ap_centers$MP)*.027 + ((`TS%`-ap_centers$`TS%`)/ap_centers$`TS%`)*.108 + ((`2P%`-ap_centers$`2P%`)/ap_centers$`2P%`)*.081 +
           ((`3P%`-ap_centers$`3P%`)/ap_centers$`3P%`)*.081 + ((`FT%`-ap_centers$`FT%`)/ap_centers$`FT%`)*.054 + ((STL-ap_centers$STL)/ap_centers$STL)*.081 +
           ((ORB-ap_centers$ORB)/ap_centers$ORB)*.081 + ((DRB-ap_centers$DRB)/ap_centers$DRB)*.081 + ((AST-ap_centers$AST)/ap_centers$AST)*.108 + 
           ((BLK-ap_centers$BLK)/ap_centers$BLK)*.081 + ((PTS-ap_centers$PTS)/ap_centers$PTS)*.162 - ((TOV-ap_centers$TOV)/ap_centers$TOV)*.054)
stats %>% range_write(ap_centers,sheet = "> 10 MPG: Centers",range = "D1")
stats %>% range_write(centers,sheet = "> 10 MPG: Centers",range = "A3")

range_autofit(stats,sheet = "> 10 MPG: Guards")
range_autofit(stats,sheet = "> 10 MPG: Forwards")
range_autofit(stats,sheet = "> 10 MPG: Centers")



                                      