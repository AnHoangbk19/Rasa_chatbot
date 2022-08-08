from calendar import day_abbr
from cv2 import IMWRITE_PNG_STRATEGY_FILTERED
from matplotlib.pyplot import flag
import requests
import cv2
import base64
import json
import sounddevice as sd
from scipy.io.wavfile import write
from datetime import datetime
import random



#Thư mục pycode mục đích giúp thực hiện các hàm chức năng riêng của Chatbot mà không ảnh hưởng gì trong file actions.py


#Thực hiện chức năng hiển thị tgian
def show_time():
    current_time = datetime.now().strftime("%H:%M:%S")
    return current_time

#Convert ảnh từ file sang b64

def convert_img_to_b64(img):
    # img = cv2.imread(img)
    jpg_img = cv2.imencode('.jpg', img)
    b64_string = base64.b64encode(jpg_img[1]).decode('utf-8')
    return b64_string

#Kết nối API hiển thị thời tiết tại thành phố nhất định
def weather(city): 
    api_address='http://api.openweathermap.org/data/2.5/weather?appid=0c42f7f6b53b244c78a418f4f181282a&q='

    url = api_address + city 
    json_data = requests.get(url).json() 
    try:
        format_add = json_data['main']
    except:
        return
    return format_add


#Kết nối API nhận diện khuôn mặt và trả về kết quả
def face_recog(b64_img):
    url = 'http://172.16.40.157:5000/api/recognize_frame'
    myobj ={"image":b64_img}
    x = requests.post(url, json = myobj)
    return x.json()


def take_picture():
    video = cv2.VideoCapture(0)
    check, frame = video.read()
    cv2.imwrite('file_img.jpg',frame)
    video.release()
    cv2.destroyAllWindows()
    return frame


def record_voice():
    fs = 44100  
    seconds = 3
    print("Bat dau record")
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()  
    print("Ket thuc record")
    write('output.wav', fs, myrecording) 

#Thực hiện dịch vụ kiểm tra ngày phép 
def check_dayoff():
    num = random.random()
    day = random.randrange(1, 11)
    flag = False
    if num < 0.5:
        msg = "Theo Alita kiểm tra thì tháng này bạn đã nghỉ hết số ngày được nghỉ phép rồi nha🧐🧐🧐"
        flag = 0
    else:
        msg = "Alita đã kiểm tra rồi nha...Tháng này bạn còn được {} ngày nghỉ phép nha😙😙😙".format(day)
        flag = day
    return msg , flag



#Thực hiện nhiệm vụ kết nối webhook của chatbot từ đó có thể deploy lên website
def get_chatbot():
    url = 'http://localhost:5005/webhooks/rest/webhook'
    myobj = {
        "sender": "test_user", 
        "message": "hello"
    }
    x = requests.post(url,json=myobj)
    print(x.json())
    temp= ""
    for i in x.json():
        temp = temp + i['text'] +"#"
    return temp


#Nhận diện khuôn mặt rồi trả về kết quả
def voice_recog():
    enc = base64.b64encode(open("output.wav", "rb+").read()).decode('utf-8')
    # with open('readme.txt','w') as f:
    #     f.write(enc)
    # print(type(enc))
    url = 'http://172.16.40.156:5000/api/Speaker-Recognition'
    myobj ={"voice":enc}
    x = requests.post(url, json = myobj)
    return x.json()

# record_voice()
# print(voice_recog().json)

