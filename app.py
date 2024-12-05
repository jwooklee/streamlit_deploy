import streamlit as st
import speech_recognition as sr
import os
from datetime import datetime
import io

def speech_to_text(audio_bytes):
    r = sr.Recognizer()
    
    # WAV 파일로 임시 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_file = f"temp_audio_{timestamp}.wav"
    
    try:
        with open(temp_file, 'wb') as f:
            f.write(audio_bytes)
        
        with sr.AudioFile(temp_file) as source:
            audio = r.record(source)
            
        try:
            text = r.recognize_google(audio, language='ko-KR')
            return text
        except sr.UnknownValueError:
            return "음성을 인식할 수 없습니다."
        except sr.RequestError:
            return "음성 인식 서비스에 접근할 수 없습니다."
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def main():
    st.title("🎙️ 실시간 음성 녹음 및 텍스트 변환")
    st.write("버음 버튼을 클릭하여 음성을 녹음하고 텍스트로 변환하세요.")
    
    # Streamlit의 기본 오디오 레코더 사용
    audio_bytes = st.audio_recorder()
    
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        text = speech_to_text(audio_bytes)
        st.write("## 변환된 텍스트:")
        st.write(text)
    
    st.divider()
    
    # 파일 업로더
    st.write("또는 WAV 파일을 업로드하세요:")
    uploaded_file = st.file_uploader("WAV 파일 선택", type=['wav'])
    if uploaded_file is not None:
        audio_bytes = uploaded_file.read()
        text = speech_to_text(audio_bytes)
        st.write("## 변환된 텍스트:")
        st.write(text)

if __name__ == "__main__":
    main()