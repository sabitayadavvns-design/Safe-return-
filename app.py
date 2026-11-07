import streamlit as st
import random
import qrcode

# --- INITIALIZE SESSION STATE ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "items_db" not in st.session_state:
    # Central mock database for our single school
    st.session_state.items_db = {
        "SR-1001": {"name": "Aarav Sharma", "class": "7-B", "item_name": "Blue Water Bottle", "zone": "Cafeteria", "status": "Found"},
        "SR-1002": {"name": "Diya Patel", "class": "6-A", "item_name": "Math Textbook", "zone": "N/A", "status": "Registered"}
    }

# --- TWO-LAYER SECURITY CONFIGURATION ---
AUTHORIZED_ADMINS = {
    "+919876543210": "7842",
    "+919811122233": "5591"
}

# --- APP SIDEBAR NAVIGATION ---
st.sidebar.title("🎒 SafeReturn Portal")
app_mode = st.sidebar.radio("Navigate to:", ["Public: Register Item", "Public: Scan Finder View", "🔒 Staff Admin Dashboard"])

# ==========================================
# 1. PUBLIC: REGISTER ITEM (Student / Parent)
# ==========================================
if app_mode == "Public: Register Item":
    st.title("📝 Student Item Registration")
    st.write("Register a school item to generate your secure privacy tag and instant QR code.")
    
    with st.form("registration_form"):
        student_name = st.text_input("Student Name")
        student_class = st.text_input("Class / Section (e.g., 7-B)")
        item_name = st.text_input("Item Description (e.g., Blue Water Bottle)")
        submit_reg = st.form_submit_button("Generate SafeReturn ID & QR")
        
        if submit_reg and student_name and item_name:
            new_id = f"SR-{random.randint(2000, 9999)}"
            
            st.session_state.items_db[new_id] = {
                "name": student_name,
                "class": student_class,
                "item_name": item_name,
                "zone": "N/A",
                "status": "Registered"
            }
            st.success(f"Item successfully registered! Your Secure ID is: **{new_id}**")
            
            # --- AUTOMATIC QR CODE GENERATOR ---
            # Creates a scannable QR code linking directly to the item report view
            qr_data = f"https://safereturn.streamlit.app/?item={new_id}"
            img = qrcode.make(qr_data)
            
            # Save temporarily and display
            img_path = "temp_qr.png"
            img.save(img_path)
            
            st.image(img_path, caption=f"QR Code for {item_name} ({new_id})", width=200)
            st.info("📲 Take a screenshot of this QR code, print it out, and attach it securely to the student's item!")

# ==========================================
# 2. PUBLIC: SCAN FINDER VIEW (Anonymous Finder)
# ==========================================
elif app_mode == "Public: Scan Finder View":
    st.title("📍 Found an Item?")
    st.write("Thank you for helping! Please select the zone where you found this item to alert the school coordinator anonymously.")
    
    # Allow selecting from registered items
    scanned_id = st.selectbox("Select Scanned Item ID", list(st.session_state.items_db.keys()))
    
    if scanned_id:
        item = st.session_state.items_db[scanned_id]
        st.info(f"**Item Type:** {item['item_name']} (Owner details remain completely private)")
        
        found_zone = st.selectbox("Where did you find it?", ["Cafeteria", "Sports Ground", "Main Hall", "Library", "Bus Bay"])
        
        if st.button("Notify School Coordinator"):
            st.session_state.items_db[scanned_id]["zone"] = found_zone
            st.session_state.items_db[scanned_id]["status"] = "Found"
            
            st.success("✅ Alert sent successfully to the school coordinator! Thank you for being a good citizen.")

# ==========================================
# 3. SECURE ADMIN DASHBOARD (Two-Layer Security)
# ==========================================
elif app_mode == "🔒 Staff Admin Dashboard":
    st.title("🏫 School Coordinator Portal")
    
    # Check if admin is logged in
    if not st.session_state.admin_logged_in:
        st.subheader("🔐 Two-Layer Secure Verification")
        st.write("Please enter your authorized credentials to access active campus alerts.")
        
        # --- LAYER 1: PHONE NUMBER WHITELIST CHECK ---
        entered_phone = st.text_input("Enter Registered Coordinator Phone Number", placeholder="+919876543210")
        
        if entered_phone:
            if entered_phone in AUTHORIZED_ADMINS:
                st.success("Phone number recognized. Please enter your security code.")
                
                # --- LAYER 2: PRE-SHARED SECRET CODE CHECK ---
                entered_code = st.text_input("Enter Secret Access Code", type="password", placeholder="****")
                
                if st.button("Verify & Enter Dashboard"):
                    if entered_code == AUTHORIZED_ADMINS[entered_phone]:
                        st.session_state.admin_logged_in = True
                        st.success("Access Granted! Loading dashboard...")
                        st.rerun()
                    else:
                        st.error("Incorrect secret access code. Please try again.")
            else:
                st.error("Access Denied: This phone number is not authorized as a school administrator.")
                
    else:
        # --- UNLOCKED ADMIN DASHBOARD ---
        if st.sidebar.button("Log Out of Admin"):
            st.session_state.admin_logged_in = False
            st.rerun()
            
        st.header("📊 Live Active Alerts Dashboard")
        st.write("Review items reported found across campus and manage student reunifications.")
        
        # Filter items that are currently "Found"
        found_items = {item_id: details for item_id, details in st.session_state.items_db.items() if details["status"] == "Found"}
        
        if found_items:
            st.warning(f"⚠️ You have {len(found_items)} item(s) waiting for pickup.")
            
            for item_id, details in found_items.items():
                with st.container(border=True):
                    st.subheader(f"📦 Item ID: {item_id}")
                    st.write(f"**Item:** {details['item_name']}")
                    st.write(f"**Found At Zone:** {details['zone']}")
                    st.markdown(f"**Owner Details:** {details['name']} (Class: {details['class']})")
                    
                    if st.button(f"Mark as Returned & Resolve ({item_id})", key=item_id):
                        st.session_state.items_db[item_id]["status"] = "Returned"
                        st.success(f"Item {item_id} marked as successfully returned!")
                        st.rerun()
        else:
            st.info("🎉 All clear! No active lost items reported right now.")
        
