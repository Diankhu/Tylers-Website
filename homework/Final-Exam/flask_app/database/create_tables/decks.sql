CREATE TABLE IF NOT EXISTS `decks` (
`deck_id`           int(11)       NOT NULL AUTO_INCREMENT	COMMENT 'The deck id',
`user_id`           int(11)       NOT NULL 				    COMMENT 'FK:The user id',
`name`              varchar(100)  NOT NULL					COMMENT 'Name of the skill',
`languages`         varchar(500)  DEFAULT NULL              COMMENT 'Languages used',
`access`            varchar(100)  DEFAULT NULL              COMMENT 'the accessibility',
PRIMARY KEY (`deck_id`),
FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="decks";