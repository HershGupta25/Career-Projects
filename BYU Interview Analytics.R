library(ncaahoopR)
library(rvest)
library(xml2)
library(corrplot)

college <- read_html("https://www.sports-reference.com/cbb/seasons/2019-ratings.html")
college_18_19 <- college %>% html_node("#div_ratings") %>% html_table() 
colnames(college_18_19) <- college_18_19[1,]
college_18_19 <- college_18_19[(college_18_19$Rk != "" & college_18_19$Rk != "Rk") & -1,!(colnames(college_18_19)=="NA")]

teams <- read_html("https://www.ncaa.com/brackets/basketball-men/d1/2019")
names <- teams %>% html_nodes(".seed,.name") %>% html_text() %>% 
         stringr::str_replace_all(c("St."="State","Ky."="Kentucky","N.C."="North Carolina","Ole Miss"="Mississippi",
                                    "LSU"="Louisiana State","State John's"="St. John's","VCU"="Virginia Commonwealth",
                                    "UCF"="Central Florida","C I"="C-I"))
seeds <- c(17 - c(1,1,1,2,1,3,2,2,2,3,5,4,3,4,6,4,5,7,3,6,7,5,6,10,4,9,5,7,6,10,12,7,11,8,9,9,11,10,8,9,8,8,11,10,12,11,12,11,11,13,14,12,13,13,14,13,14,14,15,15,15,15,16,16,16,16,16,16),integer(285))

tourney_18_19 <- college_18_19 %>% 
                mutate(Tourney = 0,Tourney = ifelse(School %in% names,1,0)) %>%
                arrange(desc(Tourney)) %>%
                mutate(Seed = seeds)

corr_mat <- tourney_18_19 %>% 
            select(W:SOS,ORtg:Seed) %>% 
            mutate_if(is.character,as.numeric) %>% 
            cor(use = "pairwise.complete.obs")
corrplot(corr_mat,method="color",type="upper",
         tl.srt=45,col=colorRampPalette(c("red3","darkgreen"))(20),
         tl.col="black",insig = "blank",addCoef.col = "white")

adv_stats <- read_html("https://www.sports-reference.com/cbb/seasons/2019-advanced-school-stats.html") %>%
             html_node("#div_adv_school_stats") %>% html_table()
colnames(adv_stats) <- adv_stats[1,]
adv_stats <- adv_stats[(adv_stats$Rk != "" & adv_stats$Rk != "Rk") & -1,!(colnames(adv_stats)=="NA")]
colnames(adv_stats)[c(4,5,9:16)] <- c("Ovr. W","Ovr. L","Conf. W","Conf. L","Home W","Home L","Away W","Away L","Tm. Pts","Opp Pts")

seeds_adv <- tourney_18_19 %>% arrange(desc(Tourney),School) %>% select(Seed)
seeds_adv[9:58,] <- seeds_adv[8:57,]
seeds_adv[8] <- 4

adv_stats <- adv_stats %>% mutate(Tourney = ifelse(stringr::str_detect(School,"NCAA"),1,0)) %>%
              arrange(desc(Tourney)) %>%
              mutate(Seed = seeds_adv) 

corr_mat_wl <- adv_stats %>% 
                select(G:`W-L%`,`Conf. W`:`Away L`,Tourney:Seed) %>% 
                mutate_if(is.character,as.numeric) %>% 
                cor(use = "pairwise.complete.obs")
corrplot(corr_mat_wl,method="color",type="upper",
         tl.srt=45,col=colorRampPalette(c("red3","darkgreen"))(20),
         tl.col="black",insig = "blank",addCoef.col = "white")

corr_mat_adv <- adv_stats %>% 
                select(Pace,FTr:Seed) %>% 
                mutate_if(is.character,as.numeric) %>% 
                cor(use = "pairwise.complete.obs")
corrplot(corr_mat_adv,method="color",type="upper",
         tl.srt=45,col=colorRampPalette(c("red3","darkgreen"))(20),
         tl.col="black",insig = "blank",addCoef.col = "white")


college_teams <- ids$team
all_player_data <- purrr::map_df(college_teams,function(x) season_boxscore(x,"2018-19","raw"))
player_load <- test %>% group_by(player) %>% summarize_if(is.numeric,sum,na.rm=T) %>% mutate(`Pts + Asts` = PTS + (AST/2)) %>% arrange(desc(`Pts + Asts`))


