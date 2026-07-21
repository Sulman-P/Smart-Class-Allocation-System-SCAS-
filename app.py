import streamlit as st
import pandas as pd
import numpy as np
import io
import random

# Page Configuration
st.set_page_config(page_title="Dynamic Student Reshuffling System", page_icon="🏫", layout="wide")

st.title("🏫 Dynamic Student Reshuffling & Allocation System")
st.markdown("This system dynamically balances students across multiple streams using a **Serpentine Stratification Algorithm** to ensure equal distribution of gender, boarding status, and academic performance.")

# --- SIDEBAR: SYSTEM CONFIGURATION ---
st.sidebar.header("⚙️ System Configuration")

# 1. Target Grade/Level
grade_level = st.sidebar.text_input("Target Grade / Level", value="Form 1", help="e.g., Form 1, Grade 9")

# 2. Adjustable Streams (Max 8)
num_streams = st.sidebar.slider("Number of Streams", min_value=2, max_value=8, value=4)

# 3. Dynamic Stream Naming
st.sidebar.subheader("📋 Stream Names")
stream_names = []
for i in range(num_streams):
    default_name = f"Stream {chr(65 + i)}" # Generates Stream A, Stream B, etc.
    name = st.sidebar.text_input(f"Name for Stream {i+1}", value=default_name, key=f"stream_name_{i}")
    stream_names.append(name)

# 4. Teacher List Input
st.sidebar.subheader("🧑‍🏫 Class Teachers")
teachers_input = st.sidebar.text_area(
    "Enter teacher names (One per line):", 
    value="Mr. John Doe\nMs. Jane Smith\nMr. Alex Cooper\nMrs. Sarah Jenkins\nMr. Brian Vance\nMs. Lucy Heart\nMr. David Miller\nMrs. Emily Rose"
)
teacher_list = [t.strip() for t in teachers_input.split("\n") if t.strip()]

# --- MAIN PAGE: DATA INPUT ---
st.header("📊 Student Data Input")

# Provide a sample template download link for convenience
template_df = pd.DataFrame({
    'Student ID': ['ST001', 'ST002', 'ST003', 'ST004'],
    'Name': ['Alice Jones', 'Bob Smith', 'Charlie Brown', 'Diana Prince'],
    'Gender': ['F', 'M', 'M', 'F'],
    'Status': ['Boarder', 'Day', 'Boarder', 'Day'],
    'Academic Score': [85.5, 72.0, 91.3, 64.8]
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

uploaded_file = st.file_file = st.file_uploader("Upload Student Excel Spreadsheet (.xlsx)", type=["xlsx"])

# --- PROCESSING ENGINE ---
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        
        # Validate Required Columns
        required_cols = ['Student ID', 'Name', 'Gender', 'Status', 'Academic Score']
        if not all(col in df.columns for col in required_cols):
            st.error(f"Error: Excel file must contain these exact columns: {', '.join(required_cols)}")
        elif len(teacher_list) < num_streams:
            st.error(f"Error: You selected {num_streams} streams but only provided {len(teacher_list)} teacher(s). Please add more teachers.")
        else:
            st.success("✅ Student data loaded successfully!")
            
            # --- RESHUFFLING LOGIC ---
            # 1. Segment into groups based on Gender and Boarding Status
            groups = df.groupby(['Gender', 'Status'])
            
            # Initialize empty structures to hold assigned streams
            assigned_data = {name: [] for name in stream_names}
            
            # 2. Serpentine Distribution algorithm per group
            for (gender, status), group_df in groups:
                # Rank students descending by Academic Score within this specific sub-category
                sorted_group = group_df.sort_values(by='Academic Score', ascending=False).to_dict('records')
                
                forward = True
                stream_index = 0
                
                for student in sorted_group:
                    target_stream = stream_names[stream_index]
                    assigned_data[target_stream].append(student)
                    
                    # Move to next stream using serpentine pattern
                    if forward:
                        if stream_index < num_streams - 1:
                            stream_index += 1
                        else:
                            forward = False  # Reverse direction at the edge
                    else:
                        if stream_index > 0:
                            stream_index -= 1
                        else:
                            forward = True   # Reverse back to forward direction
            
            # 3. Unbiased Teacher Assignment
            selected_teachers = random.sample(teacher_list, num_streams)
            teacher_mapping = {stream_names[i]: selected_teachers[i] for i in range(num_streams)}
            
            # --- GENERATING THE DASHBOARD REPORT ---
            summary_data = []
            final_streams_dfs = {}
            
            for stream in stream_names:
                stream_students = pd.DataFrame(assigned_data[stream])
                
                if not stream_students.empty:
                    # Individual Stream Data Prep (Sorted Alphabetically by Name)
                    stream_students = stream_students.sort_values(by='Name')
                    final_streams_dfs[stream] = stream_students
                    
                    # Compute Dashboard Metrics
                    total_students = len(stream_students)
                    avg_score = round(stream_students['Academic Score'].mean(), 2)
                    male_count = len(stream_students[stream_students['Gender'] == 'M'])
                    female_count = len(stream_students[stream_students['Gender'] == 'F'])
                    boarder_count = len(stream_students[stream_students['Status'] == 'Boarder'])
                    day_count = len(stream_students[stream_students['Status'] == 'Day'])
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
            
            # Display Dashboard to User
            st.header("📊 Reshuffle Performance Dashboard")
            st.dataframe(summary_df, use_container_width=True)
            
            # --- EXCEL EXPORT GENERATION ---
            output_buffer = io.BytesIO()
            with pd.ExcelWriter(output_buffer, engine='xlsxwriter') as writer:
                # Tab 1: Dashboard Summary
                summary_df.to_excel(writer, sheet_name='Dashboard Summary', index=False)
                
                # Dynamic Tabs for Each Individual Stream
                for stream in stream_names:
                    # Write Class Teacher Information at the top row
                    workbook  = writer.book
                    worksheet = workbook.add_worksheet(stream[:31]) # Excel limits tab names to 31 chars
                    writer.sheets[stream[:31]] = worksheet
                    
                    worksheet.write(0, 0, f"Class Teacher: {teacher_mapping[stream]}")
                    
                    # Write Roster table starting below the teacher name row
                    final_streams_dfs[stream].to_excel(writer, sheet_name=stream[:31], startrow=2, index=False)
            
            st.markdown("### ✨ Allocation Ready")
            st.download_button(
                label=f"📥 Download {grade_level}_Reshuffle_Report.xlsx",
                data=output_buffer.getvalue(),
                file_name=f"{grade_level.replace(' ', '_')}_Reshuffle_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Stream Previewer UI element
            with st.expander("🔍 Preview Stream Rosters"):
                selected_preview = st.selectbox("Select stream roster to view:", stream_names)
                st.write(f"**Assigned Teacher:** {teacher_mapping[selected_preview]}")
                st.dataframe(final_streams_dfs[selected_preview], use_container_width=True)
                
    except Exception as e:
        st.error(f"An unexpected error occurred during processing: {e}")
