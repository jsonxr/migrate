create table datatypes(
    c_bit BIT,
    c_bit_64 BIT(64),

    c_tinyint TINYINT, # -128 .. 127
    c_tinyint1 TINYINT(1),
    c_tinyint4 TINYINT(4),
    c_tinyint_u TINYINT UNSIGNED, # 0 .. 255
    c_tinyint_u_z TINYINT UNSIGNED ZEROFILL,
    c_bool BOOL,
    c_boolean BOOLEAN,
    
    c_smallint SMALLINT,  # -32768 .. 32767
    c_smallint_u SMALLINT UNSIGNED, # 0 .. 65535
    c_smallint_u_z SMALLINT UNSIGNED ZEROFILL,

    
    c_mediumint MEDIUMINT,  # -8388608 .. 8388607
    c_mediumint_u MEDIUMINT UNSIGNED, # 0 .. 16777215
    c_mediumint_u_z MEDIUMINT UNSIGNED ZEROFILL,

    c_int INT,  # -2147483648 .. 2147483647
    c_integer INTEGER,
    c_int_u INT UNSIGNED, # 0 .. 4294967295
    c_int_u_z INT UNSIGNED ZEROFILL,

    c_bitint BIGINT, # -9223372036854775808 .. 9223372036854775807
    c_bigint_u BIGINT UNSIGNED, # 18446744073709551615
    c_serial SERIAL, # ALIAS FOR BIGINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE

    # EXACT FIXED-POINT NUMBER
    # DECIMAL[(M[,D])]  M is the total number of digits (precision), D is the number of digits after decimal (scale)
    c_decimal DECIMAL(10,0), # THIS IS THE DEFAULT FOR DECIMAL
    c_decimal_money DECIMAL(65,2), # Only two decimal points if we store money
    c_decimal_u DECIMAL(10,0) UNSIGNED,
    c_decimal_u_z DECIMAL(10,0) UNSIGNED ZEROFILL,
    c_dec DEC(10,0),
    c_numeric NUMERIC(10,0),
    c_fixed FIXED(10,0),

    # FLOAT
    # FLOAT[(M[,D])]  M,D same as decimal
    #  Permissible values are -3.402823466E+38 to -1.175494351E-38, 0, and 1.175494351E-38 to 3.402823466E+38
    # Using FLOAT might give you some unexpected problems because all calculations in MySQL are done with double precision
    c_float FLOAT,
    c_float_u FLOAT UNSIGNED,
    c_float_u_z FLOAT UNSIGNED ZEROFILL,

    # Accurate to approximately 15 decimal places
    c_double DOUBLE,  # Permissible values are -1.7976931348623157E+308 to -2.2250738585072014E-308
    c_double_u DOUBLE UNSIGNED, # Permissible values are 2.2250738585072014E-308 to 1.7976931348623157E+308.

    c_real REAL, # synonym for either float or double depending on a flag

    c_date DATE, # '1000-01-01' to '9999-12-31'.
    c_datetime DATETIME,  # '1000-01-01 00:00:00' to '9999-12-31 23:59:59'.
    c_timestamp TIMESTAMP, # UNIX timestamp.  '1000-01-01 00:00:00' to '9999-12-31 23:59:59'.
    c_time TIME,
    c_year YEAR,
    c_year2 YEAR(2),

    c_char CHAR,
    c_char_5 CHAR(5), # The length can be any value from 0 to 255. When CHAR values are stored, they are right-padded with spaces to the specified length.
    c_varchar_5 VARCHAR(5), # The length can be specified as a value from 0 to 65,535. The effective maximum length of a VARCHAR is subject to the maximum row size (65,535 bytes, which is shared among all columns)
    c_char_binary CHAR(5) BINARY, # Treated as char(5) character set latin1 collate latin1_bin if default char set is latin1
    c_varchar_binary VARCHAR(5) BINARY, 

    c_binary BINARY(5),  # Right padded with 0x00
    c_varbinary VARBINARY(5), #If the value retrieved must be the same as the value specified for storage with no padding, it might be preferable to use VARBINARY or one of the BLOB data types instead.

    c_tinyblob TINYBLOB, # length < 2^8
    c_blob BLOB, # length < 2^16, SAME AS VARBINARY without a length restriction.
    c_mediumblob MEDIUMBLOB, # length < 2^24
    c_longblob LONGBLOB, # length < 2^32

    c_tinytext TINYTEXT,
    c_tinytext_binary TINYTEXT BINARY,
    c_text TEXT,
    c_text_binary TEXT BINARY,
    c_mediumtext MEDIUMTEXT,
    c_mediumtext_binary MEDIUMTEXT BINARY,
    c_longtext LONGTEXT,
    c_longtext_binary LONGTEXT BINARY,

    c_enum ENUM('x-small', 'small', 'medium', 'large', 'x-large'),
    c_set SET('a','b','c'),
    c_set_notnull SET('a','b','c') NOT NULL
);