CREATE DATABASE IF NOT EXISTS `wechat_group_ibot` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER 'wxibotuser'@'localhost' IDENTIFIED BY 'test';
GRANT ALL PRIVILEGES ON wechat_group_ibot.* TO 'wxibotuser'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;


DROP TABLE IF EXISTS `wx_chat_group`;
CREATE TABLE `wx_chat_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(64) COLLATE utf8mb4_unicode_ci  NOT NULL DEFAULT '',
  PRIMARY KEY `id` (`id`)
)
ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4 COLLATE utf8mb4_unicode_ci;

INSERT INTO `wx_chat_group` (`id`, `name`) VALUES (1, 'IT群1');
INSERT INTO `wx_chat_group` (`id`, `name`) VALUES (3, 'IT群2');
INSERT INTO `wx_chat_group` (`id`, `name`) VALUES (5, 'IT群3');

DROP TABLE IF EXISTS `wx_chat_history`;
CREATE TABLE `wx_chat_history` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(9) UNSIGNED NOT NULL,
  `msg_type` VARCHAR(16) COLLATE utf8_unicode_ci NOT NULL DEFAULT 'Text',
  `wx_puid` VARCHAR(16) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `gp_user_name` VARCHAR(70) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `sender_name` VARCHAR(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `receiver_name` VARCHAR(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `msg` VARCHAR(2048) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Create time',
  PRIMARY KEY `id` (`id`),
  INDEX `idx_group_id` (`group_id`),
  INDEX `idx_create_time` (`create_time`)
)
ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4 COLLATE utf8mb4_unicode_ci;


DROP TABLE IF EXISTS `wx_chat_nickname_check`;
CREATE TABLE `wx_chat_nickname_check` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(9) UNSIGNED NOT NULL,
  `wx_puid` VARCHAR(16) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `nickname` VARCHAR(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Create time',
  PRIMARY KEY `id` (`id`),
  INDEX `idx_group_id` (`group_id`),
  INDEX `idx_create_time` (`create_time`)
)
ENGINE = InnoDB
DEFAULT CHARSET = utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ALTER TABLE wx_chat_history MODIFY `sender_name` VARCHAR(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '';
-- ALTER TABLE wx_chat_history MODIFY `receiver_name` VARCHAR(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '';
-- ALTER TABLE wx_chat_history MODIFY `msg` VARCHAR(2048) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '';
-- ALTER TABLE wx_chat_nickname_check MODIFY `nickname` VARCHAR(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '';

