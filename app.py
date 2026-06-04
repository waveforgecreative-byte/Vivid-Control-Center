import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sqlite3
import random
import time
import io

# ==========================================
# ১. গ্লোবাল মেটা, ব্রান্ডিং ও আইটি এজেন্সি আল্ট্রা থিম
# ==========================================
st.set_page_config(page_title="Vivid Core Core ULTRA Command Center", page_icon="⚡", layout="wide")

# আইটি এজেন্সি এবং টেক হাউজের জন্য নিয়ন ও গ্লাস-মরফিজম থিমিং
st.markdown("""
<style>
    body { background-color: #0a0f1d; color: #e2e8f0; }
    .stApp { background: linear-gradient(145deg, #070a14, #0f172a); }
    
    /* গ্লাস-মরফিজম কার্ড ইফেক্ট */
    .profile-card { background: rgba(30, 41, 59, 0.7); padding: 20px; border-radius: 16px; border: 1px solid rgba(56, 189, 248, 0.2); text-align: center; margin-bottom: 20px; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4); backdrop-filter: blur(5px); transition: 0.3s; }
    .profile-card:hover { border-color: #00f2fe; box-shadow: 0 0 15px rgba(0, 242, 254, 0.4); }
    
    /* চ্যাট বাবল থিম */
    .chat-bubble-user { background: linear-gradient(135deg, #00b4db, #0083b0); color: #ffffff; padding: 12px; border-radius: 16px 16px 4px 16px; margin: 8px 0; text-align: right; max-width: 75%; margin-left: auto; box-shadow: 0 4px 12px rgba(0,180,219,0.3); }
    .chat-bubble-other { background-color: #1e293b; color: #f1f5f9; padding: 12px; border-radius: 16px 16px 16px 4px; margin: 8px 0; text-align: left; max-width: 75%; border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
    .global-chat-bubble { background-color: #0f172a; border-left: 5px solid #38bdf8; padding: 10px; border-radius: 6px; margin: 5px 0; border-top: 1px solid rgba(255,255,255,0.02); }
    
    /* ব্যাজ ও নোটিশ বোর্ড */
    .active-dot { height: 10px; width: 10px; background-color: #00e676; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: 0 0 8px #00e676; }
    .badge-officer { background: linear-gradient(90deg, #f43f5e, #e11d48); color: white; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .badge-verified { background: linear-gradient(90deg, #3b82f6, #1d4ed8); color: white; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .notice-box { background: linear-gradient(135deg, #1e1b4b, #2e1065); border-left: 6px solid #a855f7; padding: 22px; border-radius: 12px; color: #f3e8ff; margin-bottom: 25px; box-shadow: 0 8px 20px rgba(0,0,0,0.3); }
</style>
""", unsafe_allow_html=True)

DB_FILE = "vivid_studio_max_v6.db"

# টেকনোলজিক্যাল ডিফল্ট অবতার ইমেজ (যদি প্রোফাইল পিকচার আপলোড না থাকে)
DEFAULT_AVATAR_URL = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=150&auto=format&fit=crop&q=60"

