import streamlit as st
from google import genai
import json
import time
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AIP-C01 Tutor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;600;700&family=Source+Sans+3:wght@400;500;600&display=swap');

  html, body, [class*="css"] { font-family: 'Source Sans 3', sans-serif; }
  h1, h2, h3 { font-family: 'Lora', serif; }

  .main { background-color: #faf7f2; }
  .block-container { padding-top: 2rem; max-width: 860px; }

  .badge {
    display: inline-block; padding: 3px 12px; border-radius: 20px;
    font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;
  }
  .badge-hard   { background: #ffccbc; color: #bf360c; }
  .badge-medium { background: #fff9c4; color: #f57f17; }
  .badge-easy   { background: #c8e6c9; color: #1b5e20; }

  .question-card {
    background: #ffffff; border: 1px solid #ddd4c0; border-radius: 12px;
    padding: 24px; margin-bottom: 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  }
  .domain-label {
    font-size: 11px; letter-spacing: 2px; text-transform: uppercase;
    color: #8a7050; margin-bottom: 8px;
  }
  .question-text { font-size: 16px; line-height: 1.7; color: #1a1208; }

  .feedback-correct {
    background: #f1f8e9; border-left: 4px solid #4caf50;
    border-radius: 0 8px 8px 0; padding: 16px; margin-top: 16px;
  }
  .feedback-wrong {
    background: #fff3e0; border-left: 4px solid #ff9800;
    border-radius: 0 8px 8px 0; padding: 16px; margin-top: 16px;
  }
  .tip-box {
    background: rgba(0,0,0,0.03); border-left: 3px solid #a89060;
    border-radius: 0 6px 6px 0; padding: 10px 14px; margin-top: 12px;
    font-size: 14px; color: #2c2416;
  }

  .stat-card {
    background: white; border: 1px solid #ddd4c0; border-radius: 10px;
    padding: 16px; text-align: center;
  }
  .stat-value { font-size: 32px; font-weight: 700; font-family: 'Lora', serif; }
  .stat-label { font-size: 12px; color: #8a7050; margin-top: 4px; }

  .history-item {
    background: white; border-radius: 8px; padding: 12px 16px;
    margin-bottom: 8px; border: 1px solid #e8dfd0;
    font-size: 13px;
  }

  div[data-testid="stButton"] button {
    background: #2c2416; color: #e8d5b7;
    border: none; border-radius: 8px;
    font-family: 'Lora', serif; font-size: 15px;
    padding: 10px 24px; width: 100%;
    transition: background 0.2s;
  }
  div[data-testid="stButton"] button:hover { background: #3d3020; }

  .stRadio label { font-size: 14px !important; line-height: 1.6 !important; }
  [data-testid="stSidebar"] { background: #1a1208; }
  [data-testid="stSidebar"] * { color: #e8d5b7 !important; }
  [data-testid="stSidebar"] .stSelectbox label { color: #a89060 !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
DOMAINS = {
    "🎲 All Domains": "any domain — GenAI Fundamentals, Bedrock, RAG, Agentic AI, SageMaker, Data Management, Operational Efficiency, Governance, Security",
    "I. GenAI Fundamentals & Bedrock": "GenAI Fundamentals and Amazon Bedrock: Foundation Models (Nova, Claude, Llama, Titan, Jurassic-2, Stable Diffusion), RAG architecture, Knowledge Bases, Fine-tuning (labeled prompt/completion pairs, S3 image paths), Guardrails (word/topic/PII filtering, contextual grounding checks), Prompt Engineering (few-shot, chain-of-thought), Bedrock Flows, chunking strategies (hierarchical vs semantic), vector stores (OpenSearch, Pinecone, Redis, Aurora, MemoryDB, MongoDB Atlas)",
    "II. Managing Data for GenAI": "Managing Data for GenAI: Amazon Textract, Amazon Comprehend (NER, custom classification, PII redaction), Amazon Transcribe (ASR, custom vocabularies, toxicity detection), Bedrock Data Automation (BDA, Blueprints, multimodal IDP), OpenSearch vector optimization (binary vectors, FP16, hierarchical indices, neural plugin), data structuring with divider strings, Lambda preprocessors, Glue ETL",
    "III. Agentic AI": "Agentic AI: Bedrock Agents (Action Groups, OpenAPI/Swagger schemas on S3, Planning Module), multi-agent workflows (Orchestrator, worker LLMs, Synthesizer), Chain of Sequence vs Parallelization, MCP protocol (JSON-RPC 2.0), agent memory (short-term sessions vs long-term AgentCore Memory), Amazon Q Business (data connectors, IAM Identity Center, plugins), Amazon Q Developer (IDE extensions, ./amazon/rules), Humans in the Loop (HITL, escalation criteria, confidence routing)",
    "IV. Operational Efficiency": "Operational Efficiency: CountTokens API, CloudWatch InputTokenCount/outputTokenCount, Context Pruning (RAG chunk limits, metadata filtering, chat history summarisation), Response Size Controls (maxTokens), Provisioned Throughput (model ARN-specific), Dynamic Routing / Intelligent Prompt Routing, Bedrock Evaluations for cost/performance tradeoffs, Prompt Caching (static prefix caching, Time to First Token TTFT), Temperature/Top_p/Top_k tuning, Circuit Breaker pattern (Step Functions + DynamoDB), Exponential Backoff",
    "V. SageMaker AI": "SageMaker AI: Persistent Endpoints vs Batch Transform, SageMaker Model Monitor (CloudWatch alerts, data drift detection, missing features), SageMaker Clarify (bias detection, Class Imbalance CI, Difference in Proportions of Labels DPL, feature explainability), data labeling (Rekognition, Comprehend), GPU instance types (ml.p4d.24xlarge for large models, ml.c5.9xlarge for NER), container health check and download timeout quotas",
    "VI–VII. Governance & QA": "Governance, QA, and Responsible AI: Responsible AI dimensions (Fairness, Explainability, Privacy, Safety, Controllability, Veracity, Robustness, Governance, Transparency), Bedrock Evaluation Jobs (RAG metrics: Correctness, Completeness, Helpfulness, Faithfulness, Logical Coherence), ROUGE metrics for summarisation, Human Evaluation for non-deterministic GenAI, Amazon A2I for human review loops, Bedrock Agent Tracing (PreProcessing, Orchestration, PostProcessing, Guardrail trace types), CloudWatch Logs (log groups, log streams, KMS encryption, export to S3/Kinesis/Lambda/OpenSearch)",
    "VIII. Security & Compliance": "Security, Identity, and Compliance: IAM roles and permissions, AWS KMS encryption key management, Amazon Macie (data security, DLP, sensitive data discovery), AWS Secrets Manager (credentials rotation), Amazon Cognito (web/mobile app auth), AWS WAF (web exploit protection), Amazon VPC and AWS PrivateLink (private connectivity for sensitive fine-tuning data, no public internet exposure), CloudTrail API logging",
}

SYSTEM_PROMPT = """You are an expert AWS certification tutor for the AIP-C01 AWS Certified Generative AI Developer – Professional exam.

Key exam facts:
- 65–75 scored questions, ~130 minutes, passing score 750/1000
- All questions are scenario-based; pick the BEST from 4 plausible options
- Heavily tests: Amazon Bedrock full feature set, RAG architecture, chunking, vector stores, SageMaker, agentic AI, governance, security
- Questions are dense with layered requirements (cost + latency + security + scalability simultaneously)
- Anti-patterns matter — often 2+ answers look correct; tiny AWS-specific details decide the winner
- Real exam takers say it is one of AWS's hardest exams

Generate ONE realistic exam-style question for the specified domain.

RESPOND ONLY WITH THIS EXACT JSON (no markdown fences, no preamble):
{
  "question": "Scenario-based question (3-5 sentences with real constraints like data residency, cost, latency, security)",
  "options": {
    "A": "Option A text",
    "B": "Option B text",
    "C": "Option C text",
    "D": "Option D text"
  },
  "correct": "A",
  "explanation": "2-3 sentences: why the correct answer wins, and why the distractors fail. Reference specific AWS services and AIP-C01 concepts.",
  "domain": "Short domain label",
  "difficulty": "Medium or Hard"
}

Make questions genuinely hard with plausible wrong answers. Use real AWS service names."""

FEEDBACK_PROMPT = """You are an AIP-C01 exam tutor reviewing a student's answer.

Question: {question}
Student answered: {student_answer}
Correct answer: {correct}
Explanation: {explanation}

Respond ONLY with this JSON (no markdown):
{{
  "verdict": "correct" or "incorrect",
  "message": "2-3 sentences of personalised feedback. If wrong, explain the key concept missed. If right, reinforce WHY it was correct and add one extra insight about the real exam.",
  "tip": "One concrete study tip related to this topic (e.g. 'In Bedrock, ask yourself: is this a retrieval problem (RAG/Knowledge Bases) or a behaviour problem (fine-tuning)?')"
}}"""

# ── Session state init ────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "question": None,
        "selected_answer": None,
        "feedback": None,
        "score": {"correct": 0, "total": 0},
        "history": [],
        "streak": 0,
        "generating": False,
        "tab": "quiz",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── API helpers ───────────────────────────────────────────────────────────────
def get_client():
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    if not api_key:
        st.error("⚠️  Add your Google API key to `.streamlit/secrets.toml` as `GOOGLE_API_KEY = 'your-key-here'`")
        st.stop()
    return genai.Client(api_key=api_key)

def generate_question(domain_context: str) -> dict:
    client = get_client()
    prompt = f"{SYSTEM_PROMPT}\n\nGenerate one AIP-C01 exam question for: {domain_context}. Return only JSON."
    response = client.models.generate_content(
        model='gemini-1.5-pro',
        contents=prompt
    )
    text = response.text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    return json.loads(text)

def generate_feedback(question_text, student_ans, correct_ans, explanation) -> dict:
    client = get_client()
    prompt = FEEDBACK_PROMPT.format(
        question=question_text,
        student_answer=student_ans,
        correct=correct_ans,
        explanation=explanation,
    )
    response = client.models.generate_content(
        model='gemini-1.5-pro',
        contents=prompt
    )
    text = response.text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    return json.loads(text)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 AIP-C01 Tutor")
    st.markdown("*AWS Certified Generative AI Developer – Professional*")
    st.divider()

    domain_choice = st.selectbox("📚 Select Domain", list(DOMAINS.keys()), key="domain_select")

    st.divider()
    score = st.session_state.score
    total = score["total"]
    correct = score["correct"]
    pct = round(correct / total * 100) if total > 0 else 0
    st.markdown(f"**Score:** {correct} / {total}")
    if total > 0:
        color = "green" if pct >= 75 else "orange" if pct >= 60 else "red"
        st.markdown(f"**Accuracy:** :{color}[{pct}%]")
        st.progress(pct / 100)
    if st.session_state.streak >= 3:
        st.markdown(f"🔥 **Streak:** {st.session_state.streak}")

    st.divider()
    st.markdown("""
**Exam Quick Facts**
- ⏱ 130 min · 65–75 questions
- 🎯 Pass: 750 / 1000
- 📊 Target 85%+ in practice
- ⚠️ One of AWS's hardest exams
    """)

    st.divider()
    if st.button("🔄 Reset Session"):
        for k in ["question", "selected_answer", "feedback", "score", "history", "streak"]:
            st.session_state[k] = {"correct": 0, "total": 0} if k == "score" else ([] if k == "history" else 0 if k == "streak" else None)
        st.rerun()

# ── Main content ──────────────────────────────────────────────────────────────
st.markdown("# AWS AIP-C01 Practice Tutor")
st.markdown("*Scenario-based questions · AI-powered feedback · Real exam difficulty*")

tab_quiz, tab_stats, tab_history = st.tabs(["🎯 Practice", "📊 Stats", "📋 History"])

# ─── QUIZ TAB ─────────────────────────────────────────────────────────────────
with tab_quiz:
    col1, col2 = st.columns([3, 1])
    with col1:
        generate_btn = st.button(
            "▶ Generate Question" if st.session_state.question is None else "→ Next Question",
            use_container_width=True,
        )
    with col2:
        if st.session_state.question:
            diff = st.session_state.question.get("difficulty", "Medium")
            color = "red" if diff == "Hard" else "orange"
            st.markdown(f":{color}[**{diff}**]", unsafe_allow_html=False)

    if generate_btn:
        with st.spinner("Generating exam-style question..."):
            try:
                q = generate_question(DOMAINS[domain_choice])
                st.session_state.question = q
                st.session_state.selected_answer = None
                st.session_state.feedback = None
            except Exception as e:
                st.error(f"Error generating question: {e}")
        st.rerun()

    q = st.session_state.question
    if q:
        st.markdown(f'<div class="domain-label">{q.get("domain", domain_choice)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="question-card"><div class="question-text">{q["question"]}</div></div>', unsafe_allow_html=True)

        answer_labels = {
            "A": f"**A.** {q['options']['A']}",
            "B": f"**B.** {q['options']['B']}",
            "C": f"**C.** {q['options']['C']}",
            "D": f"**D.** {q['options']['D']}",
        }

        if not st.session_state.selected_answer:
            choice = st.radio(
                "Select your answer:",
                options=list(answer_labels.keys()),
                format_func=lambda x: answer_labels[x],
                key="answer_radio",
                index=None,
            )
            if st.button("✅ Submit Answer", use_container_width=True):
                if choice is None:
                    st.warning("Please select an answer first.")
                else:
                    st.session_state.selected_answer = choice
                    is_correct = choice == q["correct"]
                    st.session_state.score["total"] += 1
                    st.session_state.score["correct"] += (1 if is_correct else 0)
                    st.session_state.streak = st.session_state.streak + 1 if is_correct else 0
                    st.session_state.history.append({
                        "question": q["question"][:120] + "...",
                        "domain": q.get("domain", ""),
                        "your": choice,
                        "correct": q["correct"],
                        "is_correct": is_correct,
                        "timestamp": datetime.now().strftime("%H:%M"),
                    })
                    with st.spinner("Analysing your answer..."):
                        try:
                            fb = generate_feedback(
                                q["question"],
                                f"{choice}: {q['options'][choice]}",
                                f"{q['correct']}: {q['options'][q['correct']]}",
                                q["explanation"]
                            )
                            st.session_state.feedback = fb
                        except Exception:
                            st.session_state.feedback = {
                                "verdict": "correct" if is_correct else "incorrect",
                                "message": q["explanation"],
                                "tip": "Review the relevant AWS Bedrock documentation for this topic."
                            }
                    st.rerun()
        else:
            # Show answered options with colour coding
            chosen = st.session_state.selected_answer
            correct = q["correct"]
            for letter, text in q["options"].items():
                if letter == correct:
                    st.success(f"**{letter}.** {text} ✓")
                elif letter == chosen and chosen != correct:
                    st.error(f"**{letter}.** {text} ✗ (your answer)")
                else:
                    st.markdown(f"**{letter}.** {text}")

            fb = st.session_state.feedback
            if fb:
                css_class = "feedback-correct" if fb["verdict"] == "correct" else "feedback-wrong"
                icon = "✅" if fb["verdict"] == "correct" else "❌"
                st.markdown(f"""
                <div class="{css_class}">
                  <strong>{icon} {fb["verdict"].capitalize()}</strong><br><br>
                  {fb["message"]}
                  <div class="tip-box">
                    <strong>💡 Study tip:</strong> {fb["tip"]}
                  </div>
                </div>
                """, unsafe_allow_html=True)

# ─── STATS TAB ────────────────────────────────────────────────────────────────
with tab_stats:
    score = st.session_state.score
    total = score["total"]
    correct_count = score["correct"]
    pct = round(correct_count / total * 100) if total > 0 else 0

    if total == 0:
        st.info("No questions answered yet. Head to the Practice tab to get started!")
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{total}</div><div class="stat-label">Questions Answered</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:#2e7d32">{correct_count}</div><div class="stat-label">Correct Answers</div></div>', unsafe_allow_html=True)
        with c3:
            col = "#2e7d32" if pct >= 75 else "#e65100" if pct < 60 else "#f57f17"
            st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:{col}">{pct}%</div><div class="stat-label">Accuracy</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="stat-card"><div class="stat-value">🔥{st.session_state.streak}</div><div class="stat-label">Current Streak</div></div>', unsafe_allow_html=True)

        st.markdown("### Exam Readiness")
        st.progress(pct / 100)
        if pct >= 85:
            st.success("🎯 **Exam ready!** You're consistently hitting the 85% target. Consider booking your exam.")
        elif pct >= 75:
            st.warning("📈 **Almost there!** Aim for 85%+ before booking. Focus on your weak domains.")
        elif pct >= 60:
            st.warning("📚 **Keep going!** You're building a foundation. Target weak domains specifically.")
        else:
            st.error("🔄 **Early stages** — consistent daily practice is key. Don't rush to book.")

        st.markdown("### 💡 Real Exam Insights")
        st.info("""
**From actual AIP-C01 takers:**
- Questions have 2–3 plausible answers — you need to find the *subtle detail* that makes one option best
- Almost every question has multi-dimensional constraints: cost + latency + security + scalability together
- Exam takers used nearly all of the 130-minute time limit
- The biggest gap candidates have: not enough hands-on time with Bedrock Agents and Knowledge Bases
- **Tip:** For every question, ask *"what specific AWS constraint eliminates the other 3 options?"*
        """)

# ─── HISTORY TAB ─────────────────────────────────────────────────────────────
with tab_history:
    history = st.session_state.history
    if not history:
        st.info("No history yet. Answer some questions to track your progress!")
    else:
        st.markdown(f"**{len(history)} questions answered**")
        for item in reversed(history):
            icon = "✅" if item["is_correct"] else "❌"
            border_color = "#4caf50" if item["is_correct"] else "#f44336"
            wrong_note = "" if item["is_correct"] else f" · <span style='color:#c62828'>You: {item['your']} · Correct: {item['correct']}</span>"
            st.markdown(f"""
            <div class="history-item" style="border-left: 3px solid {border_color}">
              {icon} <strong>{item['domain']}</strong> <span style="color:#8a7050;font-size:11px">{item['timestamp']}</span>{wrong_note}<br>
              <span style="color:#5d4037">{item['question']}</span>
            </div>
            """, unsafe_allow_html=True)
