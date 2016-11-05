create table if not exists users (
	uid integer primary key autoincrement,
	username text not null,
	email text not null,
	join_date text not null,
	foreign key(username) references login(username)
);

create table if not exists article (
	aid integer primary key autoincrement,
	title text not null,
	content text not null,
	author text not null,
	category_id integer not null,
	a_date text not null,
	foreign key(author) references users(username),
	foreign key(category_id) references category(category_id)
);

create table if not exists category (
	category_id integer primary key autoincrement,
	category_name text not null
);

create table if not exists tag (
	tag_id integer primary key autoincrement,
	tag_name text not null
);

create table if not exists login (
	username text primary key,
	password text not null
);