"""
Streamlit Dashboard for Compliance Continuum MCP Server
- Run compliance checks
- View audit logs
- Manage regulatory rules
"""
import streamlit as st
import requests
import uuid

API_URL = "http://localhost:8000"  # Change if your backend runs elsewhere

st.set_page_config(page_title="Compliance Continuum Dashboard", layout="wide")
st.title("Compliance Continuum Dashboard")

# --- Authentication ---
import base64
import json

def login(username, password):
    resp = requests.post(f"{API_URL}/auth/token", data={"username": username, "password": password})
    if resp.status_code == 200:
        return resp.json()["access_token"]
    else:
        return None

def decode_jwt(token):
    """Decode JWT payload to extract user info (role, etc)."""
    try:
        payload = token.split(".")[1]
        # Pad base64 if needed
        padded = payload + '=' * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(padded)
        return json.loads(decoded)
    except Exception:
        return {}

def get_headers():
    token = st.session_state.get("jwt_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

if "jwt_token" not in st.session_state:
    st.session_state["jwt_token"] = None
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.subheader("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            token = login(username, password)
            if token:
                st.session_state["jwt_token"] = token
                st.session_state["logged_in"] = True
                # Decode JWT to get user role
                user_info = decode_jwt(token)
                st.session_state["user_role"] = "admin" if user_info.get("is_admin") else "user"
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials.")
else:
    # Decode role if not yet set
    if "user_role" not in st.session_state or not st.session_state["user_role"]:
        user_info = decode_jwt(st.session_state["jwt_token"])
        st.session_state["user_role"] = "admin" if user_info.get("is_admin") else "user"
    role = st.session_state["user_role"]
    st.sidebar.success(f"Logged in as {role}")
    if st.sidebar.button("Logout"):
        st.session_state["jwt_token"] = None
        st.session_state["logged_in"] = False
        st.session_state["user_role"] = None
        st.rerun()
    # --- Sidebar: Navigation ---
    nav_options = ["Run Compliance Check", "View Audit Logs"]
    if role == "admin":
        nav_options.append("Manage Regulatory Rules")
        nav_options.append("User Management")
    menu = st.sidebar.radio("Navigation", nav_options)

    # --- Navigation-controlled sections ---
    if menu == "Run Compliance Check":
        st.header("Run Compliance Check")
        with st.form("compliance_check_form"):
            code = st.text_area("Paste code to check for compliance:")
            submitted = st.form_submit_button("Run Compliance Check")
            if submitted:
                if not code.strip():
                    st.warning("Please paste some code to check.")
                else:
                    resp = requests.post(f"{API_URL}/compliance/check", json={"code": code}, headers=get_headers())
                    if resp.status_code == 200:
                        result = resp.json()
                        st.success("Compliance Check Results:")
                        st.json(result)
                    else:
                        st.error(f"Error: {resp.status_code} {resp.text}")
    elif menu == "View Audit Logs":
        st.header("Audit Logs")
        resp = requests.post(f"{API_URL}/audit/logs", json={}, headers=get_headers())
        if resp.status_code == 200:
            logs = resp.json()
            if logs:
                import pandas as pd
                df = pd.DataFrame(logs)
                st.dataframe(df)
                st.download_button("Download Logs as CSV", df.to_csv(index=False), file_name="audit_logs.csv", mime="text/csv")
            else:
                st.info("No audit logs available.")
        else:
            st.error(f"Error fetching logs: {resp.status_code} {resp.text}")
    elif menu == "Manage Regulatory Rules" and st.session_state.get("user_role") == "admin":
        st.header("Manage Regulatory Rules")
        if st.button("Refresh Rules") or "reg_rules" not in st.session_state:
            resp = requests.get(f"{API_URL}/regulatory/rules", headers=get_headers())
            if resp.status_code == 200:
                st.session_state["reg_rules"] = resp.json()
            else:
                st.error(f"Error fetching rules: {resp.status_code} {resp.text}")
                st.session_state["reg_rules"] = []
        rules = st.session_state.get("reg_rules", [])
        st.subheader("Current Rules")
        for rule in rules:
            with st.expander(f"{rule['name']} ({'Enabled' if rule['enabled'] else 'Disabled'})"):
                st.write(f"**Description:** {rule['description']}")
                st.write(f"**Pattern:** `{rule['pattern']}`")
                st.write(f"**Created:** {rule['created_at']}")
                st.write(f"**Updated:** {rule['updated_at']}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_enabled = st.checkbox("Enabled", value=rule['enabled'], key=f"enabled_{rule['id']}")
                with col2:
                    if st.button("Update", key=f"update_{rule['id']}"):
                        update_data = {"enabled": new_enabled}
                        resp = requests.put(f"{API_URL}/regulatory/rules/{rule['id']}", json=update_data, headers=get_headers())
                        if resp.status_code == 200:
                            st.success("Rule updated.")
                        else:
                            st.error(f"Update failed: {resp.status_code} {resp.text}")
                with col3:
                    if st.button("Delete", key=f"delete_{rule['id']}"):
                        resp = requests.delete(f"{API_URL}/regulatory/rules/{rule['id']}", headers=get_headers())
                        if resp.status_code == 200:
                            st.success("Rule deleted.")
                        else:
                            st.error(f"Delete failed: {resp.status_code} {resp.text}")
        st.subheader("Add New Rule")
        with st.form("add_rule_form"):
            name = st.text_input("Rule Name")
            description = st.text_area("Description")
            pattern = st.text_input("Regex Pattern")
            enabled = st.checkbox("Enabled", value=True)
            submitted = st.form_submit_button("Add Rule")
            if submitted:
                if not name or not description or not pattern:
                    st.warning("All fields are required.")
                else:
                    new_rule = {
                        "name": name,
                        "description": description,
                        "pattern": pattern,
                        "enabled": enabled
                    }
                    resp = requests.post(f"{API_URL}/regulatory/rules", json=new_rule, headers=get_headers())
                    if resp.status_code == 200:
                        st.success("Rule added.")
                    else:
                        st.error(f"Add failed: {resp.status_code} {resp.text}")
    elif menu == "User Management" and st.session_state.get("user_role") == "admin":
        st.header("User Management")
        if st.button("Refresh Users") or "users" not in st.session_state:
            resp = requests.get(f"{API_URL}/users", headers=get_headers())
            if resp.status_code == 200:
                st.session_state["users"] = resp.json()
            else:
                st.error(f"Error fetching users: {resp.status_code} {resp.text}")
                st.session_state["users"] = []
        users = st.session_state.get("users", [])
        st.subheader("Current Users")
        for user in users:
            with st.expander(f"{user['username']} ({'Admin' if user['is_admin'] else 'User'})"):
                st.write(f"**Email:** {user['email']}")
                st.write(f"**Active:** {user['is_active']}")
                st.write(f"**Created:** {user['created_at']}")
                st.write(f"**User ID:** {user['id']}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_active = st.checkbox("Active", value=user['is_active'], key=f"active_{user['id']}")
                    new_admin = st.checkbox("Admin", value=user['is_admin'], key=f"admin_{user['id']}")
                with col2:
                    if st.button("Update", key=f"update_user_{user['id']}"):
                        update_data = {"is_active": new_active, "is_admin": new_admin}
                        resp = requests.put(f"{API_URL}/users/{user['id']}", json=update_data, headers=get_headers())
                        if resp.status_code == 200:
                            st.success("User updated.")
                        else:
                            st.error(f"Update failed: {resp.status_code} {resp.text}")
                with col3:
                    if st.button("Delete", key=f"delete_user_{user['id']}"):
                        resp = requests.delete(f"{API_URL}/users/{user['id']}", headers=get_headers())
                        if resp.status_code == 200:
                            st.success("User deleted.")
                        else:
                            st.error(f"Delete failed: {resp.status_code} {resp.text}")
        st.subheader("Add New User")
        with st.form("add_user_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            is_admin = st.checkbox("Admin", value=False)
            is_active = st.checkbox("Active", value=True)
            submitted = st.form_submit_button("Add User")
            if submitted:
                if not username or not email or not password:
                    st.warning("All fields are required.")
                else:
                    new_user = {
                        "username": username,
                        "email": email,
                        "password": password,
                        "is_admin": is_admin,
                        "is_active": is_active
                    }
                    resp = requests.post(f"{API_URL}/users", json=new_user, headers=get_headers())
                    if resp.status_code == 200:
                        st.success("User added.")
                    else:
                        st.error(f"Add failed: {resp.status_code} {resp.text}")
    elif menu == "Compliance Analytics" and st.session_state.get("user_role") == "admin":
        st.header("Compliance Analytics")
        # --- Analytics Filters ---
        import pandas as pd
        with st.expander("Analytics Filters", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                start_date = st.date_input("Start Date", help="Show data from this date onwards.")
            with col2:
                end_date = st.date_input("End Date", help="Show data up to this date.")
            with col3:
                user_filter = st.text_input("User ID (optional)", help="Filter by a specific user ID.")
            resource_filter = st.text_input("Resource ID (optional)", help="Filter by a specific resource ID.")
            filter_btn = st.button("Apply Filters")
        filter_payload = {}
        if start_date:
            filter_payload["start_date"] = str(start_date)
        if end_date:
            filter_payload["end_date"] = str(end_date)
        if user_filter:
            filter_payload["user_id"] = user_filter
        if resource_filter:
            filter_payload["resource_id"] = resource_filter
        logs = []
        if filter_btn or any(filter_payload.values()):
            resp = requests.post(f"{API_URL}/audit/logs", json=filter_payload, headers=get_headers())
            if resp.status_code == 200:
                logs = resp.json()
            else:
                st.info("No analytics data available for selected filters.")
        else:
            resp = requests.post(f"{API_URL}/audit/logs", json={}, headers=get_headers())
            if resp.status_code == 200:
                logs = resp.json()
        if logs:
            total_checks = len(logs)
            passed = sum(1 for l in logs if l.get("compliance_status") == "passed")
            failed = sum(1 for l in logs if l.get("compliance_status") == "failed")
            by_rule = {}
            by_date = {}
            user_ids = set()
            resource_ids = set()
            for l in logs:
                rule = l.get("action_type", "unknown")
                by_rule[rule] = by_rule.get(rule, 0) + 1
                date = l.get("timestamp", "").split("T")[0]
                by_date[date] = by_date.get(date, 0) + 1
                if l.get("user_id"): user_ids.add(l["user_id"])
                if l.get("resource_id"): resource_ids.add(l["resource_id"])
            st.metric("Total Checks", total_checks)
            st.metric("Passed", passed)
            st.metric("Failed", failed)
            st.bar_chart(by_rule)
            st.line_chart(by_date)
            st.subheader("Per-User Dashboard")
            user_select = st.selectbox("Select User for Drill-down", sorted(user_ids), key="per_user_select", help="See analytics for a specific user.") if user_ids else None
            if user_select:
                user_logs = [l for l in logs if l.get("user_id") == user_select]
                st.write(f"Analytics for User: {user_select}")
                st.metric("User's Checks", len(user_logs))
                st.metric("Passed", sum(1 for l in user_logs if l.get("compliance_status") == "passed"))
                st.metric("Failed", sum(1 for l in user_logs if l.get("compliance_status") == "failed"))
                user_by_rule = {}
                for l in user_logs:
                    rule = l.get("action_type", "unknown")
                    user_by_rule[rule] = user_by_rule.get(rule, 0) + 1
                st.bar_chart(user_by_rule)
            st.subheader("Per-Resource Dashboard")
            resource_select = st.selectbox("Select Resource for Drill-down", sorted(resource_ids), key="per_resource_select", help="See analytics for a specific resource.") if resource_ids else None
            if resource_select:
                res_logs = [l for l in logs if l.get("resource_id") == resource_select]
                st.write(f"Analytics for Resource: {resource_select}")
                st.metric("Resource's Checks", len(res_logs))
                st.metric("Passed", sum(1 for l in res_logs if l.get("compliance_status") == "passed"))
                st.metric("Failed", sum(1 for l in res_logs if l.get("compliance_status") == "failed"))
                res_by_rule = {}
                for l in res_logs:
                    rule = l.get("action_type", "unknown")
                    res_by_rule[rule] = res_by_rule.get(rule, 0) + 1
                st.bar_chart(res_by_rule)
            df = pd.DataFrame(logs)
            st.download_button("Export Analytics as CSV", df.to_csv(index=False), file_name="compliance_analytics.csv", mime="text/csv")
        else:
            st.info("No analytics data available.")
            # List all users
            if st.button("Refresh Users") or "users" not in st.session_state:
                resp = requests.get(f"{API_URL}/users", headers=get_headers())
                if resp.status_code == 200:
                    st.session_state["users"] = resp.json()
                else:
                    st.error(f"Error fetching users: {resp.status_code} {resp.text}")
                    st.session_state["users"] = []
            users = st.session_state.get("users", [])
            st.subheader("Current Users")
            for user in users:
                with st.expander(f"{user['username']} ({'Admin' if user['is_admin'] else 'User'})"):
                    st.write(f"**Email:** {user['email']}")
                    st.write(f"**Active:** {user['is_active']}")
                    st.write(f"**Created:** {user['created_at']}")
                    st.write(f"**User ID:** {user['id']}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        new_active = st.checkbox("Active", value=user['is_active'], key=f"active_{user['id']}")
                        new_admin = st.checkbox("Admin", value=user['is_admin'], key=f"admin_{user['id']}")
                    with col2:
                        if st.button("Update", key=f"update_user_{user['id']}"):
                            update_data = {"is_active": new_active, "is_admin": new_admin}
                            resp = requests.put(f"{API_URL}/users/{user['id']}", json=update_data, headers=get_headers())
                            if resp.status_code == 200:
                                st.success("User updated.")
                            else:
                                st.error(f"Update failed: {resp.status_code} {resp.text}")
                    with col3:
                        if st.button("Delete", key=f"delete_user_{user['id']}"):
                            resp = requests.delete(f"{API_URL}/users/{user['id']}", headers=get_headers())
                            if resp.status_code == 200:
                                st.success("User deleted.")
                            else:
                                st.error(f"Delete failed: {resp.status_code} {resp.text}")
            # Add new user
            st.subheader("Add New User")
            with st.form("add_user_form"):
                username = st.text_input("Username")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                is_admin = st.checkbox("Admin", value=False)
                is_active = st.checkbox("Active", value=True)
                submitted = st.form_submit_button("Add User")
                if submitted:
                    if not username or not email or not password:
                        st.warning("All fields are required.")
                    else:
                        new_user = {
                            "username": username,
                            "email": email,
                            "password": password,
                            "is_admin": is_admin,
                            "is_active": is_active
                        }
                        resp = requests.post(f"{API_URL}/users", json=new_user, headers=get_headers())
                st.session_state["reg_rules"] = []
        rules = st.session_state.get("reg_rules", [])
        st.subheader("Current Rules")
        for rule in rules:
            with st.expander(f"{rule['name']} ({'Enabled' if rule['enabled'] else 'Disabled'})"):
                st.write(f"**Description:** {rule['description']}")
                st.write(f"**Pattern:** `{rule['pattern']}`")
                st.write(f"**Created:** {rule['created_at']}")
                st.write(f"**Updated:** {rule['updated_at']}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_enabled = st.checkbox("Enabled", value=rule['enabled'], key=f"enabled_{rule['id']}")
                with col2:
                    if st.button("Update", key=f"update_{rule['id']}"):
                        update_data = {"enabled": new_enabled}
                        resp = requests.put(f"{API_URL}/regulatory/rules/{rule['id']}", json=update_data, headers=get_headers())
                        if resp.status_code == 200:
                            st.success("Rule updated.")
                        else:
                            st.error(f"Update failed: {resp.status_code} {resp.text}")
                with col3:
                    if st.button("Delete", key=f"delete_{rule['id']}"):
                        resp = requests.delete(f"{API_URL}/regulatory/rules/{rule['id']}", headers=get_headers())
                        if resp.status_code == 200:
                            st.success("Rule deleted.")
                        else:
                            st.error(f"Delete failed: {resp.status_code} {resp.text}")
        # Add new rule
        st.subheader("Add New Rule")
        with st.form("add_rule_form"):
            name = st.text_input("Rule Name")
            description = st.text_area("Description")
            pattern = st.text_input("Regex Pattern")
            enabled = st.checkbox("Enabled", value=True)
            submitted = st.form_submit_button("Add Rule")
            if submitted:
                if not name or not description or not pattern:
                    st.warning("All fields are required.")
                else:
                    new_rule = {
                        "name": name,
                        "description": description,
                        "pattern": pattern,
                        "enabled": enabled
                    }
                    resp = requests.post(f"{API_URL}/regulatory/rules", json=new_rule, headers=get_headers())
                    if resp.status_code == 200:
                        st.success("Rule added.")
                    else:
                        st.error(f"Add failed: {resp.status_code} {resp.text}")
