import streamlit as st
import json
import os
import requests
from pathlib import Path

API_BASE = st.secrets.get('api_base', 'http://localhost:8000')

st.title('SAR Narrative Generator — Demo')

# list sample cases
sample_dir = Path(__file__).resolve().parents[1] / 'sample_data'
samples = [p.name for p in sample_dir.glob('*.json')]
sel = st.selectbox('Select sample case', ['-- choose --'] + samples)

if sel and sel != '-- choose --':
    case_file = sample_dir / sel
    case = json.loads(case_file.read_text())
    st.subheader('Case payload')
    st.json(case)

    if st.button('Create case in backend'):
        resp = requests.post(f"{API_BASE}/cases/create", json=case)
        if resp.status_code == 200:
            st.write('Create response:', resp.json())
        else:
            st.error(f"Error creating case: {resp.status_code} - {resp.text}")

    if st.button('Generate SAR draft'):
        case_id = case.get('case_id')
        resp = requests.post(f"{API_BASE}/sars/generate", params={'case_id': case_id})
        if resp.status_code == 200:
            data = resp.json()
            st.subheader('SAR Draft')
            st.text_area('Draft', value=data.get('sar_draft', ''), height=300)
            st.subheader('Audit')
            st.json(data.get('audit'))
            st.subheader('Explainability')
            st.json(data.get('explain'))
        else:
            st.error(f"Error generating SAR: {resp.status_code} - {resp.text}")

        # Download PDF button
        if st.button('Download SAR as PDF'):
            sar_id = data.get('sar_id')
            pdf_resp = requests.get(f"{API_BASE}/sars/export/{sar_id}")
            if pdf_resp.status_code == 200:
                st.download_button('Download PDF', data=pdf_resp.content, file_name=f"{sar_id}.pdf", mime='application/pdf')
            else:
                st.error('Failed to fetch PDF')

        # Versions and compare
        if st.button('List SAR Versions'):
            case_id = case.get('case_id')
            vresp = requests.get(f"{API_BASE}/sars/versions/{case_id}")
            if vresp.status_code == 200:
                st.json(vresp.json())
            else:
                st.error('Failed to list versions')

        if st.button('Compare Versions'):
            case_id = case.get('case_id')
            vresp = requests.get(f"{API_BASE}/sars/versions/compare/{case_id}")
            if vresp.status_code == 200:
                diffs = vresp.json().get('diffs', [])
                for d in diffs:
                    st.subheader(d.get('version_id'))
                    st.code(d.get('diff') or 'No diff')
            else:
                st.error('Failed to compare versions')

        # RAG actions
        st.markdown('---')
        st.subheader('RAG Management')
        if st.button('Reindex RAG'):
            r = requests.post(f"{API_BASE}/rag/reindex")
            if r.status_code == 200:
                st.success(f"Reindexed: {r.json()}")
            else:
                st.error(f"Reindex failed: {r.status_code}")

        if st.button('Save RAG Index'):
            r = requests.post(f"{API_BASE}/rag/save", json='vector_store/faiss_index')
            if r.status_code == 200:
                st.success(f"Saved index: {r.json()}")
            else:
                st.error('Save failed')

        if st.button('Load RAG Index'):
            r = requests.post(f"{API_BASE}/rag/load", json='vector_store/faiss_index')
            if r.status_code == 200:
                st.success(f"Loaded index: {r.json()}")
            else:
                st.error('Load failed')
