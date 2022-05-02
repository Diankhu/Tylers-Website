CREATE TABLE IF NOT EXISTS `words` (
`word_id`         int(11)  	   NOT NULL auto_increment	  COMMENT 'the id of this word',
`date`            varchar(100)  NOT NULL                   COMMENT 'the date that the word was stored',
`word`            varchar(100) NOT NULL            		    COMMENT 'the word',

PRIMARY KEY (`word_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains the word of the day information";
