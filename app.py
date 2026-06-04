import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sqlite3
import time
import io

# ==========================================
# ১. গ্লোবাল মেটা, ব্রান্ডিং ও আইটি এজেন্সি আল্ট্রা থিম
# ==========================================
st.set_page_config(page_title="Vivid Core ULTRA Command Center", page_icon="⚡", layout="wide")

# লাইভ সেশন ও ইনস্ট্যান্ট চ্যাট মেকানিজম স্টেট
if "last_heartbeat" not in st.session_state:
    st.session_state.last_heartbeat = time.time()
if "global_chats" not in st.session_state:
    st.session_state.global_chats = []
if "notifications" not in st.session_state:
    st.session_state.notifications = []
if "active_users" not in st.session_state:
    st.session_state.active_users = {}

# CSS ফিক্স: Blur ইফেক্ট শুধু কার্ডের ব্যাকগ্রাউন্ডে থাকবে, ইমেজে কোনো ব্লার বা স্ট্রেচ পড়বে না
st.markdown("""
<style>
    body { background-color: #0a0f1d; color: #e2e8f0; }
    .stApp { background: linear-gradient(145deg, #070a14, #0f172a); }
    
    /* গ্লাস-মরফিজম কার্ড (ব্লার ফিল্টার শুধু ব্যাকগ্রাউন্ড এলিমেন্টে সীমাবদ্ধ) */
    .profile-card { 
        background: rgba(30, 41, 59, 0.7); 
        padding: 20px; 
        border-radius: 16px; 
        border: 1px solid rgba(56, 189, 248, 0.2); 
        text-align: center; 
        margin-bottom: 20px; 
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4); 
        backdrop-filter: blur(12px) !important; 
    }
    
    /* প্রোফাইল পিকচার ফিক্স: ব্লার মুক্ত এবং অরিজিনাল অ্যাস্পেক্ট রেশিও */
    .profile-card img, .stSidebar img, .current-profile-img img {
        border-radius: 12px !important;
        object-fit: cover !important;
        border: 2px solid #00f2fe !important;
        filter: none !important; /* কোনো ব্লার বা ফিল্টার ইমেজের ওপর কাজ করবে না */
        backdrop-filter: none !important;
    }
    
    /* কাউন্টার উইজেট স্টাইল */
    .counter-box { text-align: center; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; }
    .counter-title { font-size: 12px; color: #94a3b8; font-weight: 500; }
    .counter-value { font-size: 22px; color: #ffffff; font-weight: bold; margin-top: 5px; }
    
    /* চ্যাট বাবল থিম */
    .chat-bubble-user { background: linear-gradient(135deg, #00b4db, #0083b0); color: #ffffff; padding: 12px; border-radius: 16px 16px 4px 16px; margin: 8px 0; text-align: right; max-width: 75%; margin-left: auto; }
    .chat-bubble-other { background-color: #1e293b; color: #f1f5f9; padding: 12px; border-radius: 16px 16px 16px 4px; margin: 8px 0; text-align: left; max-width: 75%; border: 1px solid rgba(255,255,255,0.05); }
    .global-chat-bubble { background-color: #0f172a; border-left: 5px solid #38bdf8; padding: 10px; border-radius: 6px; margin: 5px 0; }
    
    /* ব্যাজ ও নোচ্ছেদ */
    .active-dot { height: 10px; width: 10px; background-color: #00e676; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: 0 0 8px #00e676; }
    .badge-officer { background: linear-gradient(90deg, #f43f5e, #e11d48); color: white; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .badge-verified { background: linear-gradient(90deg, #3b82f6, #1d4ed8); color: white; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

DB_FILE = "vivid_studio_max_v6.db"
DEFAULT_AVATAR_URL = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=200&auto=format&fit=crop&q=80"

# ==========================================
# ২. ডেটাবেস আর্কিটেকচার ও মাস্টার কনফিগারেশন
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
        id INTEGER PRIMARY KEY AUTOINCREMENT, client TEXT, editor TEXT, task_detail TEXT, 
        assign_time TEXT, start_time TEXT, submit_time TEXT,
        status TEXT, final_link TEXT, revision_note TEXT, editor_payment REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS goals (month_tag TEXT PRIMARY KEY, target_amount REAL)''')
    
    # INSERT OR IGNORE ব্যবহারের ফলে অলরেডি reyadh আইডি থাকলে তার এক্সিসটিং ডেটা ডিলিট বা ওভাররাইট হবে না
    cursor.execute("SELECT COUNT(*) FROM users WHERE username='reyadh'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""INSERT OR IGNORE INTO users VALUES (
            'reyadh', 'cto123', 'Reyadh (CTO)', 'CTO', '01825221830', 
            'CTO & Production Shareholder (49%) | System Architect, Tech Lead, and Business Partner. Orchestrating advanced production pipelines, server security, and automation infrastructure while co-steering the agency''s core growth engines.', 
            'CTO & Tech Lead | System Architecture, Advanced Automation, Full-Stack Dev, S', 1, NULL)""")
        
    current_month = datetime.now().strftime("%Y-%m")
    cursor.execute("INSERT OR IGNORE INTO goals VALUES (?, 150000)", (current_month,))
    conn.commit()
    conn.close()

