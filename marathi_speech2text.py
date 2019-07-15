import speech_recognition as sr
def speech2text(wavfile,lang='mr-IN'):    
    r = sr.Recognizer()
    with sr.AudioFile(wavfile) as source:
        audio = r.record(source)

    try:
        s = r.recognize_google(audio,language = lang)
        print("Text: "+s)
        filename=wavfile.replace('.wav','.txt')
        f = open(filename, "a")
        f.write(s)
        f.close()
                
    except Exception as e:
        print("Exception: "+str(e))
if __name__ == "__main__":
    speech2text("marathi.wav")