import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import random
import urllib.parse

# ১. পেজ সেটআপ ও নাম (Vivid Control Center)
st.set_page_config(page_title="Vivid Control Center", page_icon="🎬", layout="wide")

# --- ডাইনামিক মোটিভেশনাল বানী ও বিজনেস টিপস ---
MOTIVATION_SUCCESS = [
    "🎉 অসাধারণ! Vivid Vistas টিম এই মাসের টার্গেট ধুলোয় উড়িয়ে দিয়েছে! পরবর্তী বড় প্রজেক্টের জন্য ক্যামেরা চার্জ করুন! 🎥",
    "🚀 টার্গেট ফিল-আপ! প্রোডাকশন কোয়ালিটি যখন ওয়ার্ল্ড-ক্লাস হয়, সেলস তখন এমনিই আসে। পুরো টিমকে একটা ট্রিট দেওয়া যাক! 🍕",
    "💎 Boom! লক্ষ্য অর্জন হয়েছে। এবার সময় এসেছে আমাদের স্টুডিওর গিয়ার বা ইকুইপমেন্ট আপগ্রেড করার! 📸",
    "🌟 ইউজাররা আমাদের ভালোবাসে, তার প্রমাণ এই মাসের চার্ট! Vivid Vistas Productions এগিয়ে যাচ্ছে ফুল স্পিডে!",
    "🏆 মিশন কমপ্লিট! এই এনার্জিটাই ধরে রাখতে হবে। আমরা শুধু লোকাল না, গ্লোবাল স্ট্যান্ডার্ডে কাজ করছি!"
]

MOTIVATION_FAILURE = [
    "💡 টার্গেট মিস হয়েছে? নো টেনশন! ক্লায়েন্টদের ফলো-আপ ইমেইল পাঠান। পুরাতন ২০% কাস্টমার থেকেই ৮০% নতুন বিজনেস আসে!",
    "🎬 সিনেমাটিক শট যেমন ওয়ান-টেক-এ হয় না, বিজনেসও তেমন মাঝেমাঝে ড্রপ করে। ফেসবুক ও ইনস্টাগ্রামে নতুন رিলস/শর্টস ছাড়ুন, রিচ বাড়বে!",
    "🔥 'সাফল্য চূড়ান্ত নয়, ব্যর্থতাও শেষ নয়'—চলুন এই মাসে স্টুডিও সেকশনের মার্কেটিংয়ে একটু বেশি জোর দিই।",
    "📈 সেলস বাড়াতে অন্য কোনো ওয়েডিং এজেন্সি বা কর্পোরেট ব্র্যান্ডের সাথে কোলাবোরেশনে যান। নেটওয়ার্কিং-ই নেট-ওয়ার্থ!",
    "🔍 এই মাসের ডাটা অ্যানালাইসিস করুন: কোন সার্ভিসটা সবচেয়ে কম সেল হয়েছে? সেটার প্রাইসিং বা অফার রি-ডিজائن করুন।"
]

# --- ২. লাইভ রিফ্রেশ মেকানিজম (৫ সেকেন্ড পর পর অটো ডাটা রিড) ---
@st.cache_resource(ttl=5)
def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

def load_sheet_data(worksheet_name):
    try:
        df = get_connection().read(worksheet=worksheet_name)
        if df is None or df.empty:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()

# লাইভ ডাটা লোড (৩টি আলাদা ট্যাব থেকে)
df_orders = load_sheet_data("orders_db")
df_users = load_sheet_data("users_db")
df_tasks = load_sheet_data("tasks_db")

# --- ৩. আইডি, পাসওয়ার্ড ও রোলস ---
DEFAULT_USERS = {
    "admin": {"password": "123", "role": "Admin"},
    "manager": {"password": "456", "role": "Manager"},
    "moderator": {"password": "789", "role": "Moderator"}
}

USER_DB = DEFAULT_USERS.copy()
if not df_users.empty and "Username" in df_users.columns and "Password" in df_users.columns:
    for _, row in df_users.iterrows():
        u_id = str(row.get("Username", "")).strip()
        u_pass = str(row.get("Password", "")).strip()
        u_role = str(row.get("Role", "Moderator")).strip()
        if u_id and u_pass:
            USER_DB[u_id] = {"password": u_pass, "role": u_role}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = ""
    st.session_state.user = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- ৪. সাইডবার ডিজাইন ---
st.sidebar.markdown("<h2 style='text-align: center; color: #FF4B4B;'>🎬 VIVID SERVER</h2>", unsafe_allow_html=True)
st.sidebar.image("https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?w=400", caption="Vivid Control Center", use_container_width=True)

