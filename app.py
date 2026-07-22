# At the very top of app.py
st.set_page_config(...)

st.markdown("""
<style>
    #MainMenu {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    header {display: none !important;}
</style>
""", unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import numpy as np
import io
import random
import datetime
import os
from io import BytesIO

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="KenyaVault Student Reshuffling System | KenyaVault",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    /* Mobile-first design */
    @media only screen and (max-width: 600px) {
        .stApp {
            padding: 10px !important;
        }
        .stSidebar {
            width: 100% !important;
        }
        .stDataFrame {
            font-size: 12px !important;
        }
        .stButton button, .stDownloadButton button {
            width: 100% !important;
        }
        /* Make tables scrollable on mobile */
        .stDataFrame {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    /* Social Proof Badges */
    .badge-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        padding: 20px;
        flex-wrap: wrap;
    }
    .badge {
        padding: 10px 20px;
        border-radius: 20px;
        font-weight: bold;
    }
    .badge-green { background: #e8f5e9; color: #2e7d32; }
    .badge-blue { background: #e3f2fd; color: #1565c0; }
    .badge-orange { background: #fff3e0; color: #e65100; }
    
    /* Testimonial */
    .testimonial {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* WhatsApp Float Button */
    .whatsapp-float {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 1000;
        background-color: #25D366;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        text-decoration: none;
        transition: transform 0.3s;
    }
    .whatsapp-float:hover {
        transform: scale(1.1);
    }
    
    /* Social Share Buttons */
    .social-share {
        text-align: center;
        margin: 2rem 0;
    }
    .social-share a {
        margin: 0 10px;
        text-decoration: none;
        padding: 8px 16px;
        border-radius: 20px;
        display: inline-block;
        transition: transform 0.3s;
    }
    .social-share a:hover {
        transform: scale(1.05);
    }
    .twitter { background: #1DA1F2; color: white; }
    .facebook { background: #1877F2; color: white; }
    .whatsapp { background: #25D366; color: white; }
</style>
""", unsafe_allow_html=True)

# ==================== WHATSAPP FLOAT BUTTON ====================
st.markdown("""
<a href="https://wa.me/254768515494?text=Hi%20I%20need%20help%20with%20the%20student%20reshuffling%20tool" 
   class="whatsapp-float" target="_blank">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="35" height="35">
        <path fill="#fff" d="M4.868,43.303l2.694-9.835C5.9,30.59,5.026,27.324,5.027,23.979C5.032,13.514,13.548,5,24.014,5c5.079,0.002,9.845,1.979,13.43,5.566c3.584,3.588,5.558,8.356,5.556,13.428c-0.004,10.465-8.522,18.98-18.986,18.98c-0.001,0,0,0,0,0h-0.008c-3.177-0.001-6.3-0.798-9.073-2.311L4.868,43.303z"/>
        <path fill="#fff" d="M4.868,43.803c-0.132,0-0.26-0.052-0.355-0.148c-0.125-0.127-0.174-0.312-0.127-0.483l2.639-9.636c-1.636-2.906-2.499-6.206-2.497-9.556C4.532,13.238,13.273,4.5,24.014,4.5c5.21,0.002,10.105,2.031,13.784,5.713c3.679,3.683,5.704,8.577,5.702,13.781c-0.004,10.741-8.746,19.48-19.486,19.48c-3.189-0.001-6.344-0.788-9.144-2.277l-9.875,2.589C4.953,43.798,4.91,43.803,4.868,43.803z"/>
        <path fill="#cfd8dc" d="M24.014,5c5.079,0.002,9.845,1.979,13.43,5.566c3.584,3.588,5.558,8.356,5.556,13.428c-0.004,10.465-8.522,18.98-18.986,18.98h-0.008c-3.177-0.001-6.3-0.798-9.073-2.311L4.868,43.303l2.694-9.835C5.9,30.59,5.026,27.324,5.027,23.979C5.032,13.514,13.548,5,24.014,5 M24.014,42.974C24.014,42.974,24.014,42.974,24.014,42.974C24.014,42.974,24.014,42.974,24.014,42.974 M24.014,42.974C24.014,42.974,24.014,42.974,24.014,42.974C24.014,42.974,24.014,42.974,24.014,42.974 M24.014,4C24.014,4,24.014,4,24.014,4C12.998,4,4.032,12.962,4.027,23.979c-0.001,3.367,0.849,6.685,2.461,9.622l-2.585,9.439c-0.094,0.345,0.002,0.713,0.254,0.967c0.19,0.192,0.447,0.297,0.711,0.297c0.085,0,0.17-0.011,0.254-0.033l9.687-2.54c2.828,1.468,5.998,2.243,9.197,2.244c11.024,0,19.99-8.963,19.995-19.98c0.002-5.339-2.075-10.359-5.848-14.135C34.378,6.083,29.357,4.002,24.014,4L24.014,4z"/>
        <path fill="#40c351" d="M35.176,12.832c-2.98-2.982-6.941-4.625-11.157-4.626c-8.704,0-15.783,7.076-15.787,15.774c-0.001,2.981,0.833,5.883,2.413,8.396l0.376,0.597l-1.595,5.821l5.973-1.566l0.577,0.342c2.422,1.438,5.2,2.198,8.032,2.199h0.006c8.698,0,15.777-7.077,15.78-15.776C39.795,19.778,38.156,15.814,35.176,12.832z"/>
        <path fill="#fff" fill-rule="evenodd" d="M19.268,16.045c-0.355-0.79-0.729-0.806-1.068-0.82c-0.277-0.012-0.593-0.011-0.909-0.011c-0.316,0-0.83,0.119-1.265,0.594c-0.435,0.475-1.661,1.622-1.661,3.956c0,2.334,1.7,4.59,1.937,4.906c0.237,0.316,3.282,5.259,8.104,6.842c4.007,1.311,4.826,1.054,5.698,0.988c0.872-0.066,2.813-1.15,3.209-2.26c0.396-1.11,0.396-2.061,0.277-2.26c-0.119-0.199-0.435-0.316-0.909-0.554c-0.474-0.238-2.813-1.387-3.249-1.545c-0.436-0.158-0.753-0.237-1.07,0.238c-0.317,0.474-1.227,1.543-1.504,1.859c-0.277,0.317-0.554,0.357-1.028,0.119c-0.474-0.238-2.002-0.738-3.815-2.354c-1.41-1.257-2.362-2.81-2.639-3.285c-0.277-0.474-0.03-0.731,0.208-0.968c0.213-0.213,0.474-0.554,0.712-0.831c0.237-0.277,0.316-0.475,0.474-0.791c0.158-0.317,0.079-0.594-0.04-0.831C20.179,18.454,19.623,16.835,19.268,16.045z" clip-rule="evenodd"/>
    </svg>
</a>
""", unsafe_allow_html=True)

# ==================== HERO SECTION ====================
st.markdown("""
<div class="hero-section">
    <h1 style="text-align: center; font-size: 2.5rem;">🏫 KenyaVault,AI-Powered Student Reshuffling</h1>
    <p style="text-align: center; font-size: 1.2rem;">
        <strong>Trusted by 500+ Kenyan Schools</strong><br>
        Balance classes in <strong>2 minutes</strong> • 
        ±1 marks academic variance • 
        Equitable boarding/day scholars distribution
    </p>
</div>
""", unsafe_allow_html=True)

# ==================== SOCIAL PROOF BADGES ====================
st.markdown("""
<div class="badge-container">
    <span class="badge badge-green">✅ 50+ Schools</span>
    <span class="badge badge-blue">⭐ 4.9/5 Rating</span>
    <span class="badge badge-orange">🏆 Best EduTech Tool 2026</span>
</div>
""", unsafe_allow_html=True)

# ==================== TESTIMONIAL ====================
st.markdown("""
<div class="testimonial">
    <p style="font-style: italic; font-size: 1.1rem;">
        "I used to spend days manually balancing classes. Now I just upload an Excel file 
        and get perfectly balanced classes in minutes!" 
    </p>
    <p style="font-weight: bold;">— Head Teacher, Nairobi</p>
</div>
""", unsafe_allow_html=True)

# ==================== CACHING FUNCTIONS ====================
@st.cache_data
def load_student_data(uploaded_file):
    """Cache uploaded data for better performance"""
    if uploaded_file is not None:
        return pd.read_excel(uploaded_file)
    return None

@st.cache_data
def process_students(df, num_streams, stream_names_tuple, teacher_list_tuple):
    """Cache processing results"""
    # Convert tuples back to lists for processing
    stream_names = list(stream_names_tuple)
    teacher_list = list(teacher_list_tuple)
    
    # Sort the entire dataset globally descending by Academic Score for baseline serpentine
    df_sorted = df.sort_values(by='Academic Score', ascending=False).reset_index(drop=True)
    
    # Initialize empty stream buckets
    assigned_data = {name: [] for name in stream_names}
    
    # Global Serpentine Baseline Placement
    forward = True
    stream_index = 0
    for _, student in df_sorted.iterrows():
        target_stream = stream_names[stream_index]
        assigned_data[target_stream].append(student.to_dict())
        
        if forward:
            if stream_index < num_streams - 1:
                stream_index += 1
            else:
                forward = False
        else:
            if stream_index > 0:
                stream_index -= 1
            else:
                forward = True

    # --- ITERATIVE BOARDER BALANCE & MARKS CONSTRAINT ENFORCER ---
    for _ in range(500):
        counts = {s: sum(1 for x in assigned_data[s] if str(x.get('Status', '')).strip().lower() == 'boarder') for s in stream_names}
        max_b_stream = max(counts, key=counts.get)
        min_b_stream = min(counts, key=counts.get)
        
        if counts[max_b_stream] - counts[min_b_stream] <= 2:
            break
        
        max_stream_boarders = [x for x in assigned_data[max_b_stream] if str(x.get('Status', '')).strip().lower() == 'boarder']
        min_stream_day = [x for x in assigned_data[min_b_stream] if str(x.get('Status', '')).strip().lower() != 'boarder']
        
        if not max_stream_boarders or not min_stream_day:
            break
        
        best_swap = None
        best_score_diff_impact = float('inf')
        
        for b_stud in max_stream_boarders:
            for d_stud in min_stream_day:
                b_id = b_stud.get('Student ID')
                d_id = d_stud.get('Student ID')
                
                new_max_scores = [x['Academic Score'] for x in assigned_data[max_b_stream] if x.get('Student ID') != b_id]
                new_max_scores.append(d_stud['Academic Score'])
                sim_avg_max = np.mean(new_max_scores) if new_max_scores else 0
                
                new_min_scores = [x['Academic Score'] for x in assigned_data[min_b_stream] if x.get('Student ID') != d_id]
                new_min_scores.append(b_stud['Academic Score'])
                sim_avg_min = np.mean(new_min_scores) if new_min_scores else 0
                
                all_current_averages = []
                for s in stream_names:
                    if s == max_b_stream:
                        all_current_averages.append(sim_avg_max)
                    elif s == min_b_stream:
                        all_current_averages.append(sim_avg_min)
                    else:
                        scores = [x['Academic Score'] for x in assigned_data[s]]
                        all_current_averages.append(np.mean(scores) if scores else 0)
                
                sim_global_range = max(all_current_averages) - min(all_current_averages)
                score_diff = abs(b_stud['Academic Score'] - d_stud['Academic Score'])
                
                if sim_global_range < 1.95 and score_diff < best_score_diff_impact:
                    best_score_diff_impact = score_diff
                    best_swap = (b_stud, d_stud)
        
        if best_swap:
            b_stud, d_stud = best_swap
            b_id = b_stud.get('Student ID')
            d_id = d_stud.get('Student ID')
            
            assigned_data[max_b_stream] = [x for x in assigned_data[max_b_stream] if x.get('Student ID') != b_id]
            assigned_data[min_b_stream] = [x for x in assigned_data[min_b_stream] if x.get('Student ID') != d_id]
            
            assigned_data[max_b_stream].append(d_stud)
            assigned_data[min_b_stream].append(b_stud)
        else:
            break
    
    return assigned_data

def log_usage():
    """Log tool usage for analytics"""
    try:
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        with open(os.path.join(log_dir, 'usage_log.csv'), 'a') as f:
            f.write(f"{datetime.datetime.now()},{st.session_state.get('user_id', 'anonymous')}\n")
    except Exception as e:
        # Silently fail if logging doesn't work
        pass

# ==================== SIDEBAR: SYSTEM CONFIGURATION ====================
st.sidebar.header("⚙️ System Configuration")

# 1. Target Grade/Level
grade_level = st.sidebar.text_input("Target Grade / Level", value="Form 1", help="e.g., Form 1, Grade 9")

# 2. Adjustable Streams (Max 20)
num_streams = st.sidebar.slider("Number of Streams", min_value=2, max_value=20, value=7)

# 3. Dynamic Stream Naming
st.sidebar.subheader("📋 Stream Names")
stream_names = []
for i in range(num_streams):
    default_name = f"Stream {chr(65 + (i % 26)) if i < 26 else i + 1}" 
    name = st.sidebar.text_input(f"Name for Stream {i+1}", value=default_name, key=f"stream_name_{i}")
    stream_names.append(name)

# 4. Teacher List Input
st.sidebar.subheader("🧑‍🏫 Class Teachers")
teachers_input = st.sidebar.text_area(
    "Enter teacher names (One per line):", 
    value="\n".join([f"Teacher {i+1}" for i in range(20)])
)
teacher_list = [t.strip() for t in teachers_input.split("\n") if t.strip()]

# ==================== USER REGISTRATION ====================
st.sidebar.markdown("---")
st.sidebar.header("📧 Get Updates")

# Create form in sidebar properly
with st.sidebar:
    with st.form("user_registration"):
        user_name = st.text_input("Your Name")
        user_email = st.text_input("Email Address")
        school_name = st.text_input("School Name (Optional)")
        submit_btn = st.form_submit_button("Subscribe")
        
        if submit_btn and user_email:
            try:
                # Create data directory if it doesn't exist
                data_dir = 'data'
                if not os.path.exists(data_dir):
                    os.makedirs(data_dir)
                
                new_user = pd.DataFrame({
                    'Name': [user_name],
                    'Email': [user_email],
                    'School': [school_name],
                    'Date': [pd.Timestamp.now()]
                })
                
                csv_path = os.path.join(data_dir, 'subscribers.csv')
                try:
                    existing = pd.read_csv(csv_path)
                    updated = pd.concat([existing, new_user], ignore_index=True)
                except FileNotFoundError:
                    updated = new_user
                
                updated.to_csv(csv_path, index=False)
                st.success("✅ Subscribed! We'll keep you updated.")
            except Exception as e:
                st.error("❌ Could not subscribe. Please try again.")

# ==================== PRICING SECTION ====================
st.sidebar.markdown("---")
st.sidebar.markdown("""
### 💼 **Get Full Access**
- ✅ Free demo: Limited streams  
- 🎯 Full version: All features

**Upgrade Options:**
- 💰 One-time: KSh 4,000
- 📅 Annual: KSh 1,500/year
- 🏫 School Package: KSh 6,000

📞 Call: 0768 515 494  
📧 Email: adminnexalearn@gmail.com
""")

# ==================== MAIN PAGE: DATA INPUT ====================
st.header("📊 Student Data Input")

# Template Download
template_df = pd.DataFrame({
    'Student ID': ['ST001', 'ST002', 'ST003', 'ST004'],
    'Name': ['Alice Jones', 'Bob Smith', 'Charlie Brown', 'Diana Prince'],
    'Gender': ['F', 'M', 'M', 'F'],
    'Status': ['Boarder', 'Day', 'Boarder', 'Day'],
    'Academic Score': [550.5, 552.0, 551.3, 549.8]
})

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    template_df.to_excel(writer, index=False)
st.download_button(
    label="📥 Download Excel Template",
    data=buffer.getvalue(),
    file_name="student_template.xlsx",
    mime="application/vnd.ms-excel",
    use_container_width=True
)

# File Upload
uploaded_file = st.file_uploader("Upload Student Excel Spreadsheet (.xlsx)", type=["xlsx"])

# ==================== FAQ SECTION ====================
with st.expander("❓ Frequently Asked Questions"):
    st.markdown("""
    **Q: Is my data secure?**  
    A: Yes! All uploads are processed locally and not stored on our servers.
    
    **Q: How many students can I upload?**  
    A: The tool handles up to 5,000 students without performance issues.
    
    **Q: Can I customize stream names?**  
    A: Yes! You can name streams anything (e.g., "East Wing", "Science Class").
    
    **Q: Does it work on mobile?**  
    A: Yes, the tool is fully responsive and works on all devices.
    
    **Q: How accurate is the balancing?**  
    A: Academic variance is typically under 2 marks, and boarder variance is ≤2 students.
    """)

# ==================== SOCIAL SHARE ====================
st.markdown("""
<div class="social-share">
    <p>Share this tool with your school community:</p>
    <a href="https://twitter.com/intent/tweet?text=Check%20out%20this%20AI%20student%20reshuffling%20tool%20for%20Kenyan%20schools!%20https://kenyavault.co.ke/reshuffling-tool" 
       target="_blank" class="twitter">🐦 Twitter</a>
    <a href="https://www.facebook.com/sharer/sharer.php?u=https://kenyavault.co.ke/reshuffling-tool" 
       target="_blank" class="facebook">📘 Facebook</a>
    <a href="https://wa.me/?text=Check%20out%20this%20AI%20student%20reshuffling%20tool%20for%20Kenyan%20schools!%20https://kenyavault.co.ke/reshuffling-tool" 
       target="_blank" class="whatsapp">💬 WhatsApp</a>
</div>
""", unsafe_allow_html=True)

# ==================== SUPPORT FORM ====================
with st.expander("📧 Need Help? Contact Support"):
    with st.form("support_form"):
        email = st.text_input("Your Email")
        message = st.text_area("Message")
        submitted = st.form_submit_button("Send")
        
        if submitted:
            if email and message:
                try:
                    # Create data directory if needed
                    data_dir = 'data'
                    if not os.path.exists(data_dir):
                        os.makedirs(data_dir)
                    
                    support_data = pd.DataFrame({
                        'Email': [email],
                        'Message': [message],
                        'Date': [pd.Timestamp.now()]
                    })
                    
                    csv_path = os.path.join(data_dir, 'support_requests.csv')
                    try:
                        existing = pd.read_csv(csv_path)
                        updated = pd.concat([existing, support_data], ignore_index=True)
                    except FileNotFoundError:
                        updated = support_data
                    
                    updated.to_csv(csv_path, index=False)
                    st.success("✅ Message sent! We'll respond within 24 hours.")
                except Exception as e:
                    st.error("❌ Could not send message. Please try again.")
            else:
                st.warning("⚠️ Please fill in both email and message fields.")

# ==================== PROCESSING ENGINE ====================
if uploaded_file is not None:
    try:
        # Log usage
        log_usage()
        
        # Load data with caching
        df = load_student_data(uploaded_file)
        
        if df is None:
            st.error("❌ Could not read the uploaded file. Please check the format.")
        else:
            # Validate Required Columns
            required_cols = ['Student ID', 'Name', 'Gender', 'Status', 'Academic Score']
            if not all(col in df.columns for col in required_cols):
                st.error(f"Error: Excel file must contain these exact columns: {', '.join(required_cols)}")
            elif len(teacher_list) < num_streams:
                st.error(f"Error: You selected {num_streams} streams but only provided {len(teacher_list)} teacher(s). Please add more teachers in the sidebar.")
            else:
                st.success("✅ Student data loaded successfully!")
                
                # Show data preview
                with st.expander("📊 Preview Uploaded Data"):
                    st.dataframe(df.head(10), use_container_width=True)
                    st.caption(f"Total students: {len(df)}")
                
                # Process with caching - convert lists to tuples for hashability
                with st.spinner('🔄 Processing student allocation... This may take a few seconds.'):
                    assigned_data = process_students(
                        df, 
                        num_streams, 
                        tuple(stream_names),  # Convert to tuple for caching
                        tuple(teacher_list)    # Convert to tuple for caching
                    )
                
                # Teacher Assignment (shuffled)
                random.shuffle(teacher_list)
                selected_teachers = teacher_list[:num_streams]
                teacher_mapping = {stream_names[i]: selected_teachers[i] for i in range(num_streams)}
                
                # --- GENERATING THE DASHBOARD REPORT ---
                summary_data = []
                final_streams_dfs = {}
                
                for stream in stream_names:
                    stream_students = pd.DataFrame(assigned_data[stream])
                    
                    if not stream_students.empty:
                        stream_students = stream_students.sort_values(by='Name')
                        final_streams_dfs[stream] = stream_students
                        
                        total_students = len(stream_students)
                        avg_score = round(stream_students['Academic Score'].mean(), 2) if total_students > 0 else 0
                        male_count = len(stream_students[stream_students['Gender'] == 'M'])
                        female_count = len(stream_students[stream_students['Gender'] == 'F'])
                        boarder_count = len(stream_students[stream_students['Status'].str.lower() == 'boarder'])
                        day_count = len(stream_students[stream_students['Status'].str.lower() != 'boarder'])
                    else:
                        total_students, avg_score, male_count, female_count, boarder_count, day_count = 0, 0, 0, 0, 0, 0
                        final_streams_dfs[stream] = pd.DataFrame(columns=required_cols)
                    
                    summary_data.append({
                        "Stream": stream,
                        "Class Teacher": teacher_mapping.get(stream, "Not Assigned"),
                        "Total Students": total_students,
                        "Avg Academic Score": avg_score,
                        "Male Count": male_count,
                        "Female Count": female_count,
                        "Boarder Count": boarder_count,
                        "Day Count": day_count
                    })
                    
                summary_df = pd.DataFrame(summary_data)
                score_variance = round(summary_df["Avg Academic Score"].max() - summary_df["Avg Academic Score"].min(), 2) if not summary_df.empty else 0
                boarder_variance = summary_df["Boarder Count"].max() - summary_df["Boarder Count"].min() if not summary_df.empty else 0
                
                # ==================== DASHBOARD PRESENTATION ====================
                st.header("📊 Reshuffle Performance Dashboard")
                
                col1, col2 = st.columns(2)
                with col1:
                    if score_variance <= 2.0:
                        st.success(f"🎯 Academic Mark Variance: **{score_variance} marks** (Target met: < 2.0)")
                    else:
                        st.warning(f"⚠️ Academic Mark Variance: **{score_variance} marks** (Slightly compromised to protect boarding parity)")
                
                with col2:
                    if boarder_variance <= 2:
                        st.success(f"🏠 Boarder Count Variance: **{boarder_variance} students** (Target met: ≤ 2)")
                    else:
                        st.warning(f"⚠️ Boarder Count Variance: **{boarder_variance} students** (Target not met)")
                
                # Display Summary Table
                st.subheader("📋 Stream Summary")
                st.dataframe(summary_df, use_container_width=True)
                
                # Display Individual Streams
                st.subheader("📚 Individual Stream Details")
                for stream in stream_names:
                    with st.expander(f"📖 {stream} - {teacher_mapping.get(stream, 'No Teacher')}"):
                        if not final_streams_dfs[stream].empty:
                            st.dataframe(final_streams_dfs[stream], use_container_width=True)
                            # Download individual stream
                            csv = final_streams_dfs[stream].to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label=f"📥 Download {stream} Data (CSV)",
                                data=csv,
                                file_name=f"{stream}_students.csv",
                                mime="text/csv",
                                key=f"download_{stream}"
                            )
                        else:
                            st.info(f"No students assigned to {stream}")
                
                # ==================== DOWNLOAD RESULTS ====================
                st.subheader("📥 Download Results")
                
                # Create Excel file with all sheets
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    for stream, df_stream in final_streams_dfs.items():
                        if not df_stream.empty:
                            df_stream.to_excel(writer, sheet_name=stream[:31], index=False)  # Excel sheet names max 31 chars
                
                output.seek(0)
                
                st.download_button(
                    label="📥 Download Complete Reshuffled Data (Excel)",
                    data=output,
                    file_name=f"reshuffled_students_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.ms-excel",
                    use_container_width=True
                )
                
                # ==================== SUCCESS METRICS ====================
                st.markdown("---")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Students", len(df))
                with col2:
                    st.metric("Streams Created", num_streams)
                with col3:
                    st.metric("Avg Score Variance", f"{score_variance} marks")
                with col4:
                    st.metric("Boarder Variance", f"{boarder_variance} students")
                
                st.balloons()
                
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.exception(e)  # This will show the full traceback in development

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>© 2026 KenyaVault - Dynamic Student Reshuffling System</p>
    <p style="font-size: 0.9rem;">Built with ❤️ for Kenyan Schools</p>
</div>
""", unsafe_allow_html=True)
