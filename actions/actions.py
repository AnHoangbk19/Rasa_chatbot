# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
import random
from email.mime import message
from tkinter.messagebox import NO
from typing import Any, Text, Dict, List
from unicodedata import name
from matplotlib.pyplot import flag, text
#from rasa_core_sdk import Action
#from rasa_core_sdk.events import Restarted
from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher

from rasa_sdk.types import DomainDict
from rasa_sdk.events import EventType
from openpyxl.utils import get_column_letter
from sqlalchemy import values
from pycode.functions import weather, show_time, take_picture, convert_img_to_b64, face_recog,record_voice, check_dayoff,voice_recog

import sounddevice as sd
from scipy.io.wavfile import write
###############################################################################################################################
###############################################################################################################################




###############################################################################################################################
###############################################################################################################################




class ActionQueryTime(Action):

    def name(self) -> Text:
        return "action_query_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_time = show_time()
        restr = "Bây giờ là " + current_time + " nha."

        dispatcher.utter_message(text=restr)

        return []

class ActionChatbotAnswer(Action):
    def name(self) -> Text:
        return "action_chatbot_answer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        bot_event = next(e for e in reversed(tracker.events) if e["event"] == "bot")
        msg =  bot_event["text"]
        print(msg)
        if msg == "Cần tớ giúp xem thời gian bây giờ không?":
            timenow = show_time()
            msg = "Hiện giờ là "+ timenow+ " nha." 
            dispatcher.utter_message(text= msg)
            dispatcher.utter_message(response="utter_continue")
        elif msg=="Có cần Alita hỗ trợ thêm thông tin của công ty không?😎😎😎":
            dispatcher.utter_message(response="utter_info_nois")
            dispatcher.utter_message(response="utter_continue")
        elif msg =="Bạn có kiểm tra thông tin nhiệt độ tại thành phố mình muốn không?...Alita sẽ hỗ trợ cho bạn😙😙😙":
            dispatcher.utter_message(response="utter_ask_city")
        elif msg == "Bạn có muốn biết thêm các dịch vụ của công ty không?":
            button = [
                {"payload": '/cloud_service',"title": "Azure Cloud Services" },
                {"payload": '/software_service',"title": "Custom Software Development" },
                {"payload": '/data_service',"title": "Data Analytics, Machine Learning & AI" }
            ]
            dispatcher.utter_message(text="Hiện đây là các dịch vụ mà NOIS đang có nha....Bạn muốn Alita tư vấn dịch vụ nào😙😙😙:",buttons= button)

        return []


class ActionCheckTemperature(Action):

    def name(self) -> Text:
        return "action_check_temperature"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        city = tracker.latest_message['text']
        city_data = weather(city)
        if city_data == None:
            dispatcher.utter_message(text="Xin lỗi Alita vẫn chưa hiểu tên thành phố mà bạn nói😅😅😅...Bạn nói lại giúp mình với:")
        else:
            temp = city_data['temp'] -273
            msg = "Okeee mình đã check thông tin xong...Nhiệt độ tại thành phố {0} là {1:.2f} độ.".format(city,temp)
            dispatcher.utter_message(text=msg)
            dispatcher.utter_message(response="utter_ask")
        return []


class ActionCheckRecog(Action):

    def name(self) -> Text:
        return "action_check_recog"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent= tracker.latest_message['intent'].get('name')
        if intent == "face_recog":
            dispatcher.utter_message(response= "utter_commit_face")
        elif intent == "voice_recog":
            dispatcher.utter_message(response= "utter_start_record")
        return []

class ActionRecog(Action):

    def name(self) -> Text:
        return "action_recog"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        bot_event = next(e for e in reversed(tracker.events) if e["event"] == "bot")
        msg =  bot_event["text"]
        name = None
        emo = None
        if msg == "Vậy Alita bắt đầu nhận diện khuôn mặt của bạn đây nha😊😊😊":
            pic = take_picture()
            b64_img = convert_img_to_b64(pic)
            # x = face_recog(b64_img)
            x = {
                'status' : True,
                'name' : "Hoàng An",
                'Emotion' : 'Sad'
            }
            print(x)
            emo = x["Emotion"]
            print(emo)
            if x['status']:
                name = x['name']
                msg = "Cho mình xác nhận bạn có phải là {} không?".format(name)
                dispatcher.utter_message(text=msg)
            else:
                # msg2 = "Xin lỗi Alita không nhận diện được bạn là ai😓😓😓...Bạn vui lòng chọn lại phương thức đăng nhập giúp mình"
                # dispatcher.utter_message(text=msg2)
                dispatcher.utter_message(response= "utter_request_login_again")
        elif msg == "Vậy Alita sẽ bắt đầu record giọng nói trong 5s nha....Bắt đầu:":
            print("hello")
            fs = 44100  
            seconds = 5 
            # print("Bat dau record")
            myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
            sd.wait()  
            write('output.wav', fs, myrecording) 
            x = voice_recog()
            # x = {
            #     'status' : True,
            #     'name' : "Hoàng An"
            # }
            name = x['name']
            msg2 = "Record kết thúc....cảm ơn bạn đã hợp tác với Alita😊😊😊"
            dispatcher.utter_message(text=msg2)
            msg = "Cho mình xác nhận bạn có phải là {} không?".format(name)
            dispatcher.utter_message(text=msg)
        return [SlotSet('cus_name',name),SlotSet('emotion',emo)]


