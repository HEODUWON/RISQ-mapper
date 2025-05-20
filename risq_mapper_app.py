import streamlit as st
import json
import re
import os


st.set_page_config(page_title="RightShip RISQ 3.1", layout="centered")
st.title("RightShip RISQ 3.1 (Test Edition)")

# 입력 방식 선택
tab1, tab2 = st.tabs(["Let's find RISQ No.", "Search by Key Word"])

with open("risq_data.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

base_path = "SOLUTION DATA"

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

def highlight_korean_lines(text):
    import re
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
            styled_lines.append(line)
    return '<br>'.join(styled_lines)

with tab1:
    risq_no = st.text_input("RISQ 번호 입력 (예: 4.16)")
    if risq_no:
        if risq_no in dummy_data:
            st.success(f"[RISQ {risq_no}] 매핑 결과")

            question_text = dummy_data[risq_no]['question']
            desc_parts = question_text.split('\n')
            english_desc = desc_parts[0].strip()
            korean_desc = desc_parts[1].strip() if len(desc_parts) > 1 else ""

            st.markdown(f"**Question (English)**\n\n{english_desc}")
            st.markdown(f"**Question (Korean)**\n\n{korean_desc}")

            guide_text = dummy_data[risq_no]['guide']
            pretty_guide = highlight_korean_lines(guide_text)

            scrollable_box = f"<div style='height: 400px; overflow-y: auto; padding: 10px; border: 1px solid #ccc; background-color: #f9f9f9'>{pretty_guide}</div>"
            st.markdown(scrollable_box, unsafe_allow_html=True)

            st.markdown(f"**Action (E)**\n\n{dummy_data[risq_no]['action_e']}")
            st.markdown(f"**Action (K)**\n\n{dummy_data[risq_no]['action_k']}")
           
            folder_path = os.path.join(base_path, risq_no)
            st.markdown("**Relevant Documents:**")

            if os.path.exists(folder_path):
                files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.pdf', '.docx', '.xlsx', '.jpg', '.jpeg', '.png'))]
                if files:
                    for file_name in files:
                        file_path = os.path.join(folder_path, file_name)
                        with open(file_path, "rb") as file_obj:
                            file_bytes = file_obj.read()

                            # MIME 타입 매핑
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

                            st.download_button(
                                label=f"Download {file_name}",
                                data=file_bytes,
                                file_name=file_name,
                                mime=mime_type
                            )
                else:
                     st.info("🔍 해당 폴더에 문서가 없습니다.")
            else:
                 st.warning(f"❗ [SOLUTION DATA/{risq_no}] 폴더가 존재하지 않습니다.")

with tab2:
    full_keyword = st.text_input("Search by key word (ex: safety officer, enclosed space etc.,)")
    if full_keyword:
        matches = []
        for risq_no, content in dummy_data.items():
            question_text = content.get("question", "")
            guide_text = content.get("guide", "")
            action_e_text = content.get("action_e", "")
            action_k_text = content.get("action_k", "")

            if full_keyword.lower() in question_text.lower():
                highlighted = re.sub(f"({re.escape(full_keyword)})", r"**:red[\1]**", question_text, flags=re.IGNORECASE)
                matches.append((risq_no, "DESCRIPTION", highlighted))
            elif full_keyword.lower() in guide_text.lower():
                snippet = guide_text[:300] + ("..." if len(guide_text) > 300 else "")
                highlighted = re.sub(f"({re.escape(full_keyword)})", r"**:red[\1]**", snippet, flags=re.IGNORECASE)
                matches.append((risq_no, "GUIDE", highlighted))
            elif full_keyword.lower() in action_e_text.lower():
                highlighted = re.sub(f"({re.escape(full_keyword)})", r"**:red[\1]**", action_e_text, flags=re.IGNORECASE)
                matches.append((risq_no, "Action (E)", highlighted))
            elif full_keyword.lower() in action_k_text.lower():
                highlighted = re.sub(f"({re.escape(full_keyword)})", r"**:red[\1]**", action_k_text, flags=re.IGNORECASE)
                matches.append((risq_no, "Action (K)", highlighted))

        if matches:
            for risq_no, section, highlighted_content in matches:
                st.markdown(f"### RISQ {risq_no}")
                st.markdown(f"**matched item ({section})**\n\n{highlighted_content}")
                if section == "GUIDE" and dummy_data[risq_no]['guide']:
                    with st.expander("View Full Guide"):
                        pretty_full_guide = dummy_data[risq_no]['guide'].replace('. ', '.\n\n')
                        st.text_area("Full Guide", value=pretty_full_guide, height=400)
        else:
            st.info("🔍 해당 키워드와 일치하는 결과가 없습니다")

with st.expander("Send us your feedback"):
    st.markdown("### 📬 Contact & Feedback")

    st.markdown(
        """
        We'd love to hear your thoughts and feedback!  
        If you have any suggestions, bug reports, or ideas to improve this app,  
        please feel free to contact the person in charge below:
        
        ---
        📧 **Email**: [dwheo@summitms.co.kr](mailto:dwheo@summitms.co.kr)  
        🧑‍💼 **P.I.C**: Heoduwon  
        ---
        """
    )
