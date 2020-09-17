--create database RIOT;

create table `all_league_entry`(
    `leagueId` varchar(255) not null,
    `queueType` varchar(255),
    `tier` TINYTEXT,
    `rank` char(3),
    `summonerId` varchar(255) not null,
    `summonerName` varchar(255),
    `leaguePoints` MEDIUMINT,
    `wins` MEDIUMINT,
    `losses` MEDIUMINT,
    `veteran` TINYINT(1),
    `inactive` TINYINT(1),
    `freshBlood` TINYINT(1),
    `hotStreak` TINYINT(1),
    `accountId` varchar(255) not null,
    `puuid` varchar(255) not null,
    `summonerLevel` MEDIUMINT,
    primary key(`summonerId`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


