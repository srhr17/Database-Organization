CREATE DATABASE library;
SHOW databases;
USE library;

-- Strong Entities
CREATE TABLE USERS(userID integer auto_increment, firstName varchar(250),lastName varchar(250),email varchar(250) not null unique,memberSince datetime default NOW(),password varchar(250) not null,dob date,primary key(userID));

CREATE TABLE DOCUMENTS (documentID integer auto_increment,availability binary default 1,typeOfDocument varchar(250) not null,primary key(documentID));

CREATE TABLE BOOKS(documentID integer, title varchar(250) not null,edition integer not null,publishedOn date, publishedBy varchar(250),primary key(documentID),foreign key(documentID) references DOCUMENTS(documentID));

CREATE TABLE ARTICLES(documentID integer, title varchar(250) not null,journalName varchar(250) not null,journalPublishedOn date, journalPublishedBy varchar(250),primary key(documentID),foreign key(documentID) references DOCUMENTS(documentID));

CREATE TABLE ISSUES (documentID integer,title varchar(250) not null,dateOfIssue date,magazineName varchar(250),primary key(documentID),foreign key(documentID) references DOCUMENTS(documentID));

-- Multivalued Attributes
CREATE TABLE BOOKAUTHORS(documentID integer,authorName varchar(250), primary key(documentID,authorName),foreign key(documentID) references BOOKS(documentID));

CREATE TABLE ARTICLEAUTHORS(documentID integer,authorName varchar(250), primary key(documentID,authorName),foreign key(documentID) references ARTICLES(documentID));

CREATE TABLE ISSUECONTRIBUTOREDITOR(documentID integer,contributorEditorName varchar(250), primary key(documentID,contributorEditorName),foreign key(documentID) references ISSUES(documentID));

CREATE TABLE JOURNALEDITOR(documentID integer,editorName varchar(250), primary key(documentID,editorName),foreign key(documentID) references ARTICLES(documentID));

CREATE TABLE DOCUMENTKEYWORD(documentID integer,keyword varchar(250), primary key(documentID,keyword),foreign key(documentID) references DOCUMENTS(documentID));

CREATE TABLE DOCUMENTCLASSIFICATION(documentID integer,classification varchar(250), primary key(documentID,classification),foreign key(documentID) references DOCUMENTS(documentID));

-- Relations 
CREATE TABLE DOCUMENTADDMODIFY(userID integer,documentID integer,addormodify varchar(250),primary key(userID,documentID),foreign key(userID)references USERS(userID),foreign key(documentID) references DOCUMENTS(documentID));

CREATE TABLE BORROW(borrowID integer auto_increment,userID integer,documentID integer, borrowDate datetime,status binary,primary key(borrowID),foreign key(userID) references USERS(userID),foreign key(documentID) references DOCUMENTS(documentID));

CREATE TABLE SEARCHHISTORY(searchID integer auto_increment,userID integer, documentID integer,searchQuery varchar(250),primary key(searchID),foreign key(userID) references USERS(userID),foreign key(documentID) references DOCUMENTS(documentID));

CREATE TABLE MANAGED(librarianID integer, memberID integer,primary key(librarianID,memberID),foreign key(librarianID) references USERS(userID),foreign key(memberID) references USERS(userID));

-- Indexes
CREATE INDEX IDX_BOOK_TITLE ON BOOKS(title);

CREATE INDEX IDX_BOOK_AUTHORS ON BOOKAUTHORS(authorName);

CREATE INDEX IDX_ARTICLE_TITLE ON ARTICLES(title);

CREATE INDEX IDX_ARTICLE_AUTHORS ON ARTICLEAUTHORS(authorName);

CREATE INDEX IDX_ISSUE_TITLE ON ISSUES(title);

CREATE INDEX IDX_KEYWORD ON DOCUMENTKEYWORD(keyword);

CREATE INDEX IDX_CLASSIFICATION ON DOCUMENTCLASSIFICATION(classification);

