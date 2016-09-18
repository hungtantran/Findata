package main

import (
    "database/sql"
    "fmt"
    _ "github.com/go-sql-driver/mysql"
    "log"
)

type User struct {
    Id sql.NullInt64
    Username sql.NullString
    Fullname sql.NullString
    Email sql.NullString
    Passwordhash sql.NullString
    Passwordsalt sql.NullString
    Isdisabled sql.NullBool
}

func (user *User) String() string {
    return fmt.Sprintf("%d %s %s %s %s %s %t",
		user.Id.Int64,
        user.Username.String,
        user.Fullname.String,
        user.Email.String,
        user.Passwordhash.String,
        user.Passwordsalt.String,
        user.Isdisabled.Bool);
}

type UsersDatabase struct {
    dbType string
    dbUserName string
    dbPassword string
    dbServer string
    dbDatabase string
    dbTableName string
    db *sql.DB
}

func NewUsersDatabase(
        dbType string,
        dbUserName string, 
        dbPassword string,
        dbServer string,
        dbDatabase string,
        dbTableName string) *UsersDatabase {
    log.Println(dbType, dbUserName, dbPassword, dbServer, dbDatabase, dbTableName)
    var usersDatabase *UsersDatabase = new(UsersDatabase);
    usersDatabase.dbType = dbType;
    usersDatabase.dbUserName = dbUserName;
    usersDatabase.dbPassword = dbPassword;
    usersDatabase.dbServer = dbServer;
    usersDatabase.dbDatabase = dbDatabase;
    usersDatabase.dbTableName = dbTableName;

    connectionString :=
        usersDatabase.dbUserName + ":" +
        usersDatabase.dbPassword + "@tcp(" + 
        usersDatabase.dbServer + ":3306)/" +
        usersDatabase.dbDatabase;
    log.Println("Connect to users database use connection string " + connectionString);
    db, err := sql.Open(usersDatabase.dbType, connectionString)
	if err != nil {
		log.Println(err)
	}
    usersDatabase.db = db;
    return usersDatabase;
}

func (usersDatabase *UsersDatabase) GetUser(username string, passwordHash string) *User {
    rows, err := usersDatabase.db.Query("SELECT * FROM users WHERE username = ? AND passwordHash = ? LIMIT 1", username, passwordHash);
    if err != nil {
        log.Println(err)
    }
    defer rows.Close()
    var user *User;
    user = nil;
    if rows.Next() {
        user = new(User);
        err := rows.Scan(
                &user.Id,
                &user.Username,
                &user.Fullname,
                &user.Email,
                &user.Passwordhash,
                &user.Passwordsalt,
                &user.Isdisabled);
        if err != nil {
            log.Println(err);
        }
    }
    return user;
}

func (usersDatabase *UsersDatabase) InsertUser(username string, fullname string, email string, password string) bool {
    stmt, err := usersDatabase.db.Prepare("INSERT users SET username=?, fullname=?, email=?, passwordhash=?, passwordsalt=?, isdisabled=?");
    if err != nil {
        log.Println(err);
        return false;
    }

    // TODO actually calculate hash and salt
    passwordsalt := "";
    isdisabled := false;
    res, err := stmt.Exec(username, fullname, email, password, passwordsalt, isdisabled);
    if err != nil {
        log.Println(err);
        return false;
    }

    id, err := res.LastInsertId();
    if err != nil {
        log.Println(err);
        return false;
    }

    log.Println(id);
    return true;
}

func (usersDatabase *UsersDatabase) close() {
    usersDatabase.db.Close();
}