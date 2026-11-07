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
    .main {
        padding: 0px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
    }
    h1 {
        color: #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.title("🎒 SafeReturn")
st.caption("Smart Campus Lost & Found System")

# Session state initialization for mock database
if "items_db" not in st.session_state:
    st.session_state.items_db = {}

# Tabs for Mobile Navigation
tab1, tab2, tab3 = st.tabs(["🏷️ Register Tag", "🔍 Finder View", "🏆 Karma Hub"])

# ========================================
# TAB 1: REGISTER ITEM & GENERATE QR
# ========================================
with tab1:
    st.subheader("Create a Smart Tag")
    st.write("Generate a privacy-first QR tag for your valuable item.")
    
    student_name = st.text_input("Your Name:")
    student_class = st.text_input("Class / Section (e.g., 9-B):")
    item_name = st.text_input("Item Description (e.g., Blue Water Bottle):")
    
    if st.button("Generate QR Code"):
        if student_name and student_class and item_name:
            # Generate a unique secure ID
            item_id = f"SR-{random.randint(1000, 9999)}"
            
            # Save to mock database session state
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

            # Encode the full live web app URL with the item ID so scanning opens it directly
            app_url = f"https://penfvm3xpyxjjm2xwi6iyk.streamlit.app/?item={item_id}"
            

            # Generate high-contrast QR code image containing the live link
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(app_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            buf = BytesIO()
            img.save(buf, format="PNG")

            st.image(buf.getvalue(), caption=f"Tag for {item_name} ({student_name})")
            st.info("📱 When parents scan this QR code with their phone camera, it will instantly open the link!")
        else:
            st.error("Please fill in all details.")

# ========================================
# TAB 2: FINDER VIEW (SCAN QR & ZONE TRACKING)
# ========================================
with tab2:
    st.subheader("Found an Item?")
    st.write("Scan a SafeReturn tag or enter its ID to notify the owner.")
    
    found_id = st.text_input("Enter Item ID (from QR tag):")
    
    if found_id:
        if found_id in st.session_state.items_db:
            st.info(f"Looking up item: **{found_id}**")
            
            # Campus zones dropdown
            zone_options = ["Main Gate", "Cafeteria", "Science Block", "Sports Ground", "Library", "Bus Bay"]
            found_zone = st.selectbox("Select Campus Zone where found:", zone_options)
            
            finder_message = st.text_area("Optional message for owner (e.g., 'Safe with me at...')")
            
            if st.button("Notify Owner & Claim Karma"):
                st.session_state.items_db[found_id]["status"] = "Found"
                st.session_state.items_db[found_id]["zone"] = found_zone
                st.session_state.items_db[found_id]["message"] = finder_message
                
                st.success("🎉 Notification sent to owner! Thank you for being an honest finder.")
                st.balloons()
        else:
            st.error("Item ID not found in the system. Please check the code.")

# ========================================
# TAB 3: KARMA HUB (LEADERBOARD)
# ========================================
with tab3:
    st.subheader("🏆 Honest Finder Karma Hub")
    st.write("Recognizing students who make our school trustworthy and safe.")
    
    # Leaderboard display
    st.markdown("""
    | Rank | Student Name | Class | Karma Points | Badges |
    | :--- | :--- | :--- | :--- | :--- |
    | 🥇 | Aarav Sharma | 8-A | 250 | 🌟 Super Finder |
    | 🥈 | Diya Patel | 9-C | 190 | 🛡️ Honest Hero |
    | 🥉 | Rohan Verma | 7-B | 150 | 🤝 Good Samaritan |
    """)
    
    st.info("💡 Return lost items using SafeReturn to earn karma points and school recognition badges!")
    
