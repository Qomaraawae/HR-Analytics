# ========================================
# HR ANALYTICS DASHBOARD - STREAMLIT
# ========================================
# Lokasi: /Users/macbookpro/Documents/UAD/MATKUL/INTELEJEN BISNIS/HR_Analytics/hr_dashboard.py
# Jalankan: streamlit run hr_dashboard.py
# ========================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ========================================
# KONFIGURASI HALAMAN
# ========================================

st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# LOAD DATA
# ========================================

@st.cache_data
def load_data():
    base_path = '/Users/macbookpro/Documents/UAD/MATKUL/INTELEJEN BISNIS/HR_Analytics/'
    data_path = os.path.join(base_path, 'Data', 'hr_data_for_dashboard.csv')
    
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        st.sidebar.success("✅ Data dari hasil analisis lengkap")
    else:
        # Fallback ke data asli
        excel_path = os.path.join(base_path, 'HR_Analytics.xlsx')
        df = pd.read_excel(excel_path, sheet_name='Sheet1')
        df.columns = df.columns.str.replace('ï»¿', '').str.replace('¬ª', '').str.replace('¬ø', '')
        st.sidebar.warning("⚠️ Menggunakan data asli (tanpa prediksi)")
    return df

df = load_data()

# ========================================
# SIDEBAR FILTER
# ========================================

st.sidebar.title("🔍 Filter Data")
st.sidebar.markdown("---")

# Filter Department
dept_options = ['All'] + sorted(df['Department'].dropna().unique().tolist())
selected_dept = st.sidebar.selectbox("🏢 Department", dept_options)

# Filter Age Group
age_options = ['All'] + sorted(df['AgeGroup'].dropna().unique().tolist())
selected_age = st.sidebar.selectbox("📅 Age Group", age_options)

# Filter Attrition
attrition_options = ['All', 'Yes', 'No']
selected_attrition = st.sidebar.selectbox("⚠️ Attrition", attrition_options)

# Filter Job Role
job_options = ['All'] + sorted(df['JobRole'].dropna().unique().tolist())
selected_job = st.sidebar.selectbox("💼 Job Role", job_options)

# Filter OverTime
overtime_options = ['All', 'Yes', 'No']
selected_overtime = st.sidebar.selectbox("⏰ OverTime", overtime_options)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Tips:**\n"
    "- Gunakan filter untuk segmentasi data\n"
    "- Hover ke grafik untuk detail\n"
    "- Klik legenda untuk filter grafik"
)

# ========================================
# FILTER DATA
# ========================================

filtered_df = df.copy()

if selected_dept != 'All':
    filtered_df = filtered_df[filtered_df['Department'] == selected_dept]

if selected_age != 'All':
    filtered_df = filtered_df[filtered_df['AgeGroup'] == selected_age]

if selected_attrition != 'All':
    filtered_df = filtered_df[filtered_df['Attrition'] == selected_attrition]

if selected_job != 'All':
    filtered_df = filtered_df[filtered_df['JobRole'] == selected_job]

if selected_overtime != 'All':
    filtered_df = filtered_df[filtered_df['OverTime'] == selected_overtime]

# ========================================
# HEADER
# ========================================

st.title("📊 HUMAN RESOURCES ANALYTICS DASHBOARD")
st.markdown(f"*Menampilkan {len(filtered_df):,} karyawan dari total {len(df):,} data*")
st.markdown("---")

# ========================================
# KPI CARDS
# ========================================

st.subheader("📈 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Total Karyawan",
        value=f"{len(filtered_df):,}"
    )

with col2:
    attrition_rate = filtered_df['Attrition'].value_counts(normalize=True).get('Yes', 0) * 100
    st.metric(
        label="Attrition Rate",
        value=f"{attrition_rate:.1f}%",
        delta="⚠️ Perlu Perhatian" if attrition_rate > 15 else "✅ Baik",
        delta_color="inverse" if attrition_rate > 15 else "normal"
    )

with col3:
    avg_salary = filtered_df['MonthlyIncome'].mean()
    st.metric(
        label="Rata-rata Gaji",
        value=f"${avg_salary:,.0f}"
    )

with col4:
    avg_years = filtered_df['YearsAtCompany'].mean()
    st.metric(
        label="Rata-rata Masa Kerja",
        value=f"{avg_years:.1f} tahun"
    )

with col5:
    avg_satisfaction = filtered_df['JobSatisfaction'].mean()
    st.metric(
        label="Job Satisfaction",
        value=f"{avg_satisfaction:.2f} / 4",
        delta="⭐" * int(avg_satisfaction)
    )

st.markdown("---")

# ========================================
# ROW 1: DISTRIBUSI
# ========================================

st.subheader("📊 Distribusi Data")

col1, col2 = st.columns(2)

with col1:
    attrition_counts = filtered_df['Attrition'].value_counts().reset_index()
    attrition_counts.columns = ['Attrition', 'Count']
    fig1 = px.pie(
        attrition_counts,
        values='Count',
        names='Attrition',
        title='Distribusi Attrition',
        color='Attrition',
        color_discrete_map={'Yes': '#e74c3c', 'No': '#2ecc71'},
        hole=0.4
    )
    fig1.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.histogram(
        filtered_df,
        x='MonthlyIncome',
        nbins=30,
        title='Distribusi Monthly Income',
        color_discrete_sequence=['#3498db'],
        labels={'MonthlyIncome': 'Monthly Income (USD)'}
    )
    fig2.add_vline(x=filtered_df['MonthlyIncome'].mean(), line_dash="dash", line_color="red")
    st.plotly_chart(fig2, use_container_width=True)

