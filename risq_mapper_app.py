
import streamlit as st
import json
import re

st.set_page_config(page_title="RISQ 자동 매핑기", layout="centered")
st.title("🧭 RISQ 자동 매핑기 (Nori Edition)")

# 입력 방식 선택
tab1, tab2 = st.tabs(["🔢 RISQ 번호 검색", "🧠 전체 내용 기반 검색"])

with open("risq_data.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)
    dummy_data = {}
    for item in raw_data:
        no = item.get("NO", "").strip()
        question = item.get("DESCRIPTION", "").strip()
        guide = item.get("Guide", "").strip()
        docs = [line.strip() for line in item.get("Action", "").split("\n") if line.strip()]
        if no:
            dummy_data[no] = {
                "question": question,
                "guide": guide,
                "docs": docs
            }

with tab1:
    risq_no = st.text_input("RISQ 번호 입력 (예: 4.16)")
    if risq_no in dummy_data:
        st.success(f"[RISQ {risq_no}] 매핑 결과")
        st.markdown(f"**🟦 Question**\n\n{dummy_data[risq_no]['question']}")
        st.markdown(f"**📋 Guide 요약**\n\n{dummy_data[risq_no]['guide']}")
        st.markdown(f"**📁 관련 회사 문서**\n\n- " + '\n- '.join(dummy_data[risq_no]['docs']))
    elif risq_no:
        st.warning("해당 RISQ 번호에 대한 데이터가 없습니다.")

with tab2:
    full_keyword = st.text_input("내용 기반 키워드 검색 (예: safety officer, enclosed space 등)")
    if full_keyword:
        matches = []
        for risq_no, content in dummy_data.items():
            question_text = content.get("question", "")
            docs_text = ' '.join(content.get("docs", []))

            if full_keyword.lower() in question_text.lower():
                highlighted = re.sub(f"({re.escape(full_keyword)})", r"**:red[\1]**", question_text, flags=re.IGNORECASE)
                matches.append((risq_no, "DESCRIPTION", highlighted))
            elif full_keyword.lower() in docs_text.lower():
                highlighted_docs = [re.sub(f"({re.escape(full_keyword)})", r"**:red[\1]**", d, flags=re.IGNORECASE) for d in content.get("docs", [])]
                matches.append((risq_no, "Action", '\n- ' + '\n- '.join(highlighted_docs)))

        if matches:
            for risq_no, section, highlighted_content in matches:
                st.markdown(f"### RISQ {risq_no}")
                st.markdown(f"**🔍 매칭된 항목 ({section})**\n\n{highlighted_content}")
        else:
            st.info("일치하는 항목이 없습니다.")
