import streamlit as st
import boto3
import json
from streamlit_session_browser_storage import SessionStorage

sessionBrowserS = SessionStorage()
st.set_page_config(page_title="chatchat", layout="wide", initial_sidebar_state="collapsed",menu_items={'About':"this is about chatchat"})


st.title("chatchat")


with st.expander("Tips"):
        st.write("""
        강의평에 대해서 질문해보세요.\n
        학사일정을 질문해보세요.
        """)


def save_messages_to_storage():
    session_data = json.dumps(st.session_state.messages)
    sessionBrowserS.setItem("messages", session_data)


def clear_messages():
    st.session_state.messages = []
    sessionBrowserS.deleteItem("messages")

    
def retrieve(query, kbId):
    modelArn = 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0'
    
    return bedrock_agent_runtime.retrieve_and_generate(
        input={
            'text': query,
        },
        retrieveAndGenerateConfiguration={
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': "TTKLHCXZSC",
                'modelArn': modelArn,
                "retrievalConfiguration": { 
                    "vectorSearchConfiguration": { 
                        "numberOfResults": 7
                    }
                }
            },
            "type": "KNOWLEDGE_BASE"
        }
    )
    
    
if "messages" not in st.session_state:
    stored_messages = sessionBrowserS.getItem("messages")
    if stored_messages:
        st.session_state.messages = json.loads(stored_messages)
    else:
        st.session_state.messages = []
    
        
if st.button("clear", type="primary"):
    clear_messages()
    
    
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
 
    
bedrock_agent_runtime = boto3.client(
    service_name = "bedrock-agent-runtime", region_name='us-east-1'
)




if prompt := st.chat_input("무엇이든 물어보세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    response_container = st.empty()
    with response_container.chat_message("assistant"):
        st.write("답변 생성 중...")

    model_output = retrieve(prompt, "{KnowledgeBaseID}")["output"]["text"]
    
    response_container.empty()
    with response_container.chat_message("assistant"):
        st.write(model_output)

    
    #model_output = retrieve(prompt, "{KnowledgeBaseID}")["output"]["text"]
    #with st.chat_message("assistant"):
    #    st.write(model_output)

    st.session_state.messages.append({"role": "assistant", "content": model_output})
    save_messages_to_storage()