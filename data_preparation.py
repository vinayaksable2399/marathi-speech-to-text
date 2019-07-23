from pydub import AudioSegment
from pydub.silence import split_on_silence
import os, math,shutil
import speech_recognition as sr 
import pandas as pd
from tqdm import tqdm
import time
import argparse
import urllib.request

from urllib.error import URLError
from datetime import datetime




class split_by_silence:
    
    def __init__(self,outpathname="splited",min_silent=325):
        os.makedirs(outpathname,exist_ok=True)
        self.outpathname=os.path.realpath(outpathname)
        self.min_silent=min_silent
        print("split file store at:",self.outpathname)
        
    def file_split_by_silence(self,directory):
        for j,filename in enumerate(os.listdir(directory)):
            if filename.endswith(".wav"):
                path = os.path.join(directory, filename).replace('\\','/')
                print(path)
                self.audio_split_by_silence(path,j)

    
    def audio_split_by_silence(self,pathname,j):
        total=0
        song = AudioSegment.from_wav(pathname).set_channels(1)
        chunks = split_on_silence(
            song,

            # split on silences longer than 1000ms (1 sec)
            min_silence_len=self.min_silent,

            # anything under -16 dBFS is considered silence
            silence_thresh=song.dBFS-16, 

            # keep 200 ms of leading/trailing silence
            keep_silence=False
        )
        base = os.path.basename(pathname)
        basefilename = os.path.splitext(base)[0]
        #print(chunks)
        i=0   

        for chunk in tqdm(chunks):
            if math.ceil(chunk.duration_seconds) <= 10:
                total+=chunk.duration_seconds
                FileName='{3}/{0}_{1:0>3}_{2}.wav'.format(j,i,str(math.ceil(chunk.duration_seconds)),self.outpathname)
#                 print("Saving........  "+FileName)
                chunk.export(FileName, format="wav")
                i+=1
            else:
                song1 = AudioSegment.from_mono_audiosegments(chunk)
                chunks = split_on_silence(
                    song1,

                    # split on silences longer than 1000ms (1 sec)
                    min_silence_len=self.min_silent,

                    # anything under -16 dBFS is considered silence
                    silence_thresh=song.dBFS-16, 

                    # keep 200 ms of leading/trailing silence
                    keep_silence=False

                )
                for chunk in chunks:
                    if math.ceil(chunk.duration_seconds) <= 10:
                        total+=chunk.duration_seconds
                        FileName='{3}/{0}_{1:0>3}_{2}.wav'.format(j,i,str(math.ceil(chunk.duration_seconds)),self.outpathname)
#                         print("Saving........  "+FileName)
                        chunk.export(FileName, format="wav")
                        i+=1
        print("Total duration we extract:%s"%time.strftime('%H:%M:%S', time.gmtime(total)))
        print("Total duration of file:%s"%time.strftime('%H:%M:%S', time.gmtime(round(song.duration_seconds,2))))
        # print("we loss: %d" %(100-total*100/round(song.duration_seconds))+" %")
        
        


