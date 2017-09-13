# encoding: utf-8
import sys, requests, json

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FollowEvent, UnfollowEvent
)
from linebot.exceptions import LineBotApiError

app = Flask(__name__)

line_bot_api = LineBotApi('HdDEyTifuEOVJFujW93ez1J6NR5pIeyM9QM/hIfGyM0NJTDh+tfq0JvhtL8ISRk0mFpgrkzqFHwe4rFJv1R6RK58FqUg7jSEXUIv+Q1R0ubjc9MZRGmrIM0D4q64RlzgR6o/hQpTNvSdzOfmRbitwAdB04t89/1O/w1cDnyilFU=') #Your Channel Access Token
handler = WebhookHandler('bc7b5e36b8caf97d10ec72b98eabc0a7') #Your Channel Secret

def airQuality(areaName):

    url = 'http://opendata2.epa.gov.tw/AQX.json'
    response = requests.get(url)
    response.raise_for_status()

    airDataList = json.loads(response.text)

    p(airDataList)
    status =''
    pmData =''
    for airDict in airDataList:
        dicAreaStr = airDict['SiteName']
        if areaName in dicAreaStr:
            status = airDict['Status'] 
            pmData = airDict['PM2.5']
            break

    return pmData, status

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    p("Request body: " + body);

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(FollowEvent)
def follow(event):
    p("follow event.type: "+event.type)

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text #message from user

    p("event.reply_token: "+event.reply_token)
    p("event.type: "+event.type)
    p("event.source.userId: "+event.source.user_id)

    try:
        profile = line_bot_api.get_profile(event.source.user_id)
        p("profile.display_name: "+profile.display_name)
        p("profile.user_id: "+profile.user_id)
        p("profile.picture_url: "+profile.picture_url)
    except LineBotApiError as e:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='咦～尋找你的資料好像有點問題～'))

    #Line 系統token 不回應
    if event.reply_token == '00000000000000000000000000000000':
       return 'Line reply_token 檢核,不作回應';

    if 'pm2.5' in text:
        allTexts = text.split(' ',1)

        areaName = allTexts[1]

        p("text:"+areaName);

        pmData, status = airQuality(areaName)

        replyText = ''
        if len(pmData) > 0:

            p("text:"+areaName + '的 pm2.5 為 '+ pmData +'，' + '狀態 : ' + status);

            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='哈囉 '+profile.display_name+' 以下是你要的資料～'+'\n\n'+areaName + '的 pm2.5 為 '+ pmData +'，' + '狀態 : ' + status))
        else:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='沒有找到你要的唷～'))

def p(log):
  print(log) 
  sys.stdout.flush()  


import os
if __name__ == "__main__":
    # app.run(host='0.0.0.0',port=os.environ['PORT'])
    app.run()