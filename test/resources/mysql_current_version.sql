create table test1 (
    col1 varchar(5),
    col2 int(11)
);

create table test2 (
    col1 float,
    col2 char(2)
);

create table migrations (

name: migration
columns:
    - name: version
      type: string
    - name: yml
      type: text
    - name: applied_by
      type: string
    - name: applied_on_utc
      type: "datetime"

);