import streamlit as st
from PIL import Image
import pandas as pd
import time
from streamlit_chat import message
#from seqclass import predict_system
from PIL import Image
import numpy as np
from streamlit.components.v1 import html
from pyOutlook import *
import win32com.client as win32
from cos_similarity import predictions
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import math
#import streamlit.report_thread as ReportThread
#from streamlit.server.server import Server
pd.set_option("display.max_colwidth", 10000)



# logo
image = Image.open('streamlit.png')
st.sidebar.image(image, width = 150)
st.sidebar.title("FAQ chatbot")
st.sidebar.write("An Initiative of the Company")

if st.sidebar.button("Back to Menu"):
    st.session_state.clear()
    st.experimental_rerun()
    
def sendmail(prompt1):
#     reqno = 'MQ'+str(int(round(time.time(),0)))
#     mail.Subject = reqno+" - "+prompt1
    
#     outlook = win32.Dispatch('outlook.application')
#     mail = outlook.CreateItem(0)
#     mail.To = 'dileep127463@exlservice.com'
#     #mail.Subject = 'Message subject'
#     mail.Body = prompt1
    #mail.HTMLBody = '<h2>HTML Message body</h2>' #this field is optional

    # To attach a file to the email (optional):
    #attachment  = "Path to the attachment"
    #mail.Attachments.Add(attachment)
    
    SERVER = "your server"
    FROM = "from mail"
    TO = ["to mail list"] # must be a list
    reqno = 'MQ'+str(int(round(time.time(),0)))
    #     mail.Subject = reqno+" - "+prompt1
        

    SUBJECT = reqno
    TEXT = prompt1

    # Prepare actual message
    message = """From: %s\r\nTo: %s\r\nSubject: %s\r\n\

    %s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    # Send the mail
    import smtplib
    server = smtplib.SMTP(SERVER)
    
    server.ehlo()
    # secure our email with tls encryption
    server.starttls()
    # re-identify ourselves as an encrypted connection
    server.ehlo()
    server.login('mailid', 'pwd')

    server.sendmail(FROM, TO, message)
    server.quit()
    
    return
    
    
    
    
    
    
    
    

def Rerun():
    st.session_state.clear()
    st.experimental_rerun()

@st.cache_data
def load_data():
    # read data to populate as bubble
    data = pd.read_csv('qna_v10.csv')
    return data

@st.cache_resource
def load_model():
    model = SentenceTransformer("all-mpnet-base-v2")
    return model
       

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

    qna_data = load_data()
    mpn_model = load_model()
    st.session_state.qna_data = qna_data
    st.session_state.model = mpn_model

if "disabled" not in st.session_state:
    st.session_state.disabled = False


# Display chat messages from history on app rerun
for i,msg in enumerate(st.session_state.messages):
    # with st.chat_message(msg["role"]):
    #     st.markdown(msg["content"])
    if msg["role"]=="user":
        message(msg["content"], is_user=True, key=i+1, avatar_style='icons',seed='Maggie')
    else:
        message(msg["content"], key=i+1, avatar_style='bottts',seed=13)

# Initialize chat memory
if "lvl" not in st.session_state:
    st.session_state.lvl = 0

    # Display assistant response in chat message container
    assistant_response = f"Currently, the chatbot offers support to selected issues only. \
        Please click on the *System* that you are facing an issue with (or) enter your query below"
    
    # with st.chat_message("assistant"):
    #     message_placeholder = st.empty()        
    #     message_placeholder.markdown(assistant_response)
    message(assistant_response, key=0, avatar_style='bottts',seed=13)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    

if "sel" not in st.session_state:
    st.session_state.sel = ''

if st.session_state.lvl == 0:
    qna_data = st.session_state.qna_data
    lst = list(qna_data['System'].unique())
    assistant_response = f"Thank you for your selection. \
        Please select the *Model type* to narrow down the issue:"
elif st.session_state.lvl == 1:
    selected = st.session_state.sel
    qna_data = st.session_state.qna_data
    qna_data = qna_data[qna_data['System']==selected]
    st.session_state.qna_data = qna_data
    st.session_state.disabled = True
    lst = list(qna_data['ModelType'].unique())
    assistant_response = f"Thank you for your selection. \
        Please select the *Issue* from the following options:"

elif st.session_state.lvl == 2:
    selected = st.session_state.sel
    qna_data = st.session_state.qna_data
    qna_data = qna_data[qna_data['ModelType']==selected]
    st.session_state.qna_data = qna_data
    lst = list(qna_data['Issues'].unique())
    
elif st.session_state.lvl == 3:
    selected = st.session_state.sel
    qna_data = st.session_state.qna_data


col1, col2 = st.columns(2)

#Display buttons for column 1
with col1:
    if st.session_state.lvl < 3:
        if len(lst)>1:
            if len(lst)%2 == 1:
                col1_lst_size = int(np.floor(len(lst)/2)+1)
                col2_lst_size = int(np.floor(len(lst)/2))
            else:
                col1_lst_size = int(np.floor(len(lst)/2))
                col2_lst_size = int(np.floor(len(lst)/2))
        else:
            col1_lst_size = int(len(lst))
            
        if len(lst)>1:
            col1_lst = lst[0:col1_lst_size]
            col2_lst = lst[col1_lst_size:int(len(lst))]
        else:
            col1_lst = lst[0:col1_lst_size]
            col2_lst = []

        button_space = st.empty()
        with button_space.container():
            for item in col1_lst:
                if st.button(item):
                    st.session_state.lvl += 1
                    st.session_state.sel = item
                    # Add user message to chat history
                    st.session_state.messages.append({"role": "user", "content": item})
                    # Display user message in chat message container
                    with st.chat_message("user"):
                        st.markdown(item)
                        js = f"""
    <script>
        function scroll(dummy_var_to_force_repeat_execution){{
            var textAreas = parent.document.querySelectorAll('section.main');
            for (let index = 0; index < textAreas.length; index++) {{
                textAreas[index].style.color = 'black'
                textAreas[index].scrollTop = textAreas[index].scrollHeight;
            }}
        }}
        scroll({len(st.session_state.messages)})
    </script>
    """
                        html(js)
                          
                        
                    if st.session_state.lvl == 3:
                        # Display the answer as assistant response
                        selected  = st.session_state.sel
                        assistant_response = qna_data[qna_data['Issues']==selected]['Answers'].to_string(index=False)
                        print(assistant_response)
                        # Display assistant response in chat message container
                        
                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()                    
                
                        message_placeholder.markdown(assistant_response)
                        # Add assistant response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                        js = f"""
  <script>
      function scroll(dummy_var_to_force_repeat_execution){{
          var textAreas = parent.document.querySelectorAll('section.main');
          for (let index = 0; index < textAreas.length; index++) {{
              textAreas[index].style.color = 'black'
              textAreas[index].scrollTop = textAreas[index].scrollHeight;
          }}
      }}
      scroll({len(st.session_state.messages)})
  </script>
  """
                        html(js)
                        st.experimental_rerun()
                        
#Display buttons for column 2
                        
with col2:
    if st.session_state.lvl < 3:
        if len(lst)>1:
            if len(lst)%2 == 1:
                col1_lst_size = int(np.floor(len(lst)/2)+1)
                col2_lst_size = int(np.floor(len(lst)/2))
            else:
                col1_lst_size = int(np.floor(len(lst)/2))
                col2_lst_size = int(np.floor(len(lst)/2))
        else:
            col1_lst_size = int(len(lst))
            
        if len(lst)>1:
            col1_lst = lst[0:col1_lst_size]
            col2_lst = lst[col1_lst_size:int(len(lst))]
        else:
            col1_lst = lst[0:col1_lst_size]
            col2_lst = []

        button_space = st.empty()
        with button_space.container():
              for item in col2_lst:
                  if st.button(item):
                      st.session_state.lvl += 1
                      st.session_state.sel = item
                      # Add user message to chat history
                      st.session_state.messages.append({"role": "user", "content": item})
                      # Display user message in chat message container
       
                      #html(js)
                      with st.chat_message("user"):
                          st.markdown(item)
                          js = f"""
      <script>
          function scroll(dummy_var_to_force_repeat_execution){{
              var textAreas = parent.document.querySelectorAll('section.main');
              for (let index = 0; index < textAreas.length; index++) {{
                  textAreas[index].style.color = 'black'
                  textAreas[index].scrollTop = textAreas[index].scrollHeight;
              }}
          }}
          scroll({len(st.session_state.messages)})
      </script>
      """
                          html(js)
                          
                          
                      #if prompt == '':
                      if st.session_state.lvl == 3:
                        # Display the answer as assistant response
                        selected  = st.session_state.sel
                        assistant_response = qna_data[qna_data['Issues']==selected]['Answers'].to_string(index=False)
                        print(assistant_response)
                        # Display assistant response in chat message container
                        
                      with st.chat_message("assistant"):
                          message_placeholder = st.empty()                    
                         
                          message_placeholder.markdown(assistant_response)
                          # Add assistant response to chat history
                          st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                          js = f"""
    <script>
        function scroll(dummy_var_to_force_repeat_execution){{
            var textAreas = parent.document.querySelectorAll('section.main');
            for (let index = 0; index < textAreas.length; index++) {{
                textAreas[index].style.color = 'black'
                textAreas[index].scrollTop = textAreas[index].scrollHeight;
            }}
        }}
        scroll({len(st.session_state.messages)})
    </script>
    """
                          html(js)
                          st.experimental_rerun()               

                         


# Accept user input


if st.session_state.lvl==4:
    st.session_state.clear()    
    st.experimental_rerun()

def disable():
    st.session_state["disabled"] = True

# st.text_input(
#     "Enter some text", 
#     disabled=st.session_state.disabled, 
#     on_change=disable
# )
if "prompt1" not in st.session_state:
    st.session_state.prompt1 = ""


def submit():
    st.session_state.prompt1 = st.session_state.widget
    st.session_state.widget = ""
#import streamlit as st

# # Forms can be declared using the 'with' syntax
# with st.form(key='my_form'):
#     text_input = st.text_input(label='Enter your name')
#     submit_button = st.form_submit_button(label='Submit')

styl = f"""
<style>
    .stTextInput {{
      position: fixed;
      bottom: 3rem;
    }}
