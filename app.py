import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime
import random

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
    "🎬 সিনেমাটিক শট যেমন ওয়ান-টেক-এ হয় না, বিজনেসও তেমন মাঝেমাঝে ড্রপ করে। ফেসবুক ও ইনস্টাগ্রামে নতুন রিলস/শর্টস ছাড়ুন, রিচ বাড়বে!",
    "🔥 'সাফল্য চূড়ান্ত নয়, ব্যর্থতাও শেষ নয়'—চলুন এই মাসে স্টুডিও সেকশনের মার্কেটিংয়ে একটু বেশি জোর দিই।",
    "📈 সেলস বাড়াতে অন্য কোনো ওয়েডিং এজেন্সি বা কর্পোরেট ব্র্যান্ডের সাথে কোলাবোরেশনে যান। নেটওয়ার্কিং-ই নেট-ওয়ার্থ!",
    "🔍 এই মাসের ডাটা অ্যানালাইসিস করুন: কোন সার্ভিসটা সবচেয়ে কম সেল হয়েছে? সেটার প্রাইসিং বা অফার রি-ডিজাইন করুন।"
]

# --- ২. নতুন নিয়মে গুগল শিট লাইভ কানেকশন ---
@st.cache_resource(ttl=5) # প্রতি ৫ সেকেন্ড পর পর ডাটা অটো রিফ্রেশ হবে
def connect_sheet():
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception:
        return None

conn = connect_sheet()

def load_data():
    if conn:
        try:
            # শিটের প্রথম ট্যাব থেকে ডাটা রিড করা
            return conn.read(worksheet="vivid_vistas_db")
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

df_main = load_data()