class speech2text:
    def __init__(self,ranamefilepath="speech2text",lang='hi-IN'):
        os.makedirs(ranamefilepath,exist_ok=True)
        self.ranamefilepath=os.path.realpath(ranamefilepath)
        self.lang=lang
        print("%s data store at:"%self.lang,self.ranamefilepath)

    def WavtoText(self,directory,startno=1,i=0):
        duration=0
        df = pd.DataFrame(columns=['ID','TEXT'])
        initial=startno
        i = 0
        error_file=[]
        def wait_for_internet_connection():            
            while True:
                try:
                    response = urllib.request.urlopen('http://www.google.com',timeout=100)
                    return True
                except URLError:
                	print("Internet not connected",datetime.now().time())
                	pass
        for filename in sorted(os.listdir(directory)):
            if filename.endswith(".wav"):
                path = os.path.join(directory, filename).replace('\\','/')
                rfilepath= os.path.join(self.ranamefilepath, str(startno)+".wav").replace('\\','/')
                #print(rfilepath)
                shutil.copy(path,rfilepath)
                AUDIO_FILE = (path) 
                if wait_for_internet_connection():
                    r = sr.Recognizer() 
                    with sr.AudioFile(AUDIO_FILE) as source:
                        audio=r.record(source)
                        #print("Stop record")
                    try:
                        Text =(r.recognize_google(audio, language = self.lang))
                        z = Text.encode(encoding='UTF-8',errors='strict')
                        df.loc[i,'ID']=startno
                        df.loc[i,'TEXT']=Text
                        duration=math.ceil(len(audio.get_wav_data())/(audio.sample_rate*audio.sample_width))+duration
                        i=i+1
                        startno = startno+1
                    except:
                        # print("Error:"+filename)
                        error_file.append(filename)
                        pass;
                continue
            else:
                continue
        csvpath = os.path.join(self.ranamefilepath, "Hindi_%d_%d.csv"%(initial,startno-1)).replace('\\','/') 
        
        
        

        def is_not_ascii(string):
            return string is not None and any([ord(s) >= 128 for s in string])

        df = df[df['TEXT'].apply(is_not_ascii)]
        df.to_csv(csvpath,index=False, encoding='utf-8')
        # Please open the csv file in Text Editor to see the Hindi Text.
        shutil.rmtree(directory)
        # print(error_file)
        print("total data :",time.strftime('%H:%M:%S', time.gmtime(duration)))
        # msg=input("are you sure to see, not converted wav file? Y/[N]")
        # if msg.upper() in ['Y','YES']:
        # 	print(error_file)

        return startno, csvpath,duration

def main():
	parser = argparse.ArgumentParser()
	# parser.add_argument('--past_data', help='data from easy app')
	parser.add_argument('-i','--inputs', help='data folder')
	parser.add_argument('-o','--outputs',default='speech2text' ,help='text to speech files')
	args = parser.parse_args()
	silence_splite=split_by_silence(min_silent=500)
	silence_splite.file_split_by_silence(args.inputs)
	s2t=speech2text(ranamefilepath=args.outputs)
	print(s2t.WavtoText(silence_splite.outpathname)[1])

def main1(inputs,outputs,startno):
    silence_splite=split_by_silence(min_silent=500)
    silence_splite.file_split_by_silence(inputs)
    s2t=speech2text(outputs)
    return s2t.WavtoText(silence_splite.outpathname,startno)  

def data_file():
    parser = argparse.ArgumentParser()
    # parser.add_argument('--past_data', help='data from easy app')
    parser.add_argument('-i','--file', help='data folder')
    parser.add_argument('-o','--outputs',default='speech2text' ,help='text to speech files')
    args = parser.parse_args()
    os.makedirs(args.outputs,exist_ok=True)
    j=21
    startno=10301
    duration=44035
    for i,filename in enumerate(os.listdir(args.file)):    
        path = os.path.join(args.file, filename)
        if i>59:
            if i%3 ==0:
                folder=os.path.join(args.outputs,"file_%d-%d"%(i,i+2))
                os.makedirs(folder,exist_ok=True)
                rfilepath= os.path.join(folder, "%d.wav"%i).replace('\\','/')
                        #print(rfilepath)
                shutil.copy(path,rfilepath)
            else:
                rfilepath= os.path.join(folder, "%d.wav"%i).replace('\\','/')
                        #print(rfilepath)
                shutil.copy(path,rfilepath)
            if i==j*3-1:
                print(i,os.listdir(folder))
                savepath=folder.replace('file','folder')
                startno,_,time1=main1(folder,savepath,startno)
                duration+=time1
                print("\n\n\tup to total data :",time.strftime('%H:%M:%S', time.gmtime(duration)))
                shutil.rmtree(folder)
                j+=1



if __name__ == '__main__':
	# main()
	data_file()