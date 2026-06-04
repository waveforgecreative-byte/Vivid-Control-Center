import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sqlite3
import random
import time
from PIL import Image
import io

# ==========================================
# ১. গ্লোবাল মেটা, ব্রান্ডিং ও থিমিং (Developed by REYADH)
# ==========================================
st.set_page_config(page_title="Vivid Core ULTRA Command Center", page_icon="⚡", layout="wide")

# সাইবারপাঙ্ক প্রিমিয়াম ডার্ক ইউআই থিম
st.markdown("""
<style>
    .reportview-container { background: #0b0e14; }
    .chat-bubble-user { background-color: #005c4b; color: #d9fdd3; padding: 12px; border-radius: 12px; margin: 8px 0; text-align: right; max-width: 75%; margin-left: auto; box-shadow: 1px 1px 5px rgba(0,0,0,0.2); }
    .chat-bubble-other { background-color: #202c33; color: #e9edef; padding: 12px; border-radius: 12px; margin: 8px 0; text-align: left; max-width: 75%; box-shadow: 1px 1px 5px rgba(0,0,0,0.2); }
    .global-chat-bubble { background-color: #1f2c34; border-left: 5px solid #00a884; padding: 10px; border-radius: 4px; margin: 5px 0; }
    .active-dot { height: 12px; width: 12px; background-color: #00e676; border-radius: 50%; display: inline-block; margin-right: 8px; }
    .profile-card { background: #1a1f2c; padding: 15px; border-radius: 12px; border: 1px solid #2d3748; text-align: center; margin-bottom: 15px; }
    .badge-officer { background-color: #e53e3e; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; }
    .badge-verified { background-color: #3182ce; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; }
    .notice-box { background: linear-gradient(135deg, #1e1b4b, #311042); border-left: 6px solid #d946ef; padding: 20px; border-radius: 10px; color: #f3e8ff; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

DB_FILE = "vivid_studio_max_v5.db"

# ==========================================
# ২. ডাইনামিক ডেটাবেস ইঞ্জিন আর্কিটেকচার
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # অর্ডার টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, client_name TEXT, client_number TEXT,
        service_name TEXT, total_price REAL, advance_paid REAL, due_amount REAL,
        editor_name TEXT, editor_cost REAL, operation_cost REAL, month_tag TEXT)''')
    
    # অ্যাডভান্সড ইউজার প্রোফাইল টেবিল (সেকশন বাদ, হোয়াটসঅ্যাপ, বায়ো, ছবি, স্কিল এবং ভেরিফাইড অফিসার লক যুক্ত)
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, password TEXT, fullname TEXT, role TEXT, 
        whatsapp TEXT, bio TEXT, skills TEXT, is_officer_verified INTEGER, profile_pic BLOB)''')
    
    # টাস্ক টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY, client TEXT, editor TEXT, task_detail TEXT, 
        assign_time TEXT, start_time TEXT, submit_time TEXT,
        status TEXT, final_link TEXT, revision_note TEXT, editor_payment REAL)''')
    
    # গ্লোবাল নোটিশ বোর্ড টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, role_tag TEXT, title TEXT, content TEXT, timestamp TEXT)''')
    
    # টার্গেট গোল টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS goals (month_tag TEXT PRIMARY KEY, target_amount REAL)''')
    
    # ডিফল্ট অ্যাডমিন (চেয়ারম্যান) ও প্রোফাইল সেটআপ
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""INSERT INTO users VALUES (
            'admin', '123', 'Chairman Reyadh', 'Chairman', '01700000000', 
            'Founder & Chairman of Vivid Core.', 'Management & Development', 1, NULL)""")
        cursor.execute("""INSERT INTO users VALUES (
            'manager_main', '456', 'Alamin Islam', 'Manager', '01800000000', 
            'General Manager', 'Operations', 1, NULL)""")
        
    current_month = datetime.now().strftime("%Y-%m")
    cursor.execute("INSERT OR IGNORE INTO goals VALUES (?, 150000)", (current_month,))
    
    conn.commit()
    conn.close()

init_db()

