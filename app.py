import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sqlite3
import random
import time

# ১. প্রিমিয়াম পেজ কনফিগারেশন ও কাস্টম থিমিং
st.set_page_config(page_title="Vivid Control Center ULTRA PRO", page_icon="🎬", layout="wide")

st.markdown("""
<style>
    .reportview-container { background: #0b0e14; }
    .chat-bubble-user { background-color: #005c4b; color: #d9fdd3; padding: 12px; border-radius: 12px; margin: 8px 0; text-align: right; max-width: 75%; margin-left: auto; box-shadow: 1px 1px 5px rgba(0,0,0,0.2); }
    .chat-bubble-other { background-color: #202c33; color: #e9edef; padding: 12px; border-radius: 12px; margin: 8px 0; text-align: left; max-width: 75%; box-shadow: 1px 1px 5px rgba(0,0,0,0.2); }
    .active-dot { height: 12px; width: 12px; background-color: #00e676; border-radius: 50%; display: inline-block; margin-right: 8px; }
</style>
""", unsafe_allow_html=True)

DB_FILE = "vivid_studio_ultimate_v4.db"

# --- ২. ডাটাবেস আর্কিটেকচার (ইউজার গোল টেবিল সহ) ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, client_name TEXT, client_number TEXT,
        section TEXT, service_name TEXT, total_price REAL, advance_paid REAL, due_amount REAL,
        editor_name TEXT, editor_cost REAL, operation_cost REAL, month_tag TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT, section TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY, client TEXT, editor TEXT, task_detail TEXT, 
        assign_time TEXT, start_time TEXT, submit_time TEXT,
        status TEXT, final_link TEXT, revision_note TEXT, editor_payment REAL)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS goals (month_tag TEXT PRIMARY KEY, target_amount REAL)''')
    
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users VALUES ('admin', '123', 'Admin', 'Management')")
        cursor.execute("INSERT INTO users VALUES ('manager_main', '456', 'Manager', 'Management')")
        cursor.execute("INSERT INTO users VALUES ('moderator_crew', '789', 'Moderator', 'Studio')")
        cursor.execute("INSERT INTO users VALUES ('shakil', 'editor123', 'Editor', 'Production')")
        cursor.execute("INSERT INTO users VALUES ('rahat', 'editor456', 'Editor', 'Studio')")
        
    # ডিফল্ট টার্গেট গোল সেটআপ
    current_month = datetime.now().strftime("%Y-%m")
    cursor.execute("INSERT OR IGNORE INTO goals VALUES (?, 100000)", (current_month,))
    
    conn.commit()
    conn.close()

init_db()

# --- ৩. ইন-মেমোরি ও ডাটাবেস লাইভ ইঞ্জিন ---
if "global_chats" not in st.session_state:
    st.session_state.global_chats = []
if "notifications" not in st.session_state:
    st.session_state.notifications = []
if "active_users" not in st.session_state:
    st.session_state.active_users = {}

def update_activity(username):
    st.session_state.active_users[username] = time.time()

def trigger_live_notification(text, target_section):
    st.session_state.notifications.append({
        "text": text, "target": target_section, "time": datetime.now().strftime("%I:%M %p")
    })

def get_target_goal(month_tag):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT target_amount FROM goals WHERE month_tag = ?", (month_tag,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else 100000.0

def update_target_goal(month_tag, amount):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO goals VALUES (?, ?)", (month_tag, amount))
    conn.commit()
    conn.close()

def load_orders():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM orders", conn)
    conn.close()
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
    return df

df_orders = load_orders()
df_users = load_users()
df_tasks = load_tasks()

USER_DB = {row["username"]: {"password": row["password"], "role": row["role"], "section": row["section"]} for _, row in df_users.iterrows()}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = ""
    st.session_state.user = ""
if "current_navigation" not in st.session_state:
    st.session_state.current_navigation = "📊 লাইভ ড্যাশবোর্ড"

# --- ৪. নোটিফিকেশন ইঞ্জিন ---
if st.session_state.logged_in and st.session_state.notifications:
    latest_notif = st.session_state.notifications[-1]
    with st.container():
        col_n1, col_n2 = st.columns([5, 1])
        col_n1.warning(f"🔔 **লাইভ অ্যালার্ট:** {latest_notif['text']}")
        if col_n2.button("সরাসরি যান ⚡", key="notif_redirect"):
            st.session_state.current_navigation = latest_notif['target']
            st.session_state.notifications.pop()
            st.rerun()

# --- ৫. সাইডবার লগইন ও এক্সেস কন্ট্রোল ---
if not st.session_state.logged_in:
    st.title("🎬 Vivid Studio Ultra Server V4")
    u_id = st.text_input("ইউজার আইডি (Username)")
    u_pass = st.text_input("পাসওয়ার্ড", type="password")
    if st.button("সার্ভারে প্রবেশ করুন 🔐", use_container_width=True):
        if u_id in USER_DB and USER_DB[u_id]["password"] == u_pass:
            st.session_state.logged_in = True
            st.session_state.user = u_id
            st.session_state.role = USER_DB[u_id]["role"]
            update_activity(u_id)
            st.rerun()
        else:
            st.error("ভুল তথ্য দিয়েছেন!")
else:
    current_user = st.session_state.user
    user_role = st.session_state.role
    update_activity(current_user)
    
    st.sidebar.markdown("<h2 style='color:#00e676; text-align:center;'>VIVID CORE</h2>", unsafe_allow_html=True)
    st.sidebar.write(f"👤 ইউজার: **{current_user.upper()}** | রোল: `{user_role}`")
    
    # লাইভ মেম্বার লিস্ট
    st.sidebar.markdown("---")
    st.sidebar.markdown("🟢 **অনলাইন টিম মেম্বারস**")
    for user, last_seen in list(st.session_state.active_users.items()):
        if time.time() - last_seen < 300:
            user_sec = USER_DB.get(user, {}).get("section", "Unknown")
            st.sidebar.markdown(f"<span class='active-dot'></span> {user} (`{user_sec}` সেকশন)", unsafe_allow_html=True)

    if st.sidebar.button("লগআউট 🚪", use_container_width=True):
        st.session_state.active_users.pop(current_user, None)
        st.session_state.logged_in = False
        st.rerun()

    # রোল অনুযায়ী মেনু ফিল্টারিং
    if user_role in ["Admin", "Manager"]:
        menu_options = ["📊 লাইভ ড্যাশবোর্ড", "📉 লাইভ প্রফিট ও রিপোর্ট হাব", "✍️ নতুন অর্ডার এন্ট্রি", "🎯 টাস্ক ডিস্ট্রিবিউটর", "💬 প্রিমিয়াম চ্যাট হাব"]
    elif user_role == "Moderator":
        menu_options = ["📊 লাইভ ড্যাশবোর্ড", "✍️ নতুন অর্ডার এন্ট্রি", "💬 প্রিমিয়াম চ্যাট হাব"]
    elif user_role == "Editor":
        menu_options = ["🎬 আমার এডিটিং প্যানেল", "💬 প্রিমিয়াম চ্যাট হাব"]
        
    if user_role == "Admin":
        menu_options.append("➕ নতুন ইউজার তৈরি (Create User)")

    if st.session_state.current_navigation not in menu_options:
        st.session_state.current_navigation = menu_options[0]
        
    selected_menu = st.sidebar.radio("সিস্টেম নেভিগেশন", menu_options, index=menu_options.index(st.session_state.current_navigation))
    st.session_state.current_navigation = selected_menu

    current_month_tag = datetime.now().strftime("%Y-%m")

    # ==========================================
    # ৬. মেইন লাইভ ড্যাশবোর্ড (Admin, Manager, Moderator দেখতে পারবে)
    # ==========================================
    if st.session_state.current_navigation == "📊 লাইভ ড্যাশবোর্ড":
        st.title("📊 লাইভ স্টুডিও ওভারভিউ ও টার্গেট ট্র্যাকার")
        
        # লক্ষ্যমাত্রা নিয়ন্ত্রণ জোন
        live_target = get_target_goal(current_month_tag)
        
        if user_role == "Admin":
            st.subheader("🎯 এই মাসের সেলস লক্ষ্যমাত্রা সেট করুন (Admin Only)")
            new_target = st.number_input("টার্গেট অ্যামাউন্ট সেট করুন (BDT)", min_value=10000, value=int(live_target), step=5000)
            if st.button("টার্গেট আপডেট করুন 📌"):
                update_target_goal(current_month_tag, new_target)
                st.success("গোল আপডেট হয়েছে!")
                st.rerun()
        else:
            # ম্যানেজার ও মডারেটর শুধু টার্গেট দেখতে পারবে
            st.info(f"🎯 **অ্যাডমিন কর্তৃক নির্ধারিত চলতি মাসের সেলস লক্ষ্যমাত্রা:** {live_target:,.0f} BDT")
            
        st.markdown("---")
        
        if df_orders.empty:
            st.info("সার্ভারে কোনো অর্ডার ডাটা নেই।")
        else:
            # রিয়েল-টাইম লাইভ ক্যালকুলেশন (পেজ লোড হলেই ইনস্ট্যান্ট আপডেট হবে)
            current_month_sales = df_orders[df_orders["month_tag"] == current_month_tag]["total_price"].sum()
            progress_pct = min(current_month_sales / live_target, 1.0) if live_target > 0 else 0.0
            
            st.subheader("📈 চলতি মাসের লাইভ লক্ষ্যমাত্রা প্রগ্রেস বার")
            col_p1, col_p2 = st.columns([3, 1])
            with col_p1:
                st.write(f"চলতি মাসের লাইভ সেলস: **{current_month_sales:,.0f} BDT** / লক্ষ্য: **{live_target:,.0f} BDT**")
                st.progress(progress_pct)
            with col_p2:
                st.markdown(f"### 📊 {progress_pct*100:.1f}% লক্ষ্য অর্জিত")
                
            if user_role in ["Admin", "Manager"]:
                st.markdown("---")
                st.subheader("💼 সার্বিক স্টুডিও রিয়েল-টাইম ফাইন্যান্স (মডারেটর এই প্যানেল দেখবে না)")
                total_sales = df_orders["total_price"].sum()
                total_due = df_orders["due_amount"].sum()
                total_expenses = df_orders["editor_cost"].sum() + df_orders["operation_cost"].sum()
                net_profit = total_sales - total_expenses
                
                m1, m2, m3 = st.columns(3)
                m1.metric("💰 মোট সেলস ভলিউম", f"{total_sales:,.0f} BDT")
                m2.metric("📈 নীট লাভ (Net Profit)", f"{net_profit:,.0f} BDT")
                m3.metric("🚨 টোটাল মার্কেট ডিউ", f"{total_due:,.0f} BDT")

    # ==========================================
    # ৭. লাইভ প্রফিট ও রিপোর্ট হাব (Admin/Manager Only - ১০০% ইন-অ্যাপ লাইভ)
    # ==========================================
    elif st.session_state.current_navigation == "📉 লাইভ প্রফিট ও রিপোর্ট হাব":
        st.title("📉 ইন-অ্যাপ লাইভ মান্থলি ও ইয়ারলি ফাইন্যান্সিয়াল রিপোর্ট")
        
        if df_orders.empty:
            st.info("কোনো অর্ডার ডাটা উপলব্ধ নেই।")
        else:
            df_orders["net_profit"] = df_orders["total_price"] - (df_orders["editor_cost"] + df_orders["operation_cost"])
            
            # ডাটাবেস থেকে ডাইনামিক মাস ফিল্টারিং
            month_list = sorted(df_orders["month_tag"].unique(), reverse=True)
            selected_month = st.selectbox("📅 কোন মাসের লাইভ রিপোর্ট দেখতে চান?", month_list)
            
            filtered_df = df_orders[df_orders["month_tag"] == selected_month]
            
            st.markdown(f"### 📊 `{selected_month}` মাসের ১০০% লাইভ পারফরম্যান্স শীট")
            
            c_s1, c_s2, c_s3 = st.columns(3)
            c_s1.metric("ঐ মাসের মোট সেলস", f"{filtered_df['total_price'].sum():,.0f} BDT")
            c_s2.metric("ঐ মাসের নীট প্রফিট", f"{filtered_df['net_profit'].sum():,.0f} BDT")
            c_s3.metric("ঐ মাসের মোট খরচ", f"{(filtered_df['editor_cost'].sum() + filtered_df['operation_cost'].sum()):,.0f} BDT")
            
            st.markdown("#### 📋 লাইভ ডাটা ম্যাট্রিক্স (গোঁজামিল বিহীন)")
            # প্রতি লাইনে সুনির্দিষ্ট এডিটরের নাম ও সেকশন থাকবেই
            st.dataframe(filtered_df[["date", "client_name", "section", "service_name", "total_price", "due_amount", "editor_name", "editor_cost", "net_profit"]], use_container_width=True)
            
            fig = px.bar(filtered_df, x="client_name", y="net_profit", color="editor_name", title="ক্লায়েন্ট ভিত্তিক প্রফিট মার্জিন এবং দায়িত্বপ্রাপ্ত এডিটর")
            st.plotly_chart(fig, use_container_width=True)

    # ==========================================
    # ৮. নতুন অর্ডার এন্ট্রি পেজ (গোঁজামিল রোধে ফিক্সড এডিটর নাম আবশ্যিক)
    # ==========================================
    elif st.session_state.current_navigation == "✍️ নতুন অর্ডার এন্ট্রি":
        st.title("📝 নতুন ক্লায়েন্ট ডাটা ও অর্ডার এন্ট্রি")
        
        editor_list = [u for u in USER_DB if USER_DB[u]["role"] == "Editor"]
        
        if not editor_list:
            st.error("🚨 ডাটাবেসে কোনো এডিটর অ্যাকাউন্ট খুঁজে পাওয়া যায়নি! আগে 'নতুন ইউজার তৈরি' সেকশন থেকে এডিটর অ্যাকাউন্ট বানান, নয়তো গোঁজামিল লাগবে।")
        else:
            with st.form("order_form_ultra_v4", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    cl_name = st.text_input("ক্লায়েন্টের নাম *")
                    cl_phone = st.text_input("মোবাইল নাম্বার *")
                    sec = st.selectbox("কোন সেকশনের কাজ? *", ["Production", "Studio"])
                    srv = st.text_input("সার্ভিস/প্যাকেজ নাম *")
                with col2:
                    t_p = st.number_input("টোটাল ডিল প্রাইস (BDT) *", min_value=0)
                    a_p = st.number_input("এডভান্স রিসিভড (BDT)", min_value=0)
                    ed_n = st.selectbox("দায়িত্বরত এডিটর সিলেক্ট করুন (বাধ্যতামূলক) *", editor_list)
                    ed_c = st.number_input("এডিটরের ফিক্সড বিল/কস্ট (BDT) *", min_value=0)
                    op_c = st.number_input("অন্যান্য অপারেশন কস্ট (BDT)", min_value=0)
                    
                if st.form_submit_button("সার্ভারে লাইভ এন্ট্রি দিন 🚀"):
                    if cl_name and cl_phone and srv and ed_n:
                        conn = sqlite3.connect(DB_FILE)
                        cursor = conn.cursor()
                        cursor.execute('''INSERT INTO orders VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                       (datetime.now().strftime("%Y-%m-%d"), cl_name, cl_phone, sec, srv, t_p, a_p, t_p-a_p, ed_n, ed_c, op_c, current_month_tag))
                        conn.commit()
                        conn.close()
                        trigger_live_notification(f"✍️ নতুন অর্ডার অ্যাড হয়েছে: {cl_name} (দায়িত্বে: {ed_n})", "📊 লাইভ ড্যাশবোর্ড")
                        st.success("🎉 অর্ডার ডাটা এবং এডিটর অ্যাসাইনমেন্ট সম্পূর্ণ লাইভ সেভ হয়েছে!")
                        st.rerun()
                    else:
                        st.error("অনুগ্রহ করে সব স্টার (*) চিহ্নিত ঘরগুলো পূরণ করুন!")

    # ==========================================
    # ৯. টাস্ক ডিস্ট্রিবিউটর (Admin/Manager ONLY)
    # ==========================================
    elif st.session_state.current_navigation == "🎯 টাস্ক ডিস্ট্রিবিউটর":
        st.title("🎯 এডিটরদের কাজ অ্যাসাইনমেন্ট ও লাইভ পেমেন্ট ট্র্যাকার")
        editor_list = [u for u in USER_DB if USER_DB[u]["role"] == "Editor"]
        
        with St.form("task_dist_form_v4", clear_on_submit=True):
            cx1, cx2 = st.columns(2)
            with cx1:
                t_cl = st.text_input("ক্লায়েন্টের নাম")
                t_ed = st.selectbox("কোন এডিটরকে কাজ দেবেন?", editor_list)
                t_dt = st.text_area("কাজের বিবরণ ও ইন্সট্রাকশন")
            with cx2:
                t_pay = st.number_input("এই কাজের জন্য এডিটর বিল (BDT)", min_value=0)
                
            if st.form_submit_button("📡 এডিটর প্যানেলে লাইভ পুশ দিন"):
                if t_cl and t_ed:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    assign_timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                    cursor.execute('INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                   (random.randint(10000, 99999), t_cl, t_ed, t_dt, assign_timestamp, "Not Started Yet", "Not Submitted Yet", "Pending", "No Link", "No Revision Note", t_pay))
                    conn.commit()
                    conn.close()
                    trigger_live_notification(f"🎬 এডিটর {t_ed} এর জন্য নতুন প্রজেক্ট পুশ করা হয়েছে!", "🎬 আমার এডিটিং প্যানেল")
                    st.success("🔥 কাজ সফলভাবে এডিটরের কাছে লাইভ পাঠিয়ে দেওয়া হয়েছে!")
                    st.rerun()

    # ==========================================
    # ১০. এডিটর লাইভ ওয়ার্কস্টেশন Panel (Editor & Admin Control)
    # ==========================================
    elif st.session_state.current_navigation == "🎬 আমার এডিটিং প্যানেল":
        st.title("🎬 Editor Live Workstation")
        
        if user_role == "Editor":
            st.subheader(f"স্বাগতম {current_user.upper()}, আপনার লাইভ প্রজেক্টসমূহ:")
            my_tasks = df_tasks[df_tasks["editor"] == current_user]
            
            if my_tasks.empty:
                st.info("আপনার কাছে এই মুহূর্তে কোনো কাজ অ্যাসাইন করা নেই।")
            else:
                for index, row in my_tasks.iterrows():
                    with st.expander(f"📌 ক্লায়েন্ট: {row['client']} | 🚦 স্ট্যাটাস: {row['status']}"):
                        st.write(f"**📝 কাজের বিবরণ:** {row['task_detail']}")
                        st.write(f"⏱️ **কাজ শুরুর সময়:** {row['start_time']}")
                        st.error(f"🔧 **অ্যাডমিনের রিভিশন নোট:** {row['revision_note']}")
                        
                        col_b1, col_b2 = st.columns(2)
                        if row['status'] == "Pending":
                            if col_b1.button("🎬 কাজ শুরু করুন (Start Work)", key=f"strt_{index}"):
                                conn = sqlite3.connect(DB_FILE)
                                cursor = conn.cursor()
                                cursor.execute('UPDATE tasks SET status="Started", start_time=? WHERE id=?', (datetime.now().strftime("%I:%M %p"), row['id']))
                                conn.commit()
                                conn.close()
                                trigger_live_notification(f"⚡ এডিটর {current_user} কাজ শুরু করেছেন!", "📊 লাইভ ড্যাশবোর্ড")
                                st.rerun()
                                
                        if row['status'] in ["Started", "Revision"]:
                            drive_link = st.text_input("ফাইনাল কাজের ড্রাইভ লিংক দিন:", value=row['final_link'], key=f"lnk_{index}")
                            if col_b2.button("🚀 কাজ জমা দিন (Submit Work)", key=f"sub_{index}"):
                                if drive_link and drive_link != "No Link":
                                    conn = sqlite3.connect(DB_FILE)
                                    cursor = conn.cursor()
                                    cursor.execute('UPDATE tasks SET status="Submitted", final_link=?, submit_time=? WHERE id=?', (drive_link, datetime.now().strftime("%I:%M %p"), row['id']))
                                    conn.commit()
                                    conn.close()
                                    trigger_live_notification(f"🟢 এডিটর {current_user} কাজ জমা দিয়েছেন!", "📊 লাইভ ড্যাশবোর্ড")
                                    st.rerun()
                                else:
                                    st.error("ড্রাইভ লিংক দিন!")

        if user_role in ["Admin", "Manager"]:
            st.subheader("🛠️ সাবমিটেড কাজ চেক ও রিভিশন কন্ট্রোল (Admin/Manager View)")
            submitted_tasks = df_tasks[df_tasks["status"] == "Submitted"]
            if submitted_tasks.empty:
                st.info("এই মুহূর্তে কোনো কাজ রিভিউ এর জন্য পেন্ডিং নেই।")
            else:
                for index, row in submitted_tasks.iterrows():
                    with st.container():
                        st.info(f"🎯 প্রজেক্ট: {row['client']} | এডিটর: {row['editor']} | লিংক: {row['final_link']}")
                        rev_text = st.text_area("রিভিশন দিতে চাইলে নোট লিখুন:", key=f"rev_text_{index}")
                        c_btn1, c_btn2 = st.columns(2)
                        if c_btn1.button("✅ কাজ ওকে (Mark Completed)", key=f"app_{index}"):
                            conn = sqlite3.connect(DB_FILE)
                            cursor = conn.cursor()
                            cursor.execute('UPDATE tasks SET status="Completed" WHERE id=?', (row['id'],))
                            conn.commit()
                            conn.close()
                            st.success("প্রজেক্ট কমপ্লিট করা হয়েছে!")
                            st.rerun()
                        if c_btn2.button("❌ রিভিশন পাঠান (Send to Revision)", key=f"rev_btn_{index}"):
                            conn = sqlite3.connect(DB_FILE)
                            cursor = conn.cursor()
                            cursor.execute('UPDATE tasks SET status="Revision", revision_note=? WHERE id=?', (rev_text if rev_text else "আবার চেক করুন", row['id']))
                            conn.commit()
                            conn.close()
                            trigger_live_notification(f"🔧 এডিটর {row['editor']} এর কাজে রিভিশন দেওয়া হয়েছে!", "🎬 আমার এডিটিং প্যানেল")
                            st.rerun()

    # ==========================================
    # ১১. প্রিমিয়াম চ্যাট হাব (১:১ লাইভ চ্যাট)
    # ==========================================
    elif st.session_state.current_navigation == "💬 প্রিমিয়াম চ্যাট হাব":
        st.title("💬 Vivid Live 1:1 প্রিমিয়াম চ্যাট হাব")
        
        all_members = list(USER_DB.keys())
        if current_user in all_members:
            all_members.remove(current_user)
            
        selected_peer = st.selectbox("👤 কার সাথে পার্সোনাল চ্যাট করবেন?", all_members)
        
        st.markdown("<div style='background-color: #0b141a; padding: 20px; border-radius: 12px; border: 1px solid #00a884; height: 350px; overflow-y: scroll;'>", unsafe_allow_html=True)
        for chat in st.session_state.global_chats:
            if chat["sender"] == current_user and chat["receiver"] == selected_peer:
                st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {chat['msg']}<br><small style='font-size:9px;color:#aebac1;'>{chat['time']}</small></div>", unsafe_allow_html=True)
            elif chat["sender"] == selected_peer and chat["receiver"] == current_user:
                st.markdown(f"<div class='chat-bubble-other'><b>{selected_peer.upper()}:</b> {chat['msg']}<br><small style='font-size:9px;color:#8696a0;'>{chat['time']}</small></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.form("chat_form_u4", clear_on_submit=True):
            msg_i = st.text_input("মেসেজ টাইপ করুন...")
            if st.form_submit_button("সেন্ড ✈️"):
                if msg_i:
                    st.session_state.global_chats.append({
                        "sender": current_user, "receiver": selected_peer, "msg": msg_i, "time": datetime.now().strftime("%I:%M %p")
                    })
                    trigger_live_notification(f"💬 {current_user} আপনাকে মেসেজ পাঠিয়েছেন!", "💬 প্রিমিয়াম চ্যাট হাব")
                    st.rerun()

    # ==========================================
    # ১২. নতুন ইউজার তৈরি (Admin Only - সেকশন ট্যাগ সহ)
    # ==========================================
    elif st.session_state.current_navigation == "➕ নতুন ইউজার তৈরি (Create User)":
        st.title("➕ নতুন টিম মেম্বার অ্যাকাউন্ট জেনারেটর")
        with st.form("cre_user_v4", clear_on_submit=True):
            n_u = st.text_input("ইউজার আইডি (Unique Username) *")
            n_p = st.text_input("পাসওয়ার্ড *")
            n_r = st.selectbox("রোল/পারমিশন লেভেল", ["Admin", "Manager", "Moderator", "Editor"])
            n_s = st.selectbox("সেকশন/বিভাগ", ["Production", "Studio", "Management"])
            
            if st.form_submit_button("সার্ভারে অ্যাকাউন্ট একটিভ করুন"):
                if n_u and n_p:
                    try:
                        conn = sqlite3.connect(DB_FILE)
                        cursor = conn.cursor()
                        cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (n_u, n_p, n_r, n_s))
                        conn.commit()
                        conn.close()
                        st.success(f"🎉 নতুন অ্যাকাউন্ট তৈরি হয়েছে: {n_u} ({n_s} সেকশন)")
                        st.rerun()
                    except:
                        st.error("এই ইউজারনেম অলরেডি আছে!")
