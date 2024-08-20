CREATE TABLE IF NOT EXISTS `cards` (
`cards_id`          int(11)       NOT NULL AUTO_INCREMENT	COMMENT 'The card id',
`deck_id`           int(11)       NOT NULL 				    COMMENT 'FK:The deck id',
`front`             varchar(100)  NOT NULL					COMMENT 'front of the card',
`back`              varchar(100)  Not Null                  COMMENT 'back of the card',
`last_seen`         varchar(500)  DEFAULT NULL              COMMENT 'last time this card was seen while reviewing',
PRIMARY KEY (`cards_id`),
FOREIGN KEY (deck_id) REFERENCES decks(deck_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="cards";