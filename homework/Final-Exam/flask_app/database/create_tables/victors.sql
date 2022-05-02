CREATE TABLE IF NOT EXISTS `victors` (
`victor_id`       int(11)  	    NOT NULL auto_increment	   COMMENT 'the id of this victor',
`username`        varchar(100)  NOT NULL                   COMMENT 'the username of the victor',
`date`            varchar(100)  NOT NULL                   COMMENT 'the date that the user won',
`time`            varchar(100)  NOT NULL            		   COMMENT 'the time it took',

PRIMARY KEY (`victor_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains the word of the day information";
