import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import time
import io

# ==========================================
# ১. গ্লোবাল মেটা, ব্রান্ডিং ও আইটি এজেন্সি আল্ট্রা থিম
# ==========================================
st.set_page_config(page_title="Vivid Core ULTRA Command Center", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    body { background-color: #0a0f1d; color: #e2e8f0; }
    .stApp { background: linear-gradient(145deg, #070a14, #0f172a); }
    
    /* গ্লাস-মরফিজম কার্ড */
    .profile-card { 
        background: rgba(30, 41, 59, 0.7); 
        padding: 20px; 
        border-radius: 16px; 
        border: 1px solid rgba(56, 189, 248, 0.2); 
        text-align: left; 
        margin-bottom: 20px; 
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4); 
        backdrop-filter: blur(12px) !important; 
    }
    
    /* প্রোفাইল পিকচার ফিক্স: ব্লার ও স্ট্রেচ মুক্ত পারফেক্ট আউটপুট */
    .profile-card img, .stSidebar img, .current-profile-img img {
        border-radius: 12px !important;
        object-fit: contain !important;
        border: 2px solid #00f2fe !important;
        filter: none !important;
        backdrop-filter: none !important;
    }
    
    /* কাউন্টার উইজেট স্টাইল */
    .counter-box { text-align: center; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; }
    .counter-title { font-size: 12px; color: #94a3b8; font-weight: 500; }
    .counter-value { font-size: 22px; color: #ffffff; font-weight: bold; margin-top: 5px; }
    
    /* চ্যাট বাবল থিম */
    .chat-container { background-color: #0b111e; padding: 20px; border-radius: 12px; height: 350px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
    .global-chat-bubble { background-color: #1e293b; border-left: 5px solid #38bdf8; padding: 12px; border-radius: 6px; color: #f1f5f9; margin: 4px 0; }
    
    .active-dot { height: 10px; width: 10px; background-color: #00e676; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: 0 0 8px #00e676; }
    .badge-verified { background: linear-gradient(90deg, #3b82f6, #1d4ed8); color: white; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    
    /* টার্গেট ব্যানার */
    .goal-success { background: linear-gradient(135deg, #064e3b, #047857); padding: 15px; border-radius: 10px; border-left: 6px solid #10b981; color: #ecfdf5; margin-bottom: 20px; }
    .goal-failed { background: linear-gradient(135deg, #7f1d1d, #b91c1c); padding: 15px; border-radius: 10px; border-left: 6px solid #ef4444; color: #fef2f2; margin-bottom: 20px; }
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
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, sender_name TEXT, sender_role TEXT, msg TEXT, timestamp TEXT)''')
    
    # এক্সিসটিং CTO ডাটাবেস প্রোটেকশন লজিক
    cursor.execute("SELECT COUNT(*) FROM users WHERE username='reyadh'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""INSERT INTO users VALUES (
            'reyadh', 'cto123', 'Reyadh (CTO)', 'CTO', '01825221830', 
            'CTO & Production Shareholder (49%) | System Architect, Tech Lead, and Business Partner. Orchestrating advanced production pipelines, server security, and automation infrastructure while co-steering the agency''s core growth engines.', 
            'CTO & Tech Lead | System Architecture, Advanced Automation, Full-Stack Dev, S', 1, NULL)""")
        
    current_month = datetime.now().strftime("%Y-%m")
    cursor.execute("INSERT OR IGNORE INTO goals VALUES (?, 150000)", (current_month,))
    conn.commit()
    conn.close()

init_db()

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
            st.success("এজেন্সি সার্ভার সিঙ্ক সাকসেসফুল!")
            st.rerun()
        else:
            st.error("ভুল ইউজার আইডি অথবা পাসওয়ার্ড!")
else:
    current_user = st.session_state.user
    my_meta = USER_DB[current_user]
    user_role = my_meta["role"]
    
    # ==========================================
    # ৩. সাইডবার ব্র্যান্ডিং (Screenshot 2026-06-04 at 11.15.30 PM.jpg হুবহু ম্যাচড)
    # ==========================================
    if my_meta["pic"]:
        st.sidebar.image(io.BytesIO(my_meta["pic"]), width=110, output_format='PNG')
    else:
        st.sidebar.image(DEFAULT_AVATAR_URL, width=110)
        
    st.sidebar.write(f"🖥️ **{my_meta['fullname']}**")
    st.sidebar.write(f"🧬 ডেজিগনেশন: `{user_role}`")
    st.sidebar.markdown("<span class='badge-verified'>⚙️ SECURE OFFICER ENABLED</span>", unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("🌌 **অনлайн নেটওয়ার্ক নোডস**")
    st.sidebar.markdown(f"<span class='active-dot'></span> {my_meta['fullname']} <small style='color:#38bdf8;'>`{user_role}`</small>", unsafe_allow_html=True)

    if st.sidebar.button("সার্ভার ডিসকানেক্ট 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # আপনার স্ক্রিনশটের হুবহু ১০টি মডিউল লিস্ট (কোনো কন্ডিশন ছাড়া উন্মুক্ত)
    menu_options = [
        "📊 লাইভ ড্যাশবোর্ড",
        "👥 এমপ্লয়ি ডিরেক্টরি হাব",
        "💬 লাইভ চ্যাট রুম",
        "👤 আমার প্রোফাইল এডিট করুন",
        "✍️ নতুন অর্ডার এন্ট্রি",
        "🎯 টাস্ক ডিস্ট্রিবিউটর",
        "⚡ মডারেটর লাইভ টাস্ক আপডেট",
        "📉 লাইভ প্রফিট ও রিপোর্ট হাব",
        "👮 অ্যাডমিন ও CTO কন্ট্রোল প্যানেল",
        "🕵️ সিক্রেট ইনবক্স活 স্পাইডার (Spy)"
    ]

    selected_menu = st.sidebar.radio("মডিউল সিলেকশন", menu_options, index=menu_options.index(st.session_state.current_navigation) if st.session_state.current_navigation in menu_options else 0)
    st.session_state.current_navigation = selected_menu
    
    current_month_tag = datetime.now().strftime("%Y-%m")
    
    # ডাটা সিঙ্ক
    conn = get_db_connection()
    df_orders = pd.read_sql_query("SELECT * FROM orders", conn)
    df_tasks = pd.read_sql_query("SELECT * FROM tasks", conn)
    df_users_all = pd.read_sql_query("SELECT * FROM users", conn)
    df_goals = pd.read_sql_query("SELECT * FROM goals", conn)
    conn.close()

    # ==========================================
    # 📊 ১. লাইভ ড্যাশবোর্ড
    # ==========================================
    if st.session_state.current_navigation == "📊 লাইভ ড্যাশবোর্ড":
        st.title("📊 Vivid Core আইটি অটোমেশন ড্যাশবোর্ড")
        
        st.subheader("👥 একটিভ টিম রিসোর্স কাউন্টার")
        roles_to_count = ["Chairman", "CEO", "CTO", "Co-Founder", "Operation Officer", "Manager", "Moderator", "Editor", "Internee"]
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

    # ==========================================
    # 👥 ২. এমপ্লয়ি ডিরেক্টরি হাব (Screenshot ফিক্সড)
    # ==========================================
    elif st.session_state.current_navigation == "👥 এমপ্লয়ি ডিরেক্টরি হাব":
        st.title("👥 আইটি ট্যালেন্ট ও রিসোর্স ডিরেক্টরি")
        
        dir_cols = st.columns(3)
        for idx, row in df_users_all.iterrows():
            with dir_cols[idx % 3]:
                st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
                st.markdown(f"### {row['fullname']}", unsafe_allow_html=True)
                st.markdown(f"📁 <b>রোল:</b> <span style='color:#00f2fe;'>{row['role']}</span>", unsafe_allow_html=True)
                if row['whatsapp']:
                    st.markdown(f"📞 <b>WhatsApp:</b> {row['whatsapp']}", unsafe_allow_html=True)
                if row['bio']:
                    st.markdown(f"📝 <b>Bio:</b> <small>{row['bio']}</small>", unsafe_allow_html=True)
                if row['skills']:
                    st.markdown(f"⚡ <b>Skills:</b> <small>{row['skills']}</small>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # 💬 ৩. লাইভ চ্যাট রুম
    # ==========================================
    elif st.session_state.current_navigation == "💬 লাইভ চ্যাট রুম":
        st.title("💬 সেশন সিঙ্ক লাইভ চ্যাট হাব")
        
        conn = get_db_connection()
        df_chat_logs = pd.read_sql_query("SELECT * FROM chat_messages ORDER BY id ASC", conn)
        conn.close()
        
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        for _, chat in df_chat_logs.iterrows():
            st.markdown(f"<div class='global-chat-bubble'><b>{chat['sender_name']} [{chat['sender_role']}]:</b> {chat['msg']} <small style='color:#64748b; float:right;'>{chat['timestamp']}</small></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.form("chat_send_form", clear_on_submit=True):
            msg_txt = st.text_input("মেসেজ ইনপুট...")
            if st.form_submit_button("ব্রডকাস্ট ডাটা ✈️"):
                if msg_txt:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO chat_messages (sender, sender_name, sender_role, msg, timestamp) VALUES (?,?,?,?,?)",
                                   (current_user, my_meta["fullname"], user_role, msg_txt, datetime.now().strftime("%I:%M %p")))
                    conn.commit()
                    conn.close()
                    st.rerun()

    # ==========================================
    # 👤 ৪. আমার প্রোফাইল এডিট করুন
    # ==========================================
    elif st.session_state.current_navigation == "👤 আমার প্রোফাইল এডিট করুন":
        st.title("👤 মাই ড্যাсходোর্ড আইডি কার্ড কন্ট্রোল")
        
        with st.form("profile_control_form"):
            col_p1, col_p2 = st.columns([2, 1])
            with col_p1:
                f_name = st.text_input("আপনার নাম (Full Name)", value=my_meta["fullname"])
                w_num = st.text_input("হোয়াটসঅ্যাপ নোড নাম্বার", value=my_meta["whatsapp"])
                b_info = st.text_area("আপনার প্রোফাইল বায়ো/পরিচিতি (Bio)", value=my_meta["bio"], height=140)
            with col_p2:
                s_box = st.text_input("টেকনিক্যাল এক্সপেরিয়েন্স ও স্কিলসেট", value=my_meta["skills"])
                st.markdown("<label>বর্তমান প্রোফাইল ছবি</label>", unsafe_allow_html=True)
                if my_meta["pic"]:
                    st.image(io.BytesIO(my_meta["pic"]), width=140)
                else:
                    st.image(DEFAULT_AVATAR_URL, width=140)
                uploaded_pic = st.file_uploader("নতুন প্রোফাইল ছবি আপলোড", type=["jpg", "png"])
            
            if st.form_submit_button("ডাটাবেস কোড সিঙ্ক করুন 💾"):
                img_bytes = my_meta["pic"]
                if uploaded_pic is not None:
                    img_bytes = uploaded_pic.read()
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET fullname=?, whatsapp=?, bio=?, skills=?, profile_pic=? WHERE username=?", 
                               (f_name, w_num, b_info, s_box, img_bytes, current_user))
                conn.commit()
                conn.close()
                st.success("ডাটাবেস সফলভাবে আপডেট হয়েছে!")
                time.sleep(0.5)
                st.rerun()

    # ==========================================
    # ✍️ ৫. নতুন অর্ডার এন্ট্রি
    # ==========================================
    elif st.session_state.current_navigation == "✍️ নতুন অর্ডার এন্ট্রি":
        st.title("✍️ নতুন ক্লায়েন্ট অর্ডার এন্ট্রি সিস্টেম")
        with st.form("order_entry_form"):
            col_o1, col_o2 = st.columns(2)
            c_name = col_o1.text_input("ক্লায়েন্টের নাম:")
            c_num = col_o1.text_input("মোবাইল নাম্বার:")
            s_name = col_o2.text_input("সার্ভিস নাম:")
            t_price = col_o2.number_input("মোট বাজেট (BDT):", min_value=0.0)
            
            col_o3, col_o4 = st.columns(2)
            adv_paid = col_o3.number_input("অগ্রিম পেমেন্ট (BDT):", min_value=0.0)
            ed_name = col_o3.text_input("অ্যাসাইনকৃত এডিটর নাম:")
            ed_cost = col_o4.number_input("এডিটর খরচ (BDT):", min_value=0.0)
            op_cost = col_o4.number_input("অপারেশনাল কস্ট (BDT):", min_value=0.0)
            
            if st.form_submit_button("অর্ডার সেভ করুন 💾"):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO orders (date, client_name, client_number, service_name, total_price, advance_paid, due_amount, editor_name, editor_cost, operation_cost, month_tag) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                               (datetime.now().strftime("%Y-%m-%d"), c_name, c_num, s_name, t_price, adv_paid, (t_price-adv_paid), ed_name, ed_cost, op_cost, current_month_tag))
                conn.commit()
                conn.close()
                st.success("অর্ডারটি ডাটাবেসে সেভ হয়েছে!")

    # ==========================================
    # 🎯 ৬. টাস্ক ডিস্ট্রিবিউটর
    # ==========================================
    elif st.session_state.current_navigation == "🎯 টাস্ক ডিস্ট্রিবিউটর":
        st.title("🎯 টিম টাস্ক ডিস্ট্রিবিউটর টার্মিনাল")
        with st.form("task_dist_form", clear_on_submit=True):
            t_client = st.text_input("ক্লায়েন্ট রেফারেন্স/কোড:")
            all_editors = df_users_all[df_users_all["role"].str.lower() == "editor"]["username"].tolist()
            t_editor = st.selectbox("টার্গেট কর্মী (Editor):", all_editors if all_editors else [current_user])
            t_detail = st.text_area("কাজের ডিটেইলস:")
            t_payment = st.number_input("বাজেট/ফি:", min_value=0.0)
            
            if st.form_submit_button("টাস্ক ও অর্ডার ইস্যু করুন 🚀"):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO tasks (client, editor, task_detail, assign_time, start_time, submit_time, status, final_link, revision_note, editor_payment) VALUES (?,?,?,?,'','','Pending','','',?)",
                               (t_client, t_editor, t_detail, datetime.now().strftime("%I:%M %p"), t_payment))
                conn.commit()
                conn.close()
                st.success("টাস্ক সফলভাবে ইস্যু করা হয়েছে!")

    # ==========================================
    # ⚡ ৭. মডারেটর লাইভ টাস্ক আপডেট
    # ==========================================
    elif st.session_state.current_navigation == "⚡ মডারেটর লাইভ টাস্ক আপডেট":
        st.title("⚡ মডারেটর লাইভ টাস্ক আপডেট")
        if df_tasks.empty:
            st.info("কোনো সক্রিয় টাস্ক পাওয়া যায়নি।")
        else:
            for idx, t_row in df_tasks.iterrows():
                with st.expander(f"📌 টাস্ক আইডি: {t_row['id']} | ক্লায়েন্ট: {t_row['client']} ({t_row['status']})"):
                    with st.form(f"mod_form_{t_row['id']}"):
                        m_status = st.selectbox("স্ট্যাটাস আপডেট করুন:", ["Pending", "Started", "Submitted", "Approved"], index=["Pending", "Started", "Submitted", "Approved"].index(t_row['status']) if t_row['status'] in ["Pending", "Started", "Submitted", "Approved"] else 0)
                        m_link = st.text_input("ফাইনাল ডেলিভারি লিংক:", value=t_row['final_link'])
                        if st.form_submit_button("টাস্ক নোড আপডেট করুন ⚙️"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE tasks SET status=?, final_link=? WHERE id=?", (m_status, m_link, t_row['id']))
                            conn.commit()
                            conn.close()
                            st.success("টাস্ক আপডেট সফল!")
                            st.rerun()

    # ==========================================
    # 📉 ৮. লাইভ প্রফিট ও রিপোর্ট হাব
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
            total_net_profit = filtered_df['net_profit'].sum()
            
            month_goal_row = df_goals[df_goals["month_tag"] == selected_month]
            target_amount = month_goal_row["target_amount"].values[0] if not month_goal_row.empty else 150000.0
            
            if total_net_profit >= target_amount:
                st.markdown(f"<div class='goal-success'><h3>🎉 মিশন সাকসেসফুল! টার্গেট এچیভড!</h3><p>টার্গেট ছিল <b>{target_amount:,.0f} BDT</b> এবং প্রফিট <b>{total_net_profit:,.0f} BDT</b>!</p></div>", unsafe_allow_html=True)
            else:
                shortage = target_amount - total_net_profit
                st.markdown(f"<div class='goal-failed'><h3>⚠️ অ্যালার্ট: মান্থলি টার্গেট ফেইলুর রিস্ক!</h3><p>আমরা এখনো টার্গেট থেকে <b>{shortage:,.0f} BDT</b> পেছনে আছি।</p></div>", unsafe_allow_html=True)
            st.dataframe(filtered_df, use_container_width=True)

    # ==========================================
    # 👮 ৯. অ্যাডমিন ও CTO কন্ট্রোল প্যানেল
    # ==========================================
    elif st.session_state.current_navigation == "👮 অ্যাডমিন ও CTO কন্ট্রোল প্যানেল":
        st.title("👮 অ্যাডমিন ও CTO কন্ট্রোল প্যানেল")
        st.subheader("👥 নতুন ইউজার/মেম্বার তৈরি করুন")
        with st.form("create_user_form"):
            new_u = st.text_input("ইউজার আইডি (Username):")
            new_p = st.text_input("পাসওয়ার্ড:")
            new_f = st.text_input("পূর্ণ নাম (Full Name):")
            new_r = st.selectbox("রোল/ডেজিগনেশন:", ["Chairman", "CEO", "CTO", "Co-Founder", "Operation Officer", "Manager", "Moderator", "Editor", "Internee"])
            
            if st.form_submit_button("নতুন মেম্বার যুক্ত করুন 🚀"):
                if new_u and new_p:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT OR IGNORE INTO users (username, password, fullname, role, whatsapp, bio, skills, is_officer_verified) VALUES (?, ?, ?, ?, '', '', '', 0)", 
                                   (new_u, new_p, new_f, new_r))
                    conn.commit()
                    conn.close()
                    st.success(f"সফলভাবে {new_f} কে যুক্ত করা হয়েছে!")
                else:
                    st.error("ইউজার আইডি এবং পাসওয়ার্ড আবশ্যিক।")

    # ==========================================
    # 🕵️ ১০. সিক্রেট ইনবক্স স্পাইডার (Spy)
    # ==========================================
    elif st.session_state.current_navigation == "🕵️ সিক্রেট ইনবক্স স্পাইডার (Spy)":
        st.title("🕵️ সিক্রেট ইনবক্স স্পাইডার (Enterprise Spy Terminal)")
        conn = get_db_connection()
        df_spy = pd.read_sql_query("SELECT * FROM chat_messages ORDER BY id DESC", conn)
        conn.close()
        if df_spy.empty:
            st.info("কোনো ডাটা পাওয়া যায়নি।")
        else:
            st.dataframe(df_spy, use_container_width=True)

    # ==========================================
    # ফুটার নোড
    # ==========================================
    st.markdown("---")
    st.caption(f"🟢 Core Server: Secure & Active | 🗄️ DB Node Connection: SQLite Verified ({DB_FILE}) | 🚀 Sync Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
