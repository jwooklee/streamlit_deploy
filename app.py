import streamlit as st
import speech_recognition as sr
import os
from datetime import datetime
from streamlit.components.v1 import html
import base64

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

def get_audio_recorder_html():
    return """
        <div class="audio-recorder">
            <button id="recordButton" onclick="toggleRecording()">녹음 시작</button>
            <div id="recordingStatus"></div>
        </div>

        <script>
            let mediaRecorder;
            let audioChunks = [];
            let isRecording = false;

            async function toggleRecording() {
                const button = document.getElementById('recordButton');
                const status = document.getElementById('recordingStatus');
                
                if (!isRecording) {
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        mediaRecorder = new MediaRecorder(stream);
                        audioChunks = [];

                        mediaRecorder.ondataavailable = (event) => {
                            audioChunks.push(event.data);
                        };

                        mediaRecorder.onstop = async () => {
                            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                            const reader = new FileReader();
                            reader.readAsDataURL(audioBlob);
                            reader.onloadend = function() {
                                const base64data = reader.result.split(',')[1];
                                // Streamlit 컴포넌트 값 업데이트
                                window.parent.postMessage({
                                    type: 'streamlit:setComponentValue',
                                    value: base64data
                                }, '*');
                            };
                        };

                        mediaRecorder.start();
                        isRecording = true;
                        button.textContent = "녹음 중지";
                        status.textContent = "녹음 중...";
                    } catch (err) {
                        console.error("Error accessing microphone:", err);
                        status.textContent = "마이크 접근 오류";
                    }
                } else {
                    mediaRecorder.stop();
                    isRecording = false;
                    button.textContent = "녹음 시작";
                    status.textContent = "녹음 완료";
                }
            }
        </script>
    """

def process_recorded_audio(base64_audio):
    try:
        # base64 데이터를 WAV 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_file = f"temp_audio_{timestamp}.wav"
        
        audio_bytes = base64.b64decode(base64_audio)
        with open(temp_file, "wb") as f:
            f.write(audio_bytes)
        
        # 음성을 텍스트로 변환
        text = speech_to_text(temp_file)
        return text
    except Exception as e:
        st.error(f"오디오 처리 중 오류 발생: {str(e)}")
        return None
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file):
            os.remove(temp_file)

def main():
    st.title("🎙️ 실시간 음성 녹음 및 텍스트 변환")
    st.write("버튼을 클릭하여 음성을 녹음하고 텍스트로 변환하세요.")
    
    # 오디오 녹음기 컴포넌트 추가
    audio_data = html(get_audio_recorder_html(), height=200, key="audio_recorder")
    
    # 녹음된 오디오 데이터 처리
    if audio_data is not None:
        text = process_recorded_audio(audio_data)
        if text:
            st.write("## 변환된 텍스트:")
            st.write(text)
    
    # 파일 업로더
    uploaded_file = st.file_uploader("또는 WAV 파일을 업로드하세요", type=['wav'])
    if uploaded_file is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_file = f"temp_audio_{timestamp}.wav"
        
        with open(temp_file, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        text = speech_to_text(temp_file)
        st.write("## 변환된 텍스트:")
        st.write(text)
        os.remove(temp_file)

if __name__ == "__main__":
    st.set_page_config(page_title="음성 녹음 및 변환")
    main()