import streamlit as st
import json
import re

st.set_page_config(page_title="RightShip RISQ 3.1", layout="centered")
st.title("🧭 RightShip RISQ 3.1 (Test Edition)")

# 입력 방식 선택
tab1, tab2 = st.tabs(["🔢 Let's find RISQ No.", "🧠 Searh by Key Word"])

with open("risq_data.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)
    dummy_data = {}
    for item in raw_data:
        no = item.get("NO", "").strip()
        question = item.get("Description", "").strip()
        guide = item.get("Guide", "").strip()
        action_e = item.get("action(E)", "").strip()
        action_k = item.get("action(K)", "").strip()
        if no:
            dummy_data[no] = {
                "question": question,
                "guide": guide,
                "action_e": action_e,
                "action_k": action_k
            }

with tab1:
    risq_no = st.text_input("RISQ 번호 입력 (예: 4.16)")
    if risq_no in dummy_data:
        st.success(f"[RISQ {risq_no}] 매핑 결과")
        question_text = dummy_data[risq_no]['question']
        desc_parts = question_text.split('\n')
        english_desc = desc_parts[0].strip()
        korean_desc = desc_parts[1].strip() if len(desc_parts) > 1 else ""

        st.markdown(f"**🗾 Question (English)**\n\n{english_desc}")
        st.markdown(f"**🗾 Question (Korean)**\n\n{korean_desc}")
        st.markdown(f"**📋 Guide summary**\n\n{dummy_data[risq_no]['guide']}")
        st.markdown(f"**📁 Action (E)**\n\n{dummy_data[risq_no]['action_e']}")
        st.markdown(f"**📁 Action (K)**\n\n{dummy_data[risq_no]['action_k']}")
    elif risq_no:
        st.warning("Can not found data for RISQ No.")

with tab2:
    full_keyword = st.text_input("Search by key workd (ex: safety officer, enclosed space etc.,)")
    if full_keyword:
        matches = []
        for risq_no, content in dummy_data.items():
            question_text = content.get("question", "")
            action_e_text = content.get("action_e", "")
            action_k_text = content.get("action_k", "")

            if full_keyword.lower() in question_text.lower():
                highlighted = re.sub(f"({re.escape(full_keyword)})", r"**:red[\1]**", question_text, flags=re.IGNORECASE)
                matches.append((risq_no, "DESCRIPTION", highlighted))
            elif full_keyword.lower() in action_e_text.lower():
                highlighted = re.sub(f"({re.escape(full_keyword)})", r"**:red[\1]**", action_e_text, flags=re.IGNORECASE)
                matches.append((risq_no, "Action (E)", highlighted))
            elif full_keyword.lower() in action_k_text.lower():
                highlighted = re.sub(f"({re.escape(full_keyword)})", r"**:red[\1]**", action_k_text, flags=re.IGNORECASE)
                matches.append((risq_no, "Action (K)", highlighted))

        if matches:
            for risq_no, section, highlighted_content in matches:
                st.markdown(f"### RISQ {risq_no}")
                st.markdown(f"**🔍 matched item ({section})**\n\n{highlighted_content}")
        else:
            st.info("No founded")
with st.expander("📣 Send us your feedback"):
    st.markdown("### 💬 User Feedback")
    st.markdown(
        """
        We'd love to hear your thoughts!  
        If you have any suggestions, bug reports, or ideas to improve this app,  
        please leave your feedback below. Your input will help us improve. 🛠️
        """
    )

    feedback = st.text_area("✍️ Write your feedback here", height=150)

    if st.button("📩 Submit Feedback"):
        if feedback.strip():
            with open("feedback_log.txt", "a", encoding="utf-8") as f:
                f.write(feedback.strip() + "\n---\n")
            st.success("✅ Thank you! Your feedback has been saved.")
        else:
            st.warning("⚠️ Please enter some feedback before submitting.")

    if st.checkbox("📂 View Submitted Feedback"):
        try:
            with open("feedback_log.txt", "r", encoding="utf-8") as f:
                logs = f.read()
            st.text_area("📋 Feedback Log", value=logs, height=300)
        except FileNotFoundError:
            st.info("No feedback has been submitted yet.")