</style>
"""
st.markdown(styl, unsafe_allow_html=True)
#i=1
#with st.form(key="my_form",clear_on_submit=True):
text_input_container0 = st.empty()

prompt1 = text_input_container0.text_input("", disabled=st.session_state.disabled, placeholder="Enter your issue/query")
    
#submitted = st.form_submit_button("Submit")

if prompt1 != "":
    text_input_container0.empty()

if prompt1:
    
    
    if st.sidebar.button("Write to us"):
        sendmail(prompt1)
        st.write('Email has been sent to the relevant team')
        #message(nassistant_response, avatar_style='bottts',seed=13)
    
    
    st.session_state.lvl=3
    #st.write(dir(prompt1))
    #prompt1 = st.session_state.prompt1
    #st.session_state.messages.append({"role": "user", "content": prompt1})
    #with st.chat_message("user"):
    #    st.markdown(prompt1)
    #message(prompt1, is_user=True, avatar_style='icons',seed='Maggie')
    #st.markdown(styl, unsafe_allow_html=True)
    message(prompt1, is_user=True, avatar_style='icons',seed='Maggie')
    #st.write(2)
    
    #st.experimental_rerun()
        
    #Get top 3 issues from the model
    
    
    
        
    #predicted = predict_system(prompt1)
    
    #Compile a list to pass them as buttons
    
    sys_lst,mdl_lst,iss_lst,cos_lst = predictions(qna_data,st.session_state.model,prompt1)
    
    #iss_lst = [predicted[0][2],predicted[1][2],predicted[2][2]] 
    #sys_lst = [predicted[0][0],predicted[1][0],predicted[2][0]] 
    #mdl_lst = [predicted[0][1],predicted[1][1],predicted[2][1]]
    #print(iss_lst)
    
    assistant_response = f"According to us, your issue may correspond to one of the following issues. Please input the relevant option number from the following options.\n"+ "1. System - "+ sys_lst[0]+", Model - "+mdl_lst[0]+", Issue you are facing - "+iss_lst[0]+" \n" + "2. System - "+ sys_lst[1]+", Model - "+mdl_lst[1]+", Issue you are facing - "+iss_lst[1]+" \n" + "3. System - "+ sys_lst[2]+", Model - "+mdl_lst[2]+", Issue you are facing - "+iss_lst[2]+" \n" +"4. None of these \n"
    
                            
    
    
    #st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    #with st.chat_message("assistant"):
    #    st.markdown(assistant_response)
    #message(assistant_response, is_user=True, avatar_style='icons',seed='Maggie')
    #with st.chat_message("assistant"):
    #st.markdown(styl, unsafe_allow_html=True)
    
    message(assistant_response, avatar_style='bottts',seed=13)
    
    js = f"""
    <script>
        function scroll(dummy_var_to_force_repeat_execution){{
            var textAreas = parent.document.querySelectorAll('section.main');
            for (let index = 0; index < textAreas.length; index++) {{
                textAreas[index].style.color = 'black'
                textAreas[index].scrollTop = textAreas[index].scrollHeight;
            }}
        }}
        scroll({len(st.session_state.messages)})
    </script>
    """
    html(js)
    

    
    #st.experimental_rerun()
    
    #st.session_state.lvl=3
    text_input_container = st.empty()

    if "level" not in st.session_state:
        st.session_state.level = 0
    #st.session_state.lvl=3
    prompt2 = text_input_container.text_input("", disabled=st.session_state.disabled,on_change=disable,placeholder="Enter relevant option number")  
    #import time
    #time.sleep(2)
    if prompt2 != "":
        text_input_container.empty()
    #st.info(t)

    if prompt2:
        #st.write(prompt2)
        option = int(prompt2)
        if option == 1:
            st.session_state.lvl=3
            st.session_state.sel = iss_lst[0]
            st.session_state.model = mdl_lst[0]
            st.session_state.system = sys_lst[0]
            item = "1. System - "+ sys_lst[0]+", Model - "+mdl_lst[0]+", Issue you are facing - "+iss_lst[0]
            st.session_state.messages.append({"role": "user", "content": item})
            # Display user message in chat message container
            #with st.chat_message("user"):
            #    st.markdown(item)
                #st.experimental_rerun()
            #st.session_state.messages.append({"role": "user", "content": item})
            #with st.chat_message("user"):
            #    st.markdown(prompt1)
            message(item, is_user=True, avatar_style='icons',seed='Maggie')
            
        elif option == 2:
            st.session_state.lvl=3
            st.session_state.sel = iss_lst[1]
            st.session_state.model = mdl_lst[1]
            st.session_state.system = sys_lst[1]
            item = "2. System - "+ sys_lst[1]+", Model - "+mdl_lst[1]+", Issue you are facing - "+iss_lst[1]
            st.session_state.messages.append({"role": "user", "content": item})
            # Display user message in chat message container
            #st.session_state.messages.append({"role": "user", "content": item})
            #with st.chat_message("user"):
            #    st.markdown(prompt1)
            message(item, is_user=True, avatar_style='icons',seed='Maggie')
            

            
        elif option == 3:
            st.session_state.lvl=3
            st.session_state.sel = iss_lst[2]
            st.session_state.model = mdl_lst[2]
            st.session_state.system = sys_lst[2]
            item = "3. System - "+ sys_lst[2]+", Model - "+mdl_lst[2]+", Issue you are facing - "+iss_lst[2]
            #st.session_state.messages.append({"role": "user", "content": item})
            st.session_state.messages.append({"role": "user", "content": item})
            #with st.chat_message("user"):
            #    st.markdown(prompt1)
            message(item, is_user=True, avatar_style='icons',seed='Maggie')
            
            # Display user message in chat message container
            # with st.chat_message("user"):
            #     st.markdown(item)

        
        else:
            st.session_state.lvl = 4
            #if st.session_state.lvl == 0:
                #st.session_state.lvl += 1
            item = "4. None of these"
            st.session_state.messages = []
            st.session_state.messages.append({"role": "user", "content": item})
            
            message(item, is_user=True, avatar_style='icons',seed='Maggie')
            assistant_response = f'Please click on "Back to Menu" to use the guided chatbot or send an email to MQ by clicking "Write to us" button.'
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            message(assistant_response, avatar_style='bottts',seed=13)
            
            js = f"""
    <script>
        function scroll(dummy_var_to_force_repeat_execution){{
            var textAreas = parent.document.querySelectorAll('section.main');
            for (let index = 0; index < textAreas.length; index++) {{
                textAreas[index].style.color = 'black'
                textAreas[index].scrollTop = textAreas[index].scrollHeight;
            }}
        }}
        scroll({len(st.session_state.messages)})
    </script>
    """
            html(js)
            
            #message(item, is_user=True, avatar_style='icons',seed='Maggie')
            
            
            #st.experimental_rerun()
            #st.stop()
                
                                         

                
                #st.session_state.clear()
                #st.experimental_rerun()
                #st.experimental_rerun()
            #st.experimental_rerun()
        
        #st.experimental_rerun()
            
        if st.session_state.lvl == 3:
        # Display the answer as assistant response
            selected  = st.session_state.sel
            #st.write(selected)
            model = st.session_state.model
            system = st.session_state.system
            
            qna_data = qna_data[qna_data['System'].str.upper()==system.upper()]
            #st.write(qna_data)
            qna_data = qna_data[qna_data['ModelType'].str.upper()==model.upper()]
            #st.write(qna_data)
                                                
            assistant_response = qna_data[qna_data['Issues'].str.upper()==selected.upper()]['Answers'].to_string(index=False)
            print(assistant_response)
                                                  # Display assistant response in chat message container
                                                  
        # with st.chat_message("assistant"):
        #     message_placeholder = st.empty()                    
                                                
        #     message_placeholder.markdown(assistant_response)
        #     # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            message(assistant_response, avatar_style='bottts',seed=13)
            

            
            fmessage = f"Please find your solution above. Thank you for using our chatbot. If you are not satisfied with the solution, go back to menu to explore other issues through the guided chatbot (by clicking 'Back to Menu') or write to MQ (by clicking 'Write to us')"
            
            st.session_state.messages.append({"role": "assistant", "content": fmessage})
            message(fmessage, avatar_style='bottts',seed=13)
            
            
            js = f"""
    <script>
        function scroll(dummy_var_to_force_repeat_execution){{
            var textAreas = parent.document.querySelectorAll('section.main');
            for (let index = 0; index < textAreas.length; index++) {{
                textAreas[index].style.color = 'black'
                textAreas[index].scrollTop = textAreas[index].scrollHeight;
            }}
        }}
        scroll({len(st.session_state.messages)})
    </script>
    """
            html(js)
                   # st.stop()
            #st.write(st.session_state.messages)
        #st.experimental_rerun()     
                                
        
       
   
                          
        
        
        

    
   


