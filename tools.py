from crewai.tools import tool
from crud import *

# Add New User
@tool("Add New User")
def add_user_tool(Name:str, Email:str) -> str:
    """
    Add a new user to the Database.
    Args:
        Name: User's full Name.
        Email: User's Email Address.
    """
    result = add_new_user(Name, Email)
    if result["success"]:
        return(
            f"✅ User added successfully.\n"
            f"User ID: {result['User_ID']}"
        )
    return f"❌ {result['message']}"

# Show All Users
@tool("Get All Users")
def get_all_users_tool() -> str:
    """Retrieve all users from the database."""
    return get_all_users()

# Search User
@tool("Search User")
def search_user_tool(keyword:str) -> str:
    """
    Search users using user id, name or email.
    Args:
        Keyword: Search Keyword
    """
    return search_user(keyword)

# Get User BY ID
@tool("Get User By ID")
def get_user_by_id_tool(user_id:int) -> str:
    """
    Get a user using user_id
    Args:
        user_id: User ID.
    """
    return get_user_by_id(user_id)

# Update User
@tool("Update User")
def update_user_tool(user_id:int, name:str, email:str) -> str:
    """
    Update an Existing User.
    Args:
        user_id: User ID.
        name: New Name.
        email: New Email.
    """
    result = update_user(user_id, name, email)
    if result["success"]:
        return "✅ User updated successfully."
    return f"❌ {result['message']}"

# Delete User
@tool("Delete User")
def delete_user_tool(user_id:int) -> str:
    """
    Delete a user from the Database
    Args:
        user_id ; User ID.
    """
    result = delete_user(user_id)
    if result["success"]:
        return "✅ User Deleted successfully."
    return f"❌ {result['message']}"

# Count Users
@tool("Total Users")
def total_users_tool() -> str:
    """
    Return total number of registered users.
    """
    total = total_users()
    return f"Total Users: {total}"