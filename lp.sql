#记录lonely planet的restaurants的一些数据
#构建venue表
CREATE TABLE IF NOT EXISTS `venue`(
	`id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增ID',
	`venue_name` varchar(128) NOT NULL COMMENT 'venue名称' ,
	`address` varchar(512) COMMENT '地址',
	`phone` varchar(64) COMMENT '联系方式',
	`area` varchar(256) COMMENT '所在地区',
	`metro` varchar(128) COMMENT '地铁',
	`hours` varchar(256) COMMENT '营业时间',
	`cards` varchar(128) COMMENT '支付方式',
	`web` varchar(128) COMMENT '网站主页',
	`happy_hour` varchar(256) COMMENT '主要营业时间',
	`price` varchar(128) COMMENT '消费价格',
	`description` text COMMENT '编辑推荐',
	`latitude` varchar(32) COMMENT '经度',
	`longitude` varchar(32) COMMENT '纬度',
	PRIMARY KEY(`id`),
	UNIQUE KEY `venue_name` (`venue_name`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

#存储tag信息
CREATE TABLE IF NOT EXISTS `tags`(
	`id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增ID',
	`tag_name` varchar(128) NOT NULL COMMENT '标签名称',
	PRIMARY KEY(`id`),
	UNIQUE KEY `tag_name` (`tag_name`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

#存储venue和tag的对应关系
CREATE TABLE IF NOT EXISTS `venue_tag`(
	`id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增ID',
	`venue_name` varchar(128) COMMENT 'venue名称',
	`tag_name` varchar(128) COMMENT '标签名称',
	PRIMARY KEY(`id`),
	UNIQUE KEY `mapping` (`venue_name`, `tag_name`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;