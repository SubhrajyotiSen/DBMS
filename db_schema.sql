drop table if exists users;
create table users(
	uid integer primary key autoincrement,
	username text not null,
	email text not null,
	join_date date not null
);

drop table if exists article;
create table article(
	aid integer primary key autoincrement,
	title text not null,
	content text not null,
	author text not null,
	category_id integer not null,
	foreign key(author) references users(username),
	foreign key(category_id) references category(category_id)
);

drop table if exists category;
create table category(
	category_id integer primary key autoincrement,
	category_name text not null
);

drop table if exists tag;
create table tag(
	tag_id integer primary key autoincrement,
	tag_name text not null
);

drop table if exists login;
create table login(
	username text not null,
	password text not null,
	foreign key(username) references users(username)
);