CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Albums CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS Tags CASCADE;


CREATE TABLE Users (
    user_id int4 AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    password varchar(255) NOT NULL,
    first_name VARCHAR(100),
	  last_name VARCHAR(100),
	  date_of_birth DATE,
	  contributionScore INTEGER, 
	  gender VARCHAR(10),
	  hometown VARCHAR(100),
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Pictures (
  picture_id int4  AUTO_INCREMENT,
  user_id int4,
  imgdata longblob,
  caption VARCHAR(255),
  INDEX upid_idx (user_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);

CREATE TABLE Albums (
  album_id int4  AUTO_INCREMENT,
	album_name VARCHAR(100),
	date_of_creation DATE,
  CONSTRAINT albums_pk PRIMARY KEY (album_id)
);

CREATE TABLE Comments (
  comment_id int4  AUTO_INCREMENT,
	comment_text VARCHAR(100),
	date_commented DATE,
  CONSTRAINT comments_pk PRIMARY KEY (comment_id)
);

CREATE TABLE Tags (
  tag_word VARCHAR(100),
  CONSTRAINT tags_pk PRIMARY KEY (tag_word)
);


INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
