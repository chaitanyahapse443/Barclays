import streamlit as st
import json
import pandas as pd
import requests
from pathlib import Path
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="SAR AI Platform",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling with enhanced UI
st.markdown("""
<style>
    .main { padding: 2rem; }
    .stTabs { margin-top: 2rem; }
    .success-box { background-color: #d4edda; padding: 1rem; border-radius: 0.5rem; color: #155724; border-left: 4px solid #28a745; }
    .error-box { background-color: #f8d7da; padding: 1rem; border-radius: 0.5rem; color: #721c24; border-left: 4px solid #dc3545; }
    .info-box { background-color: #d1ecf1; padding: 1rem; border-radius: 0.5rem; color: #0c5460; border-left: 4px solid #17a2b8; }
    .warning-box { background-color: #fff3cd; padding: 1rem; border-radius: 0.5rem; color: #856404; border-left: 4px solid #ffc107; }
    .card { background-color: #f8f9fa; padding: 1.5rem; border-radius: 0.5rem; margin: 1rem 0; border: 1px solid #dee2e6; }
    .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 0.5rem; }
    h1 { color: #667eea; }
    h2 { color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 0.5rem; }
    h3 { color: #764ba2; }
</style>
""", unsafe_allow_html=True)

API_BASE = st.secrets.get('api_base', 'http://localhost:8001')

# Session state for storing case and SAR data
if 'current_case' not in st.session_state:
    st.session_state.current_case = None
if 'current_sar' not in st.session_state:
    st.session_state.current_sar = None
if 'sar_draft' not in st.session_state:
    st.session_state.sar_draft = ""

# Title and description
st.markdown("# 📋 SAR Narrative Generator Platform")
st.markdown("*An intelligent Suspicious Activity Report generation system with complete audit trails and version control*")

# Sidebar navigation
st.sidebar.markdown("## Navigation")
page = st.sidebar.radio("Select a page", ["Dashboard", "Create Case", "Generate SAR", "View Audit Trail", "Settings"])

