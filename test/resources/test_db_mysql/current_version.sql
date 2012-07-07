create table test1 (
    col1 varchar(5),
    col2 int(11)
);

create table test2 (
    col1 float,
    col2 char(2)
);

CREATE  TABLE migrations (
  `version` VARCHAR(255) NOT NULL,
  `yml` LONGTEXT NOT NULL,
  `applied_by` VARCHAR(255) NULL,
  `applied_on` DATETIME NOT NULL,
  PRIMARY KEY (`version`),
  UNIQUE INDEX `version_UNIQUE` (`version` DESC) 
);
