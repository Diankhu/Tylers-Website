CREATE TABLE IF NOT EXISTS `feedback` (
`comment_id`     int(11)       NOT NULL AUTO_INCREMENT 	COMMENT 'The comment id',
`name`           varchar(100)  DEFAULT NULL                	COMMENT 'The commentors name',
`email`          varchar(100)  DEFAULT NULL            	    COMMENT 'The email of the commentor',
`comment`        varchar(100)  DEFAULT NULL            	    COMMENT 'The text of the comment',

PRIMARY KEY  (`comment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="User Feedback";
