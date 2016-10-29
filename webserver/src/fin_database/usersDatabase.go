package fin_database

import (
    "log"
)

type UsersDatabase struct {
    dbType string
    dbTableName string
    dbConnector *MySqlConnector
}

func NewUsersDatabase(
        dbType string,
        dbTableName string,
        dbConnector *MySqlConnector) *UsersDatabase {
    log.Println(dbType, dbTableName)
    var usersDatabase *UsersDatabase = new(UsersDatabase);
    usersDatabase.dbType = dbType;
    usersDatabase.dbConnector = dbConnector;
    usersDatabase.dbTableName = dbTableName;
    return usersDatabase;
}

func (usersDatabase *UsersDatabase) GetUser(username string, passwordHash string) *User {
    rows, err := usersDatabase.dbConnector.GetConnector().Query(
        "SELECT * FROM " + usersDatabase.dbTableName +  " WHERE username = ? AND passwordHash = ? LIMIT 1", username, passwordHash);
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
                &user.TypeStr,
                &user.Username,
                &user.Fullname,
                &user.Email,
                &user.Passwordhash,
                &user.Passwordsalt,
                &user.Metadata,
                &user.Isdisabled);
        if err != nil {
            log.Println(err);
        }
    }
    return user;
}

// This is only used for identity provider's login (Google or Facebook)
func (usersDatabase *UsersDatabase) GetUserByUsername(username string) *User {
    rows, err := usersDatabase.dbConnector.GetConnector().Query(
        "SELECT * FROM " + usersDatabase.dbTableName +  " WHERE username = ? LIMIT 1", username);
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
                &user.TypeStr,
                &user.Username,
                &user.Fullname,
                &user.Email,
                &user.Passwordhash,
                &user.Passwordsalt,
                &user.Metadata,
                &user.Isdisabled);
        if err != nil {
            log.Println(err);
        }
    }
    return user;
}

func (usersDatabase *UsersDatabase) InsertUser(typeStr string, username string, fullname string, email string, password string) bool {
    stmt, err := usersDatabase.dbConnector.GetConnector().Prepare(
        "INSERT " + usersDatabase.dbTableName +  " SET type=?, username=?, fullname=?, email=?, passwordhash=?, passwordsalt=?, isdisabled=?");
    if err != nil {
        log.Println(err);
        return false;
    }

    // TODO actually calculate hash and salt
    passwordsalt := "";
    isdisabled := false;
    res, err := stmt.Exec(typeStr, username, fullname, email, password, passwordsalt, isdisabled);
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

func (usersDatabase *UsersDatabase) Close() {
    usersDatabase.dbConnector.Close();
}