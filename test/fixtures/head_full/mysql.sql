create table test1 (
    col1 varchar(5),
    col2 int(11)
);

create table test2 (
    col1 float,
    col2 char(2)
);

create table migrations (
    version varchar(255) not null primary key,
    content longtext not null,
    content_type varchar(255) not null,
    applied_by varchar(255),
    applied_on datetime not null
);