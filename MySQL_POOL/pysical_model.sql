--create database RIOT;

-- table to store all summoner information
--create table `all_league_entry`(
--    `leagueId` varchar(255) not null,
--    `queueType` varchar(255),
--    `tier` TINYTEXT,
--    `rank` char(3),
--    `summonerId` varchar(255) not null,
--    `summonerName` varchar(255),
--    `leaguePoints` MEDIUMINT,
--    `wins` MEDIUMINT,
--    `losses` MEDIUMINT,
--    `veteran` TINYINT(1),
--    `inactive` TINYINT(1),
--    `freshBlood` TINYINT(1),
--    `hotStreak` TINYINT(1),
--    `accountId` varchar(255) not null,
--    `puuid` varchar(255) not null,
--    `summonerLevel` MEDIUMINT,
--    primary key(`summonerId`)
--)ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- table to store matches

create table `match_list`(
    `accountId` varchar(255) not null,
    `gameId` varchar(255) not null,
    `role` varchar(100),
    `season` TINYINT,
    `platformId` varchar(255),
    `champion` SMALLINT,
    `queue` SMALLINT,
    `lane` varchar(100),
    `timestamp` varchar(255),
    primary key(`gameId`),
    foreign key (`accountId`) references all_league_entry(`accountId`)
    ON DELETE CASCADE ON UPDATE CASCADE;
)ENGINE=InnoDB DEFAULT CHARSET=utf8;




