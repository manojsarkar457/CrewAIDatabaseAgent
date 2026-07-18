from crewai import Agent, Task, Crew, LLM
import os
from tools import *
import streamlit as st
import pandas as pd
import json

# Streamlit Configuration
st.set_page_config(
    page_title="AI Database Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>

.main{
    background-color:#F5F7FB;
}

.title{
    font-size:38px;
    font-weight:bold;
    color:#2563EB;
}

.subtitle{
    font-size:18px;
    color:#555555;
}

.stButton>button{
    width:100%;
    border-radius:12px;
    height:45px;
    font-size:16px;
    font-weight:bold;
}

.prompt-box{
    padding:20px;
    border-radius:15px;
    background:#FFFFFF;
    border:1px solid #E5E7EB;
}

.example{
    background:#EEF4FF;
    padding:12px;
    border-radius:10px;
    margin-top:8px;
}

</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🤖 AI Database Assistant")
    st.markdown("### Features:")
    st.write("✅ Add New User")
    st.write("✅ Show All User")
    st.write("✅ Search User")
    st.write("✅ Update User")
    st.write("✅ Delete User")

    st.info(
        """
        Example Prompt:\n
        • Add Rahul Sarkar with email rahul123@gmail.com\n
        • Show all Users\n
        • Search Rahul\n
        • Update user 3 name to abc email to abc@gmail.com\n
        • Delete user 5
        """
    )

# Header
st.markdown(
    "<div class='title'> 🤖 AI Database Assistant</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='subtitle'>Manage your SQLite database using Natural Language powered by CrewAI + Gemini.</div>",
    unsafe_allow_html=True
)

st.write("")

# Connected to LLM
llm = LLM(
    model = "gemini/gemini-3.5-flash",
    api_key = st.secrets['GEMINI_API_KEY'],
    temperature = 0
)

# Insert Agent
insert_agent = Agent(
    role = "Database Insert Expert",
    goal = """
        Insert new users into the SQLite database.
        Always extract:
        • Name
        • Email
        Use the Add User tool.""",
    backstory = """
        You are an expert database administrator.
        You only insert users into the database.
        Never answer manually.
        Always use the tool.
        """,
    llm = llm,
    tools = [add_user_tool],
    verbose = True
)

# Read Agent
read_agent = Agent(
    role="Database Reader",
    goal="""
        Read information from the database.
        Display users.
        """,
    backstory="""
        Expert SQL Reader.
        Always use tools.
        Never guess database values.
        """,
    llm=llm,
    tools=[get_all_users_tool],
    verbose=True
)

# Get User By ID Agent
get_user_by_id_agent = Agent(
    role="Database User ID Search Expert",
    goal="""
        Retrieve a single user from the database using the User ID.
        Always:
        - Extract the User ID from the user's prompt.
        - Use ONLY the Get User By ID Tool.
        - Return the tool output.
    """,
    backstory="""
        You are an expert SQLite database administrator.
        Your responsibility is to retrieve exactly one user based on the provided User ID.
        Never search by name or email.
        Never guess data.
        Always use the Get User By ID Tool.
    """,
    llm=llm,
    tools=[get_user_by_id_tool],
    verbose=True
)

# Search Agent
search_agent = Agent(
    role="Database Search",
    goal="""
        Search information from the database.
        Display users.
        Search users.
        Get total users.
        """,
    backstory="""
        Expert SQL Reader.
        Always use tools.
        Never guess database values.
        """,
    llm=llm,
    tools=[
        search_user_tool,
        total_users_tool
        ],
    verbose=True
)

# Update Agent
update_agent = Agent(
    role="Database Update Expert",
    goal="""
        Update users in the database.
        Extract
        User ID
        Name
        Email
        Then use Update Tool.
        """,
    backstory="""Expert SQLite Update Specialist.""",
    llm=llm,
    tools=[update_user_tool],
    verbose=True
)

# Delete Agent
delete_agent = Agent(
    role="Database Delete Expert",
    goal="""
        Delete users safely.
        Always extract User ID.
        Use Delete Tool.
        """,
    backstory="""
        Expert SQLite Administrator.
        Delete records carefully.
        """,
    llm=llm,
    tools=[delete_user_tool],
    verbose=True
)


# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "operation_count" not in st.session_state:
    st.session_state.operation_count = 0

# Dashboard
st.write("")
col1, col2, col3 = st.columns(3)
try:
    total = total_users()
except:
    total = 0
with col1:
    st.metric(
        label="👥 Total Users",
        value=total
    )

with col2:
    st.metric(
        label="🤖 AI Requests",
        value=st.session_state.operation_count
    )

with col3:
    st.metric(
        label="✅ Status",
        value="Online"
    )

st.divider()
# Quick Examples
st.subheader("💡 Try these commands")
example_col1, example_col2 = st.columns(2)

with example_col1:
    st.info("""
    ➕ Add Rahul Sarkar with email rahul@gmail.com\n
    ➕ Register Amit Kumar email amit@gmail.com\n
    👀 Show all users
    """)

with example_col2:
    st.info("""
    🔍 Search Rahul\n
    ✏ Update user 2 name to new name email to new@gmail.com\n
    🗑 Delete user 3
    """)

st.divider()

# Chat History
st.subheader("💬 Conversation")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
prompt = st.chat_input(
    "Ask anything about your database..."
)

# Process User Prompt
if prompt:
    # Save User Prompt
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )
    with st.chat_message("user"):
        st.markdown(prompt)
    prompt_lower = prompt.lower()
    crew = None
    task = None