# ========================================
# ROW 2: HUBUNGAN
# ========================================

st.subheader("🔗 Hubungan Antar Variabel")

col1, col2 = st.columns(2)

with col1:
    dept_attrition = pd.crosstab(filtered_df['Department'], filtered_df['Attrition']).reset_index()
    dept_attrition_melted = dept_attrition.melt(id_vars=['Department'], var_name='Attrition', value_name='Count')
    fig3 = px.bar(
        dept_attrition_melted,
        x='Department',
        y='Count',
        color='Attrition',
        title='Attrition per Department',
        barmode='group',
        color_discrete_map={'Yes': '#e74c3c', 'No': '#2ecc71'},
        text='Count'
    )
    fig3.update_traces(textposition='outside')
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    overtime_attrition = pd.crosstab(filtered_df['OverTime'], filtered_df['Attrition']).reset_index()
    overtime_attrition_melted = overtime_attrition.melt(id_vars=['OverTime'], var_name='Attrition', value_name='Count')
    fig4 = px.bar(
        overtime_attrition_melted,
        x='OverTime',
        y='Count',
        color='Attrition',
        title='Attrition vs OverTime',
        barmode='group',
        color_discrete_map={'Yes': '#e74c3c', 'No': '#2ecc71'},
        text='Count'
    )
    fig4.update_traces(textposition='outside')
    st.plotly_chart(fig4, use_container_width=True)

# ========================================
# ROW 3: ANALISIS MENDALAM
# ========================================

st.subheader("📉 Analisis Mendalam")

col1, col2 = st.columns(2)

with col1:
    fig5 = px.scatter(
        filtered_df,
        x='YearsAtCompany',
        y='MonthlyIncome',
        color='Attrition',
        title='Years at Company vs Monthly Income',
        hover_data=['EmpID', 'JobRole', 'Age', 'JobSatisfaction'],
        color_discrete_map={'Yes': '#e74c3c', 'No': '#2ecc71'},
        opacity=0.7
    )
    fig5.update_traces(marker=dict(size=8))
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    fig6 = px.box(
        filtered_df,
        x='Attrition',
        y='JobSatisfaction',
        title='Job Satisfaction vs Attrition',
        color='Attrition',
        color_discrete_map={'Yes': '#e74c3c', 'No': '#2ecc71'},
        labels={'JobSatisfaction': 'Job Satisfaction (1-4)'}
    )
    st.plotly_chart(fig6, use_container_width=True)

# ========================================
# ROW 4: CLUSTER VISUALIZATION
# ========================================

st.subheader("👥 Segmentasi Karyawan (Clustering)")

if 'Cluster' in filtered_df.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        cluster_counts = filtered_df['Cluster'].value_counts().sort_index().reset_index()
        cluster_counts.columns = ['Cluster', 'Count']
        fig7 = px.bar(
            cluster_counts,
            x='Cluster',
            y='Count',
            title='Distribusi Karyawan per Cluster',
            color='Cluster',
            color_continuous_scale='viridis',
            text='Count'
        )
        fig7.update_traces(textposition='outside')
        st.plotly_chart(fig7, use_container_width=True)
    
    with col2:
        fig8 = px.scatter(
            filtered_df,
            x='YearsAtCompany',
            y='MonthlyIncome',
            color='Cluster',
            title='Cluster Visualization: Years vs Income',
            hover_data=['EmpID', 'JobRole', 'Age'],
            color_continuous_scale='viridis',
            opacity=0.7
        )
        fig8.update_traces(marker=dict(size=8))
        st.plotly_chart(fig8, use_container_width=True)
else:
    st.info("💡 Jalankan analisis clustering terlebih dahulu untuk melihat segmentasi karyawan.")

# ========================================
# TABEL DATA
# ========================================

st.subheader("📋 Data Karyawan")

display_cols = ['EmpID', 'Age', 'Department', 'JobRole', 'MonthlyIncome', 
                'YearsAtCompany', 'JobSatisfaction', 'OverTime', 'Attrition']

if 'Attrition_Probability' in filtered_df.columns:
    display_cols.append('Attrition_Probability')

available_cols = [col for col in display_cols if col in filtered_df.columns]

st.dataframe(
    filtered_df[available_cols],
    use_container_width=True,
    height=400,
    column_config={
        "MonthlyIncome": st.column_config.NumberColumn("Monthly Income", format="$%d"),
        "Attrition_Probability": st.column_config.ProgressColumn("Risk", format="%.1f%%", min_value=0, max_value=1)
    }
)

# ========================================
# DOWNLOAD DATA
# ========================================

st.sidebar.markdown("---")
st.sidebar.subheader("📥 Download Data")

csv = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="⬇️ Download Data CSV",
    data=csv,
    file_name="hr_analytics_filtered.csv",
    mime="text/csv"
)

# ========================================
# FOOTER
# ========================================

st.markdown("---")
st.caption("HR Analytics Dashboard | Dibuat dengan Streamlit ❤️ | Data Mining: Klasifikasi, Regresi, Clustering")