class ActionGetReason(Action):

    def name(self) -> Text:
        return "action_get_reason"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent= tracker.latest_message['intent'].get('name')
        print("Intent:",intent)
        return [SlotSet('cus_reason',intent)]


class ActionCheckName(Action):

    def name(self) -> Text:
        return "action_check_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = tracker.get_slot("cus_name")
        value = 'false_name'
        if name != None:
            value = 'true_name'
        return [SlotSet('check_name',value)]

class ActionDayoffServoce(Action):

    def name(self) -> Text:
        return "action_dayoff_service"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        reason = tracker.get_slot("cus_reason")
        msg, flag = check_dayoff()
        if reason == "check_dayoff":
            dispatcher.utter_message(text=msg)
        elif reason == "submit_dayoff":
            dispatcher.utter_message(text=msg)
            if flag == 0:
                dispatcher.utter_message(response= "utter_continue")
            else:
                dispatcher.utter_message(response= "utter_ask_the_dayoff")
        return []

class ActionGetNumber(Action):

    def name(self) -> Text:
        return "action_get_number"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        bot_event = next(e for e in reversed(tracker.events) if e["event"] == "bot")
        msg =  bot_event["text"]
        num = tracker.latest_message['text']
        if msg == "Không biết bạn muốn đăng ký nghỉ ngày nào trong tháng này nhỉ(Nhập số 1-31):":
            return [SlotSet("the_dayoff",num)]
        elif msg == "Bạn nghỉ trong vòng mấy ngày nè😙😙😙...Lưu ý đừng nghỉ quá số ngày phép cho phép trong tháng này nha(Nhập số 1-31):":
            return [SlotSet("number_dayoff",num)]
        return []


class ActionAccessCus(Action):

    def name(self) -> Text:
        return "action_access_cus"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        msg = "Hình như bạn vẫn chưa đăng nhập🙄🙄🙄"
        dispatcher.utter_message(text=msg)
        dispatcher.utter_message(response="utter_request_login")
        return []

class ActionWelcomeStaff(Action):
    def name(self) -> Text:
        return "action_welcome_staff"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        staff_name = tracker.get_slot("cus_name")
        emotion = tracker.get_slot("emotion")
        if emotion != None:
            if emotion =='Angry' or emotion == 'Sad':
                msg1 = "Hôm nay trông {} có vẻ không được vui nhỉ😶😶😶...Để mình kể cho bạn một điều thú vị gì đó nha😁".format(staff_name)
                dispatcher.utter_message(text=msg1)
                msg2 = "Khi bạn cười, lượng calo sẽ được đốt cháy nhiều hơn đó😉😉😉 Vì vậy hãy luôn tươi cười nha"
                dispatcher.utter_message(text=msg2)
            else:
                msg = "Helloo {}...Không biết bạn muốn Alita hỗ trợ dịch vụ nào không nè😉😉😉".format(staff_name)
                dispatcher.utter_message(text=msg)
        else:
            msg = "Helloo {}...Không biết bạn muốn Alita hỗ trợ dịch vụ nào không nè😉😉😉".format(staff_name)
            dispatcher.utter_message(text=msg)
        return []

###############################################################################################################################
###############################################################################################################################

class ActionClearCustomerName(Action):
    def name(self) -> Text:
        return "action_clear_customer_name"
    def run(self, dispatcher: "CollectingDispatcher", tracker: Tracker, domain: "DomainDict") -> List[Dict[Text, Any]]:
        return [SlotSet("cus_name", None)]

class ActionClearCustomerReason(Action):
    def name(self) -> Text:
        return "action_clear_customer_reason"
    def run(self, dispatcher: "CollectingDispatcher", tracker: Tracker, domain: "DomainDict") -> List[Dict[Text, Any]]:
        return [SlotSet("cus_reason", None)]


