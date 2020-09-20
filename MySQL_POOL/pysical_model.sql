--create database RIOT;

-- table to store all summoner information
create table `all_league_entry`(
    `id` int not null auto_increment unique key,
    `leagueId` varchar(255) not null comment 'league game ID',
    `queueType` varchar(255) comment 'game queue type. i.e. rank solo5x5',
    `tier` TINYTEXT comment 'rank tier. i.e. diamond',
    `rank` char(3) comment 'rank level. i.e. diamond IV',
    `summonerId` varchar(255) not null comment 'game user id',
    `summonerName` varchar(255) comment 'user name in the game',
    `leaguePoints` MEDIUMINT comment '',
    `wins` MEDIUMINT comment '',
    `losses` MEDIUMINT comment '',
    `veteran` TINYINT(1) comment '',
    `inactive` TINYINT(1) comment '',
    `freshBlood` TINYINT(1) comment '',
    `hotStreak` TINYINT(1) comment '',
    `accountId` varchar(255) not null comment 'user RIOT account id encrypted',
    `puuid` varchar(255) not null comment '',
    `summonerLevel` MEDIUMINT comment '',
    primary key(`summonerId`),
    unique (`accountId`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
--alter table all_league_entry add constraint unique_account unique(`accountId`);
--alter table all_league_entry add id int not null auto_increment unique key;

-- table stores all the champions
create table `champion`(
    `id` int not null auto_increment unique key comment '',
    `version` varchar(10) comment 'current client version',
    `champion_id` varchar(255) not null comment 'champion name',
    `key`  SMALLINT not null comment 'champion id',
    `name` varchar(255) not null comment '',
    `tag1` varchar(20) not null comment 'champion tag',
    `tag2` varchar(20) not null comment '',
    `title` varchar(100) comment '',
    `hp` SMALLINT comment '',
    `hpperlevel` SMALLINT comment '',
    `mp` SMALLINT comment '',
    `mpperlevel` SMALLINT comment '',
    `movespeed` SMALLINT comment '',
    `armor` SMALLINT comment '',
    `armorperlevel` decimal(5,3) comment '',
    `spellblock` decimal(5,3) comment '',
    `spellblockperlevel` decimal(5,3) comment '',
    `attackrange` SMALLINT comment '',
    `hpregen` SMALLINT comment '',
    `hpregenperlevel` SMALLINT comment '',
    `mpregen` SMALLINT comment '',
    `mpregenperlevel` SMALLINT comment '',
    `crit` SMALLINT comment '',
    `critperlevel` SMALLINT comment '',
    `attackdamage` SMALLINT comment '',
    `attackdamageperlevel` SMALLINT comment '',
    `attackspeedperlevel` decimal(5,3) comment '',
    `attackspeed` decimal(5,3) comment '',
    primary key (`key`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- table to store matches
create table `match_list`(
	`id` int not null auto_increment comment '',
    `accountId` varchar(255) not null comment 'user RIOT account id',
    `gameId` varchar(255) not null comment 'id that refers to a specific game',
    `role` varchar(100) comment '',
    `season` TINYINT comment '',
    `platformId` varchar(255) comment '',
    `champion` SMALLINT comment 'champion id',
    `queue` SMALLINT comment '',
    `lane` varchar(100) comment '',
    `timestamp` varchar(255) comment '',
    primary key(`gameId`),
    unique key (`id`),
    foreign key(`champion`) references champion(`key`),
    foreign key (`accountId`) references all_league_entry(`accountId`)

)ENGINE=InnoDB DEFAULT CHARSET=utf8;





