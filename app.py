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

# Session state initialization for mock database & demo items
if "items_db" not in st.session_state:
    st.session_state.items_db = {
        "SR-3216": {
            "name": "Aditya Yadav",
            "class": "9-B",
            "item_name": "Blue lunch Box",
            "status": "Safe",
            "zone": "None",
            "message": "",
            "thank_you": ""
        }
    }

# Check if someone scanned a QR code containing an item query parameter in the URL
query_params = st.query_params
scanned_item_id = query_params.get("item", None)

if scanned_item_id:
    st.markdown("---")
    st.subheader("🔍 Scanned Item Lookup")
    if scanned_item_id in st.session_state.items_db:
        item_info = st.session_state.items_db[scanned_item_id]
        st.success(f"Found Item ID: **{scanned_item_id}**")
        st.write(f"🎒 **Item:** {item_info['item_name']}")
        st.write(f"👤 **Owner:** {item_info['name']} (Class: {item_info['class']})")
    else:
        st.success(f"Scanned Item ID: **{scanned_item_id}**")
        st.write("🎒 **Status:** Tag successfully scanned by finder!")
        
    # Campus zones dropdown for the finder
    zone_options = ["Main Gate", "Cafeteria", "Science Block", "Sports Ground", "Library", "Bus Bay"]
    found_zone = st.selectbox("Select Campus Zone where found:", zone_options, key="scanned_zone")
    
    finder_message = st.text_area("Optional message for owner (e.g., 'Safe with me at...')", key="scanned_msg")
    
    if st.button("Notify Owner & Claim Karma", key="scanned_btn"):
        st.success("🎉 Notification sent! Thank you for being an honest finder.")
        st.balloons()
    st.markdown("---")

# Tabs for Mobile Navigation
tab1, tab2, tab3 = st.tabs(["🏷️ Register Tag", "🔍 Finder View", "🏆 Karma Hub"])

# ========================================
# TAB 1: REGISTER ITEM & GENERATE QR
# ========================================
with tab1:
    st.subheader("Create a Smart Tag")
    st.write("Generate a privacy-first QR tag for your valuable item.")
    
    # Live App URL input so QR codes always point to your current deployment link
    base_url = st.text_input(
        "Paste your current Streamlit App URL here:", 
        value="https://safe-return-.streamlit.app", 
        help="Copy the URL from your browser address bar of this running app and paste it here."
    )
    
    student_name = st.text_input("Your Name:", key="reg_name")
    student_class = st.text_input("Class / Section (e.g., 9-B):", key="reg_class")
    item_name = st.text_input("Item Description (e.g., Blue Water Bottle):", key="reg_item")
    
    if st.button("Generate QR Code", key="reg_btn"):
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

            # Clean up base URL to avoid double slashes and append query param correctly
            clean_base = base_url.strip().rstrip("/")
            app_url = f"{clean_base}/?item={item_id}"

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
            st.info(f"📱 QR Code points to: `{app_url}`. Scan it with your phone camera to test!")
        else:
            st.error("Please fill in all details.")

# ========================================
# TAB 2: FINDER VIEW (MANUAL LOOKUP)
# ========================================
with tab2:
    st.subheader("Found an Item?")
    st.write("Enter its ID to notify the owner.")
    
    found_id = st.text_input("Enter Item ID (from QR tag):", key="manual_id")
    
    if found_id:
        if found_id in st.session_state.items_db:
            item_info = st.session_state.items_db[found_id]
            st.info(f"Looking up item: **{found_id}** ({item_info['item_name']} - {item_info['name']})")
        else:
            st.info(f"Looking up item ID: **{found_id}**")
            
        zone_options = ["Main Gate", "Cafeteria", "Science Block", "Sports Ground", "Library", "Bus Bay"]
        found_zone = st.selectbox("Select Campus Zone where found:", zone_options, key="manual_zone")
        
        finder_message = st.text_area("Optional message for owner:", key="manual_msg")
        
        if st.button("Notify Owner & Claim Karma", key="manual_btn"):
            st.success("🎉 Notification sent to owner! Thank you for being an honest finder.")
            st.balloons()

# ========================================
# TAB 3: KARMA HUB (LEADERBOARD)
# ========================================
with tab3:
    st.subheader("🏆 Honest Finder Karma Hub")
    st.write("Recognizing students who make our school trustworthy and safe.")
    
    st.markdown("""
    | Rank | Student Name | Class | Karma Points | Badges |
    | :--- | :--- | :--- | :--- | :--- |
    | 🥇 | Aarav Sharma | 8-A | 250 | 🌟 Super Finder |
    | 🥈 | Diya Patel | 9-C | 190 | 🛡️ Honest Hero |
    | 🥉 | Rohan Verma | 7-B | 150 | 🤝 Good Samaritan |
    """)
    
    st.info("💡 Return lost items using SafeReturn to earn karma points and school recognition badges!")
    
