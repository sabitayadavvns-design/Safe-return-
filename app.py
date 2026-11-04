import streamlit as st
import qrcode
from io import BytesIO
import random

# Page setup optimized for mobile view
st.set_page_config(
    page_title="SafeReturn Mobile",
    page_icon="🎒",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a native mobile app look
st.markdown("""
    <style>
    .stButton button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-weight: bold;
    }
    .stTextInput input, .stTextArea textarea {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State Databases
if "items_db" not in st.session_state:
    st.session_state.items_db = {
        "ITEM-101": {
            "name": "Aarav Sharma",
            "class": "Class 10-A",
            "item_name": "Steel Water Bottle",
            "status": "Lost",
            "zone": "School Canteen",
            "message": "",
            "thank_you": ""
        }
    }

if "karma_db" not in st.session_state:
    # Stores finder's name and their karma points/badges
    st.session_state.karma_db = {
        "Priya Patel": {"points": 30, "badge": "⭐ Campus Hero"},
        "Rahul Sen": {"points": 10, "badge": "🛡️ Guardian"}
    }

if "messages_db" not in st.session_state:
    st.session_state.messages_db = []

# App Header
st.markdown("<h2 style='text-align: center;'>🎒 SafeReturn</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Smart Privacy-First Item Recovery & Karma Hub</p>", unsafe_allow_html=True)

# Mobile-Friendly Navigation Tabs (4 Tabs now!)
tab1, tab2, tab3, tab4 = st.tabs(["📝 Register", "🔍 Scan", "🎉 Recover", "🏆 Hero Board"])

# ==========================================
# TAB 1: STUDENT REGISTRATION (CREATE QR)
# ==========================================
with tab1:
    st.subheader("Get Your QR Tag")
    
    with st.form("reg_form", clear_on_submit=True):
        student_name = st.text_input("Your Name", placeholder="e.g., Rohan Verma")
        student_class = st.text_input("Class & Section", placeholder="e.g., Class 10-B")
        item_name = st.text_input("Item Name", placeholder="e.g., Geometry Box")
        
        submitted = st.form_submit_button("Generate QR Code")
        
        if submitted:
            if student_name and student_class and item_name:
                item_id = f"ITEM-{random.randint(1000, 9999)}"
                
                st.session_state.items_db[item_id] = {
                    "name": student_name,
                    "class": student_class,
                    "item_name": item_name,
                    "status": "Safe",
                    "zone": "None",
                    "message": "",
                    "thank_you": ""
                }
                
                st.success(f"Generated! ID: **{item_id}**")
                
                # Generate QR code image
                img = qrcode.make(item_id)
                buf = BytesIO()
                img.save(buf, format="PNG")
                
                st.image(buf.getvalue(), caption=f"Sticker for: {item_name} (ID: {item_id})", width=180)
                st.info("📲 Take a screenshot of this QR code to stick on your item!")
            else:
                st.error("Please fill in all details.")

# ==========================================
# TAB 2: FINDER VIEW (SCAN QR & ZONE SELECTOR)
# ==========================================
with tab2:
    st.subheader("Found an Item?")
    
    item_id_input = st.text_input("Enter Scanned Item ID", value="ITEM-101")
    
    if item_id_input in st.session_state.items_db:
        item_info = st.session_state.items_db[item_id_input]
        
        st.warning(f"📦 Found a **{item_info['item_name']}** belonging to **{item_info['class']}**.")
        st.markdown("<small>🔒 Phone numbers are hidden for safety. Send a drop-off note:</small>", unsafe_allow_html=True)
        
        with st.form("finder_form"):
            finder_name = st.text_input("Your Name (To earn Karma Points!)", placeholder="e.g., Sneha")
            
            # Feature 1: Campus Zone Dropdown
            school_zones = [
                "📚 School Library", 
                "🍔 School Canteen", 
                "⚽ Sports Ground", 
                "💻 Computer Lab", 
                "🏫 Main Auditorium",
                "🚪 Corridor / Hallway"
            ]
            selected_zone = st.selectbox("Where did you find it?", school_zones)
            
            finder_msg = st.text_area("Additional notes for owner:", placeholder="e.g., Left with the front desk officer.")
            send_btn = st.form_submit_button("Send Secure Message & Earn Karma")
            
            if send_btn:
                if finder_msg and finder_name:
                    # Update Item Status
                    st.session_state.items_db[item_id_input]["status"] = "Found!"
                    st.session_state.items_db[item_id_input]["zone"] = selected_zone
                    st.session_state.items_db[item_id_input]["message"] = finder_msg
                    
                    # Log message
                    st.session_state.messages_db.append({
                        "item_id": item_id_input,
                        "item": item_info['item_name'],
                        "owner": item_info['name'],
                        "finder": finder_name,
                        "zone": selected_zone,
                        "message": finder_msg
                    })
                    
                    # Feature 2: Gamified Karma Points Addition
                    if finder_name not in st.session_state.karma_db:
                        st.session_state.karma_db[finder_name] = {"points": 0, "badge": "🌱 Good Samaritan"}
                    
                    st.session_state.karma_db[finder_name]["points"] += 15
                    if st.session_state.karma_db[finder_name]["points"] >= 30:
                        st.session_state.karma_db[finder_name]["badge"] = "⭐ Campus Hero"
                    elif st.session_state.karma_db[finder_name]["points"] >= 15:
                        st.session_state.karma_db[finder_name]["badge"] = "🛡️ Trusted Guardian"
                        
                    st.success(f"✅ Message sent! You earned +15 Karma Points, {finder_name}!")
                else:
                    st.error("Please enter your name and a message.")
    else:
        st.error("Invalid Item ID. Try entering 'ITEM-101'.")

# ==========================================
# TAB 3: RECOVERY LOOP & THANK YOU NOTE
# ==========================================
with tab3:
    st.subheader("Mark Item as Recovered")
    st.markdown("<small>Got your item back? Close the loop and thank the finder!</small>", unsafe_allow_html=True)
    
    with st.form("recovery_form"):
        rec_id = st.text_input("Your Item ID", placeholder="e.g., ITEM-101")
        thank_note = st.text_input("Send a Thank-You Note", placeholder="e.g., Thank you so much for returning my bottle!")
        rec_btn = st.form_submit_button("Mark as Safely Returned 🎉")
        
        if rec_btn:
            if rec_id in st.session_state.items_db:
                st.session_state.items_db[rec_id]["status"] = "Safely Returned 🎉"
                st.session_state.items_db[rec_id]["thank_you"] = thank_note
                st.success(f"Item {rec_id} marked as successfully recovered!")
            else:
                st.error("Item ID not found.")

# ==========================================
# TAB 4: LIVE DASHBOARD & KARMA LEADERBOARD
# ==========================================
with tab4:
    st.subheader("🏆 Campus Hero Leaderboard")
    st.markdown("<small>Students who help return lost items earn badges and climb the ranks!</small>", unsafe_allow_html=True)
    
    # Display Karma Leaderboard
    sorted_karma = sorted(st.session_state.karma_db.items(), key=lambda x: x[1]["points"], reverse=True)
    for rank, (user, data) in enumerate(sorted_karma, 1):
        st.info(f"**#{rank} {user}** — {data['points']} Pts | *Badge:* {data['badge']}")

    st.divider()
    st.subheader("📊 Live Activity & Database Feed")
    
    if st.session_state.messages_db:
        for msg in reversed(st.session_state.messages_db):
            st.error(f"🚨 **{msg['finder']}** found **{msg['owner']}**'s {msg['item']} at **{msg['zone']}**! Note: \"{msg['message']}\"")
    else:
        st.info("No active reports yet. Try scanning in Tab 2!")
        
    with st.expander("View Full Master Database"):
        db_list = [{"ID": k, **v} for k, v in st.session_state.items_db.items()]
        st.dataframe(db_list, use_container_width=True)
