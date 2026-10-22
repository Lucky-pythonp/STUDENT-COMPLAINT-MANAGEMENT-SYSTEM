import streamlit as st
import database as db

st.set_page_config(page_title="Student Complaint System", page_icon="🎓", layout="wide")
db.init_db()

CATEGORIES = ["Hostel", "Academic", "Canteen", "Infrastructure", "Other"]

STATUS_STYLE = {
    "Pending": {"bg": "#FDECEC", "fg": "#B3261E", "dot": "🔴"},
    "In Progress": {"bg": "#FFF6E0", "fg": "#9A6700", "dot": "🟡"},
    "Resolved": {"bg": "#E6F4EA", "fg": "#1E7B34", "dot": "🟢"},
}

CATEGORY_ICONS = {
    "Hostel": "🏠",
    "Academic": "📚",
    "Canteen": "🍴",
    "Infrastructure": "🏗️",
    "Other": "📌",
}

CUSTOM_CSS = """
<style>
#MainMenu, footer {visibility: hidden;}

.app-header {
    padding: 1.2rem 1.5rem;
    border-radius: 14px;
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    color: white;
    margin-bottom: 1.5rem;
}
.app-header h1 { margin: 0; font-size: 1.6rem; }
.app-header p { margin: 0.2rem 0 0; opacity: 0.9; font-size: 0.9rem; }

.complaint-card {
    border: 1px solid #e8e8ef;
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    background: white;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.complaint-title { font-size: 1.05rem; font-weight: 600; margin-bottom: 0.1rem; }
.complaint-meta { font-size: 0.8rem; color: #6b7280; margin-bottom: 0.4rem; }
.complaint-desc { font-size: 0.92rem; color: #374151; margin-bottom: 0.4rem; }

.status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
}

.metric-box {
    border-radius: 14px;
    padding: 1rem;
    text-align: center;
    background: #f8f9fc;
    border: 1px solid #eceefb;
}
.metric-box h2 { margin: 0; font-size: 1.8rem; }
.metric-box p { margin: 0; font-size: 0.8rem; color: #6b7280; }

.login-card {
    max-width: 420px;
    margin: 2rem auto 0;
    padding: 2rem;
    border-radius: 16px;
    background: white;
    border: 1px solid #ececf4;
    box-shadow: 0 4px 16px rgba(0,0,0,0.05);
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None


def status_badge(status):
    s = STATUS_STYLE.get(status, {"bg": "#eee", "fg": "#333"})
    return f'<span class="status-badge" style="background:{s["bg"]};color:{s["fg"]}">{s["dot"]} {status}</span>'


def login_box():
    st.markdown(
        """
        <div class="app-header" style="text-align:center;">
            <h1>🎓 Student Complaint Management System</h1>
            <p>Raise, track and resolve campus complaints — all in one place</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

        with tab1:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", use_container_width=True, type="primary"):
                user = db.verify_user(username, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            st.caption("Default admin login → username: `admin`, password: `admin123`")

        with tab2:
            new_user = st.text_input("Choose a username", key="reg_user")
            new_pass = st.text_input("Choose a password", type="password", key="reg_pass")
            if st.button("Create account", use_container_width=True, type="primary"):
                if not new_user or not new_pass:
                    st.warning("Please fill both fields.")
                else:
                    ok, msg = db.create_user(new_user, new_pass, role="student")
                    if ok:
                        st.success(msg + " Please login now.")
                    else:
                        st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)


def render_complaint_card(c, show_student=False):
    icon = CATEGORY_ICONS.get(c["category"], "📌")
    student_line = f" &nbsp;·&nbsp; Student: <code>{c['student_username']}</code>" if show_student else ""
    st.markdown(
        f"""
        <div class="complaint-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <div class="complaint-title">{icon} {c['title']}</div>
                    <div class="complaint-meta">{c['category']}{student_line}</div>
                    <div class="complaint-desc">{c['description']}</div>
                    <div class="complaint-meta">Filed: {c['created_at']} &nbsp;|&nbsp; Updated: {c['updated_at']}</div>
                </div>
                <div>{status_badge(c['status'])}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def student_view(user):
    st.sidebar.markdown(f"### 👋 {user['username']}")
    st.sidebar.caption("Role: Student")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.user = None
        st.rerun()

    st.markdown(
        """
        <div class="app-header">
            <h1>🎓 My Complaints</h1>
            <p>Track the status of complaints you've raised</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    complaints = db.get_complaints_by_student(user["username"])
    total = len(complaints)
    resolved = sum(1 for c in complaints if c["status"] == "Resolved")
    pending = sum(1 for c in complaints if c["status"] != "Resolved")

    m1, m2, m3 = st.columns(3)
    for col, label, value in [(m1, "Total filed", total), (m2, "Resolved", resolved), (m3, "Still open", pending)]:
        with col:
            st.markdown(f'<div class="metric-box"><h2>{value}</h2><p>{label}</p></div>', unsafe_allow_html=True)

    st.write("")
    with st.expander("➕ File a new complaint", expanded=False):
        title = st.text_input("Title")
        category = st.selectbox("Category", CATEGORIES)
        description = st.text_area("Description")
        if st.button("Submit complaint", type="primary"):
            if title and description:
                db.add_complaint(user["username"], title, category, description)
                st.success("Complaint submitted!")
                st.rerun()
            else:
                st.warning("Please fill title and description.")

    st.subheader("Complaint history")
    if not complaints:
        st.info("You haven't filed any complaints yet.")
    for c in complaints:
        render_complaint_card(c)


def admin_view(user):
    st.sidebar.markdown(f"### 🛠️ {user['username']}")
    st.sidebar.caption("Role: Admin")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.user = None
        st.rerun()

    st.markdown(
        """
        <div class="app-header">
            <h1>🛠️ Admin Dashboard</h1>
            <p>Review complaints and update their status</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    all_complaints = db.get_all_complaints()
    m1, m2, m3, m4 = st.columns(4)
    counts = {"Total": len(all_complaints)}
    for s in ["Pending", "In Progress", "Resolved"]:
        counts[s] = sum(1 for c in all_complaints if c["status"] == s)
    for col, label in zip([m1, m2, m3, m4], ["Total", "Pending", "In Progress", "Resolved"]):
        with col:
            st.markdown(f'<div class="metric-box"><h2>{counts[label]}</h2><p>{label}</p></div>', unsafe_allow_html=True)

    st.write("")
    status_filter = st.selectbox("Filter by status", ["All", "Pending", "In Progress", "Resolved"])
    complaints = db.get_all_complaints(status_filter)
    st.caption(f"{len(complaints)} complaint(s) found")

    for c in complaints:
        render_complaint_card(c, show_student=True)
        cols = st.columns([3, 1])
        with cols[0]:
            new_status = st.selectbox(
                "Update status",
                ["Pending", "In Progress", "Resolved"],
                index=["Pending", "In Progress", "Resolved"].index(c["status"]),
                key=f"status_{c['id']}",
                label_visibility="collapsed",
            )
        with cols[1]:
            if st.button("Update", key=f"update_{c['id']}", use_container_width=True):
                db.update_status(c["id"], new_status)
                st.success("Status updated!")
                st.rerun()
        st.write("")


def main():
    if st.session_state.user is None:
        login_box()
    else:
        if st.session_state.user["role"] == "admin":
            admin_view(st.session_state.user)
        else:
            student_view(st.session_state.user)


if __name__ == "__main__":
    main()
