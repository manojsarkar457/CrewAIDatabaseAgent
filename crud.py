import sqlite3
import json
from datetime import datetime

# Database Connection
DATABASE = "./database/userDB.sqlite3"

def get_connection():
    return sqlite3.connect(DATABASE, check_same_thread=False)

# Create Table Automatically
def initialize_database():
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.commit()
    con.close()
initialize_database()

# Add New User
def add_new_user(name:str, email:str) -> dict:
    '''adding new users to database'''
    try:
        con =get_connection()
        cursor = con.cursor()
        cursor.execute("INSERT INTO users(name, email) VALUES(?,?)",(name, email))
        con.commit()
        user_id = cursor.lastrowid
        con.close()
        return {
            "success" : True,
            "message" : "User Added Successfully",
            "user_id" : user_id
        }
    except sqlite3.IntegrityError:
        return {
            "success" : False,
            "message" : "Email Already Exists."
        }
    except Exception as e:
        return {
            "success" : False,
            "message" : str(e)
        }
    rows = cursor.rowcount
    return rows

# Get All Users
def get_all_users():
    '''getting all users from the database'''
    try:
        con = get_connection()
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        cursor.execute("SELECT * FROM users ORDER BY User_ID")
        rows = cursor.fetchall()
        con.close()
        data = [dict(row) for row in rows]
        return json.dumps(data, indent=4)
    except Exception as e:
        return json.dumps(
            {
                "success" : False,
                "message" : str(e)
            },
            indent = 4
        )

# Search User
def search_user(keyword:str):
    try:
        con = get_connection()
        con.row_factory = sqlite3.Row
        cursor = con.cursor()

        # Extract numeric ID from the keyword
        import re
        match = re.search(r"\d+", keyword)
        if match:
            user_id = int(match.group())
        else:
            user_id = -1
        cursor.execute("SELECT * FROM users WHERE user_id=? OR name LIKE ? OR email LIKE ?",
        (
            user_id,
            f"%{keyword}%",
            f"%{keyword}%"
        ))
        rows = cursor.fetchall()
        con.close()
        return json.dumps(
            [dict(row) for row in rows],
            indent=4
        )
    except Exception as e:
        return json.dumps(
            {
                "success" : False,
                "message" : str(e)
            },
            indent = 4
        )

# Update User
def update_user(user_id:int, name:str, email:str):
    '''update users from the database depends on user_id'''
    try:
        con = get_connection()
        cursor = con.cursor()
        cursor.execute("UPDATE users SET name=?, email=? where user_id=?",(name, email, user_id))
        con.commit()
        affected = cursor.rowcount
        con.close()
        if affected == 0:
            return {
                "success" : False,
                "message" : "User Not Found"
            }
        return {
            "success" : True,
            "message" : "User Updated Successfully"
        }
    except sqlite3.IntegrityError:
        return {
            "success" : False,
            "message" : "Email Already Exists."
        }
    except Exception as e:
        return {
            "success" : False,
            "message" : str(e)
        }

# Delete User
def delete_user(user_id:int):
    '''delete users from the database depends on user_id'''
    try:
        con = get_connection()
        cursor = con.cursor()
        cursor.execute("DELETE FROM users WHERE user_id=?",(user_id,))
        con.commit()
        affected = cursor.rowcount
        con.close()
        if affected == 0:
            return {
                "success" : False,
                "message" : "User Not Found"
            }
        return {
            "success" : True,
            "message" : "User Deleted Successfully."
        }
    except Exception as e:
        return {
            "success" : False,
            "message" : str(e)
        }


# Total Users
def total_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT COUNT(*)FROM users""")
    total = cursor.fetchone()[0]
    conn.close()
    return total

# Get User By ID
def get_user_by_id(user_id: int):
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM users WHERE user_id=?""",(user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return json.dumps(dict(row), indent=4)
        return json.dumps(
            {
                "success": False,
                "message": "User Not Found"
            },
            indent=4
        )
    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "message": str(e)
            },
            indent=4
        )