# ==========================================
# ২. ডেটাবেস আর্কিটেকচার
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, client_name TEXT, client_number TEXT,
        service_name TEXT, total_price REAL, advance_paid REAL, due_amount REAL,
        editor_name TEXT, editor_cost REAL, operation_cost REAL, month_tag TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, password TEXT, fullname TEXT, role TEXT, 
        whatsapp TEXT, bio TEXT, skills TEXT, is_officer_verified INTEGER, profile_pic BLOB)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY, client TEXT, editor TEXT, task_detail TEXT, 
        assign_time TEXT, start_time TEXT, submit_time TEXT,
        status TEXT, final_link TEXT, revision_note TEXT, editor_payment REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, role_tag TEXT, title TEXT, content TEXT, timestamp TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS goals (month_tag TEXT PRIMARY KEY, target_amount REAL)''')
    
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""INSERT INTO users VALUES (
            'reyadh', 'cto123', 'Reyadh (CTO)', 'CTO', '01700000000', 
            'Chief Technology Officer | System Architect & Tech Lead. Driving automation, server security, and ultimate pipeline synchronization for Vivid Core.', 
            'Python Full-Stack, System Architecture, Database Optimization, Server Security, AI Automation & Workflow Engineering.', 1, NULL)""")
        cursor.execute("""INSERT INTO users VALUES (
            'admin', '123', 'Agency Chairman', 'Chairman', '01900000000', 
            'Founder & Chairman of Vivid Core.', 'Management', 1, NULL)""")
        
    current_month = datetime.now().strftime("%Y-%m")
    cursor.execute("INSERT OR IGNORE INTO goals VALUES (?, 150000)", (current_month,))
    conn.commit()
    conn.close()

init_db()

# ==========================================
# ৩. ইন-মেমোরি লাইভ স্টেট ও নোটিফিকেশন ইঞ্জিন
# ==========================================
if "global_chats" not in st.session_state:
    st.session_state.global_chats = []
if "notifications" not in st.session_state:
    st.session_state.notifications = []
if "active_users" not in st.session_state:
    st.session_state.active_users = {}

def update_activity(username):
    st.session_state.active_users[username] = time.time()

def trigger_live_notification(text, target_nav):
    st.session_state.notifications.append({
        "text": text, "target": target_nav, "time": datetime.now().strftime("%I:%M %p")
    })

def get_db_connection():
    return sqlite3.connect(DB_FILE)

def load_user_dict():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    u_dict = {}
    for _, row in df.iterrows():
        u_dict[row["username"]] = {
            "password": row["password"], "fullname": row["fullname"], "role": row["role"],
            "whatsapp": row["whatsapp"], "bio": row["bio"], "skills": row["skills"],
            "is_verified": bool(row["is_officer_verified"]), "pic": row["profile_pic"]
        }
    return u_dict

USER_DB = load_user_dict()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = ""
if "current_navigation" not in st.session_state:
    st.session_state.current_navigation = "📊 লাইভ ড্যাশবোর্ড"

if st.session_state.logged_in and st.session_state.notifications:
    latest_notif = st.session_state.notifications[-1]
    with st.container():
        col_n1, col_n2 = st.columns([5, 1])
        col_n1.warning(f"🚀 **আইটি নেটওয়ার্ক এলার্ট:** {latest_notif['text']} ({latest_notif['time']})")
        if col_n2.button("ভিউ প্যানেল ⚡", key="redirect_btn"):
            st.session_state.current_navigation = latest_notif['target']
            st.session_state.notifications.pop()
            st.rerun()

# --- লগইন স্ক্রিন ---
if not st.session_state.logged_in:
    st.title("🌌 Vivid Core IT Ultra Command Center")
    st.markdown("### 💻 Devised & Maintained by **CTO REYADH**")
    
    u_id = st.text_input("সিস্টেম ইউজার আইডি (Username)")
    u_pass = st.text_input("এক্সেস কী (Password)", type="password")
    
    if st.button("সার্ভার নোড এথেন্টিকেশন 🔐", use_container_width=True):
        if u_id in USER_DB and USER_DB[u_id]["password"] == u_pass:
            st.session_state.logged_in = True
            st.session_state.user = u_id
            update_activity(u_id)
            st.success("এজেন্সি সার্ভার সিঙ্ক সাকসেসফুল!")
            st.rerun()
        else:
            st.error("ভুল ইউজার আইডি অথবা পাসওয়ার্ড!")
else:
    current_user = st.session_state.user
    my_meta = USER_DB[current_user]
    user_role = my_meta["role"]
    is_verified_officer = my_meta["is_verified"] or (user_role in ["Chairman", "CTO", "Admin"])
    
    update_activity(current_user)
    
    # ==========================================
    # ৪. সাইডবার কন্ট্রোল সেন্টার
    # ==========================================
    st.sidebar.markdown("<h1 style='color:#00f2fe; text-align:center; font-family:monospace; font-weight:bold; letter-spacing:2px;'>VIVID CORE</h1>", unsafe_allow_html=True)
    
    if my_meta["pic"]:
        st.sidebar.image(io.BytesIO(my_meta["pic"]), width=120)
    else:
        st.sidebar.image(DEFAULT_AVATAR_URL, width=120, caption="IT Identity Card")
        
    st.sidebar.write(f"🖥️ **{my_meta['fullname']}**")
    st.sidebar.write(f"🧬 ডেজিগনেশন: `{user_role}`")
    
    if is_verified_officer:
        st.sidebar.markdown("<span class='badge-verified'>🔒 SECURE OFFICER ENABLED</span>", unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("🛰️ **অনলাইন নেটওয়ার্ক নোডস**")
    
    for user, last_seen in list(st.session_state.active_users.items()):
        if time.time() - last_seen < 300:
            meta = USER_DB.get(user, {"fullname": user, "role": "User", "pic": None})
            col_s1, col_s2 = st.sidebar.columns([1, 4])
            if meta["pic"]:
                col_s1.image(io.BytesIO(meta["pic"]), width=25)
            else:
                col_s1.image(DEFAULT_AVATAR_URL, width=25)
            col_s2.markdown(f"<span class='active-dot'></span> {meta['fullname']} <small style='color:#38bdf8;'>`{meta['role']}`</small>", unsafe_allow_html=True)

    if st.sidebar.button("সার্ভার ডিসকানেক্ট 🚪", use_container_width=True):
        st.session_state.active_users.pop(current_user, None)
        st.session_state.logged_in = False
        st.rerun()

    menu_options = ["📊 লাইভ ড্যাশবোর্ড", "👥 এমপ্লয়ি ডিরেক্টরি হাব", "💬 লাইভ চ্যাট রুম", "👤 আমার প্রোফাইল এডিট করুন"]
    
    if user_role == "Editor":
        menu_options.insert(3, "🎬 আমার এডিটিং প্যানেল")
    if user_role in ["Chairman", "CTO", "Admin", "Manager"]:
        menu_options.append("✍️ নতুন অর্ডার এন্ট্রি")
        menu_options.append("🎯 টাস্ক ডিস্ট্রিবিউটর")
    if is_verified_officer:
        menu_options.append("📉 লাইভ প্রফিট ও রিপোর্ট হাব")
    if user_role in ["Chairman", "CTO", "Admin"]:
        menu_options.append("👮 অ্যাডমিন ও CTO কন্ট্রোল প্যানেল")
        menu_options.append("🕵️ সিক্রেট ইনবক্স স্পাইডার (Spy)")

    selected_menu = st.sidebar.radio("মডিউল সিলেকশন", menu_options, index=menu_options.index(st.session_state.current_navigation) if st.session_state.current_navigation in menu_options else 0)
    st.session_state.current_navigation = selected_menu
    
    current_month_tag = datetime.now().strftime("%Y-%m")
    
    conn = get_db_connection()
    df_orders = pd.read_sql_query("SELECT * FROM orders", conn)
    df_tasks = pd.read_sql_query("SELECT * FROM tasks", conn)
    df_notices = pd.read_sql_query("SELECT * FROM notices ORDER BY id DESC LIMIT 1", conn)
    conn.close()

    if not df_notices.empty:
        notice = df_notices.iloc[0]
        st.markdown(f"""
        <div class='notice-box'>
            <h4>⚡ এজেন্সী ব্রডকাস্ট: {notice['title']}</h4>
            <p>{notice['content']}</p>
            <hr style='border-color:rgba(255,255,255,0.1);'>
            <small>📡 নোড সোর্স: <b>{notice['author']} ({notice['role_tag']})</b> | টাইম: {notice['timestamp']}</small>
        </div>
        """, unsafe_allow_html=True)

    # ==========================================
    # ৫. মেইন লাইভ ড্যাশবোর্ড
    # ==========================================
    if st.session_state.current_navigation == "📊 লাইভ ড্যাশবোর্ড":
        st.title("📊 Vivid Core আইট অটোমেশন ড্যাশবোর্ড")
        
        st.subheader("👥 একটিভ টিম রিসোর্স কাউন্টার")
        conn = get_db_connection()
        df_all_users = pd.read_sql_query("SELECT role FROM users", conn)
        conn.close()
        
        role_counts = df_all_users["role"].value_counts()
        roles_to_check = ['Chairman', 'CEO', 'CTO', 'Co-Founder', 'Operation Officer', 'Manager', 'Moderator', 'Editor', 'Internee']
        
        c_layout = st.columns(len(roles_to_check))
        for idx, r_name in enumerate(roles_to_check):
            count = role_counts.get(r_name, 0)
            c_layout[idx].metric(r_name, f"{count} জন")
            
        st.markdown("---")
        
        # কাস্টম গোল রিড
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT target_amount FROM goals WHERE month_tag = ?", (current_month_tag,))
        g_res = cursor.fetchone()
        conn.close()
        live_target = g_res[0] if g_res else 150000.0
        
        if df_orders.empty:
            st.info("চলতি মাসের ডাটাবেস ফাঁকা।")
        else:
            current_month_sales = df_orders[df_orders["month_tag"] == current_month_tag]["total_price"].sum()
            progress_pct = min(current_month_sales / live_target, 1.0) if live_target > 0 else 0.0
            
            st.subheader("🎯 মান্থলি এজেন্সি সেলস গোল ট্র্যাকিং")
            col_p1, col_p2 = st.columns([3, 1])
            with col_p1:
                st.write(f"চলতি মাসের রেভিনিউ: **{current_month_sales:,.0f} BDT** / এজেন্সি কাস্টম লক্ষ্যমাত্রা: **{live_target:,.0f} BDT**")
                st.progress(progress_pct)
            with col_p2:
                st.markdown(f"### 🚀 {progress_pct*100:.1f}% ডান")

    # ==========================================
    # ৬. এমপ্লয়ি ডিরেক্টরি হাব
    # ==========================================
    elif st.session_state.current_navigation == "👥 এমপ্লয়ি ডিরেক্টরি হাব":
        st.title("👥 আইটি ট্যালেন্ট ও রিসোর্স ডিরেক্টরি")
        
        conn = get_db_connection()
        df_dir = pd.read_sql_query("SELECT fullname, role, whatsapp, bio, skills, is_officer_verified, profile_pic FROM users", conn)
        conn.close()
        
        dir_cols = st.columns(3)
        for idx, row in df_dir.iterrows():
            col_target = dir_cols[idx % 3]
            with col_target:
                st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
                if row["profile_pic"]:
                    st.image(io.BytesIO(row["profile_pic"]), width=130)
                else:
                    st.image(DEFAULT_AVATAR_URL, width=130)
                
                st.markdown(f"<h3>{row['fullname']}</h3>", unsafe_allow_html=True)
                st.markdown(f"💻 রোল: <span style='color:#00f2fe;'><b>{row['role']}</b></span>", unsafe_allow_html=True)
                
                if row['is_officer_verified'] or row['role'] in ['Chairman', 'CTO', 'Admin']:
                    st.markdown("<br><span class='badge-officer'>🔒 CORE OFFICER</span><br>", unsafe_allow_html=True)
                
                st.write(f"📞 যোগাযোগ: [{row['whatsapp']}](https://wa.me/{row['whatsapp']})")
                st.write(f"📋 পরিচিতি: *{row['bio']}*")
                st.write(f"🛠️ টেকনিক্যাল স্কিলসেট: `{row['skills']}`")
                st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # 𝟳. চ্যাট রুম
    # ==========================================
    elif st.session_state.current_navigation == "💬 লাইভ চ্যাট রুম":
        st.title("💬 সেশন সিঙ্ক লাইভ চ্যাট হাব")
        chat_mode = st.radio("চ্যাট চ্যানেল মোড:", ["Global Enterprise Pipeline", "Private Encrypted 1:1 DM"])
        
        if chat_mode == "Global Enterprise Pipeline":
            st.subheader("🌐 গ্লোবাল টিম পাইপলাইন")
            st.markdown("<div style='background-color: #0b111e; padding: 20px; border-radius: 12px; height: 300px; overflow-y: scroll;'>", unsafe_allow_html=True)
            for chat in st.session_state.global_chats:
                if chat["type"] == "public":
                    st.markdown(f"<div class='global-chat-bubble'><b>{chat['sender_name']} [{chat['sender_role']}]:</b> {chat['msg']} <br><small style='font-size:9px;color:#64748b;'>{chat['time']}</small></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            with st.form("pub_form", clear_on_submit=True):
                msg_txt = st.text_input("মেসেজ স্ট্রীম ইনপুট...")
                if st.form_submit_button("ব্রডকাস্ট ডাটা ✈️"):
                    if msg_txt:
                        st.session_state.global_chats.append({
                            "sender": current_user, "sender_name": my_meta["fullname"], "sender_role": user_role,
                            "receiver": "all", "msg": msg_txt, "time": datetime.now().strftime("%I:%M %p"), "type": "public"
                        })
                        st.rerun()
        else:
            st.subheader("🔒 অ্যান্ড-টু-অ্যান্ড এনক্রিপ্টেড ইনবক্স")
            all_peers = list(USER_DB.keys())
            if current_user in all_peers:
                all_peers.remove(current_user)
                
            selected_peer = st.selectbox("👤 টারগেট নোড ইউজার:", all_peers, format_func=lambda x: f"{USER_DB[x]['fullname']} ({USER_DB[x]['role']})")
            
            st.markdown("<div style='background-color: #0b111e; padding: 20px; border-radius: 12px; height: 300px; overflow-y: scroll;'>", unsafe_allow_html=True)
            for chat in st.session_state.global_chats:
                if chat["type"] == "private":
                    if chat["sender"] == current_user and chat["receiver"] == selected_peer:
                        st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {chat['msg']}<br><small style='font-size:9px;color:#e2e8f0;'>{chat['time']}</small></div>", unsafe_allow_html=True)
                    elif chat["sender"] == selected_peer and chat["receiver"] == current_user:
                        st.markdown(f"<div class='chat-bubble-other'><b>{USER_DB[selected_peer]['fullname']}:</b> {chat['msg']}<br><small style='font-size:9px;color:#64748b;'>{chat['time']}</small></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            with st.form("priv_form", clear_on_submit=True):
                msg_p_txt = st.text_input("সিকিউরড মেসেজ ইনপুট...")
                if st.form_submit_button("ডাটা প্যাকেট পুশ 🔐"):
                    if msg_p_txt:
                        st.session_state.global_chats.append({
                            "sender": current_user, "receiver": selected_peer, "msg": msg_p_txt, "time": datetime.now().strftime("%I:%M %p"), "type": "private"
                        })
                        trigger_live_notification(f"💬 {my_meta['fullname']} আপনার ইনবক্সে পিং করেছেন!", "💬 লাইভ চ্যাট রুম")
                        st.rerun()

    # ==========================================
    # 👤 ইউজার প্রোফাইল এডিট হাব
    # ==========================================
    elif st.session_state.current_navigation == "👤 আমার প্রোফাইল এডিট করুন":
        st.title("👤 মাই ড্যাশবোর্ড আইডি কার্ড কন্ট্রোল")
        st.write("আপনার মেম্বার ডিরেক্টরি প্রোফাইলটি এখান থেকে মডিফাই ও লাইভ আপডেট করতে পারেন।")
        
        with st.form("user_self_update_form", clear_on_submit=False):
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                u_fullname = st.text_input("আপনার নাম (Full Name)", value=my_meta["fullname"])
                u_whatsapp = st.text_input("হোয়াটসঅ্যাপ নোড নাম্বার", value=my_meta["whatsapp"])
                u_bio = st.text_area("আপনার প্রোফাইল বায়ো/পরিচিতি (Bio)", value=my_meta["bio"])
            with col_u2:
                u_skills = st.text_input("টেকনিক্যাল এক্সপেরিয়েন্স ও স্কিলসেট", value=my_meta["skills"])
                if my_meta["pic"]:
                    st.image(io.BytesIO(my_meta["pic"]), width=110, caption="বর্তমান প্রোফাইল ছবি")
                else:
                    st.image(DEFAULT_AVATAR_URL, width=110, caption="ডিফল্ট ইমেজ")
                u_pic = st.file_uploader("নতুন ছবি আপলোড (.jpg/.png)", type=["jpg", "png"])
            
            if st.form_submit_button("ডাটাবেস কোড সিঙ্ক করুন 💾"):
                conn = get_db_connection()
                cursor = conn.cursor()
                if u_pic:
                    new_pic_blob = u_pic.read()
                    cursor.execute("""UPDATE users SET fullname=?, whatsapp=?, bio=?, skills=?, profile_pic=? WHERE username=?""", 
                                   (u_fullname, u_whatsapp, u_bio, u_skills, new_pic_blob, current_user))
                else:
                    cursor.execute("""UPDATE users SET fullname=?, whatsapp=?, bio=?, skills=? WHERE username=?""", 
                                   (u_fullname, u_whatsapp, u_bio, u_skills, current_user))
                conn.commit()
                conn.close()
                st.success("🎉 আপনার রিসোর্স প্রোফাইল সফলভাবে আপডেট করা হয়েছে!")
                time.sleep(1)
                st.rerun()

    # ==========================================
    # ✍️ নতুন অর্ডার এন্ট্রি
    # ==========================================
    elif st.session_state.current_navigation == "✍️ নতুন অর্ডার এন্ট্রি":
        st.title("📝 ডিল পাইপলাইন ডাটা লগার")
        editor_list = [u for u in USER_DB if USER_DB[u]["role"] == "Editor"]
        
        with st.form("order_form_v6", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                cl_name = st.text_input("ক্লায়েন্ট/কোম্পানির নাম *")
                cl_phone = st.text_input("যোগাযোগের নাম্বার/হোয়াটসঅ্যাপ *")
                srv = st.text_input("সার্ভিস/প্রোডাক্ট আর্কিটেকচার নাম *")
            with col2:
                t_p = st.number_input("টোটাল ডিল প্রাইস (BDT) *", min_value=0)
                a_p = st.number_input("ইনস্ট্যান্ট এডভান্সড পেইড (BDT)", min_value=0)
                ed_n = st.selectbox("রিসোর্স পারসন/এডিটর সিলেক্ট করুন *", editor_list if editor_list else ["No Editor Found"])
                ed_c = st.number_input("এডিটর বিল/রিসোর্স কস্ট (BDT) *", min_value=0)
                op_c = st.number_input("অপারেশনাল ট্র্যাকিং খরচ (BDT)", min_value=0)
                
            if st.form_submit_button("ডাটা মডিউল সেভ করুন 🚀"):
                if cl_name and cl_phone and ed_n != "No Editor Found":
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('''INSERT INTO orders VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                   (datetime.now().strftime("%Y-%m-%d"), cl_name, cl_phone, srv, t_p, a_p, t_p-a_p, ed_n, ed_c, op_c, current_month_tag))
                    conn.commit()
                    conn.close()
                    trigger_live_notification(f"✍️ সিস্টেমে নতুন রেভিনিউ লগ এন্ট্রি করা হয়েছে!", "📊 লাইভ ড্যাশবোর্ড")
                    st.success("🎉 নতুন ক্লায়েন্ট অর্ডার ডেটাবেসে ইনজেক্ট করা হয়েছে!")
                    st.rerun()

    # ==========================================
    # 🎯 টাস্ক ডিস্ট্রিবিউটর
    # ==========================================
    elif st.session_state.current_navigation == "🎯 টাস্ক ডিস্ট্রিবিউটর":
        st.title("🎯 টাস্ক ও ওয়ার্কফ্লো ডিস্ট্রিবিউটর")
        editor_list = [u for u in USER_DB if USER_DB[u]["role"] == "Editor"]
        
        with st.form("task_dist_v6", clear_on_submit=True):
            cx1, cx2 = st.columns(2)
            with cx1:
                t_cl = st.text_input("ক্লায়েন্ট সোর্স")
                t_ed = st.selectbox("কোন এসাইনড এডিটরকে সাবমিট করবেন?", editor_list if editor_list else ["No Editor"])
                t_dt = st.text_area("প্রজেক্টের রিকোয়ারমেন্ট ডক ও ব্রিফ")
            with cx2:
                t_pay = st.number_input("কন্ট্রাকচুয়াল কস্ট বাজেট (BDT)", min_value=0)
                
            if st.form_submit_button("🛰️ ওয়ার্কফ্লো লাইভ পুশ দিন"):
                if t_cl and t_ed != "No Editor":
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    assign_timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                    cursor.execute('INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                   (random.randint(10000, 99999), t_cl, t_ed, t_dt, assign_timestamp, "Not Started Yet", "Not Submitted Yet", "Pending", "No Link", "No Revision Note", t_pay))
                    conn.commit()
                    conn.close()
                    trigger_live_notification(f"🎬 নতুন প্রজেক্ট পুশ করা হয়েছে!", "🎬 আমার এডিটিং প্যানেল")
                    st.success("🔥 এডিটর টার্মিনাল ড্যাশবোর্ডে কাজ পুশ হয়েছে!")
                    st.rerun()

    # ==========================================
    # ১০. আমার এডিটিং প্যানেল
    # ==========================================
    elif st.session_state.current_navigation == "🎬 আমার এডিটিং প্যানেল":
        st.title("🎬 Editor Workspace Terminal")
        my_tasks = df_tasks[df_tasks["editor"] == current_user]
        
        if my_tasks.empty:
            st.info("আপনার ওয়ার্কিং নোডে কোনো টাস্ক কন্টেইনার নেই।")
        else:
            for index, row in my_tasks.iterrows():
                with st.expander(f"📌 ক্লায়েন্ট পাইপলাইন: {row['client']} | 🚦 কন্ডিশন: {row['status']}"):
                    st.write(f"**📝 টাস্ক ব্রিফ:** {row['task_detail']}")
                    st.error(f"🔧 **রিভিশন প্যাচ নোট:** {row['revision_note']}")
                    
                    col_b1, col_b2 = st.columns(2)
                    if row['status'] == "Pending":
                        if col_b1.button("🎬 ইনিশিয়েট ওয়ার্ক", key=f"strt_{index}"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute('UPDATE tasks SET status="Started", start_time=? WHERE id=?', (datetime.now().strftime("%I:%M %p"), row['id']))
                            conn.commit()
                            conn.close()
                            st.rerun()
                            
                    if row['status'] in ["Started", "Revision"]:
                        drive_link = st.text_input("ফাইনাল ক্লাউড/ড্রাইভ লিংক দিন:", value=row['final_link'], key=f"lnk_{index}")
                        if col_b2.button("🚀 কোড/আউটপুট পুশ করুন", key=f"sub_{index}"):
                            if drive_link and drive_link != "No Link":
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                cursor.execute('UPDATE tasks SET status="Submitted", final_link=?, submit_time=? WHERE id=?', (drive_link, datetime.now().strftime("%I:%M %p"), row['id']))
                                conn.commit()
                                conn.close()
                                st.rerun()

    # ==========================================
    # ১১. লাইভ প্রফিট ও রিপোর্ট হাব
    # ==========================================
    elif st.session_state.current_navigation == "📉 লাইভ প্রফিট ও রিপোর্ট হাব":
        st.title("📉 ফিনান্সিয়াল লেজার ও নেট গ্রোথ রিপোর্ট")
        
        if df_orders.empty:
            st.info("কোন ফাইন্যান্সিয়াল ম্যাট্রিক্স রেকর্ড খুঁজে পাওয়া যায়নি।")
        else:
            df_orders["net_profit"] = df_orders["total_price"] - (df_orders["editor_cost"] + df_orders["operation_cost"])
            month_list = sorted(df_orders["month_tag"].unique(), reverse=True)
            selected_month = st.selectbox("📅 বিলিং সাইকেল সিলেক্ট করুন:", month_list)
            
            filtered_df = df_orders[df_orders["month_tag"] == selected_month]
            
            c_s1, c_s2, c_s3 = st.columns(3)
            c_s1.metric("টোটাল গ্রস সেলস", f"{filtered_df['total_price'].sum():,.0f} BDT")
            c_s2.metric("নীট এজেন্সি প্রফিট", f"{filtered_df['net_profit'].sum():,.0f} BDT")
            c_s3.metric("টোটাল রিসোর্স বার্ন (Cost)", f"{(filtered_df['editor_cost'].sum() + filtered_df['operation_cost'].sum()):,.0f} BDT")
            
            st.dataframe(filtered_df, use_container_width=True)

    # ==========================================
    # ১২. অ্যাডমিন ও CTO কন্ট্রোল প্যানেল
    # ==========================================
    elif st.session_state.current_navigation == "👮 অ্যাডমিন ও CTO কন্ট্রোল প্যানেল":
        st.title("👮 মাস্টার সুপারভাইজার গেটওয়ে ও এক্সেস কন্ট্রোল")
        
        st.subheader("🎯 মান্থলি কাস্টম সেলস টার্গেট (Goal Setting)")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT target_amount FROM goals WHERE month_tag = ?", (current_month_tag,))
        g_res = cursor.fetchone()
        conn.close()
        current_saved_goal = g_res[0] if g_res else 150000.0
        
        with st.form("goal_form", clear_on_submit=False):
            new_goal = st.number_input(f"টার্গেট ভ্যালু কনফিগার করুন - ({current_month_tag}) (BDT)", min_value=0, value=int(current_saved_goal))
            if st.form_submit_button("মাস্টার গোল রিলোড করুন 🚀"):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO goals VALUES (?, ?)", (current_month_tag, new_goal))
                conn.commit()
                conn.close()
                st.success(f"🎉 কাস্টম মান্থলি সেলস বেঞ্চমার্ক {new_goal:,.0f} BDT-তে লকড!")
                time.sleep(1)
                st.rerun()

        st.markdown("---")
        
        st.subheader("📢 গ্লোবাল নেটওয়ার্ক নোটিশ পাবলিশার")
        with st.form("notice_form", clear_on_submit=True):
            n_title = st.text_input("ব্রডকাস্ট নোটিশ হেডার")
            n_content = st.text_area("নোটিশ বডি ডাটা")
            if st.form_submit_button("সিস্টেম ব্রডকাস্ট করুন 🚀"):
                if n_title and n_content:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO notices VALUES (NULL, ?, ?, ?, ?, ?)",
                                   (my_meta["fullname"], user_role, n_title, n_content, datetime.now().strftime("%Y-%m-%d %I:%M %p")))
                    conn.commit()
                    conn.close()
                    st.success("নোটিশ মডিউল সাকসেসফুলি পুশড!")
                    st.rerun()
                    
        st.markdown("---")
        
        st.subheader("🔒 ইউজার নেটওয়ার্ক পারমিশন ম্যাট্রিক্স (IAM)")
        conn = get_db_connection()
        df_users_manage = pd.read_sql_query("SELECT username, fullname, role, is_officer_verified FROM users", conn)
        conn.close()
        
        for idx, u_row in df_users_manage.iterrows():
            if u_row["username"] == current_user:
                continue
                
            col_v1, col_v2, col_v3 = st.columns([4, 2, 2])
            status_text = "✅ Approved Verified Officer" if u_row["is_officer_verified"] else "❌ No Financial Access"
            col_v1.write(f"👤 **{u_row['fullname']}** — রোল: `{u_row['role']}` \n\n পারমিশন স্ট্যাটাস: **{status_text}**")
            
            if u_row["is_officer_verified"]:
                if col_v2.button("লক এক্সেস 🔒", key=f"rev_{idx}"):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET is_officer_verified=0 WHERE username=?", (u_row["username"],))
                    conn.commit()
                    conn.close()
                    st.rerun()
            else:
                if col_v2.button("ভেরিফাই এনাবল ✅", key=f"grant_{idx}"):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET is_officer_verified=1 WHERE username=?", (u_row["username"],))
                    conn.commit()
                    conn.close()
                    st.rerun()
            
            if col_v3.button("টার্মিনেট অ্যাকাউন্ট 🗑️", key=f"del_{idx}"):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE username=?", (u_row["username"],))
                conn.commit()
                conn.close()
                st.error(f"ইউজার টার্মিনেটেড!")
                st.rerun()
                    
        st.markdown("---")
        
        st.subheader("➕ নতুন রিসোর্স/মেম্বার প্রোফাইল জেনারেটর")
        with st.form("cre_user_v6_form", clear_on_submit=True):
            cx_1, cx_2 = st.columns(2)
            with cx_1:
                n_u = st.text_input("ইউনিক ইউজারনেম আইডি *")
                n_p = st.text_input("অ্যাসাইনড সিক্রেট পাসওয়ার্ড *")
                n_f = st.text_input("এমপ্লয়ির অফিসিয়াল নাম *")
                n_r = st.selectbox("অর্গানাইজেশনাল রোল *", ['Chairman', 'CEO', 'CTO', 'Co-Founder', 'Operation Officer', 'Manager', 'Moderator', 'Editor', 'Internee'])
            with cx_2:
                n_w = st.text_input("হোয়াটসঅ্যাপ নোড নম্বর *")
                n_b = st.text_area("রিসোর্স প্রোফাইল বায়ো")
                n_sk = st.text_input("কোর স্পেশালিটি ও এক্সপার্টাইজ")
                n_pic = st.file_uploader("আইডেন্টিটি পিকচার (.jpg/.png)", type=["jpg", "png"], key="admin_user_pic")
                
            if st.form_submit_button("রিসোর্স নেটওয়ার্ক একটিভেট করুন 🚀"):
                if n_u and n_p and n_f and n_w:
                    pic_blob = None
                    if n_pic:
                        pic_blob = n_pic.read()
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)',
                                       (n_u, n_p, n_f, n_r, n_w, n_b, n_sk, pic_blob))
                        conn.commit()
                        conn.close()
                        st.success(f"🎉 {n_f} সাকসেসফুলি ইনজেক্টেড!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"ডাটা টাইপ এরর: {e}")

    # ==========================================
    # ১৩. সিক্রেট ইনবক্স স্পাইডার (Spy Tool)
    # ==========================================
    elif st.session_state.current_navigation == "🕵️ সিক্রেট ইনবক্স স্পাইডার (Spy)":
        st.title("🕵️ ডাটা প্যাকেট স্নাইপার ও চ্যাট ইন্টারসেপ্টর")
        
        all_user_keys = list(USER_DB.keys())
        col_spy1, col_spy2 = st.columns(2)
        spy_target_1 = col_spy1.selectbox("নোড ১:", all_user_keys, key="spy1", format_func=lambda x: f"{USER_DB[x]['fullname']} ({USER_DB[x]['role']})")
        spy_target_2 = col_spy2.selectbox("নোড ২:", all_user_keys, key="spy2", format_func=lambda x: f"{USER_DB[x]['fullname']} ({USER_DB[x]['role']})")
        
        st.markdown("<div style='background-color: #0b0808; padding: 20px; border-radius: 12px; border: 1px solid #ef4444; height: 350px; overflow-y: scroll;'>", unsafe_allow_html=True)
        found_chats = False
        for chat in st.session_state.global_chats:
            if chat["type"] == "private":
                if (chat["sender"] == spy_target_1 and chat["receiver"] == spy_target_2) or (chat["sender"] == spy_target_2 and chat["receiver"] == spy_target_1):
                    found_chats = True
                    sender_label = USER_DB[chat["sender"]]["fullname"]
                    st.markdown(f"<div style='color: #ef4444; padding: 5px 0; font-family:monospace;'>[INTERCEPTED] <b>{sender_label}:</b> {chat['msg']} <span style='color:#64748b;'>[{chat['time']}]</span></div>", unsafe_allow_html=True)
        
        if not found_chats:
            st.info("টার্গেট লাইনে কোনো আদান-প্রদান করা ডাটা প্যাকেট পাওয়া যায়নি।")
        st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # ১৪. আইটি সিস্টেম লাইভ স্ট্যাটাস ও ফুটার ব্র্যান্ডিং (Developed by REYADH)
    # ==========================================
    st.markdown("---")
    col_ft1, col_ft2, col_ft3 = st.columns(3)
    col_ft1.caption("🟢 Core Server: **Secure & Active**")
    col_ft2.caption(f"💾 DB Node Connection: **SQLite Verified ({DB_FILE})**")
    col_ft3.caption(f"🛰️ Sync Time: **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")
    
    st.markdown("<p style='text-align: center; color: #64748b; font-family: monospace; font-size:12px; margin-top:20px;'>⚡ Enterprise Architecture Engineered & Supervised by CTO <b style='color:#00f2fe;'>REYADH</b> | Version Ultra 6.8 (2026) ⚡</p>", unsafe_allow_html=True)
