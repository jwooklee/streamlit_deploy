import streamlit as st
import speech_recognition as sr
import os
from datetime import datetime
from streamlit_webrtc import webrtc_streamer
import numpy as np
import wave
import tempfile

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
    st.title("🎙️ 음성 녹음 및 텍스트 변환")
    
    # 탭 생성
    tab1, tab2 = st.tabs(["실시간 녹음", "파일 업로드"])
    
    with tab1:
        st.write("마이크 버튼을 클릭하여 음성을 녹음하세요.")
        webrtc_ctx = webrtc_streamer(
            key="speech-to-text",
            audio_receiver_size=1024,
            rtc_configuration={
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            },
            media_stream_constraints={
                "video": False,
                "audio": True
            }
        )
        
        if st.button("음성 변환", disabled=not webrtc_ctx.state.playing):
            if webrtc_ctx.audio_receiver:
                try:
                    # 임시 WAV 파일 생성
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                        audio_frames = webrtc_ctx.audio_receiver.get_frames()
                        audio_data = b''.join([frame.to_ndarray().tobytes() for frame in audio_frames])
                        
                        # WAV 파일 작성
                        with wave.open(temp_file.name, 'wb') as wf:
                            wf.setnchannels(1)
                            wf.setsampwidth(2)
                            wf.setframerate(48000)
                            wf.writeframes(audio_data)
                        
                        # 음성을 텍스트로 변환
                        text = speech_to_text(temp_file.name)
                        st.write("## 변환된 텍스트:")
                        st.write(text)
                        
                        # 임시 파일 삭제
                        os.unlink(temp_file.name)
                except Exception as e:
                    st.error(f"오류 발생: {str(e)}")
    
    with tab2:
        st.write("WAV 파일을 업로드하세요:")
        uploaded_file = st.file_uploader("WAV 파일 선택", type=['wav'])
        if uploaded_file is not None:
            # 임시 파일로 저장
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_file_path = temp_file.name
            
            try:
                # 음성을 텍스트로 변환
                text = speech_to_text(temp_file_path)
                st.write("## 변환된 텍스트:")
                st.write(text)
            finally:
                # 임시 파일 삭제
                os.unlink(temp_file_path)

if __name__ == "__main__":
    main()