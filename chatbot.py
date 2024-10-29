import streamlit as st
import os, utils, opik
from groq import Groq

# --- Groq 및 Opik API Key 설정 -------------------------------------------------
# Streamlit Cloud의 secrets 기능을 사용하여 Groq과 Opik API Key를 설정한다.
# Streamlit Cloud 웹사이트의 앱 설정(settings)에서 secrets 탭을 클릭하여,
# API Key를 TOML 형식으로 secrets에 저장하면 환경 변수로 설정된다.
# 이로 인해 Opik의 경우, opik.configure 메서드와 api_key 매개변수를 사용하지 않아도 API 인증이 가능하며, 
# Groq도 client = Groq(api_key=GROQ_API_KEY)가 아닌 client = Groq()로 간편하게 사용할 수 있다.
  
# Groq 초기화
client = Groq()

# --- 패션 제품 목록 ------------------------------------------------------------
# 온라인 패션 상점에서 판매할 제품 목록을 문자열로 정의한다.
# 이 목록은 챗봇의 컨텍스트로 사용하며, 사용자가 대화 중에 요청할 수 있는 제품 정보를 포함한다.
product_list = '''
# 패션샵 제품 목록

## 남성 의류:
- 티셔츠
  - 가격: 20 달러
  - 사이즈: Small, Medium, Large, XL
  - 가능한 색상: 그린, 화이트, 블랙, 그레이, 네이비

- 청바지
  - 가격: 50 달러
  - 사이즈: Small, Medium, Large, XL
  - 가능한 색상: 블루, 블랙, 그레이, 네이비

## 여성 의류:
- 티셔츠
  - 가격: 20 달러
  - 사이즈: Small, Medium, Large, XL
  - 가능한 색상: 레드, 화이트, 블랙, 그레이, 네이비

- 드레스
  - 가격: 50 달러
  - 사이즈: Small, Medium, Large, XL
  - 가능한 색상: 레드, 화이트, 블랙, 그레이, 네이비
'''


# --- 챗봇의 System Message 설정 --------------------------------------------------
SYSTEM_MESSAGE = f'''
당신은 온라인 패션 상점 Trendy Fahsion 의 AI 어시스턴트인 Shopbot 입니다.

당신의 역할은 고객을 응대하고, 고객이 원하는 제품을 찾도록 재고 목록을 참고하여 정보를 제공하며, 구매 과정을 안내하는 것입니다.

**반드시** 고객이 사용하는 언어에 맞춰서 응답해야 합니다. 만약 고객이 한국어로 메시지를 보냈다면, 반드시 한국어로 응답해야 합니다. 한국어와 영어 이외 다른 언어는 사용하지마세요.

저희 상점에서는 현재 남성 의류와 여성 의류를 판매하고 있습니다.

전체 재고 목록은 다음과 같습니다:

```{product_list}```

**환영 인사는 처음 한번만 합니다. 이미 고객에게 인사 메시지를 보여준 상태이므로, 고객이 '안녕하세요' 등으로 인사를 하더라도 똑같이 인사를 하지말고, 바로 찾고 있는 제품이 있는지 물어보세요.**

고객의 메시지에는 항상 친절하게 답변해야합니다.
'''

GREETINGS = ''' 반갑습니다, 고객님

Trendy Fashion에 오신 것을 환영합니다. 

저는 이 상점의 AI 어시스턴트인 Shoptbot입니다. 

어떤 상품을 찾고 계신가요? 

남성분들을 위한 👕티셔츠와 👖청바지, 여성분들을 위한 👚티셔츠와 👗드레스가 준비되어있습니다.

궁금한 점이 있거나 도움이 필요하면 언제든지 저에게 알려주세요. 

'''

# 시스템 메시지와 인사말을 설정한다.
context = [
    {'role': 'system', 'content': SYSTEM_MESSAGE},
    {'role': 'assistant', 'content': GREETINGS}
]

# --- Streamlit 구성 -----------------------------------------------------------
# 메인 화면에 타이틀과 캡션을 설정한다.
st.title('🛍️ Trendy Fashion 🛍️')    # 웹 애플리케이션의 제목을 설정한다.
st.caption('🤖 AI 쇼핑 어시스턴트입니다.')       # 설명 문구(부제목)를 추가한다.

# AI 챗봇이 먼저 인사말을 한다.
st.chat_message(name='ai').write(GREETINGS)

# 세션 상태에 'messages' 키가 없으면 빈 리스트로 초기화한다.
if 'messages' not in st.session_state:  
    st.session_state['messages'] = []

# 세션 상태에 저장한 메시지를 화면에 출력한다.
for msg in st.session_state.messages:  
    st.chat_message(msg['role']).write(msg['content'])  

# 사용자 입력을 처리하고 LLM 모델의 응답을 생성한다.
if prompt := st.chat_input():  
    # 사용자 입력을 대화 기록에 추가한다.  
    st.session_state['messages'].append({'role': 'user', 'content': prompt}) 
    # 화면에 사용자 입력을 출력한다.
    st.chat_message('user').write(prompt)
    
    # LLM 모델을 사용하여 응답을 생성한다.
    response = client.chat.completions.create(
        model='gemma2-9b-it',
        messages=context + st.session_state['messages']  # context와 대화 기록을 결합하여 모델에 전달한다.
    )

    # 모델의 응답을 대화 기록에 추가하고 화면에 출력한다.
    msg = response.choices[0].message.content  # 모델의 응답 메시지 내용을 추출한다.
    st.session_state['messages'].append({'role': 'assistant', 'content': msg})
    st.chat_message('assistant').write(msg)   # 화면에 모델의 응답을 출력한다.

    # --- Comet Opik에 기록 ----------------------------------------------------
    utils.opik_trace(prompt, msg, context)
    # ------------------------------------------------------------------------