# ==========================================
# ৩. ইন-মেমোরি লাইভ স্টেট ও নোটিফিকেশন ইঞ্জিন
# ==========================================
if "global_chats" not in st.session_state:
    st.session_state.global_chats = [] # ফরম্যাট: {"sender":x, "receiver":y, "msg":z, "time":t, "type": "public"/"private"}
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

# ==========================================
# ৪. ডেটাবেস ডাটা লোডার্স
# ==========================================
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

# ==========================================
# ৫. সেশন ও লগইন সিকিউরিটি ভেরিফিকেশন
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = ""
if "current_navigation" not in st.session_state:
    st.session_state.current_navigation = "📊 লাইভ ড্যাশবোর্ড"

# লাইভ অ্যালার্ট টপ পপআপ
if st.session_state.logged_in and st.session_state.notifications:
    latest_notif = st.session_state.notifications[-1]
    with st.container():
        col_n1, col_n2 = st.columns([5, 1])
        col_n1.warning(f"🔔 **লাইভ নোটিফিকেশন:** {latest_notif['text']} ({latest_notif['time']})")
        if col_n2.button("ভিউ করুন ⚡", key="redirect_btn"):
            st.session_state.current_navigation = latest_notif['target']
            st.session_state.notifications.pop()
            st.rerun()

# --- লগইন স্ক্রিন ---
if not st.session_state.logged_in:
    st.title("⚡ Vivid Core Ultimate Command Center V5")
    st.markdown("### System Developed & Maintained by **REYADH**")
    
    u_id = st.text_input("ইউজার আইডি (Username)")
    u_pass = st.text_input("পাসওয়ার্ড", type="password")
    
    if st.button("সার্ভারে কানেক্ট করুন 🔐", use_container_width=True):
        if u_id in USER_DB and USER_DB[u_id]["password"] == u_pass:
            st.session_state.logged_in = True
            st.session_state.user = u_id
            update_activity(u_id)
            st.success("সফলভাবে লগইন হয়েছে!")
            st.rerun()
        else:
            st.error("ভুল ইউজার আইডি অথবা পাসওয়ার্ড!")
