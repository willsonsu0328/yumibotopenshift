# encoding: utf-8
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('HdDEyTifuEOVJFujW93ez1J6NR5pIeyM9QM/hIfGyM0NJTDh+tfq0JvhtL8ISRk0mFpgrkzqFHwe4rFJv1R6RK58FqUg7jSEXUIv+Q1R0ubjc9MZRGmrIM0D4q64RlzgR6o/hQpTNvSdzOfmRbitwAdB04t89/1O/w1cDnyilFU=') #Your Channel Access Token
handler = WebhookHandler('bc7b5e36b8caf97d10ec72b98eabc0a7') #Your Channel Secret

def airQuality(areaName):

    url = 'http://opendata2.epa.gov.tw/AQX.json'
    response = requests.get(url)
    response.raise_for_status()

    airDataList = json.loads(response.text)

    # logging.debug(airData)
    status =''
    pmData =''
    dicAreaStr = ''
    isfound = False
    for airDataIndex in range(len(airDataList)):
        dicAreaStr = airDataList[airDataIndex]['SiteName']
        if areaName in dicAreaStr:
            status = airDataList[airDataIndex]['Status'] 
            pmData = airDataList[airDataIndex]['PM2.5']
            # areaName = airData['SiteName']
            isfound = True
            break

    return pmData, status

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text #message from user

    if 'pm2.5' in text:
        allTexts = text.split(' ',1)

        areaName = allTexts[1]

        pmData, status = airQuality(areaName)

        replyText = ''
        if len(pmData) > 0:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=areaName + '的 pm2.5 為 '+ pmData +'，' + '狀態 : ' + status))
        else:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='沒有找到你要的唷～'))


        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text)) 
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='我不知道什麼意思～'))

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])
    # app.run()