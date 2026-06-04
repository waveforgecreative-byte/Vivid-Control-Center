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
    
    /* 🔐 আল্ট্রা প্রিমিয়াম সাইবার লগইন ইন্টারফেস */
    .login-wrapper {
        max-width: 480px;
        margin: 60px auto;
        padding: 40px;
        background: rgba(15, 23, 42, 0.65);
        border-radius: 24px;
        border: 1px solid rgba(56, 189, 248, 0.2);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 0 0 40px rgba(56, 189, 248, 0.05);
        backdrop-filter: blur(20px);
        text-align: center;
    }
    .login-header {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(90deg, #00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
        letter-spacing: 0.5px;
    }
    .login-subheader {
        font-size: 14px;
        color: #94a3b8;
        margin-bottom: 30px;
        font-weight: 400;
    }
    
    /* গ্লোবাল নোটিশ ব্যানার */
    .notice-board {
        background: linear-gradient(90deg, #7c2d12, #9a3412);
        color: #ffedd5;
        padding: 12px 20px;
        border-radius: 8px;
        border-left: 6px solid #f97316;
        margin-bottom: 25px;
        font-weight: 500;
        font-size: 15px;
    }
    
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
        status TEXT, final_link TEXT, revision_note TEXT, editor_payment REAL, target_type TEXT DEFAULT 'Editor')''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS goals (month_tag TEXT PRIMARY KEY, target_amount REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, sender_name TEXT, sender_role TEXT, msg TEXT, timestamp TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS system_notice (id INTEGER PRIMARY KEY, notice_text TEXT, updated_by TEXT, timestamp TEXT)''')
    
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN target_type TEXT DEFAULT 'Editor'")
    except sqlite3.OperationalError:
        pass

    # ডিফল্ট নোটিশ ইনিশিয়ালাইজেশন
    cursor.execute("SELECT COUNT(*) FROM system_notice WHERE id=1")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO system_notice (id, notice_text, updated_by, timestamp) VALUES (1, 'স্বাগতম Vivid Core এ! সার্ভার নোড সফলভাবে চালু হয়েছে।', 'System', '')")

    # CTO Reyadh Profile Lock Node
    cursor.execute("SELECT COUNT(*) FROM users WHERE username='reyadh'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""INSERT INTO users (username, password, fullname, role, whatsapp, bio, skills, is_officer_verified, last_seen) VALUES (
            'reyadh', 'cto123', 'Developed by Md Reyadh', 'CTO & Lead Developer', '01825221830', 
            'The Supreme Mind behind Vivid Core IT Ecosystem. System Architect, Lead Developer, and Ultimate Platform Owner.', 
            'System Architecture, Enterprise Automation, Core Backend Dev, Full-Stack Dev, Software Infrastructure, Database Optimization.', 1, '')""")
    
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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = ""
if "current_navigation" not in st.session_state:
    st.session_state.current_navigation = "📊 লাইভ ড্যাশবোর্ড"

# ==========================================
# ৩. ক্লোজড গেটওয়ে লগইন প্যানেল (নতুন বিউটিফাইড UI)
# ==========================================
if not st.session_state.logged_in:
    # সেন্ট্রাল রেন্ডারিং এর জন্য খালি কলাম আর্কিটেকচার
    _, center_col, _ = st.columns([1, 1.8, 1])
    
    with center_col:
        st.markdown("""
        <div class="login-wrapper">
            <div class="login-header">🌌 Vivid Core IT</div>
            <div class="login-subheader">ULTRA COMMAND CENTER • SECURE ACCESS NODE</div>
        </div>
        """, unsafe_allow_html=True)
        
        # ইনপুট প্যানেল ফর্ম
        with st.form("cyber_login_form", clear_on_submit=False):
            u_id = st.text_input("🔑 ইউজার আইডি (Username)", placeholder="Enter your system ID...")
            u_pass = st.text_input("🔒 এক্সেস কী (Password)", type="password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_login = st.form_submit_button("সার্ভার নোড এথেন্টিকেশন ⚡", use_container_width=True)
            
            if submit_login:
                conn = get_db_connection()
                user_data = pd.read_sql_query("SELECT * FROM users WHERE username=?", conn, params=(u_id.lower().strip(),))
                conn.close()
                
                if not user_data.empty and user_data.iloc[0]["password"] == u_pass:
                    st.session_state.logged_in = True
                    st.session_state.user = u_id.lower().strip()
                    update_user_heartbeat(u_id.lower().strip())
                    st.rerun()
                else:
                    st.error("❌ ভুল ইউজার আইডি বা পাসওয়ার্ড! নোড রিফিউজড।")

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
    live_notice = pd.read_sql_query("SELECT * FROM system_notice WHERE id=1", conn).iloc[0]
    conn.close()
    
    user_role = my_meta["role"]
    is_editor = user_role.lower() == "editor"
    is_moderator = user_role.lower() == "moderator"
    is_verified = int(my_meta["is_officer_verified"]) == 1
    
    # পাওয়ার ম্যাট্রিক্স
    has_notice_power = user_role in ["CEO", "CTO & Lead Developer", "Chairman"]
    has_admin_power = user_role in ["CEO", "CTO & Lead Developer", "Manager", "Chairman"]

    # 📢 গলোবাল লাইভ নোটিশ ব্রডকাস্টার
    st.markdown(f"<div class='notice-board'>📢 <b>লাইভ নোটিশ ({live_notice['updated_by']}):</b> {live_notice['notice_text']} <small style='float:right; opacity:0.7;'>{live_notice['timestamp']}</small></div>", unsafe_allow_html=True)

    # সাইডবার ইন্টারফেস ও প্রোফাইল নোড
    st.sidebar.markdown("### 🌌 Vivid Core Node")
    if my_meta["profile_pic"]:
        st.sidebar.image(io.BytesIO(my_meta["profile_pic"]), width=90)
    else:
        st.sidebar.image(DEFAULT_AVATAR, width=90)
        
    st.sidebar.write(f"🖥️ **{my_meta['fullname']}**")
    st.sidebar.write(f"🧬 রোল: `{user_role}`")
    if is_verified:
        st.sidebar.markdown("<span class='card-verified'>🛡️ VERIFIED OFFICER</span>", unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("🛰️ **অনলাইন ট্র্যাকার (৫ মি.)**")
    five_mins_ago = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    active_users = df_users_all[df_users_all["last_seen"] >= five_mins_ago]
    for _, u_row in active_users.iterrows():
        st.sidebar.markdown(f"<span class='active-dot'></span> **{u_row['fullname']}** (`{u_row['role']}`)", unsafe_allow_html=True)

    if st.sidebar.button("সার্ভার ডিসকানেক্ট 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    current_month_tag = datetime.now().strftime("%Y-%m")

    # 🔒 এডিটর ও মডারেটরদের লাইভ ব্যক্তিগত টাস্ক প্যানেল
    if is_editor or is_moderator:
        target_type_check = "Editor" if is_editor else "Moderator"
        st.title(f"🛠️ {user_role} ড্যাশবোর্ড ও লাইভ ওয়ার্ক প্যানেল")
        
        conn = get_db_connection()
        my_tasks = pd.read_sql_query("SELECT * FROM tasks WHERE editor=? AND target_type=? ORDER BY id DESC", conn, params=(current_user, target_type_check))
        conn.close()
        
        if my_tasks.empty:
            st.info("আপনার জন্য বর্তমানে কোনো সক্রিয় কাজ বরাদ্দ নেই।")
        else:
            for idx, t_row in my_tasks.iterrows():
                with st.expander(f"📌 টাস্ক আইডি: {t_row['id']} | রেফারেন্স: {t_row['client']} | অবস্থা: {t_row['status']}"):
                    st.markdown(f"💬 **কাজের বিবরণ:** {t_row['task_detail']}")
                    st.markdown(f"💰 **ফি/বাজেট:** {t_row['editor_payment']} BDT")
                    if t_row['revision_note']:
                        st.error(f"⚠️ **রিভিশন নোট:** {t_row['revision_note']}")
                    
                    with st.form(f"task_form_{t_row['id']}"):
                        new_status = st.selectbox("কাজের প্রগ্রেস:", ["Started", "Submitted"], index=0 if t_row['status']=="Pending" else 1)
                        delivery_link = st.text_input("ওয়ার্ক/ডেলিভারি লিংক:", value=t_row['final_link'])
                        
                        if st.form_submit_button("আপডেট সাবমিট করুন 🚀"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE tasks SET status=?, final_link=? WHERE id=?", (new_status, delivery_link, t_row['id']))
                            conn.commit()
                            conn.close()
                            st.success("টাস্ক প্রগ্রেস ডাটাবেসে লাইভ সেভ হয়েছে!")
                            st.rerun()

    # 🏢 সিইও, ওনার, ম্যানেজার এবং সাধারণ মেম্বারদের মূল আর্কিটেকচার
    else:
        if is_verified:
            menu_options = [
                "📊 লাইভ ড্যাশবোর্ড",
                "📉 লাইভ প্রফিট ও রিপোর্ট হাব",
                "👥 EMপ্লয়ি ডিরেক্টরি হাব",
                "💬 লাইভ চ্যাট রুম",
                "✍️ নতুন অর্ডার এন্ট্রি",
                "🎯 টাস্ক ডিস্ট্রিবিউটর",
                "⚡ মডারেটর লাইভ টাস্ক আদেশ",
                "👮 অ্যাডমিন ও CTO কন্ট্রোল প্যানেল",
                "🕵️ সিক্রেট ইনবক্স স্পাইডার (Spy)",
                "👤 আমার প্রোফাইল এডিট করুন"
            ]
        else:
            menu_options = [
                "💬 লাইভ চ্যাট রুম",
                "✍️ নতুন অর্ডার এন্ট্রি",
                "👤 আমার প্রোফাইল এডিট করুন"
            ]
            st.warning("🔒 আপনি বর্তমানে আন-ভেরিফাইড মোডে আছেন। আপনি শুধু ডাটা ইনপুট এবং লাইভ চ্যাট করতে পারবেন।")

        selected_menu = st.sidebar.radio("মডিউল সিলেকশন", menu_options, index=0)
        st.session_state.current_navigation = selected_menu

        if has_notice_power:
            with st.sidebar.expander("📢 লাইভ নোটিশ চেঞ্জার প্যানেল"):
                with st.form("notice_change_form"):
                    new_notice_text = st.text_area("নতুন গ্লোবাল নোটিশ লিখুন:")
                    if st.form_submit_button("লাইভ ব্রডকাস্ট করুন 📡"):
                        if new_notice_text:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE system_notice SET notice_text=?, updated_by=?, timestamp=? WHERE id=1",
                                           (new_notice_text, user_role, datetime.now().strftime("%I:%M %p")))
                            conn.commit()
                            conn.close()
                            st.success("নোটিশ সফলভাবে লাইভ পরিবর্তন করা হয়েছে!")
                            st.rerun()

        # 📊 ১. লাইভ ড্যাশবোর্ড
        if st.session_state.current_navigation == "📊 লাইভ ড্যাশবোর্ড" and is_verified:
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

        # 📉 ২. লাইভ প্রফিট ও রিপোর্ট হাব
        elif st.session_state.current_navigation == "📉 লাইভ প্রফিট ও রিপোর্ট হাব" and is_verified:
            st.title("📉 ফিনান্সিয়াল লেজার ও মান্থলি গোল")
            
            df_orders["net_profit"] = df_orders["total_price"] - (df_orders["editor_cost"] + df_orders["operation_cost"])
            total_net_profit = df_orders[df_orders["month_tag"] == current_month_tag]['net_profit'].sum()
            
            month_goal_row = df_goals[df_goals["month_tag"] == current_month_tag]
            target_amount = month_goal_row["target_amount"].values[0] if not month_goal_row.empty else 150000.0
            
            if total_net_profit >= target_amount:
                st.markdown(f"<div class='goal-success'><h3>🎉 মিশন সাকসেসফুল! টার্গেট এچیভড!</h3><p>চলতি মাসের নেট প্রফিট অর্জিত হয়েছে <b>{total_net_profit:,.0f} BDT</b>!</p></div>", unsafe_allow_html=True)
            else:
                shortage = target_amount - total_net_profit
                st.markdown(f"<div class='goal-failed'><h3>⚠️ অ্যালার্ট: টার্গেট ফেইলুর রিস্ক!</h3><p>চলতি মাসের নেট প্রফিট: <b>{total_net_profit:,.0f} BDT</b> | শর্টেজ/বাকি: <b>{shortage:,.0f} BDT</b></p></div>", unsafe_allow_html=True)
                
            st.dataframe(df_orders, use_container_width=True)

        # 👥 ৩. এমপ্লয়ি ডিরেক্টরি হাব
        elif st.session_state.current_navigation == "👥 EMপ্লয়ি ডিরেক্টরি হাব" and is_verified:
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
                    st.markdown("</div>", unsafe_allow_html=True)

        # 💬 ৪. লাইভ চ্যাট রুম
        elif st.session_state.current_navigation == "💬 লাইভ চ্যাট রুম":
            st.title("💬 লাইভ চ্যাট হাব (Messenger Mode)")
            conn = get_db_connection()
            df_chat_logs = pd.read_sql_query("SELECT * FROM chat_messages ORDER BY id ASC", conn)
            conn.close()
            st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
            for _, chat in df_chat_logs.iterrows():
                st.markdown(f"<div class='global-chat-bubble'><b>{chat['sender_name']} [{chat['sender_role']}]:</b> {chat['msg']}</div>", unsafe_allow_html=True)
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
                if st.form_submit_button("অर्डर সেভ করুন 💾"):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO orders (date, client_name, client_number, service_name, total_price, advance_paid, due_amount, editor_name, editor_cost, operation_cost, month_tag) VALUES (?,?,?,?,?,0,?, ?,?,?,?)",
                                   (datetime.now().strftime("%Y-%m-%d"), c_name, c_num, s_name, t_price, t_price, ed_name, ed_cost, op_cost, current_month_tag))
                    conn.commit()
                    conn.close()
                    st.success("অर्डरটি ডাটাবেসে সেভ হয়েছে!")

        # 🎯 ৬. টাস্ক ডিস্ট্রিবিউটর
        elif st.session_state.current_navigation == "🎯 টাস্ক ডিস্ট্রিবিউটর" and is_verified:
            st.title("🎯 টিম টাস্ক ডিস্ট্রিবিউটর টার্মিনাল")
            if not has_admin_power:
                st.error("🔒 দুঃখিত, এই পাওয়ার আপনার রোলের জন্য বরাদ্দ নয়।")
            else:
                tab1, tab2 = st.tabs(["🎬 এডিটর লাইভ টাস্ক বক্স", "⚡ মডারেটর লাইভ টাস্ক বক্স"])
                with tab1:
                    with st.form("editor_task_form", clear_on_submit=True):
                        e_client = st.text_input("ক্লায়েন্ট রেফারেন্স কোড:")
                        e_editor = st.text_input("টার্গেট এডিটর (Username):")
                        e_detail = st.text_area("কাজের ডিটেইলস:")
                        e_payment = st.number_input("বজেট/ফি (Editor BDT):", min_value=0.0)
                        if st.form_submit_button("এডিটর টাস্ক ইস্যু করুন 🚀"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO tasks (client, editor, task_detail, assign_time, start_time, submit_time, status, final_link, revision_note, editor_payment, target_type) VALUES (?,?,?,?,'','','Pending','','',?,'Editor')",
                                           (e_client, e_editor.lower().strip(), e_detail, datetime.now().strftime("%I:%M %p"), e_payment))
                            conn.commit()
                            conn.close()
                            st.success("টাস্ক সফলভাবে অ্যাসাইন হয়েছে!")

        # ⚡ ৭. মডারেটর লাইভ টাস্ক আপডেট
        elif st.session_state.current_navigation == "⚡ মডারেটর লাইভ টাস্ক আদেশ" and is_verified:
            st.title("⚡ মডারেটর লাইভ টাস্ক আপডেট টার্মিনাল")
            conn = get_db_connection()
            tasks_current = pd.read_sql_query("SELECT * FROM tasks ORDER BY id DESC", conn)
            conn.close()
            for idx, t_row in tasks_current.iterrows():
                with st.expander(f"📌 [{t_row['target_type']}] টাস্ক আইডি: {t_row['id']} | স্ট্যাটাস: {t_row['status']}"):
                    with st.form(f"mod_form_{t_row['id']}"):
                        m_status = st.selectbox("স্ট্যাটাস আপডেট:", ["Pending", "Started", "Submitted", "Approved", "Revision"])
                        m_link = st.text_input("ফাইনাল লিংক:", value=t_row['final_link'])
                        m_rev = st.text_input("রিভিশন নোট:", value=t_row['revision_note'])
                        if st.form_submit_button("আপডেট নোড ⚙️"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE tasks SET status=?, final_link=?, revision_note=? WHERE id=?", (m_status, m_link, m_rev, t_row['id']))
                            conn.commit()
                            conn.close()
                            st.success("লাইভ সিঙ্ক সফল!")
                            st.rerun()

        # 👮 ৮. অ্যাডমিন ও CTO প্যানেল
        elif st.session_state.current_navigation == "👮 অ্যাডমিন ও CTO কন্ট্রোল প্যানেল" and is_verified:
            st.title("👮 অ্যাডমিন ও ওনার কন্ট্রোল প্যানেল")
            st.subheader("👥 টিম মেম্বারদের ভেরিফাইড গেটওয়ে স্ট্যাটাস")
            for idx, u_row in df_users_all.iterrows():
                st.write(f"👤 **{u_row['fullname']}** (`{u_row['role']}`)")

        # 🕵️ ৯. সিক্রেট ইনবক্স স্পাইডার
        elif st.session_state.current_navigation == "🕵️ সিক্রেট ইনবক্স স্পাইডার (Spy)" and is_verified:
            st.title("🕵️ সিক্রেট ইনবক্স স্পাইডার")
            conn = get_db_connection()
            df_spy = pd.read_sql_query("SELECT * FROM chat_messages ORDER BY id DESC", conn)
            conn.close()
            st.dataframe(df_spy, use_container_width=True)

        # 👤 ১০. আমার প্রোফাইল এডিট করুন
        elif st.session_state.current_navigation == "👤 আমার প্রোফাইল এডিট করুন":
            st.title("👤 প্রোফাইল আইডি কার্ড কন্ট্রোল")
            with st.form("profile_control_form"):
                f_name = st.text_input("আপনার নাম", value=my_meta["fullname"])
                w_num = st.text_input("হোয়াটসঅ্যাপ", value=my_meta["whatsapp"])
                b_info = st.text_area("বায়ো", value=my_meta["bio"])
                if st.form_submit_button("সেভ করুন 💾"):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET fullname=?, whatsapp=?, bio=? WHERE username=?", 
                                   (f_name, w_num, b_info, current_user))
                    conn.commit()
                    conn.close()
                    st.success("সফলভাবে প্রোফাইল সেভ হয়েছে!")
                    st.rerun()

    # ==========================================
    # ৫. গ্লোবাল ফুটার 
    # ==========================================
    st.markdown("---")
    col_foot1, col_foot2 = st.columns([1, 1])
    with col_foot1:
        st.caption("⚡ Developed by Md Reyadh (CTO)")
    with col_foot2:
        st.markdown("<p style='text-align: right; margin: 0; padding: 0; font-size: 0.85rem; color: #64748b;'>🟢 Server Node Status: Secure & Active | Core Database Synced Successfully</p>", unsafe_allow_html=True)
