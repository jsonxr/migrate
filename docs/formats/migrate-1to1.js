//----------------------------------------------------------------------------
// This would be a global object defined by the app that loads this javascript
//----------------------------------------------------------------------------
tables = {
    person: {
        rows: [
            {"id": 1, "full_name": "Jason Rowland", "birthday": "1973-09-12"},
            {"id": 2, "full_name": "Erin Rowland", "birthday": "1975-02-26"}
        ],
        each: function(func) {
            for (var i = 0; i < this.rows.length; i++) {
                 var row = this.rows[i];
                 func(row)
            }
        }
    }
}

function sql_up() {
    // This will actually be an SQL statement to drop the field
    tables.person.each(
        function(row) {
            delete row.full_name
        }
    );
}

function sql_down() {
    // This will actually be an SQL statement to drop the field
    tables.person.each(
        function(row) {
            delete(row.first_name);
            delete(row.last_name);
        }
    );
}
//----------------------------------------------------------------------------
// This would be defined in a migration file
//----------------------------------------------------------------------------
migration = {
    "up": function() {
        tables.person.each(
            function(row) {
                var result = /^(\w*) (\w*)$/.exec(row.full_name)
                row.first_name = result[1]
                row.last_name = result[2]
            }
        );
    },
    "down": function() {
        tables.person.each(
            function(row) {
                row.full_name = row.first_name + " " + row.last_name        
            }
        );
    }
}

//----------------------------------------------------------------------------
// This is executed by the engine
//----------------------------------------------------------------------------
console.log(tables.person.rows)

migration.up();
sql_up();
console.log(tables.person.rows)

migration.down();
sql_down();
console.log(tables.person.rows)