# Detect User Intent
    # -------- ADD USER --------
    if any(word in prompt_lower for word in [
        "add",
        "insert",
        "save",
        "register",
        "create"
    ]):
        task = Task(
            description=f"""
                User Prompt:{prompt}
                Your Job:
                1. Extract the user's name.
                2. Extract the email address.
                3. Use ONLY the Add User Tool.
                4. Do not answer manually.
                5. Return only the tool output.
                """,
            expected_output="User successfully added.",
            agent=insert_agent
        )
        crew = Crew(
            agents=[insert_agent],
            tasks=[task],
            verbose=True
        )

    # -------- SHOW USER BY ID --------
    elif "show user" in prompt_lower:
        task = Task(
            description=f"""
                User Prompt:{prompt}
                Extract ONLY the User ID.
                Use ONLY the Get User By ID Tool.
                Do not use any other tool.
                Return only the tool output.
                """,
            expected_output="One user details.",
            agent=read_agent
        )

        crew = Crew(
            agents=[get_user_by_id_agent],
            tasks=[task],
            verbose=False
        )

    # -------- SHOW ALL USERS --------
    elif any(word in prompt_lower for word in [
        "show all user",
        "display all user",
        "list of all user",
        "read all user",
        "all users",
        "view all user"
    ]):

        task = Task(
            description=f"""
                User Prompt:{prompt}
                Display every user stored in the database.
                Always use the Get All Users Tool.
                Return the tool result.
                """,
            expected_output="JSON containing all users.",
            agent=search_agent
        )
        crew = Crew(
            agents=[search_agent],
            tasks=[task],
            verbose=True
        )

    # -------- SEARCH USER --------
    elif any(word in prompt_lower for word in [
        "search",
        "find",
        "locate"
    ]):
        task = Task(
            description=f"""
                User Prompt:{prompt}
                Extract the search keyword.
                Search by:
                • Name
                • Email
                • User ID
                Use the Search User Tool.
                Return the tool output.
                """,
            expected_output="Matching users.",
            agent=search_agent
        )
        crew = Crew(
            agents=[search_agent],
            tasks=[task],
            verbose=True
        )

    # -------- UPDATE USER --------
    elif "update" in prompt_lower:
        task = Task(
            description=f"""
                User Prompt:{prompt}
                Extract
                • User ID
                • New Name
                • New Email
                Use ONLY the Update User Tool.
                Return tool output.
                """,
            expected_output="User updated successfully.",
            agent=update_agent
        )
        crew = Crew(
            agents=[update_agent],
            tasks=[task],
            verbose=True
        )

    # -------- DELETE USER --------
    elif any(word in prompt_lower for word in [
        "delete",
        "remove"
    ]):
        task = Task(
            description=f"""
                User Prompt:{prompt}
                Extract the User ID.
                Use ONLY the Delete User Tool.
                Return tool output.
                """,
            expected_output="User deleted successfully.",
            agent=delete_agent
        )
        crew = Crew(
            agents=[delete_agent],
            tasks=[task],
            verbose=True
        )

    # -------- UNKNOWN PROMPT --------
    else:
        with st.chat_message("assistant"):
            st.warning(
                """
                I couldn't understand your request.
                Try something like:
                • Add Rahul with email rahul@gmail.com
                • Show all users
                • Search Rahul
                • Update user 2
                • Delete user 5
                """
            )
        st.stop()

# Execute Crew
    try:
        with st.spinner("🤖 Gemini is thinking..."):
            result = crew.kickoff()
        if hasattr(result, "raw"):
            response = result.raw
        else:
            response = str(result)

    except Exception as e:
        response = f"❌ Error:\n\n{e}"

# Show Assistant Response
    with st.chat_message("assistant"):
        try:
            import re
            match = re.search(r"\[.*\]", response, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                data = json.loads(response)

            # Convert dictionary to list
            if isinstance(data, dict):
                data = [data]

            # Display any list of users as a table
            if isinstance(data, list):

                df = pd.DataFrame(data)

                df.rename(
                        columns={
                            "User_ID":"User ID",
                            "user_id":"User ID",
                            "Name":"Name",
                            "name":"Name",
                            "Email":"Email",
                            "email":"Email",
                            "Created_at":"Created On",
                            "created":"Created On",
                            "created_at":"Created On"
                        },
                        inplace=True
                    )

                st.success(f"✅ Total Users: {len(df)}")

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.markdown(response)

        except Exception:
            st.markdown(response)

# Save Conversation
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

    st.session_state.operation_count += 1

# Refresh Button
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Dashboard"):
    st.rerun()

# Download Chat History
chat_json = json.dumps(
    st.session_state.messages,
    indent=4
)
st.sidebar.download_button(
    label="⬇ Download Chat",
    data=chat_json,
    file_name="chat_history.json",
    mime="application/json"
)

# Clear Chat
if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.session_state.operation_count = 0
    st.success("Chat history cleared successfully.")
    st.rerun()

# Footer
st.markdown("---")

st.markdown(
    """
    <div style="text-align:center;padding:15px">
    <h4>🤖 AI Database Assistant</h4>

    <p>
    Built with
    <b>Python</b> |
    <b>Streamlit</b> |
    <b>CrewAI</b> |
    <b>Gemini</b> |
    <b>SQLite</b>
    </p>

    <p style="color:gray">
    Developed & Maintained by Manoj Sarkar
    </p>

    </div>
    """,
    unsafe_allow_html=True
)
