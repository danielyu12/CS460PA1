DROP DATABASE IF EXISTS photoshare;
CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;


CREATE TABLE Users (
    user_id int4 NOT NULL AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    password varchar(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
	  last_name VARCHAR(100) NOT NULL,
	  date_of_birth DATE NOT NULL,
	  contributionScore INTEGER, 
	  gender VARCHAR(10),
	  hometown VARCHAR(100),
  PRIMARY KEY (user_id)
);

CREATE TABLE Albums (
  album_id int4  AUTO_INCREMENT,
	album_name VARCHAR(100) NOT NULL,
	date_of_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
  user_id int4 NOT NULL, 
  PRIMARY KEY (album_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Pictures (
  picture_id int4 NOT NULL AUTO_INCREMENT ,
  user_id int4 ,
  imgdata longblob,
  caption VARCHAR(255),
  album_id int4 NOT NULL, 
  PRIMARY KEY (picture_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id),
  FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE
);

CREATE TABLE Comments (
  comment_id int4  NOT NULL AUTO_INCREMENT,
	comment_text VARCHAR(100) NOT NULL,
	date_commented DATETIME DEFAULT CURRENT_TIMESTAMP,
  user_id int4 NOT NULL,
  picture_id int4 NOT NULL,
  PRIMARY KEY (comment_id),
   FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);

CREATE TABLE Likes(
  user_id int4 NOT NULL,
  picture_id int4 NOT NULL,
  PRIMARY KEY (user_id,picture_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);

CREATE TABLE Tags (
  tag_id int4 NOT NULL AUTO_INCREMENT, 
  tag_word VARCHAR(100),
  PRIMARY KEY (tag_id)
);

CREATE TABLE Tagged (
  picture_id int4,
  tag_id int4,
	PRIMARY KEY (tag_id, picture_id),
	FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id),
	FOREIGN KEY (tag_id) REFERENCES Tags(tag_id));

CREATE TABLE Friends (
  userID1 INTEGER,
  userID2 INTEGER,
  CHECK (userID1 <> userID2),
	PRIMARY KEY (userID1, userID2),
	FOREIGN KEY (userID1) REFERENCES Users(user_id),
	FOREIGN KEY (userID2) REFERENCES Users(user_id));



INSERT INTO Users (email, password, first_name, last_name) VALUES ('test@bu.edu', 'test', 'linah', 'uchiyama');
INSERT INTO Users (email, password, first_name, last_name) VALUES ('test1@bu.edu', 'test', 'olivia', 'hur');

