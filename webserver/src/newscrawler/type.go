package main

import (
    "database/sql"
    "time"
)

type NewsInfo struct {
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `source` varchar(32) NOT NULL,
    `date` datetime DEFAULT NULL,
    `headline` varchar(255) DEFAULT NULL,
    `print_headline` varchar(255) DEFAULT NUL
    `abstract` text,
    `section` varchar(255) DEFAULT NULL,
    `subsection` varchar(255) DEFAULT NULL,
    `tags` varchar(255) DEFAULT NULL,
    `keywords` varchar(255) DEFAULT NULL,
    `link` varchar(255) DEFAULT NULL,
    `authors` varchar(255) DEFAULT NULL,
    `metadata` text,
}

type NewsContent struct {
    `id` int(11) NOT NULL,
    `full_data` text NOT NULL,
}