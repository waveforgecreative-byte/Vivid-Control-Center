import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import random
import urllib.parse
import sqlite3
import io
import time

# ১. প্রিমিয়াম পেজ সেটআপ ও স্টাইলিং
st.set_page_config(page_title="Vivid Control Center PRO", page_icon="🎬", layout="wide")

st.markdown("""
<style>
    .reportview-container { background: #0e1117; }
    .stNotification { border-radius: 10px; border-left: 5px solid #FF4B4B; }
    .chat-bubble-user { background-color: #005c4b; color: #d9fdd3; padding: 10px; border-radius: 10px; margin: 5px; text-align: right; max-width: 70%; margin-left: auto; }
    .chat-bubble-other { background-color: #202c33; color: #e9edef; padding: 10px; border-radius: 10px; margin: 5px; text-align: left; max-width: 70%; }
    .active-dot { height: 10px; width: 10px; background-color: #23d160; border-radius: 50%; display: inline-block; margin-right: 5px; }
    .idle-dot { height: 10px; width: 10px; background-color: #ffdd57; border-radius: 50%; display: inline-block; margin-right: 5px; }
</style>
""", unsafe_allow_html=True)

DB_FILE = "vivid_studio_storage_v2.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, client_name TEXT, client_number TEXT,
        section TEXT, service_name TEXT, total_price REAL, advance_paid REAL, due_amount REAL,
        camera_hours REAL, editor_cost REAL, operation_cost REAL)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY, client TEXT, editor TEXT, task_detail TEXT, deadline TEXT,
        client_phone TEXT, status TEXT, final_link TEXT, revision_note TEXT)''')
    
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users VALUES ('admin', '123', 'Admin')")
        cursor.execute("INSERT INTO users VALUES ('manager', '456', 'Manager')")
        cursor.execute("INSERT INTO users VALUES ('shakil_editor', '789', 'Moderator')")
        cursor.execute("INSERT INTO users VALUES ('rahat_editor', '789', 'Moderator')")
    conn.commit()
    conn.close()

init_db()

if "global_chats" not in st.session_state:
    st.session_state.global_chats = []
if "notifications" not in st.session_state:
    st.session_state.notifications = []
if "active_users" not in st.session_state:
    st.session_state.active_users = {}

def update_activity(username):
    st.session_state.active_users[username] = time.time()

def load_orders():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM orders", conn)
    conn.close()
    if not df.empty:
        df.columns = ["ID", "Date", "Client Name", "Client Number", "Section", "Service Name", "Total Package Price", "Advance Paid", "Due Amount", "Camera Rent Hours", "Editor Cost", "Operation Cost"]
    return df

def load_users():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    return df

def load_tasks():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM tasks", conn)
    conn.close()
    if not df.empty:
        df.columns = ["Task ID", "Client", "Editor", "Task Detail", "Deadline", "Client Phone", "Status", "Final File Link", "Revision Note"]
    return df

df_orders = load_orders()
df_users = load_users()
df_tasks = load_tasks()

USER_DB = {row["username"]: {"password": row["password"], "role": row["role"]} for _, row in df_users.iterrows()}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = ""
    st.session_state.user = ""
if "current_navigation" not in st.session_state:
    st.session_state.current_navigation = "📊 মেইন ড্যাশবোর্ড"

def trigger_notification(text, target_section):
    st.session_state.notifications.append({"text": text, "target": target_section, "time": datetime.now().strftime("%H:%M")})

# --- মোটিভেশনাল ডাটা লিস্ট ---
MOTIVATION_SUCCESS = [
    "🎉 অসাধারণ! Vivid Vistas টিম এই মাসের টার্গেট ধুলোয় উড়িয়ে দিয়েছে! পরবর্তী বড় প্রজেক্টের জন্য ক্যামেরা চার্জ করুন! 🎥",
    "🚀 টার্গেট ফিল-আপ! প্রোডাকশন কোয়ালিটি যখন ওয়ার্ল্ড-ক্লাস হয়, সেলস তখন এমনিই আসে। পুরো টিমকে একটা ট্রিট দেওয়া যাক! 🍕",
    "💎 Boom! লক্ষ্য অর্জন হয়েছে। এবার সময় এসেছে আমাদের স্টুডিওর গিয়ার বা ইকুইপমেন্ট আপগ্রেড করার! 📸"
]
MOTIVATION_FAILURE = [
    "💡 টার্গেট মিস হয়েছে? নো টেনশন! ক্লায়েন্টদের ফলো-আপ ইমেইল পাঠান। পুরাতন ২০% কাস্টমার থেকেই ৮০% নতুন বিজনেস আসে!",
    "🎬 সিনেমাটিক শট যেমন ওয়ান-টেক-এ হয় না, বিজনেসও তেমন মাঝেমাঝে ড্রপ করে। ফেসবুক ও ইনস্টাগ্রামে নতুন রিলস/শর্টস ছাড়ুন।"
]

if not st.session_state.logged_in:
    st.title("🎬 Vivid Control Center PRO")
    username = st.text_input("ইউজার আইডি (Username)")
    password = st.text_input("পাসওয়ার্ড (Password)", type="password")
    if st.button("লগইন করুন 🚀", use_container_width=True):
        if username in USER_DB and USER_DB[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.role = USER_DB[username]["role"]
            update_activity(username)
            st.rerun()
        else:
            st.error("ভুল ইউজারনেম বা পাসওয়ার্ড!")
else:
    current_user = st.session_state.user
    update_activity(current_user)
    
    if st.session_state.notifications:
        latest_notif = st.session_state.notifications[-1]
        with st.container():
            col_n1, col_n2 = st.columns([4, 1])
            col_n1.info(f"🔔 **লাইভ নোটিফিকেশন [{latest_notif['time']}]:** {latest_notif['text']}")
            if col_n2.button("সরাসরি যান 👉", key="notif_btn"):
                st.session_state.current_navigation = latest_notif['target']
                st.session_state.notifications.pop()
                st.rerun()

    st.sidebar.markdown(f"<h2 style='color:#FF4B4B;text-align:center;'>VIVID PRO v2</h2>", unsafe_allow_html=True)
    st.sidebar.markdown(f"👤 ইউজার: **{current_user.upper()}** ({st.session_state.role})")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🟢 লাইভ অ্যাক্টিভ মেম্বার")
    current_time = time.time()
    for user, last_seen in list(st.session_state.active_users.items()):
        if current_time - last_seen < 300:
            st.sidebar.markdown(f"<span class='active-dot'></span> {user} (Active Now)", unsafe_allow_html=True)
        else:
            st.sidebar.markdown(f"<span class='idle-dot'></span> {user} (Idle)", unsafe_allow_html=True)
            
    if st.sidebar.button("লগআউট", use_container_width=True):
        st.session_state.active_users.pop(current_user, None)
        st.session_state.logged_in = False
        st.rerun()

    menu_options = ["📊 মেইন ড্যাশবোর্ড", "✍️ নতুন অর্ডার এন্ট্রি", "📋 টাস্ক ও ডেডলাইন", "💬 প্রিমিয়াম চ্যাট হাব (1:1)"]
    if st.session_state.role == "Admin":
        menu_options.append("➕ নতুন ইউজার তৈরি (Create User)")
        
    selected_menu = st.sidebar.radio("মেনু নেভিগেশন", menu_options, index=menu_options.index(st.session_state.current_navigation))
    st.session_state.current_navigation = selected_menu

    # ==========================================
    # ৫. মেইন ড্যাশবোর্ড পেজ (মোটিভেশন অন করা হলো)
    # ==========================================
    if st.session_state.current_navigation == "📊 মেইন ড্যাশবোর্ড":
        st.title("📊 Vivid Live ড্যাশবোর্ড ও অ্যানালিটিক্স")
        
        if df_orders.empty:
            st.info("কোনো ডাটা রেকর্ড নেই। 'নতুন অর্ডার এন্ট্রি' সেকশন থেকে প্রথম অর্ডারটি দিন।")
        else:
            df_orders["Total"] = pd.to_numeric(df_orders["Total Package Price"]).fillna(0)
            df_orders["Advance"] = pd.to_numeric(df_orders["Advance Paid"]).fillna(0)
            df_orders["Due"] = pd.to_numeric(df_orders["Due Amount"]).fillna(0)
            df_orders["Editor_Cost"] = pd.to_numeric(df_orders["Editor Cost"]).fillna(0)
            df_orders["Op_Cost"] = pd.to_numeric(df_orders["Operation Cost"]).fillna(0)
            df_orders["Net_Profit"] = df_orders["Total"] - (df_orders["Editor_Cost"] + df_orders["Op_Cost"])
            
            df_orders["Month"] = pd.to_datetime(df_orders["Date"]).dt.strftime('%Y-%m')
            
            # সাইডবার ফিল্টার এবং টার্গেট ইনপুট
            st.sidebar.markdown("---")
            sales_target = st.sidebar.number_input("🎯 এই মাসের সেলস টার্গেট (BDT)", min_value=10000, value=100000, step=10000)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("💰 মোট সেলস", f"{df_orders['Total'].sum():,.0f} BDT")
            m2.metric("📈 নীট প্রফিট (লাভ)", f"{df_orders['Net_Profit'].sum():,.0f} BDT")
            m3.metric("🚨 টোটাল মার্কেট ডিউ", f"{df_orders['Due'].sum():,.0f} BDT")
            
            # 🔥🔥🔥 [ACTIVATED] মোটিভেশন ও সেলস টার্গেট ট্র্যাকার সেকশন 🔥🔥🔥
            st.markdown("---")
            st.subheader("🎯 এই মাসের সেলস লক্ষ্য ও পারফরম্যান্স ট্র্যাকার")
            
            current_month_str = datetime.now().strftime("%Y-%m")
            # কারেন্ট মাসের সেলস ফিল্টার
            current_month_sales = df_orders[df_orders["Month"] == current_month_str]["Total"].sum() if current_month_str in df_orders["Month"].values else 0
            
            progress_pct = min(current_month_sales / sales_target, 1.0) if sales_target > 0 else 0.0
            
            col_p1, col_p2 = st.columns([3, 1])
            with col_p1:
                st.write(f"চলতি মাসের লাইভ সেলস: **{current_month_sales:,.0f} BDT** / লক্ষ্য: **{sales_target:,.0f} BDT**")
                st.progress(progress_pct)
            with col_p2:
                st.markdown(f"### 📊 {progress_pct*100:.1f}% ডান")
                
            st.markdown("#### 💬 Vivid Vistas বিজনেস বুস্টার জোন")
            if current_month_sales >= sales_target and sales_target > 0:
                st.success(random.choice(MOTIVATION_SUCCESS))
            else:
                st.info(random.choice(MOTIVATION_FAILURE))
            # 🔥🔥🔥 ========================================== 🔥🔥🔥
            
            st.markdown("---")
            st.subheader("📋 অল-টাইম ডাটা শীট")
            st.dataframe(df_orders, use_container_width=True)
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_orders.to_excel(writer, index=False, sheet_name='All_Orders')
            st.download_button(label="🟢 এক্সেল রিপোর্ট ডাউনলোড করুন (.xlsx)", data=buffer.getvalue(), file_name="Vivid_Master_Report.xlsx", mime="application/vnd.ms-excel")

    # ==========================================
    # ৬. নতুন অর্ডার এন্ট্রি পেজ
    # ==========================================
    elif st.session_state.current_navigation == "✍️ নতুন অর্ডার এন্ট্রি":
        st.title("📝 নতুন অর্ডার ও কস্টিং ইনপুট")
        with st.form("order_entry_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                c_name = st.text_input("ক্লায়েন্টের নাম *")
                c_phone = st.text_input("মোবাইল নাম্বার *")
                section = st.selectbox("বিভাগ", ["Production", "Studio"])
                srv_name = st.text_input("সার্ভিসের নাম")
            with c2:
                total = st.number_input("মোট চুক্তি (BDT)", min_value=0)
                adv = st.number_input("এডভান্স পেমেন্ট (BDT)", min_value=0)
                ed_cost = st.number_input("এডিটর বিল (BDT)", min_value=0)
                op_cost = st.number_input("অন্যান্য অপারেশন খরচ (BDT)", min_value=0)
                
            if st.form_submit_button("সার্ভারে লাইভ সেভ দিন 🚀", use_container_width=True):
                if c_name and c_phone:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute('''INSERT INTO orders (date, client_name, client_number, section, service_name, total_price, advance_paid, due_amount, camera_hours, editor_cost, operation_cost)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)''', (datetime.now().strftime("%Y-%m-%d"), c_name, c_phone, section, srv_name, total, adv, total-adv, ed_cost, op_cost))
                    conn.commit()
                    conn.close()
                    trigger_notification(f"✍️ নতুন অর্ডার যোগ করেছেন {current_user}: ক্লায়েন্ট {c_name}", "📊 মেইন ড্যাশবোর্ড")
                    st.success("🎉 ওрядок লাইভ সেভ হয়েছে!")
                    st.cache_resource.clear()
                    st.rerun()

    # ==========================================
    # ৭. টাস্ক, ডেডলাইন ও এডিটর রিভিশন বক্স
    # ==========================================
    elif st.session_state.current_navigation == "📋 টাস্ক ও ডেডলাইন":
        st.title("📋 টাস্ক ডিস্ট্রিবিউশন ও লাইভ রিভিশন প্যানেল")
        
        if st.session_state.role in ["Admin", "Manager"]:
            st.subheader("🎯 নতুন এডিটিং টাস্ক অ্যাসাইন করুন")
            with st.form("task_assign_form", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    t_client = st.text_input("ক্লায়েন্টের নাম")
                    t_editor = st.selectbox("দায়িত্বরত এডিটর সিলেক্ট করুন", list(USER_DB.keys()))
                with col2:
                    t_detail = st.text_input("কী কাজ করতে হবে? (e.g. Cinematic Teaser)")
                    t_deadline = st.date_input("ডেডлайн")
                with col3:
                    t_phone = st.text_input("ক্লায়েন্টের ফোন নাম্বার")
                
                if st.form_submit_button("📡 এডিটর প্যানেলে লাইভ পুশ করুন"):
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                   (random.randint(1000, 9999), t_client, t_editor, t_detail, str(t_deadline), t_phone, "Pending", "No Submission Yet", "No Revision Notes Yet"))
                    conn.commit()
                    conn.close()
                    trigger_notification(f"📋 নতুন টাস্ক এসাইন করা হয়েছে এডিটর {t_editor}-কে!", "📋 টাস্ক ও ডেডলাইন")
                    st.success("🔥 টাস্ক এডিটরের কাছে চলে গেছে!")
                    st.rerun()

        st.markdown("---")
        st.subheader("🏃‍♂️ রানিং প্রোডাকশন টাস্ক ও লাইভ রিভিশন বক্স")
        
        if df_tasks.empty:
            st.info("কোনো রানিং টাস্ক নেই এই মুহূর্তে।")
        else:
            for index, row in df_tasks.iterrows():
                if st.session_state.role in ["Admin", "Manager"] or str(row["Editor"]).strip() == current_user:
                    with st.expander(f"📌 {row['Client']} এর কাজ | 👤 এডিটর: {row['Editor']} | 🚦 স্ট্যাটাস: {row['Status']}"):
                        st.write(f"**কাজের বিবরণ:** {row['Task Detail']}")
                        st.write(f"**ডেডлайн:** {row['Deadline']}")
                        st.info(f"🚨 **লাইভ রিভিশন নোট:** {row.get('Revision Note', 'No Revision Note yet')}")
                        
                        new_link = st.text_input("ফাইনাল কাজের ড্রাইভ/ডাউনলোড লিংক", value=row['Final File Link'], key=f"lnk_{index}")
                        status_update = st.selectbox("কাজের প্রোগ্রেস আপডেট করুন", ["Pending", "In Progress", "Completed"], index=["Pending", "In Progress", "Completed"].index(row['Status']), key=f"sts_{index}")
                        
                        revision_input = ""
                        if st.session_state.role in ["Admin", "Manager"]:
                            revision_input = st.text_area("🔧 ক্লায়েন্ট কোনো কারেকশন বা রিভিশন দিলে এখানে লিখুন:", value=row.get('Revision Note', ''), key=f"rev_{index}")
                        
                        if st.button("সার্ভারে ডাটা আপডেট করুন 💾", key=f"upbtn_{index}"):
                            conn = sqlite3.connect(DB_FILE)
                            cursor = conn.cursor()
                            final_rev = revision_input if revision_input else row.get('Revision Note', 'No Revision')
                            cursor.execute('UPDATE tasks SET status=?, final_link=?, revision_note=? WHERE id=?', 
                                           (status_update, new_link, final_rev, row['Task ID']))
                            conn.commit()
                            conn.close()
                            
                            trigger_notification(f"🔄 টাস্ক ID {row['Task ID']} আপডেট করেছেন {current_user}!", "📋 টাস্ক ও ডেডলাইন")
                            st.success("✅ টাস্ক ও রিভিশন ডেটা ইনস্ট্যান্ট আপডেট হয়েছে!")
                            st.rerun()

    # ==========================================
    # ৮. প্রিমিয়াম চ্যাট হাব (১:১ পার্সোনাল চ্যাট)
    # ==========================================
    elif st.session_state.current_navigation == "💬 প্রিমিয়াম চ্যাট হাব (1:1)":
        st.title("💬 Vivid Live 1:1 প্রিমিয়াম চ্যাট হাব")
        
        all_members = list(USER_DB.keys())
        if current_user in all_members:
            all_members.remove(current_user)
        
        selected_peer = st.selectbox("👤 কার সাথে পার্সোনাল চ্যাটে কথা বলবেন?", all_members)
        
        st.markdown(f"#### 🟢 Chat Terminal with **{selected_peer.upper()}**")
        st.markdown("<div style='background-color: #0d141b; padding: 20px; border-radius: 10px; border: 1px solid #00a884; height: 350px; overflow-y: scroll;'>", unsafe_allow_html=True)
        
        for chat in st.session_state.global_chats:
            if (chat["sender"] == current_user and chat["receiver"] == selected_peer):
                st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {chat['msg']} <br><small style='font-size:10px;'>{chat['time']}</small></div>", unsafe_allow_html=True)
            elif (chat["sender"] == selected_peer and chat["receiver"] == current_user):
                st.markdown(f"<div class='chat-bubble-other'><b>{selected_peer.upper()}:</b> {chat['msg']} <br><small style='font-size:10px;'>{chat['time']}</small></div>", unsafe_allow_html=True)
                
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.form("chat_send_form", clear_on_submit=True):
            input_msg = st.text_input("আপনার মেসেজটি লিখুন...")
            if st.form_submit_button("মেসেজ পাঠান ✈️", use_container_width=True):
                if input_msg:
                    timestamp = datetime.now().strftime("%I:%M %p")
                    st.session_state.global_chats.append({
                        "sender": current_user, "receiver": selected_peer, "msg": input_msg, "time": timestamp
                    })
                    trigger_notification(f"💬 {current_user} আপনাকে একটি পার্সোনাল মেসেজ পাঠিয়েছেন!", "💬 প্রিমিয়াম চ্যাট হাব (1:1)")
                    st.rerun()

    # ==========================================
    # ৯. নতুন ইউজার তৈরি (Admin Only)
    # ==========================================
    elif st.session_state.current_navigation == "➕ নতুন ইউজার তৈরি (Create User)":
        st.title("➕ নতুন টিম মেম্বার অ্যাকাউন্ট তৈরি করুন")
        with st.form("user_form", clear_on_submit=True):
            new_uid = st.text_input("নতুন ইউজার আইডি (Username) *")
            new_pass = st.text_input("লগইন পাসওয়ার্ড (Password) *")
            new_role = st.selectbox("রোল সিলেক্ট করুন", ["Admin", "Manager", "Moderator"])
            
            if st.form_submit_button("অ্যাকাউন্ট অ্যাক্টিভেট করুন 🛠️"):
                if new_uid and new_pass:
                    try:
                        conn = sqlite3.connect(DB_FILE)
                        cursor = conn.cursor()
                        cursor.execute('INSERT INTO users VALUES (?, ?, ?)', (new_uid, new_pass, new_role))
                        conn.commit()
                        conn.close()
                        st.success(f"🎉 নতুন টিম মেম্বার রেডি: {new_uid}")
                        st.rerun()
                    except:
                        st.error("দুঃখিত, এই ইউজার আইডি অলরেডি বুকড!")
