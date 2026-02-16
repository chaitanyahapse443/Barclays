from datetime import datetime
from .prompt_templates import SAR_SYSTEM_PROMPT
from .rag_store import get_rag_store
from . import llm


def generate_sar_narrative(case, transactions, risk_summary, templates=None):
    """Build a prompt using case, transactions, and retrieved templates and ask the LLM to generate.
    Returns (narrative_text, audit_dict)
    """
    who = case.get("customer_name", "Unknown")
    when = datetime.utcnow().isoformat()
    # retrieve templates from RAG store
    rag = get_rag_store()
    q = f"Customer: {who}. Transactions: {len(transactions)}. Risk: {risk_summary}"
    retrieved = rag.query(q, top_k=3) if rag else []
    templates_text = "\n---\n".join([r['text'] for r in retrieved]) if retrieved else ""

    prompt = SAR_SYSTEM_PROMPT + "\n\n" + f"Case: {case}\nTransactions: {transactions}\nRiskSummary: {risk_summary}\n" + "\nRelevant templates:\n" + templates_text + "\n\nPlease draft a SAR narrative in Who/What/When/Where/Why/How format. Keep neutral tone. Include a brief reasoning trace." 

    resp = llm.generate(prompt)
    narrative = resp.get('text')
    audit = {
        "generated_at": when,
        "model": resp.get('model', 'unknown'),
        "prompt_version": "v1",
        "data_points": {"tx_count": len(transactions), "retrieved_templates": [r.get('source') for r in retrieved]},
    }
    return narrative, audit