if not st.session_state.logged_in:
    st.title("🎬 Vivid Control Center — Admin Panel")
    username = st.text_input("ইউজার আইডি (Username)")
    password = st.text_input("পাসওয়ার্ড (Password)", type="password")
    
    if st.button("লগইন", use_container_width=True):
        if username in USER_DB and USER_DB[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.role = USER_DB[username]["role"]
            st.rerun()
        else:
            st.error("ভুল আইডি বা পাসওয়ার্ড!")
else:
    st.sidebar.title(f"👤 {st.session_state.user.upper()}")
    st.sidebar.info(f"অ্যাক্সেস লেভেল: **{st.session_state.role}**")
    
    # 🟢 লাইভ অ্যাক্টিভ মেম্বার সিস্টেম
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🟢 লাইভ অ্যাক্টিভ মেম্বার")
    st.sidebar.success(f"● {st.session_state.user} (Active Now)")
    st.sidebar.text("● editor_shakil (Idle)")
    st.sidebar.text("● manager_rahat (Away)")

    if st.sidebar.button("লগআউট", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # রোল অনুযায়ী মেনু ফিল্টার
    menu_options = ["📊 মেইন ড্যাশবোর্ড", "✍️ নতুন অর্ডার এন্ট্রি", "📋 টাস্ক ও ডেডলাইন ট্র্যাকার", "💬 Vivid WhatsApp Chat"]
    if st.session_state.role == "Admin":
        menu_options.append("➕ নতুন ইউজার তৈরি (Create User)")
        
    menu = st.sidebar.radio("মেনু নেভিগেশন", menu_options)

    # ==========================================
    # ৫. মেইন ড্যাশবোর্ড ও লাভ-ক্ষতি পেজ (পুরনো সব ফিচার সহ)
    # ==========================================
    if menu == "📊 মেইন ড্যাশবোর্ড":
        st.title("📊 Vivid Control Center — রিয়েল-টাইম অ্যানালিটিক্স")
        
        if df_orders.empty or "Total Package Price" not in df_orders.columns:
            st.warning("গুগল শিটে কোনো ডাটা পাওয়া যায়নি বা কানেকশন পেন্ডিং।")
        else:
            # অল-টাইম ডাটা টাইপ ও হিসাব ফিক্স করা (আগের ফিচার ফেরত আনা হলো)
            df_orders["Total"] = pd.to_numeric(df_orders["Total Package Price"], errors='coerce').fillna(0)
            df_orders["Advance"] = pd.to_numeric(df_orders["Advance Paid"], errors='coerce').fillna(0)
            df_orders["Due"] = pd.to_numeric(df_orders["Due Amount"], errors='coerce').fillna(0)
            df_orders["Editor_Cost"] = pd.to_numeric(df_orders.get("Editor Cost", 0), errors='coerce').fillna(0)
            df_orders["Op_Cost"] = pd.to_numeric(df_orders.get("Operation Cost", 0), errors='coerce').fillna(0)
            df_orders["Net_Profit"] = df_orders["Total"] - (df_orders["Editor_Cost"] + df_orders["Op_Cost"])
            
            if "Date" in df_orders.columns:
                df_orders["Month"] = pd.to_datetime(df_orders["Date"], errors='coerce').dt.strftime('%Y-%m')
                df_orders["Year"] = pd.to_datetime(df_orders["Date"], errors='coerce').dt.strftime('%Y')
            else:
                df_orders["Month"] = datetime.now().strftime("%Y-%m")
                df_orders["Year"] = datetime.now().strftime("%Y")

            # সাইডবার ফিল্টার
            st.sidebar.markdown("---")
            st.sidebar.subheader("📅 অটো REPORT FILTER")
            available_months = sorted(df_orders["Month"].astype(str).unique(), reverse=True)
            filter_type = st.sidebar.selectbox("রিপোর্টের ধরন", ["অল-টাইম (A-Z)", "মাসিক রিপোর্ট"])
            
            if filter_type == "মাসিক রিপোর্ট" and available_months:
                selected_month = st.sidebar.selectbox("মাস সিলেক্ট করুন", available_months)
                df_filtered = df_orders[df_orders["Month"].astype(str) == selected_month]
            else:
                df_filtered = df_orders

            # মাসিক সেলস টার্গেট ইনপুট
            st.sidebar.markdown("---")
            sales_target = st.sidebar.number_input("🎯 এই মাসের সেলস টার্গেট (BDT)", min_value=10000, value=100000, step=10000)
            
            # সামারি কার্ডস (আগের সব কস্টিং ক্যালকুলেশন সহ)
            total_sales = df_filtered["Total"].sum()
            total_profit = df_filtered["Net_Profit"].sum()
            total_due = df_filtered["Due"].sum()
            
            m1, m2, m3 = st.columns(3)
            m1.metric("💰 ফিল্টারকৃত মোট সেলস", f"{total_sales:,.0f} BDT")
            m2.metric("📈 নীট প্রফিট (লাভ)", f"{total_profit:,.0f} BDT")
            m3.metric("🚨 মার্কেট ডিউ (বাকি টাকা)", f"{total_due:,.0f} BDT", delta_color="inverse")
            
            # --- 🎯 সেলস টার্গেট ও মোটিভেশন জোন ---
            st.markdown("---")
            st.subheader("🎯 এই মাসের সেলস টার্গেট ও পারফরম্যান্স ট্র্যাকার")
            
            current_month_str = datetime.now().strftime("%Y-%m")
            current_month_sales = df_orders[df_orders["Month"].astype(str) == current_month_str]["Total"].sum() if "Month" in df_orders.columns else 0
            
            progress_pct = min(current_month_sales / sales_target, 1.0) if sales_target > 0 else 0.0
            
            col_p1, col_p2 = st.columns([2, 1])
            with col_p1:
                st.write(f"চলতি মাসের সেলস: **{current_month_sales:,.0f} BDT** / লক্ষ্য: **{sales_target:,.0f} BDT**")
                st.progress(progress_pct)
            with col_p2:
                st.subheader(f"📊 {progress_pct*100:.1f}% সম্পন্ন")
                
            # মোটিভেশনাল বক্স
            st.markdown("### 💬 Vivid Vistas বিজনেস বুস্টার জোন")
            if current_month_sales >= sales_target and sales_target > 0:
                msg = random.choice(MOTIVATION_SUCCESS)
                st.balloons()
                st.success(msg)
            else:
                msg = random.choice(MOTIVATION_FAILURE)
                st.info(msg)
                
            st.markdown("---")
            
            # ভিজ্যুয়াল চার্ট (Production vs Studio লাভ-ক্ষতি সহ)
            c_graph1, c_graph2 = st.columns(2)
            with c_graph1:
                st.subheader("🎬 সেকশন পারফরম্যান্স (Production vs Studio)")
                if "Section" in df_filtered.columns:
                    sec_df = df_filtered.groupby("Section")[["Total", "Net_Profit"]].sum().reset_index()
                    fig = px.bar(sec_df, x="Section", y=["Total", "Net_Profit"], barmode="group",
                                 labels={"value": "টাকা (BDT)", "variable": "ক্যাটাগরি"}, color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig, use_container_width=True)
                
            with c_graph2:
                st.subheader("📈 সার্ভিস অনুযায়ী সেলস ডিস্ট্রিবিউশন")
                if "Service Name" in df_filtered.columns:
                    srv_df = df_filtered.groupby("Service Name")["Total"].sum().reset_index()
                    fig_pie = px.pie(srv_df, values="Total", names="Service Name", hole=0.4)
                    st.plotly_chart(fig_pie, use_container_width=True)

            # ডাটা টেবিল রিপোর্ট
            st.subheader("📋 সম্পূর্ণ ডাটা রিপোর্ট শীট (A-Z)")
            st.dataframe(df_filtered.drop(columns=["Month", "Year"], errors='ignore'), use_container_width=True)

    # ==========================================
    # ৬. নতুন অর্ডার এন্ট্রি পেজ (আগের কস্টিং ইনপুট বক্স ফেরত আনা হলো)
    # ==========================================
    elif menu == "✍️ নতুন অর্ডার এন্ট্রি":
        st.title("📝 অর্ডার ও খরচের লাইভ ইনপুট")
        
        with st.form("order_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                client_name = st.text_input("ক্লায়েন্টের নাম *")
                client_phone = st.text_input("মোবাইল নাম্বার *")
                section = st.selectbox("বিভাগ (Section)", ["Production", "Studio"])
                service_name = st.text_input("সার্ভিসের নাম (e.g. Wedding, Commercial)")
            with c2:
                total_price = st.number_input("মোট চুক্তি (BDT)", min_value=0, value=0)
                advance_paid = st.number_input("এডভান্স পেমেন্ট (BDT)", min_value=0, value=0)
                camera_hours = st.number_input("ক্যামেরা রেন্ট কালীন সময় (Hours)", min_value=0.0, value=0.0)
            
            st.markdown("---")
            st.subheader("💸 কস্টিং বা খরচের হিসাব (আগের ফিচার)")
            c3, c4 = st.columns(2)
            with c3:
                editor_cost = st.number_input("এডিটর/কালারিস্ট বিল (BDT)", min_value=0, value=0)
            with c4:
                operation_cost = st.number_input("অন্যান্য অপারেশন কস্ট (BDT)", min_value=0, value=0)
                
            submit_btn = st.form_submit_button("সাইটে লাইভ সেভ করুন 🚀", use_container_width=True)
            
            if submit_btn:
                if not client_name or not client_phone:
                    st.error("ক্লায়েন্টের নাম এবং মোবাইল নাম্বার দেওয়া বাধ্যতামূলক!")
                else:
                    new_order = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d"), "Client Name": client_name, "Client Number": client_phone,
                        "Section": section, "Service Name": service_name, "Total Package Price": total_price,
                        "Advance Paid": advance_paid, "Due Amount": total_price - advance_paid, 
                        "Camera Rent Hours": camera_hours, "Editor Cost": editor_cost, "Operation Cost": operation_cost
                    }])
                    
                    updated_df = new_order if df_orders.empty else pd.concat([df_orders, new_order], ignore_index=True)
                    get_connection().update(worksheet="orders_db", data=updated_df)
                    st.success("🎉 চমৎকার! প্রজেক্ট ডাটা কস্টিং সহ লাইভ সেভ হয়েছে।")
                    st.cache_resource.clear()

    # ==========================================
    # ৭. টাস্ক ও ডেডлайн ট্র্যাকার (এডিটর প্যানেল + ড্রাইভ লিংক বক্স)
    # ==========================================
    elif menu == "📋 টাস্ক ও ডেডлайн ট্র্যাকার":
        st.title("📋 টাস্ক ডিস্ট্রিবিউশন ও ডেডлайн ট্র্যাকার")
        
        if st.session_state.role in ["Admin", "Manager"]:
            st.subheader("🎯 নতুন টাস্ক অ্যাসাইন করুন")
            with st.form("task_form", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    t_client = st.text_input("কোন ক্লায়েন্টের কাজ?")
                    t_editor = st.text_input("কোন এডিটরকে দিচ্ছেন? (Username)")
                with col2:
                    t_task = st.text_input("কী কাজ? (e.g. Wedding Teaser)")
                    t_deadline = st.date_input("ডেডлайн বা শেষ সময়")
                with col3:
                    t_phone = st.text_input("ক্লায়েন্টের হোয়াটসঅ্যাপ নাম্বার")
                    
                t_submit = st.form_submit_button("এডিটরকে টাস্ক দিন 📡")
                if t_submit:
                    new_task = pd.DataFrame([{
                        "Task ID": random.randint(1000, 9999), "Client": t_client, "Editor": t_editor,
                        "Task Detail": t_task, "Deadline": str(t_deadline), "Client Phone": t_phone,
                        "Status": "Pending", "Final File Link": "No Submission Yet"
                    }])
                    
                    updated_tasks = new_task if df_tasks.empty else pd.concat([df_tasks, new_task], ignore_index=True)
                    get_connection().update(worksheet="tasks_db", data=updated_tasks)
                    st.success(f"🔥 টাস্কটি সফলভাবে {t_editor} এর কাছে পাঠানো হয়েছে।")
                    st.cache_resource.clear()
                    st.rerun()

        st.markdown("---")
        st.subheader("🏃‍♂️ রানিং টাস্ক ও ডেডлайн লিস্ট")
        if df_tasks.empty or "Editor" not in df_tasks.columns:
            st.info("এই মুহূর্তে কোনো টাস্ক অ্যাসাইন করা নেই।")
        else:
            for index, row in df_tasks.iterrows():
                if st.session_state.role == "Admin" or str(row["Editor"]).strip() == st.session_state.user:
                    with st.expander(f"📌 Task for {row.get('Client', 'Unknown')} | 📅 Deadline: {row.get('Deadline', 'N/A')} | 🚦 Status: {row.get('Status', 'Pending')}"):
                        st.write(f"**কাজের বিবরণ:** {row.get('Task Detail', '')}")
                        st.write(f"**দায়িত্বরত এডিটর:** {row.get('Editor', '')}")
                        st.write(f"**ফাইনাল ফাইল লিংক:** {row.get('Final File Link', '')}")
                        
                        new_link = st.text_input("ফাইন্যাল কাজের ড্রাইভ/ডাউনলোড লিংক সাবমিট করুন", key=f"link_{index}")
                        status_update = st.selectbox("কাজের আপডেট পরিবর্তন করুন", ["Pending", "In Progress", "Completed"], key=f"status_{index}")
                        
                        if st.button("আপডেট সাবমিট করুন 💾", key=f"btn_{index}"):
                            df_tasks.at[index, "Status"] = status_update
                            if new_link:
                                df_tasks.at[index, "Final File Link"] = new_link
                            get_connection().update(worksheet="tasks_db", data=df_tasks)
                            st.success("✅ কাজের প্রোগ্রেস ও ফাইল লিংক সার্ভারে আপলোড হয়েছে!")
                            st.cache_resource.clear()
                            st.rerun()

    # ==========================================
    # ৮. কাস্টম ইউজার ক্রিয়েশন (Admin Only + ওয়ান ক্লিক কপি)
    # ==========================================
    elif menu == "➕ নতুন ইউজার তৈরি (Create User)":
        st.title("➕ নতুন টিম মেম্বার অ্যাকাউন্ট তৈরি করুন")
        
        with st.form("user_creation_form", clear_on_submit=True):
            new_uid = st.text_input("নতুন ইউজার আইডি (Username) *")
            new_pass = st.text_input("লগইন পাসওয়ার্ড (Password) *")
            new_role = st.selectbox("ইউজার রোল (Role)", ["Admin", "Manager", "Moderator"])
            
            u_submit = st.form_submit_button("অ্যাকাউন্ট তৈরি করুন 🛠️")
            if u_submit:
                if not new_uid or not new_pass:
                    st.error("আইডি এবং পাসওয়ার্ড দুইটাই দিতে হবে!")
                else:
                    new_user_row = pd.DataFrame([{"Username": new_uid, "Password": new_pass, "Role": new_role}])
                    updated_users = new_user_row if df_users.empty else pd.concat([df_users, new_user_row], ignore_index=True)
                    get_connection().update(worksheet="users_db", data=updated_users)
                    st.success(f"🎉 অ্যাকাউন্ট রেডি! ইউজার আইডি: {new_uid}")
                    st.cache_resource.clear()
                    st.rerun()
                    
        st.markdown("---")
        st.subheader("👥 বর্তমান টিম মেম্বার লিস্ট ও চাবি (Credentials)")
        if not df_users.empty and "Username" in df_users.columns:
            for i, r in df_users.iterrows():
                col_u, col_p, col_r, col_c = st.columns([2,2,2,2])
                col_u.text(f"ID: {r.get('Username', '')}")
                col_p.text(f"Pass: {r.get('Password', '')}")
                col_r.info(f"Role: {r.get('Role', 'Moderator')}")
                col_c.code(f"{r.get('Username', '')}:{r.get('Password', '')}")

    # ==========================================
    # ৯. হোয়াটসঅ্যাপ লাইভ চ্যাট হাব
    # ==========================================
    elif menu == "💬 Vivid WhatsApp Chat":
        st.title("💬 Vivid WhatsApp Live Hub")
        
        target_phone = st.text_input("যাকে মেসেজ পাঠাতে চান তার ফোন নাম্বার লিখুন (e.g. 88017XXXXXXXX)")
        
        st.markdown("<div style='background-color: #0d141b; padding: 20px; border-radius: 10px; border: 1px solid #00a884;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #00a884; margin-top:0;'>🟢 Live Chat Terminal</h4>", unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            if msg["sender"] == "You":
                st.markdown(f"<p style='text-align: right; color: #d9fdd3; background-color: #005c4b; padding: 8px; border-radius: 5px; display: block; margin-left: auto; max-width: 60%;'>{msg['text']}</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='text-align: left; color: #e9edef; background-color: #202c33; padding: 8px; border-radius: 5px; display: block; max-width: 60%;'>{msg['text']}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        chat_msg = st.text_input("আপনার মেসেজটি এখানে টাইপ করুন...")
        if st.button("মেসেজ পাঠান 📲", use_container_width=True):
            if chat_msg and target_phone:
                st.session_state.chat_history.append({"sender": "You", "text": chat_msg})
                encoded_msg = urllib.parse.quote(chat_msg)
                wa_url = f"https://api.whatsapp.com/send?phone={target_phone}&text={encoded_msg}"
                st.markdown(f'<a href="{wa_url}" target="_blank" style="background-color:#25D366;color:white;padding:10px 20px;text-align:center;text-decoration:none;display:block;border-radius:5px;font-weight:bold;">👉 Click to Confirm & Send via WhatsApp Backup Gateway 👈</a>', unsafe_allow_html=True)
            else:
                st.error("ফোন নাম্বার এবং মেসেজ দুটোই দেওয়া আবশ্যক!")
