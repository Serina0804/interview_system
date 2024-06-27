import speech_recognition as sr

def audio_recognize():
    # 音声認識器のインスタンスを作成
    recognizer = sr.Recognizer()
    
    # マイクから音声を受け取る
    with sr.Microphone() as source:
        print("何か言ってください...")
        audio = recognizer.listen(source)
    if audio:
        try:
            text = recognizer.recognize_google(audio, language="ja-JP")
            print("認識結果:", text)
            return text
        except sr.UnknownValueError:
            text = "音声が認識できませんでした"
            print("音声が認識できませんでした")
            return text
        except sr.RequestError as e:
            print(f"認識エラー: {e}")
    else:
        print("マイクからの音声がありません")
