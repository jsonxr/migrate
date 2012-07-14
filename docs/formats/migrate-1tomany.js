//----------------------------------------------------------------------------
// This would be a global object defined by the app that loads this javascript
//----------------------------------------------------------------------------
tables = {
    person: {
        rows: [
            {"id": 1, "full_name": "Jason Rowland", "birthday": "1973-09-12", "person_type": "employee" },
            {"id": 2, "full_name": "Erin Rowland", "birthday": "1975-02-26", "person_type": "manager"}
        ],
        each: function(func) {
            for (var i = 0; i < this.rows.length; i++) {
                 var row = this.rows[i];
                 func(row)
            }
        }
    },
    person_type: {
        rows: [
            {"id": 1, "name": "employee"},
            {"id": 2, "name": "manager"}
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
    tables.person.each(function(row) {
        delete row.person_type
    });
}

function sql_down() {
    // This will actually be an SQL statement to drop the field
    tables.person.each(function(row) {
        delete row.person_type_id
    });
}
//----------------------------------------------------------------------------
// This would be defined in a migration file
//----------------------------------------------------------------------------
migration = {
    "up": function() {
        // Save the person_types for later
        var person_types = {}
        tables.person_type.each(function(row) {
            person_types[row.name] = row.id
        });
        
        // Now update each row with the right status
        tables.person.each(function(row) {
            row.person_type_id = person_types[row.person_type]
        });
    },
    "down": function() {
        var person_types = {}
        tables.person_type.each(function(row) {
            person_types[row.id] = row.name
        });

        // Now update each row with the right status
        tables.person.each(function(row) {
            row.person_type = person_types[row.person_type_id]
        });
    }
}

//----------------------------------------------------------------------------
// This is executed by the engine
//----------------------------------------------------------------------------
console.log('original--------------------------------------------------------------------')
console.log(tables.person.rows)

console.log('up--------------------------------------------------------------------------')
migration.up();
sql_up();
console.log(tables.person.rows)

console.log('down------------------------------------------------------------------------')
migration.down();
sql_down();
console.log(tables.person.rows)