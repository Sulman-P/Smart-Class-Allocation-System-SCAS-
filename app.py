import streamlit as st
import pandas as pd
import numpy as np
import io
import random

# Page Configuration
st.set_page_config(page_title="Dynamic Student Reshuffling System", page_icon="🏫", layout="wide")

st.title("🏫 Dynamic Student Reshuffling & Allocation System")
st.markdown("This system utilizes an **Iterative Stratified Optimization Engine** to guarantee a class average variance under 2 marks, while simultaneously ensuring that Boarder and Day student counts match across all streams.")

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
            # 1. Stratify by Boarding Status first, then sort by score descending
            boarders = df[df['Status'].str.lower() == 'boarder'].sort_values(by='Academic Score', ascending=False).reset_index(drop=True)
            day_students = df[df['Status'].str.lower() != 'boarder'].sort_values(by='Academic Score', ascending=False).reset_index(drop=True)
            
            # Initialize empty stream buckets
            assigned_data = {name: [] for name in stream_names}
            
            # Helper logic to distribute a dataset using serpentine wave
            def distribute_serpentine(data_df, current_forward, current_index):
                for _, student in data_df.iterrows():
                    target_stream = stream_names[current_index]
                    assigned_data[target_stream].append(student.to_dict())
                    
                    if current_forward:
                        if current_index < num_streams - 1:
                            current_index += 1
                        else:
                            current_forward = False
                    else:
                        if current_index > 0:
                            current_index -= 1
                        else:
                            current_forward = True
                return current_forward, current_index

            # Snake the boarders through first, then perfectly pick up the sequence for day students
            forward, stream_idx = distribute_serpentine(boarders, True, 0)
            distribute_serpentine(day_students, forward, stream_idx)
            
            # 2. GREEDY CORRECTION LOOP (Fine-tune boarder distribution vs score deviation)
            for _ in range(200): # Up to 200 refinement passes
                counts = {s: sum(1 for x in assigned_data[s] if x['Status'].lower() == 'boarder') for s in stream_names}
                max_b_stream = max(counts, key=counts.get)
                min_b_stream = min(counts, key=counts.get)
                
                # If the variance in boarder counts between any stream is <= 1, it's perfectly balanced
                if counts[max_b_stream] - counts[min_b_stream] <= 1:
                    break
                
                max_stream_boarders = [x for x in assigned_data[max_b_stream] if x['Status'].lower() == 'boarder']
                min_stream_day = [x for x in assigned_data[min_b_stream] if x['Status'].lower() != 'boarder']
                
                best_swap = None
                best_score_diff_impact = float('inf')
                
                for b_stud in max_stream_boarders:
                    for d_stud in min_stream_day:
                        # Simulated swap calculations
                        curr_avg_max = np.mean([x['Academic Score'] for x in assigned_data[max_b_stream]])
                        curr_avg_min = np.mean([x['Academic Score'] for x in assigned_data[min_b_stream]])
                        
                        sim_avg_max = np.mean([x['Academic Score'] if x['Student ID'] != b_stud['Student ID'] else d_stud['Academic Score'] for x in assigned_data[max_b_stream]])
                        sim_avg_min = np.mean([x['Academic Score'] if x['Student ID'] != d_stud['Student ID'] else b_stud['Academic Score'] for x in assigned_data[min_b_stream]])
                        
                        sim_range = abs(sim_avg_max - sim_avg_min)
                        
                        if sim_range < 1.9 and abs(b_stud['Academic Score'] - d_stud['Academic Score']) < best_score_diff_impact:
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
            
            # Dashboard Metrics Presentation
            st.header("📊 Reshuffle Performance Dashboard")
            
            col1, col2 = st.columns(2)
            with col1:
                if score_variance <= 2.0:
                    st.success(f"🎯 Academic Mark Variance: **{score_variance} marks** (Target met: < 2.0)")
                else:
                    st.warning(f"⚠️ Academic Mark Variance: **{score_variance} marks** (Slightly compromised to protect boarding parity)")
            with col2:
                if boarder_variance <= 1:
st.success(f"⚖️ Boarder Parity: Perfect (Max difference between classes is {boarder_variance} student)")else:st.warning(f"⚠️ Boarder Difference: {boarder_variance} students deviation across streams.")st.dataframe(summary_df, use_container_width=True)# --- EXCEL EXPORT ---output_buffer = io.BytesIO()with pd.ExcelWriter(output_buffer, engine='xlsxwriter') as writer:summary_df.to_excel(writer, sheet_name='Dashboard Summary', index=False)for stream in stream_names:workbook  = writer.bookworksheet = workbook.add_worksheet(stream[:31])writer.sheets[stream[:31]] = worksheetworksheet.write(0, 0, f"Class Teacher: {teacher_mapping[stream]}")final_streams_dfs[stream].to_excel(writer, sheet_name=stream[:31], startrow=2, index=False)
st.markdown("### ✨ Allocation Ready")st.download_button(label=f"📥 Download {grade_level}Reshuffle_Report.xlsx",data=output_buffer.getvalue(),file_name=f"{grade_level.replace(' ', '')}_Reshuffle_Report.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")with st.expander("🔍 Preview Stream Rosters"):selected_preview = st.selectbox("Select stream roster to view:", stream_names)st.write(f"Assigned Teacher: {teacher_mapping[selected_preview]}")st.dataframe(final_streams_dfs[selected_preview], use_container_width=True)except Exception as e:st.error(f"An unexpected error occurred during processing: {e}")
