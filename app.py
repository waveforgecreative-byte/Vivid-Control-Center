import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import io

# ==========================================
# ১. গ্লোবাল মেটা, ব্রান্ডিং ও আল্ট্রা ডার্ক থিম
# ==========================================
st.set_page_config(page_title="Vivid Core ULTRA Command Center", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    body { background-color: #0a0f1d; color: #e2e8f0; }
    .stApp { background: linear-gradient(145deg, #070a14, #0f172a); }
    
    /* ডিরেক্টরি প্রোফাইল কার্ড */
    .profile-card { 
        background: rgba(30, 41, 59, 0.45); 
        padding: 22px; 
        border-radius: 16px; 
        border: 1px solid rgba(56, 189, 248, 0.15); 
        text-align: left; 
        margin-bottom: 20px; 
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); 
        backdrop-filter: blur(12px) !important;
    }
    
    /* সাইডবার এবং কার্ডের ইমেজ ফিক্স */
    .stSidebar img, .profile-card img, .active-user-avatar {
        border-radius: 50% !important;
        object-fit: cover !important;
        border: 2px solid #00f2fe !important;
    }
    
    /* কাউন্টার উইজেট */
    .counter-box { text-align: center; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; }
    .counter-title { font-size: 12px; color: #94a3b8; font-weight: 500; }
    .counter-value { font-size: 22px; color: #ffffff; font-weight: bold; margin-top: 5px; }
    
    /* লাইভ চ্যাট উইন্ডো */
    .chat-container { background-color: #0b111e; padding: 20px; border-radius: 12px; height: 380px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; border: 1px solid rgba(255,255,255,0.05); }
    .global-chat-bubble { background-color: #1e293b; border-left: 5px solid #38bdf8; padding: 12px; border-radius: 6px; color: #f1f5f9; margin: 4px 0; }
    
    .active-dot { height: 10px; width: 10px; background-color: #00e676; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #00e676; }
    .card-verified { background: linear-gradient(90deg, #10b981, #059669); color: white; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; display: inline-block; margin-top: 5px; }
    
    /* গোল ট্র্যাকিং ব্যানার */
    .goal-success { background: linear-gradient(135deg, #064e3b, #047857); padding: 15px; border-radius: 10px; border-left: 6px solid #10b981; color: #ecfdf5; margin-bottom: 20px; }
    .goal-failed { background: linear-gradient(135deg, #7f1d1d, #b91c1c); padding: 15px; border-radius: 10px; border-left: 6px solid #ef4444; color: #fef2f2; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

DB_FILE = "vivid_studio_max_v6.db"
DEFAULT_AVATAR = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"

# ==========================================
# ২. ডাটাবেস কানেকশন ও কোর আর্কিটেকচার
# ==========================================
def get_db_connection():
    return sqlite3.connect(DB_FILE, timeout=30, check_same_thread=False)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, client_name TEXT, client_number TEXT,
        service_name TEXT, total_price REAL, advance_paid REAL, due_amount REAL,
        editor_name TEXT, editor_cost REAL, operation_cost REAL, month_tag TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, password TEXT, fullname TEXT, role TEXT, 
        whatsapp TEXT, bio TEXT, skills TEXT, is_officer_verified INTEGER, profile_pic BLOB, last_seen TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT, client TEXT, editor TEXT, task_detail TEXT, 
        assign_time TEXT, start_time TEXT, submit_time TEXT,
        status TEXT, final_link TEXT, revision_note TEXT, editor_payment REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS goals (month_tag TEXT PRIMARY KEY, target_amount REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, sender_name TEXT, sender_role TEXT, msg TEXT, timestamp TEXT)''')
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_seen TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass

    # CTO Reyadh Profile Lock Node
    cursor.execute("SELECT COUNT(*) FROM users WHERE username='reyadh'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""INSERT INTO users (username, password, fullname, role, whatsapp, bio, skills, is_officer_verified, last_seen) VALUES (
            'reyadh', 'cto123', 'Developed by Md Reyadh', 'CTO & Lead Developer', '01825221830', 
            'The Supreme Mind behind Vivid Core IT Ecosystem. System Architect, Lead Developer, and Ultimate Platform Owner.', 
            'System Architecture, Enterprise Automation, Core Backend Dev, Full-Stack Dev, Software Infrastructure, Database Optimization.', 1, '')""")
    else:
        cursor.execute("""UPDATE users SET 
            fullname='Developed by Md Reyadh', 
            role='CTO & Lead Developer', 
            bio='The Supreme Mind behind Vivid Core IT Ecosystem. System Architect, Lead Developer, and Ultimate Platform Owner.' 
            WHERE username='reyadh'""")
    
    current_month = datetime.now().strftime("%Y-%m")
    cursor.execute("INSERT OR IGNORE INTO goals VALUES (?, 150000)", (current_month,))
    conn.commit()
    conn.close()

init_db()

def update_user_heartbeat(username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET last_seen=? WHERE username=?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username))
        conn.commit()
        conn.close()
    except Exception:
        pass

# সেশন স্টেট ইনিশিয়ালাইজেশন
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = ""
if "current_navigation" not in st.session_state:
    st.session_state.current_navigation = "📊 লাইভ ড্যাশবোর্ড"

# ==========================================
# ৩. লগইন ও নতুন আইডি ক্রিয়েশন (Sign Up) হাব
# ==========================================
if not st.session_state.logged_in:
    st.title("🌌 Vivid Core IT Ultra Command Center")
    
    auth_tabs = st.tabs(["🔐 সার্ভার লগইন", "📝 নতুন আইডি তৈরি করুন (Sign Up)"])
    
    with auth_tabs[0]:
        u_id = st.text_input("ইউজার আইডি (Username)", key="login_uid")
        u_pass = st.text_input("এক্সেস কী (Password)", type="password", key="login_pass")
        
        if st.button("সার্ভার নোড এথেন্টিকেশন 🔐", use_container_width=True):
            conn = get_db_connection()
            user_data = pd.read_sql_query("SELECT * FROM users WHERE username=?", conn, params=(u_id.lower().strip(),))
            conn.close()
            
            if not user_data.empty and user_data.iloc[0]["password"] == u_pass:
                st.session_state.logged_in = True
                st.session_state.user = u_id.lower().strip()
                update_user_heartbeat(u_id.lower().strip())
                st.rerun()
            else:
                st.error("ভুল ইউজার আইডি বা পাসওয়ার্ড! আবার চেষ্টা করুন।")
                
    with auth_tabs[1]:
        with st.form("signup_form", clear_on_submit=True):
            st.subheader("🛠️ নতুন মেম্বার রেজিস্ট্রেশন গেটওয়ে")
            new_uid = st.text_input("ইউজার আইডি (Username - ছোট হাতের অক্ষরে, স্পেস ছাড়া):")
            new_pass = st.text_input("পাসওয়ার্ড (Password):", type="password")
            new_fullname = st.text_input("পূর্ণ নাম (Full Name):")
            new_role = st.selectbox("টিম রোল সিলেক্ট করুন:", ["Chairman", "CEO", "CTO & Lead Developer", "Co-Founder", "Operation Officer", "Manager", "Moderator", "Editor", "Internee"])
            new_whatsapp = st.text_input("হোয়াটসঅ্যাপ নাম্বার:")
            
            if st.form_submit_button("নতুন অ্যাকাউন্ট ডাটাবেসে সেভ করুন 💾"):
                clean_uid = new_uid.lower().strip()
                if not clean_uid or not new_pass or not new_fullname:
                    st.error("❌ ইউজার আইডি, পাসওয়ার্ড এবং পূর্ণ নাম অবশ্যই দিতে হবে!")
                else:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM users WHERE username=?", (clean_uid,))
                    if cursor.fetchone()[0] > 0:
                        st.error("⚠️ এই ইউজার আইডিটি ইতিমধ্যে ব্যবহার করা হয়েছে! অন্য আইডি ট্রাই করুন।")
                        conn.close()
                    else:
                        cursor.execute("""INSERT INTO users (username, password, fullname, role, whatsapp, bio, skills, is_officer_verified, last_seen) 
                                       VALUES (?, ?, ?, ?, ?, '', '', 0, '')""", 
                                       (clean_uid, new_pass, new_fullname, new_role, new_whatsapp))
                        conn.commit()
                        conn.close()
                        st.success("🎉 অ্যাকাউন্ট তৈরি সফল হয়েছে! এবার পাশের 'সার্ভার লগইন' ট্যাবে গিয়ে লগইন করুন।")

# ==========================================
# ৪. মেইন ড্যাশবোর্ড ইন্টারফেস (লগইন সাকসেসড)
# ==========================================
else:
    current_user = st.session_state.user
    update_user_heartbeat(current_user)
    
    conn = get_db_connection()
    my_meta = pd.read_sql_query("SELECT * FROM users WHERE username=?", conn, params=(current_user,)).iloc[0]
    df_users_all = pd.read_sql_query("SELECT * FROM users", conn)
    df_orders = pd.read_sql_query("SELECT * FROM orders", conn)
    df_tasks = pd.read_sql_query("SELECT * FROM tasks", conn)
    df_goals = pd.read_sql_query("SELECT * FROM goals", conn)
    conn.close()
    
    if "last_seen" not in df_users_all.columns:
        df_users_all["last_seen"] = ""
        
    user_role = my_meta["role"]
    is_editor = user_role.lower() == "editor"
    is_verified = int(my_meta["is_officer_verified"]) == 1
    
    # সাইডবার ইন্টারফেস ও প্রোফাইল নোড
    st.sidebar.markdown("### 🌌 Vivid Core Node")
    if my_meta["profile_pic"]:
        st.sidebar.image(io.BytesIO(my_meta["profile_pic"]), width=90)
    else:
        st.sidebar.image(DEFAULT_AVATAR, width=90)
        
    st.sidebar.write(f"🖥️ **{my_meta['fullname']}**")
    st.sidebar.write(f"🧬 রোল: `{user_role}`")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("🛰️ **অনলাইন ট্র্যাকার নোডস (৫ মি.)**")
    
    five_mins_ago = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    df_users_all["last_seen"] = df_users_all["last_seen"].fillna("")
    active_users = df_users_all[df_users_all["last_seen"] >= five_mins_ago]
    
    for _, u_row in active_users.iterrows():
        st.sidebar.markdown(f"<span class='active-dot'></span> **{u_row['fullname']}** (`{u_row['role']}`)", unsafe_allow_html=True)

    if st.sidebar.button("সার্ভার ডিসকানেক্ট 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    current_month_tag = datetime.now().strftime("%Y-%m")

    # 🔒 এডিটর স্পেসিফিক প্যানেল
    if is_editor:
        st.title("🛠️ এডিটর ড্যাশবোর্ড ও ওয়ার্ক প্যানেল")
        st.write(f"স্বাগতম **{my_meta['fullname']}**! আপনার বর্তমান অ্যাসাইনকৃত কাজের তালিকা:")
        
        conn = get_db_connection()
        my_tasks = pd.read_sql_query("SELECT * FROM tasks WHERE editor=? ORDER BY id DESC", conn, params=(current_user,))
        conn.close()
        
        if my_tasks.empty:
            st.info("আপনার জন্য বর্তমানে কোনো সক্রিয় কাজ বরাদ্দ নেই।")
        else:
            for idx, t_row in my_tasks.iterrows():
                with st.expander(f"📌 টাস্ক আইডি: {t_row['id']} | ক্লায়েন্ট: {t_row['client']} | অবস্থা: {t_row['status']}"):
                    st.markdown(f"💬 **কাজের বিবরণ:** {t_row['task_detail']}")
                    st.markdown(f"💰 **ফি:** {t_row['editor_payment']} BDT")
                    if t_row['revision_note']:
                        st.error(f"⚠️ **রিভিশন নোট:** {t_row['revision_note']}")
                    
                    with st.form(f"editor_form_{t_row['id']}"):
                        new_status = st.selectbox("কাজের প্রগ্রেস:", ["Started", "Submitted"], index=0 if t_row['status']=="Pending" else 1)
                        delivery_link = st.text_input("ওয়ার্ক/ডেলিভারি লিংক:", value=t_row['final_link'])
                        
                        if st.form_submit_button("আপডেট সাবমিট করুন 🚀"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE tasks SET status=?, final_link=? WHERE id=?", (new_status, delivery_link, t_row['id']))
                            conn.commit()
                            conn.close()
                            st.success("টাস্ক প্রগ্রেস ডাটাবেসে সেভ হয়েছে!")
                            st.rerun()

    # 👮 অ্যাডমিন, সিইও, কো-ফাউন্ডার ও মডারেটর মডিউলস
    else:
        menu_options = [
            "📊 লাইভ ড্যাশবোর্ড",
            "👥 এমপ্লয়ি ডিরেক্টরি হাব",
            "💬 লাইভ চ্যাট রুম",
            "👤 আমার প্রোফাইল এডিট করুন",
            "✍️ নতুন অর্ডার এন্ট্রি",
            "🎯 টাস্ক ডিস্ট্রিবিউটর",
            "⚡ মডারেটর লাইভ টাস্ক আপডেট"
        ]
        
        if is_verified:
            menu_options.append("📉 লাইভ প্রফিট ও রিপোর্ট হাব")
            menu_options.append("👮 অ্যাডমিন ও CTO কন্ট্রোল প্যানেল")
            menu_options.append("🕵️ সিক্রেট ইনবক্স স্পাইডার (Spy)")

        selected_menu = st.sidebar.radio("মডিউল সিলেকশন", menu_options, index=menu_options.index(st.session_state.current_navigation) if st.session_state.current_navigation in menu_options else 0)
        st.session_state.current_navigation = selected_menu

        # 📊 ১. লাইভ ড্যাশবোর্ড
        if st.session_state.current_navigation == "📊 লাইভ ড্যাশবোর্ড":
            st.title("📊 Vivid Core আইটি অটোমেশন ড্যাশবোর্ড")
            st.subheader("👥 একটিভ টিম রিসোর্স কাউন্টার")
            roles_to_count = ["Chairman", "CEO", "CTO & Lead Developer", "Co-Founder", "Operation Officer", "Manager", "Moderator", "Editor", "Internee"]
            c_cols = st.columns(len(roles_to_count))
            for idx, r_name in enumerate(roles_to_count):
                count_val = len(df_users_all[df_users_all["role"].str.lower() == r_name.lower()])
                with c_cols[idx]:
                    st.markdown(f"<div class='counter-box'><div class='counter-title'>{r_name}</div><div class='counter-value'>{count_val} জন</div></div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            current_month_orders = df_orders[df_orders["month_tag"] == current_month_tag]
            if current_month_orders.empty:
                st.info("চলতি মাসের ডাটাবেস ফাঁকা।")
            else:
                st.dataframe(current_month_orders, use_container_width=True)

        # 👥 ২. এমপ্লয়ি ডিরেক্টরি হাব
        elif st.session_state.current_navigation == "👥 এমপ্লয়ি ডিরেক্টরি হাব":
            st.title("👥 আইটি ট্যালেন্ট ও রিসোর্স ডিরেক্টরি")
            dir_cols = st.columns(3)
            for idx, row in df_users_all.iterrows():
                with dir_cols[idx % 3]:
                    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
                    if row['profile_pic']:
                        st.image(io.BytesIO(row['profile_pic']), width=90)
                    else:
                        st.image(DEFAULT_AVATAR, width=90)
                    if row['is_officer_verified'] == 1:
                        st.markdown("<span class='card-verified'>🛡️ OFFICER VERIFIED</span>", unsafe_allow_html=True)
                    st.markdown(f"### {row['fullname']}", unsafe_allow_html=True)
                    st.markdown(f"📁 <b>রোল:</b> <span style='color:#00f2fe;'>{row['role']}</span>", unsafe_allow_html=True)
                    st.markdown(f"📞 <b>WhatsApp:</b> {row['whatsapp'] if row['whatsapp'] else 'N/A'}", unsafe_allow_html=True)
                    st.markdown(f"📝 <b>Bio:</b> <small>{row['bio'] if row['bio'] else 'No Bio Set.'}</small>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

        # 💬 ৩. লাইভ চ্যাট রুম
        elif st.session_state.current_navigation == "💬 লাইভ চ্যাট রুম":
            st.title("💬 সেশন সিঙ্ক লাইভ চ্যাট হাব (Messenger Mode)")
            
            conn = get_db_connection()
            df_chat_logs = pd.read_sql_query("SELECT * FROM chat_messages ORDER BY id ASC", conn)
            conn.close()
            st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
            for _, chat in df_chat_logs.iterrows():
                st.markdown(f"<div class='global-chat-bubble'><b>{chat['sender_name']} [{chat['sender_role']}]:</b> {chat['msg']} <small style='color:#64748b; float:right;'>{chat['timestamp']}</small></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            with st.form("chat_send_form", clear_on_submit=True):
                msg_txt = st.text_input("মেসেজ ইনপুট করুন...")
                if st.form_submit_button("ব্রডকাস্ট ডাটা ✈️"):
                    if msg_txt:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO chat_messages (sender, sender_name, sender_role, msg, timestamp) VALUES (?,?,?,?,?)",
                                       (current_user, my_meta["fullname"], user_role, msg_txt, datetime.now().strftime("%I:%M:%S %p")))
                        conn.commit()
                        conn.close()
                        st.rerun()

        # 👤 ৪. আমার প্রোফাইল এডিট করুন
        elif st.session_state.current_navigation == "👤 আমার প্রোফাইল এডিট করুন":
            st.title("👤 মাই ড্যাсходোর্ড আইডি কার্ড কন্ট্রোল")
            with st.form("profile_control_form"):
                f_name = st.text_input("আপনার নাম (Full Name)", value=my_meta["fullname"])
                w_num = st.text_input("হোয়াটসঅ্যাপ নাম্বার", value=my_meta["whatsapp"])
                b_info = st.text_area("আপনার প্রোফাইল বায়ো", value=my_meta["bio"])
                uploaded_pic = st.file_uploader("নতুন প্রোফাইল ছবি আপলোড", type=["jpg", "png"])
                if st.form_submit_button("ডাটাবেস কোড সিঙ্ক করুন 💾"):
                    img_bytes = my_meta["profile_pic"]
                    if uploaded_pic is not None:
                        img_bytes = uploaded_pic.read()
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET fullname=?, whatsapp=?, bio=?, profile_pic=? WHERE username=?", 
                                   (f_name, w_num, b_info, img_bytes, current_user))
                    conn.commit()
                    conn.close()
                    st.success("প্রোফাইল সফলভাবে আপডেট হয়েছে!")
                    st.rerun()

        # ✍️ ৫. নতুন অর্ডার এন্ট্রি
        elif st.session_state.current_navigation == "✍️ নতুন অর্ডার এন্ট্রি":
            st.title("✍️ নতুন ক্লায়েন্ট অর্ডার এন্ট্রি")
            with st.form("order_entry_form"):
                c_name = st.text_input("ক্লায়েন্টের নাম:")
                c_num = st.text_input("মোবাইল নাম্বার:")
                s_name = st.text_input("সার্ভিস নাম:")
                t_price = st.number_input("মোট বাজেট (BDT):", min_value=0.0)
                ed_name = st.text_input("অ্যাসাইনকৃত এডিটর নাম:")
                ed_cost = st.number_input("এডিটর খরচ (BDT):", min_value=0.0)
                op_cost = st.number_input("অপারেশনাল কস্ট (BDT):", min_value=0.0)
                if st.form_submit_button("অর্ডার সেভ করুন 💾"):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO orders (date, client_name, client_number, service_name, total_price, advance_paid, due_amount, editor_name, editor_cost, operation_cost, month_tag) VALUES (?,?,?,?,?,0,?, ?,?,?,?)",
                                   (datetime.now().strftime("%Y-%m-%d"), c_name, c_num, s_name, t_price, t_price, ed_name, ed_cost, op_cost, current_month_tag))
                    conn.commit()
                    conn.close()
                    st.success("অর্ডারটি ডাটাবেসে সেভ হয়েছে!")

        # 🎯 ৬. টাস্ক ডিস্ট্রিবিউটর
        elif st.session_state.current_navigation == "🎯 টাস্ক ডিস্ট্রিবিউটর":
            st.title("🎯 টিম টাস্ক ডিস্ট্রিবিউটর টার্মিনাল")
            with st.form("task_dist_form", clear_on_submit=True):
                t_client = st.text_input("ক্লায়েন্ট রেফারেন্স কোড:")
                t_editor = st.text_input("টার্গেট কর্মী (Editor Username):")
                t_detail = st.text_area("কাজের ডিটেইলস:")
                t_payment = st.number_input("বজেট/ফি:", min_value=0.0)
                if st.form_submit_button("টাস্ক ও অর্ডার ইস্যু করুন 🚀"):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO tasks (client, editor, task_detail, assign_time, start_time, submit_time, status, final_link, revision_note, editor_payment) VALUES (?,?,?,?,'','','Pending','','',?)",
                                   (t_client, t_editor, t_detail, datetime.now().strftime("%I:%M %p"), t_payment))
                    conn.commit()
                    conn.close()
                    st.success("টাস্ক সফলভাবে ইস্যু করা হয়েছে!")

        # ⚡ ৭. মডারেটর লাইভ টাস্ক আপডেট
        elif st.session_state.current_navigation == "⚡ মডারেটর লাইভ টাস্ক আপডেট":
            st.title("⚡ মডারেটর লাইভ টাস্ক আপডেট টার্মিনাল")
            conn = get_db_connection()
            tasks_current = pd.read_sql_query("SELECT * FROM tasks ORDER BY id DESC", conn)
            conn.close()
            for idx, t_row in tasks_current.iterrows():
                with st.expander(f"📌 টাস্ক আইডি: {t_row['id']} | কর্মী: {t_row['editor']} | স্ট্যাটাস: {t_row['status']}"):
                    with st.form(f"mod_form_{t_row['id']}"):
                        current_status = t_row['status'] if t_row['status'] in ["Pending", "Started", "Submitted", "Approved", "Revision"] else "Pending"
                        m_status = st.selectbox("স্ট্যাটাস আপডেট:", ["Pending", "Started", "Submitted", "Approved", "Revision"], index=["Pending", "Started", "Submitted", "Approved", "Revision"].index(current_status))
                        m_link = st.text_input("ফাইনাল ডেলিভারি লিংক:", value=t_row['final_link'])
                        m_rev = st.text_input("রিভিশন নোট:", value=t_row['revision_note'])
                        if st.form_submit_button("নোড আপডেট সাবমিট ⚙️"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE tasks SET status=?, final_link=?, revision_note=? WHERE id=?", (m_status, m_link, m_rev, t_row['id']))
                            conn.commit()
                            conn.close()
                            st.success("টাস্ক লাইভ সিঙ্ক সফল!")
                            st.rerun()

        # 📉 ৮. লাইভ প্রফিট ও রিপোর্ট হাব (প্রটেক্টেড)
        elif is_verified and st.session_state.current_navigation == "📉 লাইভ প্রফিট ও রিপোর্ট হাব":
            st.title("📉 ফিনান্সিয়াল লেজার ও মান্থলি গোল")
            df_orders["net_profit"] = df_orders["total_price"] - (df_orders["editor_cost"] + df_orders["operation_cost"])
            total_net_profit = df_orders[df_orders["month_tag"] == current_month_tag]['net_profit'].sum()
            month_goal_row = df_goals[df_goals["month_tag"] == current_month_tag]
            target_amount = month_goal_row["target_amount"].values[0] if not month_goal_row.empty else 150000.0
            
            if total_net_profit >= target_amount:
                st.markdown(f"<div class='goal-success'><h3>🎉 মিশন সাকসেসফুল! টার্গেট এچیভড!</h3><p>নেট প্রফিট অর্জিত হয়েছে <b>{total_net_profit:,.0f} BDT</b>!</p></div>", unsafe_allow_html=True)
            else:
                shortage = target_amount - total_net_profit
                st.markdown(f"<div class='goal-failed'><h3>⚠️ অ্যালার্ট: টার্গেট ফেইলুর রিস্ক!</h3><p>শর্টেজ: <b>{shortage:,.0f} BDT</b></p></div>", unsafe_allow_html=True)
            st.dataframe(df_orders, use_container_width=True)

        # 👮 ৯. অ্যাডমিন ও CTO প্যানেল (প্রটেক্টেড)
        elif is_verified and st.session_state.current_navigation == "👮 অ্যাডমিন ও CTO কন্ট্রোল প্যানেল":
            st.title("👮 অ্যাডমিন ও ওনার কন্ট্রোল প্যানেল")
            st.subheader("👥 টিম মেম্বারদের ভেরিফাইড গেটওয়ে স্ট্যাটাস")
            for idx, u_row in df_users_all.iterrows():
                col_v1, col_v2 = st.columns([3, 1])
                with col_v1:
                    st.write(f"👤 **{u_row['fullname']}** (`{u_row['role']}`) | {'Verified 🛡️' if u_row['is_officer_verified'] == 1 else 'Unverified ❌'}")
                with col_v2:
                    if u_row['is_officer_verified'] == 0:
                        if st.button("ভেরিফাই এনাবল 🛠️", key=f"v_btn_{u_row['username']}"):
                            conn = get_db_connection()
                            conn.cursor().execute("UPDATE users SET is_officer_verified=1 WHERE username=?", (u_row['username'],))
                            conn.commit()
                            conn.close()
                            st.success("ইউজার ভেরিফাইড!")
                            st.rerun()
                    else:
                        if u_row['is_officer_verified'] == 1 and u_row['username'] != 'reyadh':
                            if st.button("ভেরিফিকেশন রিমুভ ⚠️", key=f"uv_btn_{u_row['username']}"):
                                conn = get_db_connection()
                                conn.cursor().execute("UPDATE users SET is_officer_verified=0 WHERE username=?", (u_row['username'],))
                                conn.commit()
                                conn.close()
                                st.warning("ভেরিফিকেশন রিমুভড!")
                                st.rerun()

        # 🕵️ ১০. সিক্রেট ইনবক্স概念 স্পাইডার (Spy) (প্রটেক্টেড)
        elif is_verified and st.session_state.current_navigation == "🕵️ সিক্রেট ইনবক্স স্পাইডার (Spy)":
            st.title("🕵️ সিক্রেট ইনবক্স স্পাইডার (Enterprise Spy Terminal)")
            conn = get_db_connection()
            df_spy = pd.read_sql_query("SELECT * FROM chat_messages ORDER BY id DESC", conn)
            conn.close()
            st.dataframe(df_spy, use_container_width=True)

    # ==========================================
    # ৫. গ্লোবাল ফুটার (অটো রিরান লুপ ফিক্সড)
    # ==========================================
    st.markdown("---")
    st.caption(f"🟢 Server Node Status: Secure & Active | Core Database Synced Successfully")
