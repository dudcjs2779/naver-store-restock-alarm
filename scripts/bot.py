import requests # 요청을 날릴 때 사용하는 라이브러리
import json
# https://api.slack.com/apps 슬랙 로봇 api 주소

# -X POST   #Get으로도 보낼 수 있는 이경우 주소에 데이터가 포함됨(보안)
# -H 'Content-type: application/json'   #json 파입으로 파일을 주고 받자(약속)
# --data '{"text":"Hello, World!"}' 
# https://hooks.slack.com/services/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




#자신의 webbook의 주소를 입력
# slack_url = 'https://hooks.slack.com/services/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'
# slack_url = ""

# msg = f"""
# 안녕하세요 오늘은 파이썬의 크롤링을 배웠습니다. 
# 여기에 나중에 뉴스를 공유를 할 예정입니다.
# """

# requests.post(slack_url, 
#               data=json.dumps({"text":msg}), 
#               headers={"Content-Type": "application/json"}
#               )

from requests.exceptions import MissingSchema

def send_msg_to_slack(msg, slack_url):
    try:
        requests.post(slack_url, 
              data=json.dumps({"text":msg}), 
              headers={"Content-Type": "application/json"}
              )
    except :
        print("슬랙 URL을 확인해주세요!")
        
        
    