else:
    current_user = st.session_state.user
    my_meta = USER_DB[current_user]
    user_role = my_meta["role"]
    is_verified_officer = my_meta["is_verified"] or (user_role in ["Chairman", "Admin"])
    
    update_activity(current_user)
    
    # ==========================================
    # ৬. সাইডবার কন্ট্রোল সেন্টার ও লাইভ মেম্বার ট্র্যাকার
    # ==========================================
    st.sidebar.markdown("<h2 style='color:#00e676; text-align:center;'>VIVID CORE</h2>", unsafe_allow_html=True)
    
    # প্রোফাইল পিকচার রেন্ডারিং
    if my_meta["pic"]:
        st.sidebar.image(io.BytesIO(my_meta["pic"]), width=100)
    else:
        st.sidebar.markdown("👤 *No Profile Picture*")
        
    st.sidebar.write(f"👤 **{my_meta['fullname']}**")
    st.sidebar.write(f"🎖️ পদবি: `{user_role}`")
    
    if is_verified_officer:
        st.sidebar.markdown("<span class='badge-verified'>🔒 VERIFIED OFFICER LOCK</span>", unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("🟢 **রিয়েল-টাইম লাইভ অনলাইন মেম্বারস**")
    
    for user, last_seen in list(st.session_state.active_users.items()):
        if time.time() - last_seen < 300: # ৫ মিনিটের মধ্যে একটিভ থাকলে
            meta = USER_DB.get(user, {"fullname": user, "role": "User", "pic": None})
            col_s1, col_s2 = st.sidebar.columns([1, 4])
            if meta["pic"]:
                col_s1.image(io.BytesIO(meta["pic"]), width=25)
            else:
                col_s1.write("👤")
            col_s2.markdown(f"<span class='active-dot'></span> {meta['fullname']} \n\n <small>`{meta['role']}`</small>", unsafe_allow_html=True)

    if st.sidebar.button("লগআউট করুন 🚪", use_container_width=True):
        st.session_state.active_users.pop(current_user, None)
        st.session_state.logged_in = False
        st.rerun()

    # ডাইনামিক ফিচার নেভিগেশন (রোল ও সিকিউরিটি বেসড)
    menu_options = ["📊 লাইভ ড্যাশবোর্ড", "👥 এমপ্লয়ি ডিরেক্টরি হাব", "💬 লাইভ চ্যাট রুম"]
    
    if user_role == "Editor":
        menu_options.append("🎬 আমার এডিটিং প্যানেল")
    
    if user_role in ["Chairman", "Admin", "Manager"]:
        menu_options.append("✍️ নতুন অর্ডার এন্ট্রি")
        menu_options.append("🎯 টাস্ক ডিস্ট্রিবিউটর")
        
    if is_verified_officer: # পদবি যাই হোক, ভেরিফাইড অফিসার না হলে ফাইন্যান্স লক থাকবে
        menu_options.append("📉 লাইভ প্রফিট ও রিপোর্ট হাব")
        
    if user_role in ["Chairman", "Admin"]:
        menu_options.append("👮 অ্যাডমিন সিকিউরিটি ও ইউজার কন্ট্রোল")
        menu_options.append("🕵️ সিক্রেট ইনবক্স স্পাইডার (Spy)")

    selected_menu = st.sidebar.radio("সিস্টেম নেভিগেশন", menu_options, index=menu_options.index(st.session_state.current_navigation) if st.session_state.current_navigation in menu_options else 0)
    st.session_state.current_navigation = selected_menu
    
    current_month_tag = datetime.now().strftime("%Y-%m")
    
    # ডেটাবেস থেকে রিয়েল-টাইম ডেটা রিড
    conn = get_db_connection()
    df_orders = pd.read_sql_query("SELECT * FROM orders", conn)
    df_tasks = pd.read_sql_query("SELECT * FROM tasks", conn)
    df_notices = pd.read_sql_query("SELECT * FROM notices ORDER BY id DESC LIMIT 1", conn)
    conn.close()

    # ==========================================
    # ৭. গ্লোবাল লাইভ নোটিশ বোর্ড (ড্যাশবোর্ডের উপরে)
    # ==========================================
    if not df_notices.empty:
        notice = df_notices.iloc[0]
        st.markdown(f"""
        <div class='notice-box'>
            <h4>📢 অফিশিয়াল নোটিশ: {notice['title']}</h4>
            <p>{notice['content']}</p>
            <hr style='border-color:#d946ef;'>
            <small>📍 প্রকাশ করেছেন: <b>{notice['author']} ({notice['role_tag']})</b> | সময়: {notice['timestamp']}</small>
        </div>
        """, unsafe_allow_html=True)

    # ==========================================
    # ৮. মেইন লাইভ ড্যাশবোর্ড
    # ==========================================
    if st.session_state.current_navigation == "📊 লাইভ ড্যাশবোর্ড":
        st.title("📊 Vivid Core লাইভ কমান্ড সেন্টার")
        
        # অটো কাউন্টার গ্রিড (চেয়ারম্যান থেকে ইন্টার্নি সবাই দেখতে পারবে ছবিতে)
        st.subheader("👥 আমাদের বর্তমান টিম মেম্বার ডাইনামিক কাউন্টার")
        
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
        
        # প্রগ্রেস বার ট্র্যাকিং
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT target_amount FROM goals WHERE month_tag = ?", (current_month_tag,))
        g_res = cursor.fetchone()
        conn.close()
        live_target = g_res[0] if g_res else 150000.0
        
        if df_orders.empty:
            st.info("চলতি মাসে এখনো কোনো অর্ডার এন্ট্রি করা হয়নি।")
        else:
            current_month_sales = df_orders[df_orders["month_tag"] == current_month_tag]["total_price"].sum()
            progress_pct = min(current_month_sales / live_target, 1.0) if live_target > 0 else 0.0
            
            st.subheader("🎯 এই মাসের সেলস টার্গেট প্রগ্রেস")
            col_p1, col_p2 = st.columns([3, 1])
            with col_p1:
                st.write(f"চলতি মাসের সেলস: **{current_month_sales:,.0f} BDT** / লক্ষ্যমাত্রা: **{live_target:,.0f} BDT**")
                st.progress(progress_pct)
            with col_p2:
                st.markdown(f"### 🚀 {progress_pct*100:.1f}% অর্জিত")

    # ==========================================
    # ৯. এমপ্লয়ি ডিরেক্টরি হাব (ছবি, হোয়াটসঅ্যাপ, বায়ো এবং স্কিল সহ)
    # ==========================================
    elif st.session_state.current_navigation == "👥 এমপ্লয়ি ডিরেক্টরি হাব":
        st.title("👥 এজেন্সির অফিশিয়াল মেম্বার ডিরেক্টরি")
        st.write("মালিক, অফিসার থেকে শুরু করে ইন্টার্নি—সবার লাইভ বায়ো-ডাটা প্রোফাইল কার্ড")
        
        conn = get_db_connection()
        df_dir = pd.read_sql_query("SELECT fullname, role, whatsapp, bio, skills, is_officer_verified, profile_pic FROM users", conn)
        conn.close()
        
        # গ্রিড আকারে সাজানো ৩টি কলামে
        dir_cols = st.columns(3)
        for idx, row in df_dir.iterrows():
            col_target = dir_cols[idx % 3]
            with col_target:
                st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
                if row["profile_pic"]:
                    st.image(io.BytesIO(row["profile_pic"]), width=120)
                else:
                    st.markdown("<h3>👤</h3>", unsafe_allow_html=True)
                
                st.markdown(f"<h4>{row['fullname']}</h4>", unsafe_allow_html=True)
                st.markdown(f"🧬 পদবি: **{row['role']}**", unsafe_allow_html=True)
                
                # অফিসার ভেরিফিকেশন ও স্পেশাল ব্যাজ শো
                if row['is_officer_verified'] or row['role'] in ['Chairman', 'Admin']:
                    st.markdown("<span class='badge-officer'>🔒 Verified Officer</span>", unsafe_allow_html=True)
                
                st.write(f"💬 WhatsApp: [{row['whatsapp']}](https://wa.me/{row['whatsapp']})")
                st.write(f"📝 Bio: *{row['bio']}*")
                st.write(f"⚡ Skills/Expertise: `{row['skills']}`")
                st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # ১০. টু-ওয়ে লাইভ চ্যাট রুম (পাবলিক এবং প্রাইভেট)
    # ==========================================
    elif st.session_state.current_navigation == "💬 লাইভ চ্যাট রুম":
        st.title("💬 Vivid Live প্রিমিয়াম চ্যাট হাব")
        
        chat_mode = st.radio("চ্যাট মুড সিলেক্ট করুন:", ["Global Public Wall (সবার জন্য)", "Private 1:1 DM (ব্যক্তিগত ইনবক্স)"])
        
        if chat_mode == "Global Public Wall (সবার জন্য)":
            st.subheader("🌐 গ্লোবাল চ্যাট ওয়াল")
            st.markdown("<div style='background-color: #0b141a; padding: 20px; border-radius: 12px; height: 300px; overflow-y: scroll;'>", unsafe_allow_html=True)
            for chat in st.session_state.global_chats:
                if chat["type"] == "public":
                    st.markdown(f"<div class='global-chat-bubble'><b>{chat['sender_name']} ({chat['sender_role']}):</b> {chat['msg']} <br><small style='font-size:9px;color:#8696a0;'>{chat['time']}</small></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            with st.form("pub_form", clear_on_submit=True):
                msg_txt = st.text_input("পাবলিক মেসেজ লিখুন...")
                if st.form_submit_button("সেন্ড করুন ✈️"):
                    if msg_txt:
                        st.session_state.global_chats.append({
                            "sender": current_user, "sender_name": my_meta["fullname"], "sender_role": user_role,
                            "receiver": "all", "msg": msg_txt, "time": datetime.now().strftime("%I:%M %p"), "type": "public"
                        })
                        st.rerun()
                        
        else:
            st.subheader("🔒 সিকিউরড প্রাইভেট ইনবক্স")
            all_peers = list(USER_DB.keys())
            if current_user in all_peers:
                all_peers.remove(current_user)
                
            selected_peer = st.selectbox("👤 কার সাথে সিক্রেট চ্যাট করবেন?", all_peers, format_func=lambda x: f"{USER_DB[x]['fullname']} ({USER_DB[x]['role']})")
            
            st.markdown("<div style='background-color: #0b141a; padding: 20px; border-radius: 12px; height: 300px; overflow-y: scroll;'>", unsafe_allow_html=True)
            for chat in st.session_state.global_chats:
                if chat["type"] == "private":
                    if chat["sender"] == current_user and chat["receiver"] == selected_peer:
                        st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {chat['msg']}<br><small style='font-size:9px;color:#aebac1;'>{chat['time']}</small></div>", unsafe_allow_html=True)
                    elif chat["sender"] == selected_peer and chat["receiver"] == current_user:
                        st.markdown(f"<div class='chat-bubble-other'><b>{USER_DB[selected_peer]['fullname']}:</b> {chat['msg']}<br><small style='font-size:9px;color:#8696a0;'>{chat['time']}</small></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            with st.form("priv_form", clear_on_submit=True):
                msg_p_txt = st.text_input("ইনবক্স মেসেজ লিখুন...")
                if st.form_submit_button("প্রাইভেট সেন্ড 🔐"):
                    if msg_p_txt:
                        st.session_state.global_chats.append({
                            "sender": current_user, "receiver": selected_peer, "msg": msg_p_txt, "time": datetime.now().strftime("%I:%M %p"), "type": "private"
                        })
                        trigger_live_notification(f"💬 {my_meta['fullname']} আপনাকে একটি পার্সোনাল মেসেজ পাঠিয়েছেন!", "💬 লাইভ চ্যাট রুম")
                        st.rerun()

    # ==========================================
    # ১১. নতুন অর্ডার এন্ট্রি
    # ==========================================
    elif st.session_state.current_navigation == "✍️ নতুন অর্ডার এন্ট্রি":
        st.title("📝 নতুন ক্লায়েন্ট ডাটা ও অর্ডার এন্ট্রি")
        
        editor_list = [u for u in USER_DB if USER_DB[u]["role"] == "Editor"]
        
        with st.form("order_form_v5", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                cl_name = st.text_input("ক্লায়েন্টের নাম *")
                cl_phone = st.text_input("হোয়াটসঅ্যাপ/মোবাইল নাম্বার *")
                srv = st.text_input("সার্ভিস/প্যাকেজ নাম *")
            with col2:
                t_p = st.number_input("টোটাল ডিল প্রাইস (BDT) *", min_value=0)
                a_p = st.number_input("এডভান্স রিসিভড (BDT)", min_value=0)
                ed_n = st.selectbox("দায়িত্বরত এডিটর সিলেক্ট করুন *", editor_list if editor_list else ["No Editor Found"])
                ed_c = st.number_input("এডিটরের ফিক্সড বিল/কস্ট (BDT) *", min_value=0)
                op_c = st.number_input("অন্যান্য অপারেশন কস্ট (BDT)", min_value=0)
                
            if st.form_submit_button("সার্ভারে লাইভ এন্ট্রি দিন 🚀"):
                if cl_name and cl_phone and ed_n != "No Editor Found":
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('''INSERT INTO orders VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                   (datetime.now().strftime("%Y-%m-%d"), cl_name, cl_phone, srv, t_p, a_p, t_p-a_p, ed_n, ed_c, op_c, current_month_tag))
                    conn.commit()
                    conn.close()
                    trigger_live_notification(f"✍️ নতুন অর্ডার এন্ট্রি: {cl_name} (এডিটর: {ed_n})", "📊 লাইভ ড্যাশবোর্ড")
                    st.success("🎉 অর্ডার ডাটা এবং এডিটর অ্যাসাইনমেন্ট সম্পূর্ণ লাইভ সেভ হয়েছে!")
                    st.rerun()

    # ==========================================
    # ১২. টাস্ক ডিস্ট্রিবিউটর
    # ==========================================
    elif st.session_state.current_navigation == "🎯 টাস্ক ডিস্ট্রিবিউটর":
        st.title("🎯 এডিটরদের কাজ অ্যাসাইনমেন্ট ও লাইভ পেমেন্ট ট্র্যাকার")
        editor_list = [u for u in USER_DB if USER_DB[u]["role"] == "Editor"]
        
        with st.form("task_dist_v5", clear_on_submit=True):
            cx1, cx2 = st.columns(2)
            with cx1:
                t_cl = st.text_input("ক্লায়েন্টের নাম")
                t_ed = st.selectbox("কোন এডিটরকে কাজ দেবেন?", editor_list if editor_list else ["No Editor"])
                t_dt = st.text_area("কাজের বিবরণ ও ইন্সট্রাকশন")
            with cx2:
                t_pay = st.number_input("এই কাজের জন্য এডিটর বিল (BDT)", min_value=0)
                
            if st.form_submit_button("📡 এডিটর প্যানেলে লাইভ পুশ দিন"):
                if t_cl and t_ed != "No Editor":
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    assign_timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                    cursor.execute('INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                   (random.randint(10000, 99999), t_cl, t_ed, t_dt, assign_timestamp, "Not Started Yet", "Not Submitted Yet", "Pending", "No Link", "No Revision Note", t_pay))
                    conn.commit()
                    conn.close()
                    trigger_live_notification(f"🎬 আপনার জন্য নতুন প্রজেক্ট পুশ করা হয়েছে!", "🎬 আমার এডিটিং প্যানেল")
                    st.success("🔥 কাজ সফলভাবে এডিটরের কাছে লাইভ পাঠিয়ে দেওয়া হয়েছে!")
                    st.rerun()

    # ==========================================
    # ১৩. এডিটর লাইভ ওয়ার্কস্টেশন Panel
    # ==========================================
    elif st.session_state.current_navigation == "🎬 আমার এডিটিং প্যানেল":
        st.title("🎬 Editor Live Workstation")
        my_tasks = df_tasks[df_tasks["editor"] == current_user]
        
        if my_tasks.empty:
            st.info("আপনার কাছে এই মুহূর্তে কোনো কাজ অ্যাসাইন করা নেই।")
        else:
            for index, row in my_tasks.iterrows():
                with st.expander(f"📌 ক্লায়েন্ট: {row['client']} | 🚦 স্ট্যাটাস: {row['status']}"):
                    st.write(f"**📝 কাজের বিবরণ:** {row['task_detail']}")
                    st.write(f"⏱️ **কাজ শুরুর সময়:** {row['start_time']}")
                    st.error(f"🔧 **রিভিশন নোট:** {row['revision_note']}")
                    
                    col_b1, col_b2 = st.columns(2)
                    if row['status'] == "Pending":
                        if col_b1.button("🎬 কাজ শুরু করুন", key=f"strt_{index}"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute('UPDATE tasks SET status="Started", start_time=? WHERE id=?', (datetime.now().strftime("%I:%M %p"), row['id']))
                            conn.commit()
                            conn.close()
                            st.rerun()
                            
                    if row['status'] in ["Started", "Revision"]:
                        drive_link = st.text_input("ড্রাইভ লিংক দিন:", value=row['final_link'], key=f"lnk_{index}")
                        if col_b2.button("🚀 কাজ জমা দিন", key=f"sub_{index}"):
                            if drive_link and drive_link != "No Link":
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                cursor.execute('UPDATE tasks SET status="Submitted", final_link=?, submit_time=? WHERE id=?', (drive_link, datetime.now().strftime("%I:%M %p"), row['id']))
                                conn.commit()
                                conn.close()
                                trigger_live_notification(f"🟢 এডিটর কাজ জমা দিয়েছেন!", "🎯 টাস্ক ডিস্ট্রিবিউটর")
                                st.rerun()

    # ==========================================
    # ১৪. লাইভ প্রফিট ও রিপোর্ট হাব (🔒 শুধুমাত্র ভেরিফাইড অফিসার লক যাদের ট্রু)
    # ==========================================
    elif st.session_state.current_navigation == "📉 লাইভ প্রফিট ও রিপোর্ট হাব":
        st.title("📉 ইন-ап লাইভ ফাইন্যান্সিয়াল ও নেট প্রফিট রিপোর্ট")
        
        if df_orders.empty:
            st.info("কোনো ফাইন্যান্সিয়াল ডেটা উপলব্ধ নেই।")
        else:
            df_orders["net_profit"] = df_orders["total_price"] - (df_orders["editor_cost"] + df_orders["operation_cost"])
            month_list = sorted(df_orders["month_tag"].unique(), reverse=True)
            selected_month = st.selectbox("📅 মাস সিলেক্ট করুন:", month_list)
            
            filtered_df = df_orders[df_orders["month_tag"] == selected_month]
            
            c_s1, c_s2, c_s3 = st.columns(3)
            c_s1.metric("ঐ মাসের মোট সেলস", f"{filtered_df['total_price'].sum():,.0f} BDT")
            c_s2.metric("ঐ মাসের নীট প্রফিট", f"{filtered_df['net_profit'].sum():,.0f} BDT")
            c_s3.metric("ঐ মাসের মোট খরচ", f"{(filtered_df['editor_cost'].sum() + filtered_df['operation_cost'].sum()):,.0f} BDT")
            
            st.dataframe(filtered_df, use_container_width=True)

    # ==========================================
    # ১৫. অ্যাডমিন সিকিউরিটি, ইউজার কন্ট্রোল ও নোটিশ জেনারেটর (Admin/Chairman Only)
    # ==========================================
    elif st.session_state.current_navigation == "👮 অ্যাডমিন সিকিউরিটি ও ইউজার কন্ট্রোল":
        st.title("👮 সিস্টেম সিকিউরিটি, মেম্বার ভেরিফিকেশন ও ক্রিয়েশন প্যানেল")
        
        # নোটিশ বোর্ড কন্ট্রোলার
        st.subheader("📢 গ্লোবাল নোটিশ বোর্ড আপডেট করুন")
        with st.form("notice_form", clear_on_submit=True):
            n_title = st.text_input("নোটিশের টাইটেল")
            n_content = st.text_area("নোটিশের মূল বক্তব্য")
            if st.form_submit_button("লাউডস্পিকারে অ্যানাউন্স করুন 🚀"):
                if n_title and n_content:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO notices VALUES (NULL, ?, ?, ?, ?, ?)",
                                   (my_meta["fullname"], user_role, n_title, n_content, datetime.now().strftime("%Y-%m-%d %I:%M %p")))
                    conn.commit()
                    conn.close()
                    st.success("নোটিশ লাইভ পুশ করা হয়েছে!")
                    st.rerun()
                    
        st.markdown("---")
        
        # ম্যানুয়াল 'অফিসার ভেরিফিকেশন লক' মডিউল
        st.subheader("🔒 অফিসার ফাইন্যান্সিয়াল এক্সেস কন্ট্রোল (Manual Verification)")
        conn = get_db_connection()
        df_users_manage = pd.read_sql_query("SELECT username, fullname, role, is_officer_verified FROM users", conn)
        conn.close()
        
        for idx, u_row in df_users_manage.iterrows():
            col_v1, col_v2 = st.columns([4, 2])
            status_text = "✅ Approved Verified Officer" if u_row["is_officer_verified"] else "❌ No Financial Access"
            col_v1.write(f"👤 **{u_row['fullname']}** (`{u_row['username']}`) — পদবি: `{u_row['role']}` | বর্তমান অবস্থা: **{status_text}**")
            
            if u_row["is_officer_verified"]:
                if col_v2.button("লক করুন (Revoke Access)", key=f"rev_{idx}"):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET is_officer_verified=0 WHERE username=?", (u_row["username"],))
                    conn.commit()
                    conn.close()
                    st.rerun()
            else:
                if col_v2.button("ভেরিফাই করুন (Grant Access)", key=f"grant_{idx}"):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET is_officer_verified=1 WHERE username=?", (u_row["username"],))
                    conn.commit()
                    conn.close()
                    st.rerun()
                    
        st.markdown("---")
        
        # অ্যাডভান্সড ইউজার অ্যাকাউন্ট জেনারেটর
        st.subheader("➕ নতুন মেম্বার ও প্রোফাইল বায়ো-ডাটা তৈরি করুন")
        with st.form("cre_user_v5_form", clear_on_submit=True):
            cx_1, cx_2 = st.columns(2)
            with cx_1:
                n_u = st.text_input("ইউজার আইডি (Unique Username) *")
                n_p = st.text_input("পাসওয়ার্ড *")
                n_f = st.text_input("এমপ্লয়ির পুরো নাম (Full Name) *")
                n_r = st.selectbox("অফিশিয়াল পদবি/রোল *", ['Chairman', 'CEO', 'CTO', 'Co-Founder', 'Operation Officer', 'Manager', 'Moderator', 'Editor', 'Internee'])
            with cx_2:
                n_w = st.text_input("হোয়াটসঅ্যাপ নাম্বার (Country Code সহ) *")
                n_b = st.text_area("বায়ো/পরিচিতি")
                n_sk = st.text_input("কাজের স্পেশালিটি/স্কিল (যেমন: Premiere Pro, 3D, Motion)")
                n_pic = st.file_uploader("প্রোফাইল পিকচার আপলোড (.jpg/.png)", type=["jpg", "png"])
                
            if st.form_submit_button("সার্ভারে মেম্বার একটিভ করুন 🚀"):
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
                        st.success(f"🎉 {n_f} এর অ্যাকাউন্ট সফলভাবে প্রোফাইলসহ লাইভ ডাটাবেসে সেভ হয়েছে!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"ইউজার তৈরি করা যায়নি! হয়তো এই আইডি আগেই আছে। এরর: {e}")

    # ==========================================
    # ১৬. সিক্রেট ইনবক্স স্পাইডার (🕵️ Admin/Chairman Only - Spy Tool)
    # ==========================================
    elif st.session_state.current_navigation == "🕵️ সিক্রেট ইনবক্স স্পাইডার (Spy)":
        st.title("🕵️ সিক্রেট ইনবক্স মনিটরিং ড্যাশবোর্ড (Super Admin Only)")
        st.warning("🔒 এই প্যানেলটি শুধুমাত্র চেয়ারম্যান ও মেইন অ্যাডমিন ছাড়া কেউ দেখতে পারছে না। এর মাধ্যমে ভেতরের ইন্টারনাল চ্যাট মনিটর করা যায়।")
        
        all_user_keys = list(USER_DB.keys())
        
        col_spy1, col_spy2 = st.columns(2)
        spy_target_1 = col_spy1.selectbox("প্রথম মেম্বার সিলেক্ট করুন:", all_user_keys, key="spy1", format_func=lambda x: f"{USER_DB[x]['fullname']} ({USER_DB[x]['role']})")
        spy_target_2 = col_spy2.selectbox("দ্বিতীয় মেম্বার সিলেক্ট করুন:", all_user_keys, key="spy2", format_func=lambda x: f"{USER_DB[x]['fullname']} ({USER_DB[x]['role']})")
        
        st.markdown(f"#### 🔍 `{USER_DB[spy_target_1]['fullname']}` এবং `{USER_DB[spy_target_2]['fullname']}` এর মধ্যকার গোপন ইনবক্স হিস্ট্রি:")
        
        st.markdown("<div style='background-color: #1a0f0f; padding: 20px; border-radius: 12px; border: 1px solid #e53e3e; height: 350px; overflow-y: scroll;'>", unsafe_allow_html=True)
        found_chats = False
        for chat in st.session_state.global_chats:
            if chat["type"] == "private":
                if (chat["sender"] == spy_target_1 and chat["receiver"] == spy_target_2) or (chat["sender"] == spy_target_2 and chat["receiver"] == spy_target_1):
                    found_chats = True
                    sender_label = USER_DB[chat["sender"]]["fullname"]
                    st.markdown(f"<div style='color: #f7fafc; padding: 5px 0;'><b>{sender_label}:</b> {chat['msg']} <span style='color:#a0aec0; font-size:10px;'>[{chat['time']}]</span></div>", unsafe_allow_html=True)
        
        if not found_chats:
            st.info("এই দুই মেম্বারের মধ্যে এখনো কোনো গোপন চ্যাট সংঘটিত হয়নি।")
        st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # ১৭. ফুটার ব্র্যান্ডিং (Developed by REYADH)
    # ==========================================
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #718096;'>⚡ System Developed & Maintained by <b style='color:#00e676;'>REYADH</b> | Vivid Core Command Center v5.0 (2026) ⚡</p>", unsafe_allow_html=True)
