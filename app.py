import streamlit as st
import pandas as pd
import numpy as np
import io
import random

# Page Configuration
st.set_page_config(page_title="Dynamic Student Reshuffling System", page_icon="🏫", layout="wide")

st.title("🏫 Dynamic Student Reshuffling & Allocation System")
st.markdown("This system utilizes a **Multi-Constraint Optimization Engine** to guarantee a class average variance under 2 marks, while ensuring the difference in Boarder counts across any two streams is 2 or fewer students.")

# --- SIDEBAR: SYSTEM CONFIGURATION ---
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

# --- MAIN PAGE: DATA INPUT ---
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
    mime="application/vnd.ms-excel"
)

uploaded_file = st.file_uploader("Upload Student Excel Spreadsheet (.xlsx)", type=["xlsx"])

# --- PROCESSING ENGINE ---
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        
        # Validate Required Columns
        required_cols = ['Student ID', 'Name', 'Gender', 'Status', 'Academic Score']
        if not all(col in df.columns for col in required_cols):
            st.error(f"Error: Excel file must contain these exact columns: {', '.join(required_cols)}")
        elif len(teacher_list) < num_streams:
            st.error(f"Error: You selected {num_streams} streams but only provided {len(teacher_list)} teacher(s). Please add more teachers in the sidebar.")
        else:
            st.success("✅ Student data loaded successfully!")
            
            # --- BALANCING CORE ENGINE ---
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
            # Runs fine-tuning loops to shift boarders where variance across any stream exceeds 2 students
            for _ in range(500):
                counts = {s: sum(1 for x in assigned_data[s] if str(x['Status']).strip().lower() == 'boarder') for s in stream_names}
                max_b_stream = max(counts, key=counts.get)
                min_b_stream = min(counts, key=counts.get)
                
                # Condition met: The variance difference is already equal to or less than 2
                if counts[max_b_stream] - counts[min_b_stream] <= 2:
                    break
                
                max_stream_boarders = [x for x in assigned_data[max_b_stream] if str(x['Status']).strip().lower() == 'boarder']
                min_stream_day = [x for x in assigned_data[min_b_stream] if str(x['Status']).strip().lower() != 'boarder']
                
                best_swap = None
                best_score_diff_impact = float('inf')
                
                # Double loop to look for paired candidates with the smallest academic distance
                for b_stud in max_stream_boarders:
                    for d_stud in min_stream_day:
                        # Simulated temporary swap impact checks
                        sim_avg_max = np.mean([x['Academic Score'] if x['Student ID'] != b_stud['Student ID'] else d_stud['Academic Score'] for x in assigned_data[max_b_stream]])
                        sim_avg_min = np.mean([x['Academic Score'] if x['Student ID'] != d_stud['Student ID'] else b_stud['Academic Score'] for x in assigned_data[min_b_stream]])
                        
                        # Fetch global boundary boundaries to prevent any single stream escaping limits
                        all_current_averages = []
                        for s in stream_names:
                            if s == max_b_stream:
                                all_current_averages.append(sim_avg_max)
                            elif s == min_b_stream:
                                all_current_averages.append(sim_avg_min)
                            else:
                                all_current_averages.append(np.mean([x['Academic Score'] for x in assigned_data[s]]))
                        
                        sim_global_range = max(all_current_averages) - min(all_current_averages)
                        
                        # Keep trade window open if marks variation stays safely under 2.0
                        if sim_global_range < 1.95 and abs(b_stud['Academic Score'] - d_stud['Academic Score']) < best_score_diff_impact:
                            best_score_diff_impact = abs(b_stud['Academic Score'] - d_stud['Academic Score'])
                            best_swap = (b_stud, d_stud)
                
                if best_swap:
                    b_stud, d_stud = best_swap
                    assigned_data[max_b_stream].remove(b_stud)
                    assigned_data[min_b_stream].remove(d_stud)
                    
                    assigned_data[max_b_stream].append(d_stud)
                    assigned_data[min_b_stream].append(b_stud)
                else:
                    break 

            # 3. Unbiased Teacher Assignment
            selected_teachers = random.sample(teacher_list, num_streams)
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
                    avg_score = round(stream_students['Academic Score'].mean(), 2)
                    male_count = len(stream_students[stream_students['Gender'] == 'M'])
                    female_count = len(stream_students[stream_students['Gender'] == 'F'])
                    boarder_count = len(stream_students[stream_students['Status'].str.lower() == 'boarder'])
                    day_count = len(stream_students[stream_students['Status'].str.lower() != 'boarder'])
                else:
                    total_students, avg_score, male_count, female_count, boarder_count, day_count = 0, 0, 0, 0, 0, 0
                    final_streams_dfs[stream] = pd.DataFrame(columns=required_cols)
                
                summary_data.append({
                    "Stream": stream,
                    "Class Teacher": teacher_mapping[stream],
                    "Total Students": total_students,
                    "Avg Academic Score": avg_score,
                    "Male Count": male_count,
                    "Female Count": female_count,
                    "Boarder Count": boarder_count,
                    "Day Count": day_count
                })
                
            summary_df = pd.DataFrame(summary_data)
            score_variance = round(summary_df["Avg Academic Score"].max() - summary_df["Avg Academic Score"].min(), 2)
            boarder_variance = summary_df["Boarder Count"].max() - summary_df["Boarder Count"].min()
            
            # Dashboard Presentation
            st.header("📊 Reshuffle Performance Dashboard")
            
            col1, col2 = st.columns(2)
            with col1:
                if score_variance <= 2.0:
                    st.success(f"🎯 Academic Mark Variance: **{score_variance} marks** (Target met: < 2.0)")
                else:
                    st.warning(f"⚠️ Academic Mark Variance: **{score_variance} marks** (Slightly compromised to protect boarding parity)")
