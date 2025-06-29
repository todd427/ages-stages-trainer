
# Ages & Stages Trainer (Streamlit)

## Features
- Answer questions per life stage (fully editable in `ages_and_stages.json`)
- Add new questions via the app
- Download all answers as JSONL (for LLM training/fine-tune)
- Super simple: all local files, no database required

## Quickstart (Local)

1. Install requirements:

   pip install -r requirements.txt

2. Run the app:

   streamlit run ages_and_stages_trainer.py

3. Edit `ages_and_stages.json` directly (or add new questions from the UI).

4. Download your answers as JSONL—use for LLM fine-tune, RAG, or analytics!

## Deploy on Streamlit Cloud

1. Push these files to a public GitHub repo.
2. Visit [streamlit.io/cloud](https://streamlit.io/cloud), create a free account, and connect your repo.
3. The app will auto-deploy! You can edit files in GitHub, and the live app will auto-update.
4. For “persistent” edits (like adding questions), edit `ages_and_stages.json` in GitHub, or download/upload via the app.

---

## How To Add Stages or Questions

- Open `ages_and_stages.json` in a text editor or on GitHub.
- To add a stage:
    ```json
    "Todd-age-25": {
      "questions": [
        "What did you do after school?",
        "Describe your first job."
      ]
    }
    ```
- To add questions in-app: Type a question under the selected stage and click **Add Question**.

---
🦊 Questions or feature requests? Ask Kit!
