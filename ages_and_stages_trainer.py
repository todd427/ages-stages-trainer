
import streamlit as st
import json
import os
from datetime import datetime

# --- Settings ---
QUESTIONS_PER_PAGE = 5
MIN_QUESTIONS_TO_COMMIT = 30
MAX_QUESTIONS = 50

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

st.title("Ages & Stages Trainer — Per Stage Commit")

json_file = "ages_and_stages.json"
st.sidebar.header("Config")
json_file = st.sidebar.text_input("Ages/Stages JSON", value=json_file)

if not os.path.exists(json_file):
    st.error(f"JSON file not found: {json_file}")
    st.stop()

stages = load_stages(json_file)
stage_names = list(stages.keys())

# If not present, add status for each stage
for s in stage_names:
    if "status" not in stages[s]:
        stages[s]["status"] = "building"
save_json(stages, json_file)

selected_stage = st.sidebar.selectbox("Select a stage", stage_names)

if "answers" not in st.session_state:
    st.session_state.answers = {}
if "pagination" not in st.session_state:
    st.session_state.pagination = {stage: 0 for stage in stage_names}

questions = stages[selected_stage]["questions"]
num_questions = len(questions)
status = stages[selected_stage].get("status", "building")

st.subheader(f"Stage: {selected_stage}")
st.markdown(f"**Status:** {'🟢 Building' if status == 'building' else '🔒 Committed (ready to answer)'}")

if status == "building":
    st.info(f"You have {num_questions}/{MAX_QUESTIONS} questions (min {MIN_QUESTIONS_TO_COMMIT} to commit, max {MAX_QUESTIONS}).")
    for idx, q in enumerate(questions):
        st.write(f"{idx+1}. {q}")

    # Add question UI (only if not at max)
    if num_questions < MAX_QUESTIONS:
        new_q = st.text_input("Add a new question")
        if st.button("Add Question"):
            if new_q.strip():
                stages[selected_stage]["questions"].append(new_q.strip())
                save_json(stages, json_file)
                st.success("Added! Please refresh to see the update.")
                st.experimental_rerun()
    else:
        st.warning(f"Reached max {MAX_QUESTIONS} questions for this stage.")

    # Commit UI
    if num_questions >= MIN_QUESTIONS_TO_COMMIT:
        if st.button("Commit This Stage"):
            stages[selected_stage]["status"] = "committed"
            save_json(stages, json_file)
            st.success("Stage committed! Please refresh to answer questions.")
            st.experimental_rerun()
    else:
        st.warning(f"Need at least {MIN_QUESTIONS_TO_COMMIT} questions to commit.")

elif status == "committed":
    # Q/A interface
    # Progress bar and pagination
    def answered_count(stage, questions):
        cnt = 0
        for idx, q in enumerate(questions):
            key = f"{stage}_{idx}"
            ans = st.session_state.answers.get(key, "")
            if ans.strip():
                cnt += 1
        return cnt

    num_pages = (num_questions - 1) // QUESTIONS_PER_PAGE + 1
    cur_page = st.session_state.pagination.get(selected_stage, 0)
    ans_cnt = answered_count(selected_stage, questions)
    st.progress(ans_cnt / num_questions if num_questions else 1)
    st.info(f"Answered {ans_cnt} of {num_questions} questions for **{selected_stage}**")

    start_idx = cur_page * QUESTIONS_PER_PAGE
    end_idx = min(start_idx + QUESTIONS_PER_PAGE, num_questions)
    st.write(f"### Questions {start_idx + 1}–{end_idx}")

    for idx in range(start_idx, end_idx):
        q = questions[idx]
        key = f"{selected_stage}_{idx}"
        prev = st.session_state.answers.get(key, "")
        ans = st.text_area(f"Q{idx+1}: {q}", value=prev, key=key)
        st.session_state.answers[key] = ans

    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("⏮ Prev Page", disabled=cur_page==0, key="prev_btn"):
            st.session_state.pagination[selected_stage] = max(cur_page-1, 0)
    with col3:
        if st.button("Next Page ⏭", disabled=(cur_page>=num_pages-1), key="next_btn"):
            st.session_state.pagination[selected_stage] = min(cur_page+1, num_pages-1)

    if st.button("Download Answers as JSONL"):
        data = []
        for s in stage_names:
            if stages[s].get("status") != "committed":
                continue
            qs = stages[s]["questions"]
            for idx, q in enumerate(qs):
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
