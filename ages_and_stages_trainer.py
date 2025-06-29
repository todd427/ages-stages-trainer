
import streamlit as st
import json
import os
from datetime import datetime

def load_stages(json_file):
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

def save_json(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)

def to_jsonl(data, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

st.title("Ages & Stages Trainer")
st.markdown("Answer questions for each life stage, or add your own questions. Download your answers for fine-tuning.")

json_file = "ages_and_stages.json"
st.sidebar.header("Config")
json_file = st.sidebar.text_input("Ages/Stages JSON", value=json_file)

if not os.path.exists(json_file):
    st.error(f"JSON file not found: {json_file}")
    st.stop()

stages = load_stages(json_file)

if "answers" not in st.session_state:
    st.session_state.answers = {}

stage_names = list(stages.keys())

selected_stage = st.sidebar.selectbox("Select a stage", stage_names)

st.header(f"Stage: {selected_stage}")
questions = stages[selected_stage]["questions"]

for idx, q in enumerate(questions):
    key = f"{selected_stage}_{idx}"
    prev = st.session_state.answers.get(key, "")
    ans = st.text_area(f"Q{idx+1}: {q}", value=prev, key=key)
    st.session_state.answers[key] = ans

st.subheader("Add a new question")
new_q = st.text_input("Type a new question")
if st.button("Add Question"):
    if new_q.strip():
        stages[selected_stage]["questions"].append(new_q.strip())
        save_json(stages, json_file)
        st.success("Added! Please reload the app to see it.")

if st.button("Download Answers as JSONL"):
    data = []
    for s in stage_names:
        for idx, q in enumerate(stages[s]["questions"]):
            key = f"{s}_{idx}"
            ans = st.session_state.answers.get(key, "")
            if ans.strip():
                data.append({"stage": s, "question": q, "answer": ans})
    if data:
        jsonl_path = f"answers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        to_jsonl(data, jsonl_path)
        with open(jsonl_path, "rb") as f:
            st.download_button("Download Now", f, file_name=jsonl_path)
    else:
        st.warning("No answers filled in yet!")
