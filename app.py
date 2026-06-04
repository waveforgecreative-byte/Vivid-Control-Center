import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sqlite3
import random
import time

# ১. প্রিমিয়াম পেজ কনফিগারেশন ও কাস্টম থিমিং
st.set_page_config(page_title="Vivid Control Center ULTRA", page_icon="🎬", layout="wide")

st.markdown("""
<style>
    .reportview-container { background: #0b0e14; }
    .chat-bubble-user { background-color: #005c4b; color: #d9fdd3; padding: 12px; border-radius: 12px; margin: 8px 0; text-align: right; max-width: 75%; margin-left: auto; box-shadow: 1px 1px 5px rgba(0,0,0,0.2); }
    .chat-bubble-other { background-color: #202c33; color: #e9edef; padding: 12px; border-radius: 12px; margin: 8px 0; text-align: left; max-width: 75%; box-shadow: 1px 1px 5px rgba(0,0,0,0.2); }
    .active-dot { height: 12px; width: 12px; background-color: #00e676; border-radius: 50%; display: inline-block; margin-right: 8px; animate: pulse 2s infinite; }
    .status-badge { padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 12px; color: white; }
    .bg-pending { background-color: #ff9100; }
    .bg-started { background-color: #2979ff; }
    .bg-submitted { background-color: #00e676; }
    .bg-revision { background-color: #ff1744; }
</style>
""", unsafe_allow_html=True)

DB_FILE = "vivid_studio_ultra_v3.db"

