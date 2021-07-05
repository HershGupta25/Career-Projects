library(nbastatR)
library(dplyr)
library(future)
library(matrixStats)
library(ggplot2)
library(plotly)
library(readxl)
library(pracma)

setwd("/Users/HerschelGupta/Documents/BasketballAnalytics")
player_data <- bref_players_stats(2020,c("per_game","advanced"),T,F,F,F,T,T,T)
database <- read_excel("SBCFL Cap Sheets.xlsx",sheet = "Free Agency")
avail_players <- database$Player[231:652]

avail_data <- player_data[player_data$namePlayer %in% avail_players,]

upd_data <- avail_data %>% select(namePlayer,slugPosition,agePlayer,slugTeamBREF,countGames,countGamesStarted,pctFG,pctFG3,pctFG2,pctEFG,pctFT,minutesPerGame,orbPerGame,drbPerGame,trbPerGame,astPerGame,stlPerGame,blkPerGame,
                                  tovPerGame,ptsPerGame,pct3PRate,pctFTRate,pctORB,pctDRB,pctTRB,pctAST,pctSTL,pctBLK,pctTOV,pctUSG)
forwards <- upd_data %>% filter(avail_data$groupPosition == "F") %>% arrange(desc(slugPosition),desc(minutesPerGame)) %>% 
  select(namePlayer,slugTeamBREF,slugPosition,agePlayer,minutesPerGame,ptsPerGame,pctUSG,astPerGame,pctAST,tovPerGame,pctTOV,trbPerGame,pctTRB,stlPerGame,blkPerGame,pctFG3)
for_ast <- forwards %>% filter(minutesPerGame > 15) %>% arrange(desc(pctAST)) %>% head(20) %>% select(namePlayer,slugTeamBREF,pctAST)
for_trb <- forwards %>% filter(minutesPerGame > 15) %>% arrange(desc(pctTRB)) %>% head(20) %>% select(namePlayer,slugTeamBREF,pctTRB)
for_3p <- forwards %>% filter(minutesPerGame > 15) %>% arrange(desc(pctFG3)) %>% head(20) %>% select(namePlayer,slugTeamBREF,pctFG3)
centers <- upd_data %>% filter(avail_data$groupPosition == "C") %>% arrange(desc(minutesPerGame)) %>%
  select(namePlayer,slugTeamBREF,slugPosition,agePlayer,minutesPerGame,ptsPerGame,pctUSG,astPerGame,pctAST,orbPerGame,pctORB,drbPerGame,pctDRB,trbPerGame,pctTRB,stlPerGame,blkPerGame,pctBLK,pctFG3)
cen_ast <- centers %>% filter(minutesPerGame > 15) %>% arrange(desc(pctAST)) %>% head(20) %>% select(namePlayer,slugTeamBREF,pctAST)
cen_trb <- centers %>% filter(minutesPerGame > 15) %>% arrange(desc(pctTRB)) %>% head(20) %>% select(namePlayer,slugTeamBREF,pctTRB)
cen_orb <- centers %>% filter(minutesPerGame > 15) %>% arrange(desc(pctORB)) %>% head(20) %>% select(namePlayer,slugTeamBREF,pctORB)
cen_3p <- centers %>% filter(minutesPerGame > 15) %>% arrange(desc(pctFG3)) %>% head(20) %>% select(namePlayer,slugTeamBREF,pctFG3)
center_comp <- 
guards <- upd_data %>% filter(avail_data$groupPosition == "G") %>% arrange(slugPosition,desc(minutesPerGame)) %>%
  select(namePlayer,slugTeamBREF,slugPosition,agePlayer,minutesPerGame,ptsPerGame,pctUSG,astPerGame,pctAST,tovPerGame,pctTOV,trbPerGame,pctTRB,stlPerGame,blkPerGame,pctFG3,pctSTL)
grd_ast <- guards %>% filter(minutesPerGame > 15) %>% arrange(desc(pctAST)) %>% head(20) %>% select(namePlayer,slugTeamBREF,pctAST)
grd_stl <- guards %>% filter(minutesPerGame > 15) %>% arrange(desc(pctSTL)) %>% head(20) %>% select(namePlayer,slugTeamBREF,pctSTL)
grd_trb <- guards %>% filter(minutesPerGame > 15) %>% arrange(desc(pctTRB)) %>% head(20) %>% select(namePlayer,slugTeamBREF,pctTRB)
grd_3p <- guards %>% filter(minutesPerGame > 15) %>% arrange(desc(pctFG3)) %>% head(20) %>% select(namePlayer,slugTeamBREF,pctFG3)

write.csv(forwards,"/Users/HerschelGupta/Documents/BasketballAnalytics/forwards.csv")
write.csv(for_ast,"/Users/HerschelGupta/Documents/BasketballAnalytics/for_ast.csv")
write.csv(for_trb,"/Users/HerschelGupta/Documents/BasketballAnalytics/for_trb.csv")
write.csv(for_3p,"/Users/HerschelGupta/Documents/BasketballAnalytics/for_3p.csv")
write.csv(guards,"/Users/HerschelGupta/Documents/BasketballAnalytics/guards.csv")
write.csv(grd_ast,"/Users/HerschelGupta/Documents/BasketballAnalytics/grd_ast.csv")
write.csv(grd_stl,"/Users/HerschelGupta/Documents/BasketballAnalytics/grd_stl.csv")
write.csv(grd_trb,"/Users/HerschelGupta/Documents/BasketballAnalytics/grd_trb.csv")
write.csv(grd_3p,"/Users/HerschelGupta/Documents/BasketballAnalytics/grd_3p.csv")
write.csv(centers,"/Users/HerschelGupta/Documents/BasketballAnalytics/centers.csv")
write.csv(cen_ast,"/Users/HerschelGupta/Documents/BasketballAnalytics/cen_ast.csv")
write.csv(cen_orb,"/Users/HerschelGupta/Documents/BasketballAnalytics/cen_orb.csv")
write.csv(cen_trb,"/Users/HerschelGupta/Documents/BasketballAnalytics/cen_trb.csv")
write.csv(cen_3p,"/Users/HerschelGupta/Documents/BasketballAnalytics/cen_3p.csv")