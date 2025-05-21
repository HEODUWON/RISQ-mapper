import streamlit as st

import json

import re

import os



st.set_page_config(page_title="SUMMIT RISQ MAPPER", layout="centered")



# Load RISQ JSON data

with open("risq_data.json", "r", encoding="utf-8") as f:

    raw_data = json.load(f)

    dummy_data = {

        item.get("NO", "").strip(): {

            "question": item.get("Description", "").strip(),

            "guide": item.get("Guide", "").strip(),

            "action_e": item.get("action(E)", "").strip(),

            "action_k": item.get("action(K)", "").strip()

        }

        for item in raw_data if item.get("NO", "").strip()

    }





# Sidebar

st.sidebar.markdown("### SUMMIT RISQ MAPPER")

if st.sidebar.button("🏠 Home"):
    st.session_state["risq_input"] = ""
    st.session_state["keyword_input"] = ""
    st.rerun()
    for key in list(st.session_state.keys()):
        if key in ["keyword_input", "risq_input"]:
            del st.session_state[key]


tab_option = st.sidebar.radio("🔍 Search By", ["RISQ No.", "Keyword"])



# Keyword section filter (tab2 only)

selected_section = "All"

keyword_entered = st.session_state.get("keyword_input", "")

keyword_section_counts = {}

if tab_option == "Keyword" and keyword_entered:

    section_labels = ["Question", "Guide", "Action (E)", "Action (K)"]

    keyword_section_counts = {label: 0 for label in section_labels}

    for content in dummy_data.values():

        for label, text in zip(section_labels, [content["question"], content["guide"], content["action_e"], content["action_k"]]):

            if keyword_entered.lower() in text.lower():

                keyword_section_counts[label] += 1

    total_matches = sum(keyword_section_counts.values())

    all_label = f"All ({total_matches})"

    dropdown_options = [all_label] + [f"{sec} ({cnt})" for sec, cnt in keyword_section_counts.items()]

    selected_section = st.sidebar.selectbox("📂 Filter by section", options=dropdown_options)



# Contact

st.sidebar.markdown("---")

st.sidebar.markdown("📮 **Feedback:** [dwheo@summitms.co.kr](mailto:dwheo@summitms.co.kr)")

st.sidebar.markdown("© 2025 SUMMIT Marine Service. All rights reserved.")



# Helper functions

def highlight_korean_lines(text):

    pattern = r'(?<!\d)\.(?!\d)\s*'

    text = re.sub(pattern, '.\n\n', text)

    lines = text.split('\n')

    styled_lines = []

    for line in lines:

        line = line.strip()

        if not line:

            continue

        if re.search(r'[가-힣]', line):

            styled_lines.append(f"<span style='color:#1E90FF'>{line}</span>")

        else:

            styled_lines.append(f"<span style='color:#4A4A4A'>{line}</span>")

    return '<br>'.join(styled_lines)



def extract_snippet(text, keyword):

    lower = text.lower()

    idx = lower.find(keyword.lower())

    if idx == -1:

        return ""

    prev_dot = lower.rfind('.', 0, idx)

    next_dot = lower.find('.', idx)

    start = prev_dot + 1 if prev_dot != -1 else 0

    end = next_dot + 1 if next_dot != -1 else len(text)

    snippet = text[start:end].strip()

    if start > 0:

        snippet = "..." + snippet

    if end < len(text):

        snippet = snippet + "..."

    return snippet



def render_scrollbox(text, base_height=300, max_height=500):

    line_count = text.count('\n') + 1

    height = min(base_height + line_count * 10, max_height)

    return f"<div style='margin-top: 10px; margin-bottom: 25px; height: {height}px; overflow-y: auto; padding: 10px; border: 1px solid #ccc; background-color: #f9f9f9'>{text}</div>"



def red_title(text):

    return f"<h4 style='color:red; font-weight:bold; margin-top: 25px'>{text}</h4>"



# TAB 1 - Search by RISQ No

if tab_option == "RISQ No.":

    risq_no = st.text_input("Enter RISQ No. (e.g. 4.16)", key="risq_input")

    if risq_no:

        if risq_no in dummy_data:

            st.success(f"**[RISQ {risq_no}] Mapping Result**")



            for label, key in [("Question", "question"), ("Guide", "guide"), ("Action (E)", "action_e"), ("Action (K)", "action_k")]:

                text = dummy_data[risq_no][key]

                styled = highlight_korean_lines(text)

                st.markdown(red_title(label), unsafe_allow_html=True)

                st.markdown(render_scrollbox(styled), unsafe_allow_html=True)



            # File Download

            base_path = "SOLUTION DATA"

            folder_path = os.path.join(base_path, risq_no)

            st.markdown("**📎 Related Documents:**")

            if os.path.exists(folder_path):

                files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.pdf', '.docx', '.xlsx', '.jpg', '.jpeg', '.png'))]

                for file_name in files:

                    file_path = os.path.join(folder_path, file_name)

                    with open(file_path, "rb") as file_obj:

                        file_bytes = file_obj.read()

                        ext = file_name.lower().split('.')[-1]

                        mime_types = {

                            'pdf': 'application/pdf',

                            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',

                            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',

                            'jpg': 'image/jpeg',

                            'jpeg': 'image/jpeg',

                            'png': 'image/png'

                        }

                        mime_type = mime_types.get(ext, 'application/octet-stream')

                        st.download_button(f"📥 {file_name}", file_bytes, file_name, mime=mime_type)

        else:

            st.warning("Invalid RISQ number.")



# TAB 2 - Search by keyword

if tab_option == "Keyword":

    keyword = st.text_input("Enter keyword (ex: safety officer, enclosed space etc.)", key="keyword_input")

    if keyword:

        results = []

        for risq_no, content in dummy_data.items():

            for label, field in [

                ("Question", content["question"]),

                ("Guide", content["guide"]),

                ("Action (E)", content["action_e"]),

                ("Action (K)", content["action_k"])

            ]:

                if keyword.lower() in field.lower():

                    snippet = extract_snippet(field, keyword)

                    highlighted = re.sub(f"({re.escape(keyword)})", r"<mark style='background-color:#fff3b0'>\1</mark>", snippet, flags=re.IGNORECASE)

                    fulltext = highlight_korean_lines(re.sub(f"({re.escape(keyword)})", r"<mark style='background-color:#fff3b0'>\1</mark>", field, flags=re.IGNORECASE))

                    results.append((risq_no, label, highlighted, fulltext))



        if results:

            for risq_no, section, snippet, full in results:

                base_section = section.split()[0]

                if selected_section != "All" and not selected_section.startswith(base_section):

                    continue

                st.markdown(red_title(f"RISQ {risq_no} - {section}"), unsafe_allow_html=True)

                if snippet:
                    st.markdown(snippet, unsafe_allow_html=True)
                with st.expander(f"View Full {section}"):
                    st.markdown(render_scrollbox(full), unsafe_allow_html=True)
        else:

            st.info("No results found.")