# --- ২. ডাটাবেস আর্কিটেকচার (টাইমস্ট্যাম্প ও এডিটর পেমেন্ট সহ) ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, client_name TEXT, client_number TEXT,
        section TEXT, service_name TEXT, total_price REAL, advance_paid REAL, due_amount REAL,
        editor_name TEXT, editor_cost REAL, operation_cost REAL, month_tag TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY, client TEXT, editor TEXT, task_detail TEXT, 
        assign_time TEXT, start_time TEXT, submit_time TEXT,
        status TEXT, final_link TEXT, revision_note TEXT, editor_payment REAL)''')
    
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users VALUES ('admin', '123', 'Admin')")
        cursor.execute("INSERT INTO users VALUES ('manager', '456', 'Manager')")
        cursor.execute("INSERT INTO users VALUES ('moderator_crew', '789', 'Moderator')")
        cursor.execute("INSERT INTO users VALUES ('shakil', 'editor123', 'Editor')")
        cursor.execute("INSERT INTO users VALUES ('rahat', 'editor456', 'Editor')")
    conn.commit()
    conn.close()

init_db()

# --- ৩. ইন-মেমোরি রিয়েল-টাইম স্টেট ইঞ্জিন ---
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

# ডাটা ফেচিং ফাংশনসমূহ
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

USER_DB = {row["username"]: {"password": row["password"], "role": row["role"]} for _, row in df_users.iterrows()}

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
        col_n1.warning(f"🔔 **লাইভ অ্যালার্ট [{latest_notif['time']}]:** {latest_notif['text']}")
        if col_n2.button("সরাসরি প্যানেলে যান ⚡", key="notif_redirect"):
            st.session_state.current_navigation = latest_notif['target']
            st.session_state.notifications.pop()
            st.rerun()

# --- ৫. সাইডবার ও ইউজার ট্র্যাকিং ---
if not st.session_state.logged_in:
    st.title("🎬 Vivid Studio Ultra Server")
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
            st.error("ভুল তথ্য দিয়েছেন! আবার চেষ্টা করুন।")
else:
    current_user = st.session_state.user
    user_role = st.session_state.role
    update_activity(current_user)
    
    st.sidebar.markdown("<h2 style='color:#00e676; text-align:center;'>VIVID CORE</h2>", unsafe_allow_html=True)
    st.sidebar.write(f"👤 ইউজার: **{current_user.upper()}** | রোল: `{user_role}`")
    
    # লাইভ মেম্বার ট্র্যাকার
    st.sidebar.markdown("---")
    st.sidebar.markdown("🟢 **অনলাইন টিম মেম্বারস**")
    for user, last_seen in list(st.session_state.active_users.items()):
        if time.time() - last_seen < 300:
            st.sidebar.markdown(f"<span class='active-dot'></span> {user} (Live)", unsafe_allow_html=True)

    if st.sidebar.button("লগআউট 🚪", use_container_width=True):
        st.session_state.active_users.pop(current_user, None)
        st.session_state.logged_in = False
        st.rerun()

    # রোল ভিত্তিক ডাইনামিক মেনু বিন্যাস
    if user_role in ["Admin", "Manager"]:
        menu_options = ["📊 লাইভ ড্যাশবোর্ড", "📉 লাইভ প্রফিট ও রিপোর্ট হাব", "✍️ নতুন অর্ডার এন্ট্রি", "🎯 টাস্ক ডিস্ট্রিবিউটর", "💬 প্রিমিয়াম চ্যাট হাব"]
    elif user_role == "Moderator":
        menu_options = ["✍️ নতুন অর্ডার এন্ট্রি", "💬 প্রিমিয়াম চ্যাট হাব"]
    elif user_role == "Editor":
        menu_options = ["🎬 আমার এডিটিং প্যানেল", "💬 প্রিমিয়াম চ্যাট হাব"]
        
    if user_role == "Admin":
        menu_options.append("➕ নতুন ইউজার তৈরি (Create User)")

    # মেনু সিলেকশন সিঙ্ক করা
    if st.session_state.current_navigation not in menu_options:
        st.session_state.current_navigation = menu_options[0]
        
    selected_menu = st.sidebar.radio("সিস্টেম নেভিগেশন", menu_options, index=menu_options.index(st.session_state.current_navigation))
    st.session_state.current_navigation = selected_menu

    # ==========================================
    # ৬. মেইন লাইভ ড্যাশবোর্ড (Admin/Manager)
    # ==========================================
    if st.session_state.current_navigation == "📊 লাইভ ড্যাশবোর্ড":
        st.title("📊 লাইভ স্টুডিও ওভারভিউ ও অপারেশন ড্যাশবোর্ড")
        
        if df_orders.empty:
            st.info("সার্ভারে কোনো অর্ডার ডাটা নেই।")
        else:
            # লাভ-ক্ষতি ক্যালকুলেশন
            total_sales = df_orders["total_price"].sum()
            total_advance = df_orders["advance_paid"].sum()
            total_due = df_orders["due_amount"].sum()
            total_expenses = df_orders["editor_cost"].sum() + df_orders["operation_cost"].sum()
            net_profit = total_sales - total_expenses
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("💰 মোট সেলস ভলিউম", f"{total_sales:,.0f} BDT")
            m2.metric("📈 নীট প্রফিট (লাভ)", f"{net_profit:,.0f} BDT", delta=f"খরচ বাদে {net_profit:,.0f}")
            m3.metric("🚨 টোটাল মার্কেট ডিউ", f"{total_due:,.0f} BDT")
            m4.metric("📉 মোট স্টুডিও কস্ট", f"{total_expenses:,.0f} BDT")
            
            st.markdown("---")
            st.subheader("🏃‍♂️ রানিং প্রজেক্ট ও এডিটরদের লাইভ কাজের অবস্থা")
            if df_tasks.empty:
                st.write("কোনো রানিং টাস্ক নেই।")
            else:
                for _, t in df_tasks.iterrows():
                    st.markdown(f"""
                    **🎬 প্রজেক্ট:** {t['client']} | **👤 এডিটর:** {t['editor']} | **🚦 স্ট্যাটাস:** `{t['status']}`
                    * **অ্যাসাইন করা হয়েছে:** {t['assign_time']}
                    * **কাজ শুরু হয়েছে:** {t['start_time']}
                    * **ফাইনাল সাবমিশন:** {t['submit_time']}
                    * **এডিটর বিল:** {t['editor_payment']} BDT
                    ---
                    """)

    # ==========================================
    # ৭. লাইভ প্রফিট ও রিপোর্ট হাব (এক্সেল ছাড়া ইন-অ্যাপ ফিল্টার)
    # ==========================================
    elif st.session_state.current_navigation == "📉 লাইভ প্রফিট ও রিপোর্ট হাব":
        st.title("📉 ইন-অ্যাপ লাইভ মান্থলি ও ইয়ারলি রিপোর্ট")
        
        if df_orders.empty:
            st.info("কোনো ডাটা নেই।")
        else:
            df_orders["net_profit"] = df_orders["total_price"] - (df_orders["editor_cost"] + df_orders["operation_cost"])
            
            # এক্সেল ছাড়া ডাইনামিক ফিল্টার (ওয়েবসাইটেই সব থাকবে)
            month_list = sorted(df_orders["month_tag"].unique(), reverse=True)
            selected_month = st.selectbox("📅 কোন মাসের লাইভ ডাটা দেখতে চান?", month_list)
            
            filtered_df = df_orders[df_orders["month_tag"] == selected_month]
            
            st.markdown(f"### 📊 `{selected_month}` মাসের লাইভ ফাইন্যান্সিয়াল রিপোর্ট")
            
            c_s1, c_s2, c_s3 = st.columns(3)
            c_s1.metric("ঐ মাসের মোট সেলস", f"{filtered_df['total_price'].sum():,.0f} BDT")
            c_s2.metric("ঐ মাসের নীট প্রফিট", f"{filtered_df['net_profit'].sum():,.0f} BDT")
            c_s3.metric("ঐ মাসের মোট খরচ", f"{(filtered_df['editor_cost'].sum() + filtered_df['operation_cost'].sum()):,.0f} BDT")
            
            st.markdown("#### 📋 ডাটা শিট (ইনস্ট্যান্ট লাইভ)")
            st.dataframe(filtered_df[["date", "client_name", "service_name", "total_price", "advance_paid", "due_amount", "editor_name", "editor_cost", "net_profit"]], use_container_width=True)
            
            # প্রফিট ট্রেন্ড গ্রাফ (ওয়েবসাইটেই লাইভ শো করবে)
            st.markdown("#### 📈 প্রফিট অ্যানালাইসিস চার্ট")
            fig = px.bar(filtered_df, x="client_name", y="net_profit", color="service_name", title="ক্লায়েন্ট ভিত্তিক নীট প্রফিট মার্জিন", labels={"net_profit":"Net Profit (BDT)", "client_name":"Client"})
            st.plotly_chart(fig, use_container_width=True)

    # ==========================================
    # ৮. নতুন অর্ডার এন্ট্রি পেজ (Moderator/Admin/Manager)
    # ==========================================
    elif st.session_state.current_navigation == "✍️ নতুন অর্ডার এন্ট্রি":
        st.title("📝 নতুন ক্লায়েন্ট ডাটা ও অর্ডার এন্ট্রি")
        with st.form("order_form_ultra", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                cl_name = st.text_input("ক্লায়েন্টের নাম *")
                cl_phone = st.text_input("মোবাইল নাম্বার *")
                sec = st.selectbox("সেকশন", ["Production", "Studio"])
                srv = st.text_input("সার্ভিস/প্যাকেজ নাম")
            with col2:
                t_p = st.number_input("টোটাল ডিল প্রাইস (BDT)", min_value=0)
                a_p = st.number_input("এডভান্স রিসিভড (BDT)", min_value=0)
                ed_n = st.selectbox("দায়িত্বরত এডিটর", [u for u in USER_DB if USER_DB[u]["role"] == "Editor"])
                ed_c = st.number_input("এডিটর বাজেট/বিল (BDT)", min_value=0)
                op_c = st.number_input("অন্যান্য অপারেশন কস্ট (BDT)", min_value=0)
                
            if st.form_submit_button("সার্ভারে লাইভ এন্ট্রি দিন 🚀"):
                if cl_name and cl_phone:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    current_month = datetime.now().strftime("%Y-%m")
                    cursor.execute('''INSERT INTO orders VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                   (datetime.now().strftime("%Y-%m-%d"), cl_name, cl_phone, sec, srv, t_p, a_p, t_p-a_p, ed_n, ed_c, op_c, current_month))
                    conn.commit()
                    conn.close()
                    trigger_live_notification(f"✍️ নতুন অর্ডার যুক্ত হয়েছে: {cl_name} (বাই {current_user})", "📊 লাইভ ড্যাশবোর্ড")
                    st.success("🎉 অর্ডার ডাটা সার্ভারে লাইভ যুক্ত হয়েছে!")
                    st.rerun()

    # ==========================================
    # ৯. টাস্ক ডিস্ট্রিবিউটর (Admin/Manager ONLY)
    # ==========================================
    elif st.session_state.current_navigation == "🎯 টাস্ক ডিস্ট্রিবিউটর":
        st.title("🎯 এডিটরদের কাজ অ্যাসাইনমেন্ট ও লাইভ পেমেন্ট ট্র্যাকার")
        with st.form("task_dist_form", clear_on_submit=True):
            cx1, cx2 = st.columns(2)
            with cx1:
                t_cl = st.text_input("ক্লায়েন্টের নাম")
                t_ed = st.selectbox("এডিটর সিলেক্ট করুন", [u for u in USER_DB if USER_DB[u]["role"] == "Editor"])
                t_dt = st.text_area("কাজের বিবরণ ও ইন্সট্রাকশন")
            with cx2:
                t_pay = st.number_input("এই কাজের জন্য এডিটর কত টাকা পাবেন? (BDT)", min_value=0)
                
            if st.form_submit_button("📡 এডিটর প্যানেলে লাইভ পুশ দিন"):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                assign_timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                cursor.execute('INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                               (random.randint(10000, 99999), t_cl, t_ed, t_dt, assign_timestamp, "Not Started Yet", "Not Submitted Yet", "Pending", "No Link", "No Revision Note", t_pay))
                conn.commit()
                conn.close()
                trigger_live_notification(f"🎬 {t_ed} এর জন্য নতুন প্রজেক্ট অ্যাসাইন করা হয়েছে!", "🎬 আমার এডিটিং প্যানেল")
                st.success("🔥 কাজ সফলভাবে এডিটরের কাছে লাইভ পাঠিয়ে দেওয়া হয়েছে!")
                st.rerun()

    # ==========================================
    # ১০. এডিটর লাইভ ওয়ার্কস্টেশন Panel (Editor Only)
    # ==========================================
    elif st.session_state.current_navigation == "🎬 আমার এডিটিং প্যানেল":
        st.title("🎬 Editor Live Workstation")
        st.subheader(f"স্বাগতম {current_user.upper()}, আপনার বর্তমান প্রজেক্টগুলোর লিস্ট নিচে দেওয়া হলো:")
        
        my_tasks = df_tasks[df_tasks["editor"] == current_user]
        
        if my_tasks.empty:
            st.info("আপনার কাছে এই মুহূর্তে কোনো কাজ অ্যাসাইন করা নেই।")
        else:
            for index, row in my_tasks.iterrows():
                with st.expander(f"📌 ক্লায়েন্ট: {row['client']} | 🚦 স্ট্যাটাস: {row['status']} | 💰 আপনার পেমেন্ট: {row['editor_payment']} BDT"):
                    st.write(f"**📝 কাজের বিবরণ:** {row['task_detail']}")
                    st.write(f"📅 **অ্যাসাইন করার সময়:** {row['assign_time']}")
                    st.write(f"⏱️ **কাজ শুরু করার সময়:** {row['start_time']}")
                    st.error(f"🔧 **রিভিশন নোট (অ্যাডমিন থেকে):** {row['revision_note']}")
                    
                    # লাইভ স্ট্যাটাস অ্যাকশন বাটনসমূহ
                    col_b1, col_b2 = st.columns(2)
                    
                    if row['status'] == "Pending":
                        if col_b1.button("🎬 কাজ শুরু করুন (Start Work)", key=f"strt_{index}"):
                            conn = sqlite3.connect(DB_FILE)
                            cursor = conn.cursor()
                            cursor.execute('UPDATE tasks SET status="Started", start_time=? WHERE id=?', (datetime.now().strftime("%I:%M %p (%d %b)"), row['id']))
                            conn.commit()
                            conn.close()
                            trigger_live_notification(f"⚡ এডিটর {current_user} কাজ শুরু করেছেন! ক্লায়েন্ট: {row['client']}", "📊 লাইভ ড্যাশবোর্ড")
                            st.rerun()
                            
                    if row['status'] in ["Started", "Revision"]:
                        drive_link = st.text_input("ফাইনাল কাজের ড্রাইভ লিংক এখানে দিন:", value=row['final_link'], key=f"lnk_{index}")
                        if col_b2.button("🚀 কাজ জমা দিন (Submit Work)", key=f"sub_{index}"):
                            if drive_link and drive_link != "No Link":
                                conn = sqlite3.connect(DB_FILE)
                                cursor = conn.cursor()
                                cursor.execute('UPDATE tasks SET status="Submitted", final_link=?, submit_time=? WHERE id=?', (drive_link, datetime.now().strftime("%I:%M %p (%d %b)"), row['id']))
                                conn.commit()
                                conn.close()
                                trigger_live_notification(f"🟢 এডিটর {current_user} কাজ জমা দিয়েছেন! প্রজেক্ট: {row['client']}", "📊 লাইভ ড্যাশবোর্ড")
                                st.rerun()
                            else:
                                st.error("জমা দেওয়ার আগে অবশ্যই ড্রাইভ লিংক যোগ করুন!")

        # অ্যাডমিন বা ম্যানেজারের রিভিশন পুশ করার জন্য মেইন প্যানেল অপশন (টাস্ক ট্র্যাকার সেকশনের ভেতর)
        if user_role in ["Admin", "Manager"]:
            st.markdown("---")
            st.subheader("🛠️ সাবমিটেড কাজ চেক ও রিভিশন কন্ট্রোল (Admin View)")
            for index, row in df_tasks.iterrows():
                if row['status'] == "Submitted":
                    with st.container():
                        st.info(f"🎯 প্রজেক্ট: {row['client']} | এডিটর: {row['editor']} | লিংক: {row['final_link']}")
                        rev_text = st.text_area("রিভিশন দিতে চাইলে নোট লিখুন:", key=f"rev_text_{index}")
                        c_btn1, c_btn2 = st.columns(2)
                        if c_btn1.button("✅ কাজ সম্পূর্ণ পছন্দ হয়েছে (Complete)", key=f"app_{index}"):
                            conn = sqlite3.connect(DB_FILE)
                            cursor = conn.cursor()
                            cursor.execute('UPDATE tasks SET status="Completed" WHERE id=?', (row['id'],))
                            conn.commit()
                            conn.close()
                            st.success("প্রজেক্ট কমপ্লিট হিসেবে সেভ করা হয়েছে!")
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
        st.title("💬 Vivid Live 1:1 প্রিমিয়াম কমিউনিকেশন হাব")
        
        all_members = list(USER_DB.keys())
        if current_user in all_members:
            all_members.remove(current_user)
            
        selected_peer = st.selectbox("👤 কার সাথে সিকিউরড চ্যাট করবেন?", all_members)
        
        st.markdown("<div style='background-color: #0b141a; padding: 20px; border-radius: 12px; border: 1px solid #00a884; height: 380px; overflow-y: scroll;'>", unsafe_allow_html=True)
        for chat in st.session_state.global_chats:
            if chat["sender"] == current_user and chat["receiver"] == selected_peer:
                st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {chat['msg']}<br><small style='font-size:9px;color:#aebac1;'>{chat['time']}</small></div>", unsafe_allow_html=True)
            elif chat["sender"] == selected_peer and chat["receiver"] == current_user:
                st.markdown(f"<div class='chat-bubble-other'><b>{selected_peer.upper()}:</b> {chat['msg']}<br><small style='font-size:9px;color:#8696a0;'>{chat['time']}</small></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.form("chat_form_u", clear_on_submit=True):
            msg_i = st.text_input("আপনার মেসেজটি টাইপ করুন...")
            if st.form_submit_button("সেন্ড ✈️"):
                if msg_i:
                    st.session_state.global_chats.append({
                        "sender": current_user, "receiver": selected_peer, "msg": msg_i, "time": datetime.now().strftime("%I:%M %p")
                    })
                    trigger_live_notification(f"💬 {current_user} আপনাকে একটি মেসেজ পাঠিয়েছেন!", "💬 প্রিমিয়াম চ্যাট হাব")
                    st.rerun()

    # ==========================================
    # ১২. নতুন ইউজার তৈরি (Admin Only)
    # ==========================================
    elif st.session_state.current_navigation == "➕ নতুন ইউজার তৈরি (Create User)":
        st.title("➕ নতুন টিম মেম্বার ক্রেডেনশিয়াল জেনারেটর")
        with st.form("cre_user", clear_on_submit=True):
            n_u = st.text_input("ইউজার আইডি (Unique Username) *")
            n_p = st.text_input("পাসওয়ার্ড *")
            n_r = st.selectbox("রোল/পারমিশন লেভেল", ["Admin", "Manager", "Moderator", "Editor"])
            if st.form_submit_button("সার্ভারে অ্যাকাউন্ট একটিভ করুন"):
                if n_u and n_p:
                    try:
                        conn = sqlite3.connect(DB_FILE)
                        cursor = conn.cursor()
                        cursor.execute('INSERT INTO users VALUES (?, ?, ?)', (n_u, n_p, n_r))
                        conn.commit()
                        conn.close()
                        st.success(f"🎉 নতুন {n_r} অ্যাকাউন্ট সফলভাবে ক্রিয়েট হয়েছে!")
                        st.rerun()
                    except:
                        st.error("এই ইউজারনেম অলরেডি এক্সিস্ট করে!")