# --- ৩. আইডি, পাসওয়ার্ড ও রোলস ---
USER_DB = {
    "admin": {"password": "123", "role": "Admin"},
    "manager": {"password": "456", "role": "Manager"},
    "moderator": {"password": "789", "role": "Moderator"}
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = ""
    st.session_state.user = ""

# --- ৪. সাইডবার ডিজাইন ---
# আপনার স্ক্রিনশটের ভুলটি এখানে ফিক্স করে দেওয়া হয়েছে (unsafe_allow_html=True)
st.sidebar.markdown("<h2 style='text-align: center; color: #FF4B4B;'>🎬 VIVID VISTAS</h2>", unsafe_allow_html=True)
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
    if st.sidebar.button("লগআউট", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # রোল অনুযায়ী মেনু ফিল্টার
    if st.session_state.role in ["Admin", "Manager"]:
        menu = st.sidebar.radio("মেনু নেভিগেশন", ["📊 মেইন ড্যাশবোর্ড", "✍️ নতুন অর্ডার এন্ট্রি"])
    else:
        menu = "✍️ নতুন অর্ডার এন্ট্রি"

    # ==========================================
    # ৫. নতুন অর্ডার এন্ট্রি পেজ
    # ==========================================
    if menu == "✍️ নতুন অর্ডার এন্ট্রি":
        st.title("📝 অর্ডার ও খরচের লাইভ ইনপুট")
        st.write("এখানে সাবমিট করলেই গুগল শিট ব্যাকএন্ডে অটো আপডেট হবে।")
        
        with st.form("live_input_form", clear_on_submit=True):
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
            st.subheader("💸 কস্টিং বা খরচের হিসাব")
            c3, c4 = st.columns(2)
            with c3:
                editor_cost = st.number_input("এডিটর/কালারিস্ট বিল (BDT)", min_value=0, value=0)
            with c4:
                operation_cost = st.number_input("অন্যান্য অপারেশন কস্ট (BDT)", min_value=0, value=0)
                
            submit_btn = st.form_submit_button("সাইটে লাইভ সেভ করুন 🚀", use_container_width=True)
            
            if submit_btn:
                if not client_name or not client_phone:
                    st.error("ক্লায়েন্টের নাম এবং মোবাইল নাম্বার দেওয়া বাধ্যতামূলক!")
                elif conn is None:
                    st.error("গুগল শিট কানেকশন পাওয়া যায়নি!")
                else:
                    due_amount = total_price - advance_paid
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    current_month = datetime.now().strftime("%Y-%m")
                    current_year = datetime.now().strftime("%Y")
                    
                    # নতুন ডাটার রো রেডি করা
                    new_row = pd.DataFrame([{
                        "Date": current_date, "Client Name": client_name, "Client Number": client_phone,
                        "Section": section, "Service Name": service_name, "Total Package Price": total_price,
                        "Advance Paid": advance_paid, "Due Amount": due_amount, "Camera Rent Hours": camera_hours,
                        "Editor Cost": editor_cost, "Operation Cost": operation_cost, "Month": current_month, "Year": current_year
                    }])
                    
                    try:
                        # ডাটা গুগল শিটের নিচে যুক্ত করা
                        updated_df = pd.concat([df_main, new_row], ignore_index=True)
                        conn.update(worksheet="vivid_vistas_db", data=updated_df)
                        st.success(f"🎉 চমৎকার! {client_name}-এর ডাটা সরাসরি ওয়েবসাইটে আপডেট করা হয়েছে।")
                        st.cache_resource.clear() 
                    except Exception as e:
                        st.error("ডাটা সেভ করতে সমস্যা হচ্ছে। গুগল শিটের পারমিশন চেক করুন।")

    # ==========================================
    # ৬. মেইন ড্যাশবোর্ড ও লাভ-ক্ষতি পেজ
    # ==========================================
    elif menu == "📊 মেইন ড্যাশবোর্ড":
        st.title("📊 Vivid Control Center — রিয়েল-টাইম অ্যানালিটিক্স")
        
        if df_main.empty:
            st.warning("গুগল শিটে কোনো ডাটা পাওয়া যায়নি বা কানেকশন পেন্ডিং।")
        else:
            # ডাটা টাইপ ফিক্স করা
            df_main["Total"] = pd.to_numeric(df_main["Total Package Price"], errors='coerce').fillna(0)
            df_main["Advance"] = pd.to_numeric(df_main["Advance Paid"], errors='coerce').fillna(0)
            df_main["Due"] = pd.to_numeric(df_main["Due Amount"], errors='coerce').fillna(0)
            df_main["Editor_Cost"] = pd.to_numeric(df_main["Editor Cost"], errors='coerce').fillna(0)
            df_main["Op_Cost"] = pd.to_numeric(df_main["Operation Cost"], errors='coerce').fillna(0)
            df_main["Net_Profit"] = df_main["Total"] - (df_main["Editor_Cost"] + df_main["Op_Cost"])
            
            # সাইডবার ফিল্টার
            st.sidebar.markdown("---")
            st.sidebar.subheader("📅 অটো রিপোর্ট ফিল্টার")
            available_months = sorted(df_main["Month"].astype(str).unique(), reverse=True)
            available_years = sorted(df_main["Year"].astype(str).unique(), reverse=True)
            
            filter_type = st.sidebar.selectbox("রিপোর্টের ধরন", ["মাসিক রিপোর্ট", "বার্ষিক রিপোর্ট", "অল-টাইম (A-Z)"])
            
            if filter_type == "মাসিক রিপোর্ট":
                selected_month = st.sidebar.selectbox("মাস সিলেক্ট করুন", available_months)
                df_filtered = df_main[df_main["Month"].astype(str) == selected_month]
            elif filter_type == "বার্ষিক রিপোর্ট":
                selected_year = st.sidebar.selectbox("বছর সিলেক্ট করুন", available_years)
                df_filtered = df_main[df_main["Year"].astype(str) == selected_year]
            else:
                df_filtered = df_main

            # মাসিক সেলস টার্গেট ইনপুট
            st.sidebar.markdown("---")
            sales_target = st.sidebar.number_input("🎯 এই মাসের সেলস টার্গেট (BDT)", min_value=10000, value=100000, step=10000)
            
            # চলতি মাসের মোট সেলস ক্যালকুলেশন
            current_month_str = datetime.now().strftime("%Y-%m")
            current_month_sales = df_main[df_main["Month"].astype(str) == current_month_str]["Total"].sum()
            
            # ড্যাশবোর্ডের মূল সামারি কার্ডস
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
            
            progress_pct = min(current_month_sales / sales_target, 1.0) if sales_target > 0 else 0.0
            
            col_p1, col_p2 = st.columns([2, 1])
            with col_p1:
                st.write(f"চলতি মাসের সেলস: **{current_month_sales:,.0f} BDT** / লক্ষ্য: **{sales_target:,.0f} BDT**")
                st.progress(progress_pct)
            with col_p2:
                st.subheader(f"📊 {progress_pct*100:.1f}% সম্পন্ন")
                
            # মোтивнойেশনাল বক্স
            st.markdown("### 💬 Vivid Vistas বিজনেস বুস্টার জোন")
            if current_month_sales >= sales_target:
                msg = random.choice(MOTIVATION_SUCCESS)
                st.balloons()
                st.success(msg)
            else:
                msg = random.choice(MOTIVATION_FAILURE)
                st.info(msg)
                
            st.markdown("---")
            
            # ভিজ্যুয়াল চার্ট
            c_graph1, c_graph2 = st.columns(2)
            with c_graph1:
                st.subheader("🎬 সেকশন পারফরম্যান্স (Production vs Studio)")
                sec_df = df_filtered.groupby("Section")[["Total", "Net_Profit"]].sum().reset_index()
                fig = px.bar(sec_df, x="Section", y=["Total", "Net_Profit"], barmode="group",
                             labels={"value": "টাকা (BDT)", "variable": "ক্যাটাগরি"}, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)
                
            with c_graph2:
                st.subheader("📈 সার্ভিস অনুযায়ী সেলস ডিস্ট্রিবিউশন")
                srv_df = df_filtered.groupby("Service Name")["Total"].sum().reset_index()
                fig_pie = px.pie(srv_df, values="Total", names="Service Name", hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)

            # অল-টাইম ডাটা টেবিল (A-Z)
            st.subheader("📋 সম্পূর্ণ ডাটা রিপোর্ট শীট (A-Z)")
            st.dataframe(df_filtered.drop(columns=["Month", "Year"], errors='ignore'), use_container_width=True)
