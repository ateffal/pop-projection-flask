import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)



def create_user(conn, user):
    """
    Create a new user into the users table
    :param conn:
    :param user:
    :return: user id
    """
    sql = ''' INSERT INTO users(login,pass)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, user)
    conn.commit()
    return cur.lastrowid


def create_result(conn, result):
    """
    Create a new result
    :param conn:
    :param result:
    :return:
    """

    sql = ''' INSERT INTO results(year,employees,spouses,children,user_id)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, result)
    conn.commit()
    return cur.lastrowid



def update_user(conn, user):
    """
    update login and pass of a user
    :param conn:
    :param task:
    :return: user id
    """
    sql = ''' UPDATE users
              SET login = ? ,
                  pass = ? ,
                  end_date = ?
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, user)
    conn.commit()




def delete_all_results(conn, user_id = None):
    """
    Delete all rows of a user (user_id) in the results table
    :param conn: Connection to the SQLite database
    :param user_id: id of the user
    :return:
    """

    if not user_id is None:   
        sql = 'DELETE FROM results WHERE user_id=?'
    else:
        sql = 'DELETE FROM results'
    
    cur = conn.cursor()

    if not user_id is None:  
        cur.execute(sql, (user_id,))
    else:
        cur.execute(sql)
    conn.commit()



def select_all_users(conn):
    """
    Query all rows in the users table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")

    rows = cur.fetchall()

    for row in rows:
        print(row)

def select_results_by_user(conn, user_id):
    """
    Query results by user
    :param conn: the Connection object
    :param user_id:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM results WHERE user_id=?", (user_id,))

    rows = cur.fetchall()

    for row in rows:
        print(row)






def main():
    database = "./databases/database_0.db"

    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS users (
                                        id integer PRIMARY KEY,
                                        login text NOT NULL,
                                        pass text NOT NULL
                                    ); """

    sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS results (
                                    id integer PRIMARY KEY,
                                    year integer NOT NULL,
                                    employees real NOT NULL,
                                    spouses real NOT NULL,
                                    children real NOT NULL,
                                    user_id integer NOT NULL,
                                    FOREIGN KEY (user_id) REFERENCES users (id)
                                );"""

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_projects_table)

        # create tasks table
        create_table(conn, sql_create_tasks_table)
    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    main()