init_db()

def update_activity(username):
    st.session_state.active_users[username] = time.time()

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
    
    is_verified_officer = my_meta["is_verified"] or (user_role in ["CTO", "Chairman", "Admin"])
    update_activity(current_user)
    
    # ==========================================
    # ৩. সাইডবার ব্র্যান্ডিং ও মডিউল সিলেকশন
    # ==========================================
    if my_meta["pic"]:
        st.sidebar.image(io.BytesIO(my_meta["pic"]), width=110, output_format='PNG')
    else:
        st.sidebar.image(DEFAULT_AVATAR_URL, width=110)
        
    st.sidebar.write(f"🖥️ **{my_meta['fullname']}**")
    st.sidebar.write(f"🧬 ডেজিগনেশন: `{user_role}`")
    
    if is_verified_officer:
        st.sidebar.markdown("<span class='badge-verified'>⚙️ SECURE OFFICER ENABLED</span>", unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("🌌 **অনলাইন নেটওয়ার্ক নোডস**")
    
    for user, last_seen in list(st.session_state.active_users.items()):
        if time.time() - last_seen < 300:
            meta = USER_DB.get(user, {"fullname": user, "role": "User"})
            st.sidebar.markdown(f"<span class='active-dot'></span> {meta['fullname']} <small style='color:#38bdf8;'>`{meta['role']}`</small>", unsafe_allow_html=True)

    if st.sidebar.button("সার্ভার ডিসকানেক্ট 🚪", use_container_width=True):
        st.session_state.active_users.pop(current_user, None)
        st.session_state.logged_in = False
        st.rerun()

    # মডিউল লিস্ট
    menu_options = [
        "📊 লাইভ ড্যাশবোর্ড", 
        "👥 এমপ্লয়ি ডিরেক্টরি হাব", 
        "💬 লাইভ চ্যাট রুম", 
        "👤 আমার প্রোফাইল এডিট করুন"
    ]
    
    if user_role in ["CTO", "Chairman", "Admin", "Manager", "Moderator"]:
        menu_options.append("✍️ নতুন অর্ডার এন্ট্রি")
        menu_options.append("🎯 টাস্ক ডিস্ট্রিবিউটর")
        menu_options.append("⚡ মডারেটর লাইভ টাস্ক আপডেট")
        
    if is_verified_officer or user_role in ["Admin", "Manager"]:
        menu_options.append("📉 লাইভ প্রফিট ও রিপোর্ট হাব")
        menu_options.append("👮 অ্যাডমিন ও CTO কন্ট্রোল প্যানেল")
        menu_options.append("🕵️ সিক্রেট ইনবক্স স্পাইডার (Spy)")

    selected_menu = st.sidebar.radio("মডিউল সিলেকশন", menu_options, index=menu_options.index(st.session_state.current_navigation) if st.session_state.current_navigation in menu_options else 0, key="main_navigation_radio")
    st.session_state.current_navigation = selected_menu
    
    current_month_tag = datetime.now().strftime("%Y-%m")
    
    # ডেটা সিঙ্ক
    conn = get_db_connection()
    df_orders = pd.read_sql_query("SELECT * FROM orders", conn)
    df_tasks = pd.read_sql_query("SELECT * FROM tasks", conn)
    df_users_all = pd.read_sql_query("SELECT * FROM users", conn)
    df_goals = pd.read_sql_query("SELECT * FROM goals", conn)
    conn.close()

    # ==========================================
    # 📊 লাইভ ড্যাশবোর্ড
    # ==========================================
    if st.session_state.current_navigation == "📊 লাইভ ড্যাশবোর্ড":
        st.title("📊 Vivid Core আইটি অটোমেশন ড্যাশবোর্ড")
        
        st.subheader("👥 একটিভ টিম রিসোর্স কাউন্টার")
        roles_to_count = ["Chairman", "CEO", "CTO", "Co-Founder", "Operation Officer", "Manager", "Moderator", "Editor", "Internee"]
        c_cols = st.columns(len(roles_to_count))
        
        for idx, r_name in enumerate(roles_to_count):
            count_val = len(df_users_all[df_users_all["role"].str.lower() == r_name.lower()])
            with c_cols[idx]:
                st.markdown(f"""
                <div class='counter-box'>
                    <div class='counter-title'>{r_name}</div>
                    <div class='counter-value'>{count_val} জন</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        current_month_orders = df_orders[df_orders["month_tag"] == current_month_tag]
        if current_month_orders.empty:
            st.info("চলতি মাসের ডাটাবেস ফাঁকা।")
        else:
            st.dataframe(current_month_orders, use_container_width=True)

    # ==========================================
    # 👤 আমার প্রোফাইল এডিট করুন (আইডি কার্ড কন্ট্রোল - ক্লোন)
    # ==========================================
    elif st.session_state.current_navigation == "👤 আমার প্রোফাইল এডিট করুন":
        st.title("👤 মাই ড্যাশবোর্ড আইডি কার্ড কন্ট্রোল")
        st.markdown("##### আপনার মেম্বার ডিরেক্টরি প্রোফাইলটি এখান থেকে মডিফাই ও লাইভ আপডেট করতে পারেন।")
        
        with st.form("profile_control_form", clear_on_submit=False):
            col_p1, col_p2 = st.columns([2, 1])
            
            with col_p1:
                f_name = st.text_input("আপনার নাম (Full Name)", value=my_meta["fullname"])
                w_num = st.text_input("হোয়াটসঅ্যাপ নোড নাম্বার", value=my_meta["whatsapp"])
                b_info = st.text_area("আপনার প্রোফাইল বায়ো/পরিচিতি (Bio)", value=my_meta["bio"], height=140)
                
            with col_p2:
                s_box = st.text_input("টেকনিক্যাল এক্সপেরিয়েন্স ও স্কিলসেট", value=my_meta["skills"])
                st.markdown("<label>বর্তমান প্রোফাইল ছবি</label>", unsafe_allow_html=True)
                
                # ছবির ব্লার প্রবলেম ফিক্সড কন্টেইনার
                st.markdown("<div class='current-profile-img'>", unsafe_allow_html=True)
                if my_meta["pic"]:
                    st.image(io.BytesIO(my_meta["pic"]), width=140, output_format='PNG')
                else:
                    st.image(DEFAULT_AVATAR_URL, width=140)
                st.markdown("</div>", unsafe_allow_html=True)
                
                uploaded_pic = st.file_uploader("নতুন প্রোফাইল ছবি আপলোড (.jpg/.png)", type=["jpg", "png"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("ডাটাবেস কোড সিঙ্ক করুন 💾"):
                img_bytes = my_meta["pic"]
                if uploaded_pic is not None:
                    img_bytes = uploaded_pic.read()
                    
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""UPDATE users 
                               SET fullname=?, whatsapp=?, bio=?, skills=?, profile_pic=? 
                               WHERE username=?""", 
                               (f_name, w_num, b_info, s_box, img_bytes, current_user))
                conn.commit()
                conn.close()
                st.success("আপনার আইডি কার্ড প্রোফাইল সফলভাবে সিঙ্ক ও আপডেট হয়েছে!")
                st.rerun()

    # ==========================================
    # ✍️ নতুন অর্ডার এন্ট্রি
    # ==========================================
    elif st.session_state.current_navigation == "✍️ নতুন অর্ডার এন্ট্রি":
        st.title("✍️ নতুন ক্লায়েন্ট অর্ডার এন্ট্রি সিস্টেম")
        with st.form("order_entry_form_v4", clear_on_submit=True):
            col_o1, col_o2 = st.columns(2)
            c_name = col_o1.text_input("ক্লায়েন্টের নাম:")
            c_num = col_o1.text_input("মোবাইল/হোয়াটসঅ্যাপ নাম্বার:")
            s_name = col_o2.text_input("সার্ভিস/প্রজেক্টের নাম:")
            t_price = col_o2.number_input("মোট বাজেট (BDT):", min_value=0.0)
            
            col_o3, col_o4 = st.columns(2)
            adv_paid = col_o3.number_input("অগ্রিম পেমেন্ট (BDT):", min_value=0.0)
            ed_name = col_o3.text_input("অ্যাসাইনকৃত এডিটর/রিসোর্স নাম:")
            ed_cost = col_o4.number_input("রিসোর্স ফি/এডিটর খরচ (BDT):", min_value=0.0)
            op_cost = col_o4.number_input("অপারেশনাল কস্ট (BDT):", min_value=0.0)
            
            if st.form_submit_button("অর্ডার ডেটাবেসে সেভ করুন 💾"):
                due_calc = t_price - adv_paid
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""INSERT INTO orders (date, client_name, client_number, service_name, total_price, advance_paid, due_amount, editor_name, editor_cost, operation_cost, month_tag) 
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                               (datetime.now().strftime("%Y-%m-%d"), c_name, c_num, s_name, t_price, adv_paid, due_calc, ed_name, ed_cost, op_cost, current_month_tag))
                conn.commit()
                conn.close()
                st.success("অর্ডার সফলভাবে ১ ক্লিকে এন্ট্রি করা হয়েছে!")
                st.rerun()

    # ==========================================
    # 🎯 টাস্ক ডিস্ট্রিবিউটর
    # ==========================================
    elif st.session_state.current_navigation == "🎯 টাস্ক ডিস্ট্রিবিউটর":
        st.title("🎯 টিম টাস্ক ডিস্ট্রিবিউটর টার্মিনাল")
        with st.form("task_dist_form", clear_on_submit=True):
            t_client = st.text_input("ক্লায়েন্ট রেফারেন্স/কোড:")
            all_editors = df_users_all[df_users_all["role"].str.lower() == "editor"]["username"].tolist()
            t_editor = st.selectbox("টার্গেট কর্মী (Editor Selection):", all_editors if all_editors else ["No Editors Found"])
            t_detail = st.text_area("কাজের ডিটেইলস/ব্রিফিং:")
            t_payment = st.number_input("এই টাস্কের জন্য বাজেট/ফি:", min_value=0.0)
            
            if st.form_submit_button("টাস্ক ও অর্ডার ইস্যু করুন 🚀"):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""INSERT INTO tasks (client, editor, task_detail, assign_time, start_time, submit_time, status, final_link, revision_note, editor_payment)
                               VALUES (?, ?, ?, ?, '', '', 'Pending', '', '', ?)""", 
                               (t_client, t_editor, t_detail, datetime.now().strftime("%I:%M %p"), t_payment))
                conn.commit()
                conn.close()
                st.success("টাস্ক সফলভাবে ডিস্ট্রিবিউট করা হয়েছে!")
                st.rerun()

    # ==========================================
    # 💬 লাইভ চ্যাট রুম
    # ==========================================
    elif st.session_state.current_navigation == "💬 লাইভ চ্যাট রুম":
        st.title("💬 সেশন সিঙ্ক লাইভ চ্যাট হাব")
        st.markdown("<div style='background-color: #0b111e; padding: 20px; border-radius: 12px; height: 350px; overflow-y: scroll;'>", unsafe_allow_html=True)
        for chat in st.session_state.global_chats:
            if chat["type"] == "public":
                st.markdown(f"<div class='global-chat-bubble'><b>{chat['sender_name']} [{chat['sender_role']}]:</b> {chat['msg']} <small style='color:#64748b; float:right;'>{chat['time']}</small></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        msg_txt = st.text_input("মেсеজ স্ট্রীম ইনপুট...", key="chat_msg_input")
        if st.button("ব্রডকাস্ট ডাটা ✈️", key="send_btn_v4"):
            if msg_txt:
                st.session_state.global_chats.append({
                    "sender": current_user, "sender_name": my_meta["fullname"], "sender_role": user_role,
                    "receiver": "all", "msg": msg_txt, "time": datetime.now().strftime("%I:%M %p"), "type": "public"
                })
                st.rerun()

    # ==========================================
    # 🕵️ সিক্রেট ইনবক্স স্পাইডার (Spy মডিউল)
    # ==========================================
    elif st.session_state.current_navigation == "🕵️ সিক্রেট ইনবক্স স্পাইডার (Spy)":
        st.title("🕵️ সিক্রেট ইনবক্স স্পাইডার (Enterprise Spy Terminal)")
        if not st.session_state.global_chats:
            st.info("সার্ভার পাইপলাইনে এই মুহূর্তে কোনো মেসেজ লগ ট্র্যাকিং করা যায়নি।")
        else:
            st.write(st.session_state.global_chats)

    # ==========================================
    # 📉 লাইভ প্রফিট ও রিপোর্ট হাব
    # ==========================================
    elif st.session_state.current_navigation == "📉 লাইভ প্রফিট ও রিপোর্ট হাব":
        st.title("📉 ফিনান্সিয়াল লেজার ও মান্থলি গোল")
        if df_orders.empty:
            st.info("কোনো ফাইন্যান্সিয়াল ডেটা পাওয়া যায়নি।")
        else:
            df_orders["net_profit"] = df_orders["total_price"] - (df_orders["editor_cost"] + df_orders["operation_cost"])
            month_list = sorted(df_orders["month_tag"].unique(), reverse=True)
            selected_month = st.selectbox("📅 বিলিং সাইকেল সিলেক্ট করুন:", month_list)
            
            filtered_df = df_orders[df_orders["month_tag"] == selected_month]
            st.dataframe(filtered_df, use_container_width=True)

    # ==========================================
    # 👥 এমপ্লয়ি ডিরেক্টরি হাব
    # ==========================================
    elif st.session_state.current_navigation == "👥 এমপ্লয়ি ডিরেক্টরি হাব":
        st.title("👥 আইটি ট্যালেন্ট ও রিসোর্স ডিরেক্টরি")
        dir_cols = st.columns(3)
        for idx, row in df_users_all.iterrows():
            col_target = dir_cols[idx % 3]
            with col_target:
                st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
                st.markdown(f"<h3>{row['fullname']}</h3>", unsafe_allow_html=True)
                st.markdown(f"💻 রোল: <span style='color:#00f2fe;'><b>{row['role']}</b></span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # ফুটার ও লাইভ হার্টবিট লুপ
    # ==========================================
    st.markdown("---")
    st.caption(f"🟢 Core Server: Secure & Active | 🗄️ DB Node Connection: SQLite Verified ({DB_FILE}) | 🚀 Sync Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    time.sleep(1)
    st.rerun()
