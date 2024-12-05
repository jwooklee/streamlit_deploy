import streamlit as st
import speech_recognition as sr
import os
from datetime import datetime

def speech_to_text(audio_file):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio, language='ko-KR')
        return text
    except sr.UnknownValueError:
        return "음성을 인식할 수 없습니다."
    except sr.RequestError:
        return "음성 인식 서비스에 접근할 수 없습니다."

def main():
    st.title("🎙️ 음성 파일 텍스트 변환")
    st.write("WAV 파일을 업로드하여 텍스트로 변환하세요.")
    
    uploaded_file = st.file_uploader("음성 파일 선택", type=['wav'])
    
    if uploaded_file is not None:
        # 임시 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_file = f"temp_audio_{timestamp}.wav"
        
        with open(temp_file, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 음성을 텍스트로 변환
        text = speech_to_text(temp_file)
        
        # 결과 표시
        st.write("## 변환된 텍스트:")
        st.write(text)
        
        # 임시 파일 삭제
        os.remove(temp_file)

if __name__ == "__main__":
    main()