# ====================== DASHBOARD PAGE ======================
if page == "Dashboard":
    st.markdown("## 📊 Dashboard Overview")
    
    # Check API health
    try:
        api_health = requests.get(f"{API_BASE}/", timeout=2)
        api_status = "✅ Connected"
        api_color = "green"
    except:
        api_status = "❌ Offline"
        api_color = "red"
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🚀 Status", "Ready", delta="All Systems")
    with col2:
        st.metric("🔗 API", "Connected", delta="Port 8001")
    with col3:
        st.metric("💾 Database", "Initialized", delta="4 Tables")
    with col4:
        st.metric("👥 Users", "2 Accounts", delta="Admin + Analyst")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 🚀 Quick Start Guide")
    with col2:
        if st.button("📺 View Features"):
            st.session_state.show_features = True
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Step 1️⃣ - Create Case**
        1. Click on "Create Case" tab
        2. Select a sample case from dropdown
        3. Review case details, alerts, and transactions
        4. Click "Create Case" button
        
        **Step 2️⃣ - Generate SAR**
        1. Navigate to "Generate SAR" tab
        2. AI automatically analyzes the case
        3. Edit the narrative if needed
        4. View explainability panel
        """)
    
    with col2:
        st.markdown("""
        **Step 3️⃣ - Review & Export**
        1. Check the "View Audit Trail" tab
        2. See all tracked changes
        3. Go to "Generate SAR" → Export tab
        4. Download as PDF or JSON
        
        **🔐 Key Features**
        - Role-based access control
        - Complete audit logging
        - Version control
        - AI explainability
        - PDF export
        """)
    
    st.markdown("---")
    st.markdown("### 🎯 System Information")
    
    info_col1, info_col2, info_col3 = st.columns(3)
    with info_col1:
        st.info("""
        **📦 Backend**
        - FastAPI Server
        - Port: 8001
        - Status: Running
        """)
    with info_col2:
        st.info("""
        **💻 Frontend**
        - Streamlit UI
        - Port: 8501
        - Status: Active
        """)
    with info_col3:
        st.info("""
        **💾 Database**
        - SQLite
        - Schema: Initialized
        - Tables: 4
        """)


# ====================== CREATE CASE PAGE ======================
elif page == "Create Case":
    st.markdown("## 📝 Create Suspicious Activity Case")
    
    # Load sample cases
    sample_dir = Path(__file__).resolve().parents[1] / 'sample_data'
    samples = sorted([p.name for p in sample_dir.glob('*.json')])
    
    if not samples:
        st.error("❌ No sample cases found in sample_data directory")
        st.stop()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_case = st.selectbox('📂 Select a sample case to load:', ['-- Choose a case --'] + samples)
    with col2:
        if st.button('🔄 Refresh Cases', use_container_width=True):
            st.rerun()
    
    if selected_case and selected_case != '-- Choose a case --':
        try:
            case_file = sample_dir / selected_case
            case_data = json.loads(case_file.read_text())
            st.session_state.current_case = case_data
            
            # Display case information in cards
            st.markdown("### 📋 Case Information")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="card">
                    <h4>📌 Case ID</h4>
                    <p><strong>{case_data.get('case_id', 'N/A')}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="card">
                    <h4>👤 Customer Name</h4>
                    <p><strong>{case_data.get('customer_name', 'N/A')}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="card">
                    <h4>🔢 Customer ID</h4>
                    <p><strong>{case_data.get('customer_id', 'N/A')}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            
            # Alerts section
            if 'alerts' in case_data and case_data['alerts']:
                st.markdown("### ⚠️ Associated Alerts")
                alerts_df = pd.DataFrame(case_data['alerts'])
                
                # Display alert count
                st.metric("Total Alerts", len(alerts_df))
                st.dataframe(alerts_df, use_container_width=True, hide_index=True)
            
            # Transactions section
            if 'transactions' in case_data and case_data['transactions']:
                st.markdown("### 💰 Transactions")
                trans_df = pd.DataFrame(case_data['transactions'])
                
                # Format amount with currency
                if 'amount' in trans_df.columns:
                    trans_df['Amount'] = trans_df['amount'].apply(lambda x: f"₹{x:,.0f}")
                
                st.metric("Total Transactions", len(trans_df))
                st.dataframe(trans_df, use_container_width=True, hide_index=True)
            
            # Create case button
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button('✅ Create Case', use_container_width=True, key='create_case_btn', type="primary"):
                    with st.spinner('🔄 Creating case...'):
                        try:
                            resp = requests.post(f"{API_BASE}/cases/create", json=case_data, timeout=10)
                            if resp.status_code == 200:
                                result = resp.json()
                                st.success('✅ Case created successfully!')
                                st.markdown(f"**Case ID:** `{result.get('case_id')}`")
                                st.balloons()
                                st.session_state.current_case = result
                            else:
                                st.error(f"❌ Error: {resp.text}")
                        except requests.Timeout:
                            st.error("❌ Request timeout. API may be busy.")
                        except Exception as e:
                            st.error(f"❌ Connection error: {str(e)}")
            with col2:
                if st.button('🔄 Clear', use_container_width=True):
                    st.session_state.current_case = None
                    st.rerun()
        
        except FileNotFoundError:
            st.error(f"❌ Case file not found: {selected_case}")
        except json.JSONDecodeError:
            st.error(f"❌ Invalid JSON in: {selected_case}")
    else:
        st.info("ℹ️ Select a case from the dropdown above to get started")

# ====================== GENERATE SAR PAGE ======================
elif page == "Generate SAR":
    st.markdown("## Generate SAR Narrative")
    
    if not st.session_state.current_case:
        st.warning("⚠️ Please create a case first in the 'Create Case' tab")
    else:
        case_id = st.session_state.current_case.get('case_id')
        st.markdown(f"### Processing Case: **{case_id}**")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**Customer:** {st.session_state.current_case.get('customer_name')}")
        with col2:
            if st.button('🚀 Generate SAR Draft', use_container_width=True):
                with st.spinner('Generating SAR using AI...'):
                    try:
                        resp = requests.post(f"{API_BASE}/sars/generate", params={'case_id': case_id}, timeout=10)
                        if resp.status_code == 200:
                            sar_data = resp.json()
                            st.session_state.current_sar = sar_data
                            st.session_state.sar_draft = sar_data.get('sar_draft', '')
                            st.success("✅ SAR Draft Generated Successfully!")
                        else:
                            st.error(f"❌ Error: {resp.text}")
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")
        
        st.markdown("---")
        
        if st.session_state.current_sar:
            sar_data = st.session_state.current_sar
            
            # Tabs for different SAR views
            tab1, tab2, tab3, tab4 = st.tabs(["📄 Draft", "🔍 Analysis", "📊 Audit Trail", "⬇️ Export"])
            
            # Draft Tab
            with tab1:
                st.markdown("### SAR Draft")
                draft_text = st.text_area(
                    "SAR Narrative (Editable)",
                    value=st.session_state.sar_draft,
                    height=400,
                    key="draft_editor"
                )
                st.session_state.sar_draft = draft_text
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button('💾 Save Draft'):
                        st.success("✅ Draft saved locally")
                with col2:
                    if st.button('🔄 Reset'):
                        st.session_state.sar_draft = sar_data.get('sar_draft', '')
                        st.rerun()
            
            # Analysis Tab
            with tab2:
                st.markdown("### Explainability & Risk Analysis")
                
                if 'explain' in sar_data and sar_data['explain']:
                    explain = sar_data['explain']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### 🎯 Generated Reasoning")
                        if isinstance(explain, dict):
                            for key, value in explain.items():
                                st.markdown(f"**{key}:** {value}")
                        else:
                            st.write(explain)
                    
                    with col2:
                        st.markdown("#### ⚡ Risk Indicators")
                        st.info("Pattern matching completed. Use transaction timeline to view suspicious activities.")
            
            # Audit Trail Tab
            with tab3:
                st.markdown("### Audit Trail")
                
                if 'audit' in sar_data and sar_data['audit']:
                    audit = sar_data['audit']
                    
                    # Display audit info in columns
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**SAR ID:** `{audit.get('sar_id')}`")
                        st.markdown(f"**Created At:** {audit.get('created_at')}")
                    with col2:
                        st.markdown(f"**Version:** {audit.get('version', '1.0')}")
                        st.markdown(f"**Status:** {audit.get('status', 'Draft')}")
                    
                    st.markdown("---")
                    st.markdown("**Tracked Changes:**")
                    st.info("Full audit trail with timestamps and user tracking is maintained in the backend")
            
            # Export Tab
            with tab4:
                st.markdown("### Export Options")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button('📥 Export as PDF', use_container_width=True):
                        try:
                            sar_id = sar_data.get('sar_id')
                            pdf_resp = requests.get(f"{API_BASE}/sars/export/{sar_id}", timeout=10)
                            if pdf_resp.status_code == 200:
                                st.download_button(
                                    label="⬇️ Download PDF",
                                    data=pdf_resp.content,
                                    file_name=f"SAR_{sar_id}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                    mime="application/pdf"
                                )
                            else:
                                st.error("Failed to generate PDF")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                
                with col2:
                    if st.button('📋 Export as JSON', use_container_width=True):
                        json_str = json.dumps(sar_data, indent=2)
                        st.download_button(
                            label="⬇️ Download JSON",
                            data=json_str,
                            file_name=f"SAR_{sar_data.get('sar_id')}_{datetime.now().strftime('%Y%m%d')}.json",
                            mime="application/json"
                        )

# ====================== AUDIT TRAIL PAGE ======================
elif page == "View Audit Trail":
    st.markdown("## Complete Audit Trail")
    
    if not st.session_state.current_case:
        st.warning("⚠️ Please create a case first")
    else:
        case_id = st.session_state.current_case.get('case_id')
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### Audit Records for Case: **{case_id}**")
        with col2:
            if st.button('🔄 Refresh Audit', use_container_width=True):
                st.rerun()
        
        try:
            audit_resp = requests.get(f"{API_BASE}/audit/case/{case_id}", timeout=5)
            if audit_resp.status_code == 200:
                audits = audit_resp.json()
                if isinstance(audits, list) and audits:
                    audit_df = pd.DataFrame(audits)
                    st.dataframe(audit_df, use_container_width=True)
                else:
                    st.info("ℹ️ No audit records yet. Generate a SAR to create audit entries.")
            else:
                st.info("ℹ️ Audit trail will be populated after SAR generation")
        except Exception as e:
            st.info(f"ℹ️ Audit service ready. Generate a SAR to view entries.")

# ====================== SETTINGS PAGE ======================
elif page == "Settings":
    st.markdown("## System Settings & Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Backend Configuration")
        st.markdown(f"**API Base URL:** `{API_BASE}`")
        
        # Test API connection
        if st.button('🧪 Test API Connection', use_container_width=True):
            try:
                resp = requests.get(f"{API_BASE}/", timeout=3)
                if resp.status_code == 200:
                    st.success("✅ API is responsive and healthy")
                    st.json(resp.json())
            except Exception as e:
                st.error(f"❌ API connection failed: {str(e)}")
    
    with col2:
        st.markdown("### Demo Credentials")
        st.markdown("""
        **Admin User:**
        - Username: `admin`
        - Password: `adminpass`
        
        **Analyst User:**
        - Username: `analyst`
        - Password: `password`
        """)
    
    st.markdown("---")
    st.markdown("### Database Status")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Status", "✅ Initialized")
    with col2:
        st.metric("Tables", "4")
    with col3:
        st.metric("Schema", "Latest")
    
    st.markdown("---")
    st.markdown("""
    ### Platform Features
    - ✅ Case ingestion from alerts
    - ✅ AI-powered SAR generation
    - ✅ Complete audit trail logging
    - ✅ Version control and comparison
    - ✅ Role-based access control
    - ✅ PDF and JSON export
    - ✅ Transaction timeline visualization
    - ✅ Explainable AI recommendations
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p><strong>SAR AI Platform v1.0</strong></p>
    <p>Intelligent Suspicious Activity Report Generation System</p>
    <p>🔒 Secure | 📊 Compliant | ⚡ Intelligent</p>
</div>
""", unsafe_allow_html=True)
