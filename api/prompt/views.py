import json
from django.shortcuts import render
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime

from django.shortcuts import redirect, get_object_or_404
from .serializers import CreatePromptSerializer, CreateRoleSerializer, PromptSerializer, RoleSerializer
from .factory import PromptFactory
from .models import Prompt, Role, ChatHistory
from .forms import PromptForm
import os
import openai
import base64
import random
import uuid
import logging
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from dotenv import load_dotenv, find_dotenv
from langchain.tools import tool
import requests
import re
from typing import Dict, Any, Type
from pydantic import BaseModel, Field
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import MessagesPlaceholder
from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import DocArrayInMemorySearch
from langchain.schema.runnable import RunnableMap
from langchain.memory import ConversationBufferMemory
from langchain.tools import tool
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents import AgentExecutor
from langchain.text_splitter import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from .constants import MSSQL_AGENT_FORMAT_INSTRUCTIONS,MSSQL_AGENT_PREFIX


from crewai_tools import DirectoryReadTool, FileReadTool, SerperDevTool,BaseTool
#from crewai_tools import tool
from crewai import Agent, Task, Crew, Process
from django.core.mail import send_mail

from .models import Agent as AgentModel,Task as TaskModel,Tool, Department
import os
from typing import List,Optional

openai_api_key = os.getenv('OPENAI_API_KEY')
os.environ["OPENAI_MODEL_NAME"] = 'gpt-4-1106-preview'
os.environ["SERPER_API_KEY"] = os.getenv('SERPER_API_KEY')
db_url = f"postgresql://{os.getenv('POSTGRES_USERNAME')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DBNAME')}"
print(db_url)

def index(request):
    prompts = Prompt.objects.all()
    return render(request, 'prompt/index.html', {'prompts': prompts})


def add(request):
    if request.method == 'POST':
        form = PromptForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = PromptForm()
    return render(request, 'prompt/add.html', {'form': form})


def detail(request, prompt_id):
    prompt = get_object_or_404(Prompt, id=prompt_id)

    return render(request, 'prompt/detail.html', {
        'prompt': prompt,
    })


def update(request, prompt_id):
    prompt = get_object_or_404(Prompt, pk=prompt_id)
    if request.method == 'POST':
        form = PromptForm(request.POST, instance=prompt)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = PromptForm(instance=prompt)
    return render(request, 'prompt/update.html', {'form': form, 'prompt': prompt})


def delete(request, prompt_id):
    prompt = get_object_or_404(Prompt, pk=prompt_id)
    prompt.delete()
    return redirect('index')


class saveResponse(APIView):

    def post(self, request):
        data = request.data
        company = Company.objects.get(name=data.get("company_name"))
        product = Product.objects.get(
            name=data.get("product_name"), company=company)
        prompt = Prompt.objects.filter(
            index=int(data.get("prompt_index")) + 1, product=product).last()
        prompt.data = data
        prompt.save()

        return Response({
            "success": True,
        }, status=status.HTTP_200_OK)

def retrieve_prompt(userInput):
    resp = requests.get("https://promptemplate.booksy.us.boostedchat.com/prompts/")
    prompts = [prompt['text_data'] for prompt in resp.json()]
    character_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=1000,
        chunk_overlap=0
    )
    character_split_texts = character_splitter.split_text('\n\n'.join(prompts))
    token_splitter = SentenceTransformersTokenTextSplitter(chunk_overlap=0, tokens_per_chunk=256)

    token_split_texts = []
    for text in character_split_texts:
        token_split_texts += token_splitter.split_text(text)

    embedding_function = SentenceTransformerEmbeddingFunction()
    chroma_client = chromadb.Client()
    chroma_collection = chroma_client.create_collection(f"prompts-{random.randint(1,1000)}", embedding_function=embedding_function)

    ids = [str(i) for i in range(len(token_split_texts))]

    chroma_collection.add(ids=ids, documents=token_split_texts)
    chroma_collection.count()
    results = chroma_collection.query(query_texts=[userInput], n_results=5)
    retrieved_documents = results['documents'][0]
    return retrieved_documents

def model_with_extra_info(data):
    template = """Answer the user based only on the following context and information and remember to conceal your identity as a robot, you are a sales representative:
            {context}
        information: {information}
        userInput: {userInput}
        """
    prompt = ChatPromptTemplate.from_template(template)
    model = ChatOpenAI(temperature=0)
    output_parser = StrOutputParser()
    chain = RunnableMap({
        "context": lambda x: retrieve_prompt(x["userInput"]),
        "userInput": lambda x: x["userInput"],
        "information": lambda x: x["information"]
    }) | prompt | model | output_parser
    result = chain.invoke(data)
    get_prompt = RunnableMap({
        "context": lambda x: retrieve_prompt(x["userInput"]),
        "userInput": lambda x: x["userInput"],
        "information": lambda x: x["information"]
    }) | prompt
    return {
        "result":result,
        "prompt":get_prompt.invoke(data),
        "model":model
    }

import string

def remove_punctuation(sentence):
    punctuation_to_keep = {'.', ',', '\''}
    punctuation_to_remove = ''.join(p for p in string.punctuation if p not in punctuation_to_keep) + '{}[]'
    table = str.maketrans('', '', punctuation_to_remove)
    return sentence.translate(table)

import sqlite3

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('conversation_history.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY,
        role TEXT NOT NULL,
        content TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

init_db()
def save_message(role, content):
    conn = sqlite3.connect('conversation_history.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO chat_history (role, content) VALUES (?, ?)', (role, content))
    conn.commit()
    conn.close()

def load_messages():
    conn = sqlite3.connect('conversation_history.db')
    cursor = conn.cursor()
    cursor.execute('SELECT role, content FROM chat_history')
    messages = cursor.fetchall()
    conn.close()
    return messages

@tool
def get_sales_representative_data(userInput):
    """this function returns the sales representative data and information about their role"""
    resp = requests.get("https://promptemplate.booksy.us.boostedchat.com/roles/-NmvqgR8ySgPtYKXiQ1c/")
    result = model_with_extra_info({"userInput":userInput,"information":resp.json()['description']})
    return result['result']

class generateResponse(APIView):
    def post(self, request):
        userInput = request.data.get("userInput")
        username_from_id = request.data.get("username_from_id","")
        username_to_id = request.data.get("username_to_id","")
        tools = [get_sales_representative_data]
        functions = [convert_to_openai_function(f) for f in tools]
        # model_with_extra_info = ChatOpenAI(temperature=0).bind(functions=functions)
        
        # Load existing conversation history
        chat_history = ChatHistory.objects.filter(Q(username_from_id=username_from_id)&Q(username_to_id=username_to_id))
        print(chat_history)
        
        # Initialize memory
        memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")

        # Add loaded messages to memory
        for chat in chat_history:
            if chat.role == 'user':
                memory.chat_memory.add_user_message(chat.content)
            elif chat.role == 'assistant':
                memory.chat_memory.add_ai_message(chat.content)

        # Construct the initial result with extra information
        result = model_with_extra_info({"userInput": userInput, "information": "Conceal your identity as a robot, you are a sales representative"})
        print(result)
        
        final_prompt = ChatPromptTemplate.from_messages([
            ("system", remove_punctuation(result['prompt'].messages[0].content)),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{userInput}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        # Create the chain
        model = ChatOpenAI(temperature=0).bind(functions=functions)
        
        chain = RunnablePassthrough.assign(
            agent_scratchpad=lambda x: format_to_openai_functions(x["intermediate_steps"])
        ) | final_prompt | model | OpenAIFunctionsAgentOutputParser()
        
        # Create the agent executor with memory integration
        qa = AgentExecutor(agent=chain, tools=tools, verbose=False, memory=memory)
        
        # Invoke the chain and get the response
        response = qa.invoke({"userInput": userInput})
        
        # Save user input and AI response to SQLite
        ChatHistory.objects.create(role='user', content=userInput,username_from_id=username_from_id,username_to_id=username_to_id)
        ChatHistory.objects.create(role='assistant',content= response['output'],username_from_id=username_from_id,username_to_id=username_to_id)
        
        # Save the updated memory context
        memory.save_context({"input": userInput}, {"output": response['output']})
        
        return Response({
            "response": response
        }, status=status.HTTP_200_OK)


class SentimentAnalysisTool(BaseTool):
    name: str ="Sentiment Analysis Tool"
    description: str = ("Analyzes the sentiment of text "
         "to ensure positive and engaging communication.")
    
    def _run(self, text: str) -> str:
        # Your custom code tool goes here
        return "positive"
    

class ScrappingTheCutTool(BaseTool):
    name: str = "scrapping_thecut_tool"
    description: str = """Allows one to be able to scrap from the cut effectively either,
                        per single or multiple records"""
    # number_of_leads: Optional[str] = None
    endpoint: str = "https://scrapper.booksy.us.boostedchat.com/instagram/scrapTheCut/"


    def _run(self,number_of_leads):
        # import pdb;pdb.set_trace()
        headers = {"Content-Type": "application/json"}
        payload = {
            "chain":True,
            "round":134,
            "index":0,
            "record":None,
            "refresh":False,
            "number_of_leads":number_of_leads
        }
        # import pdb;pdb.set_trace()
        response = requests.post(self.endpoint, data=json.dumps(payload), headers=headers)
        return response.json()

class InstagramSearchingUserTool(BaseTool):
    name: str = "search_instagram_tool"
    description: str = """Allows one to be able to scrap from instagram effectively either,
                        per single or multiple records"""
    # number_of_leads: Optional[str] = None
    endpoint: str = "https://scrapper.booksy.us.boostedchat.com/instagram/scrapUsers/"

    def _run(self,**kwargs):
        # import pdb;pdb.set_trace()
        headers = {"Content-Type": "application/json"}
        payload = {
            "chain":True,
            "round":134,
            "index":0,
            "query":None
        }
        # import pdb;pdb.set_trace()
        response = requests.post(self.endpoint, data=json.dumps(payload), headers=headers)
        return response.json()

class InstagramScrapingProfileTool(BaseTool):
    name: str = "scrapping_instagram_profile_tool"
    description: str = """Allows one to be able to scrap from instagram effectively either,
                        per single or multiple records"""
    # number_of_leads: Optional[str] = None
    endpoint: str = "https://scrapper.booksy.us.boostedchat.com/instagram/scrapInfo/"

    def _run(self,**kwargs):
        # import pdb;pdb.set_trace()
        headers = {"Content-Type": "application/json"}
        payload = {
            "chain":True,
            "round":134,
            "index":0,
            "delay_before_requests":18,
            "delay_after_requests":4,
            "step":3,
            "accounts":18,
        }
        # import pdb;pdb.set_trace()
        response = requests.post(self.endpoint, data=json.dumps(payload), headers=headers)
        return response.json()

class LeadScreeningTool(BaseTool):
    name: str = "fetch_leads"
    description: str = """Allows one to be able to fetch sorted leads that meet certain
                        criterion"""
    
    def _run(self,question,**kwargs):
        # import pdb;pdb.set_trace()
        db = SQLDatabase.from_uri(db_url)

        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", 
                                        verbose=True,prefix=MSSQL_AGENT_PREFIX, 
                                        format_instructions=MSSQL_AGENT_FORMAT_INSTRUCTIONS)

        result = agent_executor.invoke(question)
        return Response({"message":result.get("output","")},status=status.HTTP_200_OK)
        

class FetchLeadTool(BaseTool):
    name: str = "fetch_lead"
    description: str = """Allows one to be able to fetch a lead that meet certain
                        criterion"""
    # number_of_leads: Optional[str] = None
    endpoint: str = "https://scrapper.booksy.us.boostedchat.com/instagram/getAccount/"

    def _run(self,**kwargs):
        # import pdb;pdb.set_trace()
        headers = {"Content-Type": "application/json"}
        payload = {
            "chain":True,
            "round":134
        }
        # import pdb;pdb.set_trace()
        response = requests.post(self.endpoint, data=json.dumps(payload), headers=headers)
        return response.json()


class SlackTool(BaseTool):
    name: str = "slack_tool"
    description: str = """This tool triggers slacks message"""

    def _run(self, message, **kwargs):
        # send the message to the following email -- chat-quality-aaaamvba2tskkthmspu2nrq5bu@boostedchat.slack.com
        db = SQLDatabase.from_uri(db_url)

        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", 
                                        verbose=True,prefix=MSSQL_AGENT_PREFIX, 
                                        format_instructions=MSSQL_AGENT_FORMAT_INSTRUCTIONS)

        result = agent_executor.invoke(message)
        send_mail(subject="Scrapping Monitoring Agent Summary",message=result.get("output",""),from_email="lutherlunyamwi@gmail.com",recipient_list=["chat-quality-aaaamvba2tskkthmspu2nrq5bu@boostedchat.slack.com"])
        return Response({"message":result.get("output","")},status=status.HTTP_200_OK)

class AssignSalesRepTool(BaseTool):
    name: str = "assign_sales_rep_tool"
    description: str = """This tool will assign a lead to a salesrepresentative"""

    endpoint: str = "https://api.booksy.us.boostedchat.com/v1/sales/assign-salesrep/"

    def _run(self,**kwargs):
        headers = {"Content-Type": "application/json"}
        payload = {"username": ""}
        try:
            response = requests.post(self.endpoint, data=json.dumps(payload), headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}


class AssignInfluencerTool(BaseTool):
    name: str = "assign_influencer_tool"
    description: str = """This tool will assign a lead to an influencer"""

    endpoint: str = "https://api.booksy.us.boostedchat.com/v1/sales/assign-influencer/"

    def _run(self,**kwargs):
        headers = {"Content-Type": "application/json"}
        payload = {"username": ""}
        try:
            response = requests.post(self.endpoint, data=json.dumps(payload), headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"This error is because there is an issue with the endpoint and this is the issue:{str(e)}")
            return {"error": str(e)}


class FetchDirectPendingInboxTool(BaseTool):
    name: str = "fetch_pending_inbox_tool"
    description: str = ("Allows fetching of inbox pending requests in instagram")
    endpoint: str = "https://mqtt.booksy.us.boostedchat.com"


    def extract_inbox_data(self, data):
        headers = {
            'Content-Type': 'application/json'
        }
        
        threads = data
        result = []

        for thread in threads:
            users = thread.get('users', [])
            for user in users:
                username = user.get('username')
                thread_id = thread.get('thread_id')
                items = thread.get('items', [])

                for item in items:
                    item_id = item.get('item_id')
                    user_id = item.get('user_id')
                    item_type = item.get('item_type')
                    timestamp = item.get('timestamp')
                    message = item.get('text')

                    data_dict = {
                        'username': username,
                        'item_id': item_id,
                        'user_id': user_id,
                        'item_type': item_type,
                        'timestamp': timestamp,
                        'round': 1908,
                        'pending': True,
                        'info': {**user}
                    }

                    # Save the lead information to the lead database - scrapping microservice
                    response = requests.post(
                        "https://scrapper.booksy.us.boostedchat.com/instagram/instagramLead/",
                        headers=headers,
                        data=json.dumps(data_dict)
                    )
                    if response.status_code in [200, 201]:
                        print("right track")

                    if item_type == 'text':
                        # Save the message
                        # Create an account for it/ also equally save outsourced info for it
                        account_dict = {

                            "igname": username
                        }
                        # Save account data
                        response = requests.post(
                            "https://api.booksy.us.boostedchat.com/v1/instagram/account/",
                            headers=headers,
                            data=json.dumps(account_dict)
                        )
                        account = response.json()
                        # Save outsourced data
                        outsourced_dict = {
                            "results": {
                                **user
                            },
                            "source": "instagram"
                        }
                        response = requests.post(
                            f"https://api.booksy.us.boostedchat.com/v1/instagram/account/{account['id']}/add-outsourced/",
                            headers=headers,
                            data=json.dumps(outsourced_dict)
                        )
                        # Create a thread and store the message
                        data_dict['thread_id'] = thread_id
                        data_dict['message'] = message
                        
                        thread_dict = {
                            "thread_id": thread_id,
                            "account_id": account['id'],
                            "unread_message_count": 0,
                            "last_message_content": message,
                            "last_message_at": datetime.now().isoformat()
                        }
                        response = requests.post(
                            "https://api.booksy.us.boostedchat.com/v1/instagram/dm/create-with-account/",
                            headers=headers,
                            data=json.dumps(thread_dict)
                        )

                        thread_pk = response.json()['id']

                        # Save the message in the thread
                        message_dict = {
                            "content": message,
                            "sent_by": "Client",
                            "thread": thread_pk,
                            "sent_on": datetime.now().isoformat()
                        }
                        response = requests.post(
                            "https://api.booksy.us.boostedchat.com/v1/instagram/message/",
                            headers=headers,
                            data=json.dumps(message_dict)
                        )
                    
                    result.append(data_dict)

        return result



    def _run(self, **kwargs):

        # Set the username for which to fetch the pending inbox
        username = 'barbersince98'
        
        # Send a POST request to the fetchPendingInbox endpoint
        response = requests.post(f'{self.endpoint}/fetchPendingInbox', json={'username_from': username})
        
        # Check the status code of the response
        if response.status_code == 200:
            # Print the response JSON
            print("all is well")
            print(json.dumps(response.json(), indent=2))
            inbox_data = response.json()
            inbox_dataset = self.extract_inbox_data(inbox_data)
            print(inbox_dataset)
            
        else:
            print(f'Request failed with status code {response.status_code}')
        return response.json()

class ApproveRequestTool(BaseTool):  
    name: str = "approve_request_tol"
    description: str = ("Allows approval of requests from pending requests in instagram")
    endpoint: str = "https://mqtt.booksy.us.boostedchat.com"

    def _run(self, username, thread_id, **kwargs):
        # Send a POST request to the approve endpoint
        username = username
        thread_id = thread_id
        response = requests.post(f'{self.endpoint}/approve', json={'username_from': username,'thread_id':thread_id})
        
        # Check the status code of the response
        if response.status_code == 200:
            print('Request approved')
        else:
            print(f'Request failed with status code {response.status_code}')
        return response.json()
    

class LeadQualifierArgs(BaseModel):
    input_text: str = Field(..., description="The text to process")
    threshold: int = Field(10, description="A threshold value for processing")
    username: str = Field(..., description="The username of the lead")
    qualify_flag: bool = Field(..., description="A boolean flag to qualify lead set to true/false")
    relevant_information:Dict[str, Any] = Field(..., description="A dictionary/json containing the relevant information about the lead that is needed")

#class LeadQualifierTool(BaseTool):
class LeadQualifierTool():
    #args_schema: Type[BaseModel] = LeadQualifierArgs
    name: str = "lead_qualify_tool"
    description: str = ("Switches the qualifying flag to true for qualified leads and false to unqualified leads")
    endpoint: str = "https://scrapper.booksy.us.boostedchat.com/instagram/workflows/"

@tool
#def lead_qualify_tool(*args,**kwargs):
def lead_qualify_tool(payload):
        """
Switches the qualifying flag to true for qualified leads and false to unqualified leads.

:param payload: dict, a dictionary containing the following keys:

    username: str, the username of the lead
    qualify_flag: bool, a True/False flag showing if user is qualified or not
    relevant_information: dict, a dictionary containing additional information about the lead. The dictionary can contain the following keys:

        most_probable_name: str, the most probable name of the lead
        most_probable_country_and_location: list of str, the most probable country and location of the lead
        most_probable_venue/salon/barbershop&their_role: list of str, the most probable venue, salon, barbershop, and the lead's role
        what_to_compliment_in_a_lead: list of str, what to compliment in the lead
        other_relevant_insights: list of str, other relevant insights about the lead
        persona: str, the persona of the lead
        outreach_tactic: str, the outreach tactic for the lead

example payload:
{
    "username": "tombarber",
    "qualify_flag": True,
    "relevant_information": {
        "most_probable_name": "Jimmy",
        "most_probable_country_and_location": ["USA", "Miami"],
        "most_probable_venue/salon/barbershop&their_role": ["Top Barber Jimmy", "Owner/Barber"],
        "what_to_compliment_in_a_lead": ["Dedication to craft", "Unique styling", "Positive customer reviews"],
        "other_relevant_insights": ["Fully booked on weekends", "Available slots on weekdays", "Occasional last-minute cancellations", "Active engagement on social media platforms"],
        "persona": "Top-tier Barber",
        "outreach_tactic": "Personalized compliment on dedication and unique styling, highlighting collaboration opportunities on weekdays and promoting tools/products for top-tier barbers."
    }
}
        """
        endpoint: str = "https://scrapper.booksy.us.boostedchat.com/instagram/workflows/"
        print(payload)
        payload = json.dumps(payload)
        print(json.loads(payload)['relevant_information'])
        outbound_qualifying_data={
            "username": json.loads(payload)['username'],
            "qualify_flag": json.loads(payload)['qualify_flag'],
            "relevant_information": json.dumps(json.loads(payload)['relevant_information']),
            "scraped":True
        }
        response = requests.post("https://scrapper.booksy.us.boostedchat.com/instagram/instagramLead/qualify-account/",data=outbound_qualifying_data)
        if response.status_code in [200,201]:
            print("good")
        # inbound qualifying
        inbound_qualify_data = {
            "username": json.loads(payload)['username'],
            "qualify_flag": json.loads(payload)['qualify_flag'],
            "relevant_information": json.dumps(json.loads(payload)['relevant_information']),
            "scraped":True
        }
        response = requests.post("https://api.booksy.us.boostedchat.com/v1/instagram/account/qualify-account/",data=inbound_qualify_data)
        if response.status_code in [200,201]:
            print("best")
        return

class HumanTakeOverTool(BaseTool):
    name: str = "human_takeover_tool"
    description: str = ("Perform a human takeover when the respondent feels that they are conversing with a robot")
    
    def _run(self, username:str, **kwargs):
        data = {
            "username":username,
            "assigned_to": "Human"
        }
        response = requests.post(f"https://api.booksy.us.boostedchat.com/v1/instagram/fallback/{username}/assign-operator/",data=data)
        if response.status_code in [201,200]:
            print(response)
        return "assigned to human"


class WorkflowTool(BaseTool):
    name: str = "workflow_tool"
    description: str = ("Allows the composition of workflows "
         "in order to create as many workflows as possible")
    endpoint: str = "https://scrapper.booksy.us.boostedchat.com/instagram/workflows/"

    def _run(self, workflow_data: dict, **kwargs) -> str:
        print('==========here is workflow data==========')
        print(workflow_data)
        print('==========here is workflow data==========')
        """
        Sends a POST request to the specified endpoint with the provided workflow data and API key.
        """
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(self.endpoint, data=json.dumps(workflow_data), headers=headers)
        print('we are here------------',response)
        if response.status_code not in [200,201]:
            raise ValueError(f"Failed to send workflow data: {response.text}")

        return response.status_code

    
    

TOOLS = {
    "directory_read_tool": DirectoryReadTool(directory='prompt/instructions'),
    "file_read_tool": FileReadTool(),
    "search_internet_tool" : SerperDevTool(),
    "sentiment_analysis_tool" : SentimentAnalysisTool(),
    "workflow_tool" : WorkflowTool(),
    "scrapping_thecut_tool" : ScrappingTheCutTool(),
    "fetch_lead_tool":FetchLeadTool(),
    "lead_screening_tool":LeadScreeningTool(),
    "search_instagram_tool":InstagramSearchingUserTool(),
    "instagram_profile_tool":InstagramScrapingProfileTool(),
    "slack_tool":SlackTool(),
    "assign_salesrep_tool":AssignSalesRepTool(),
    "assign_influencer_tool":AssignInfluencerTool(),
    "fetch_pending_inbox_tool":FetchDirectPendingInboxTool(),
    "approve_requests_tool":ApproveRequestTool(),
    "qualifying_tool":lead_qualify_tool,
    "human_takeover_tool":HumanTakeOverTool()

}

class GeneratedTextOutput(BaseModel):
    text: str
    active_stage: str
    confirmed_problems: str
    human_takeover: bool


class agentSetup(APIView):
    def post(self,request):
        # workflow_data = request.data.get("workflow_data")
        workflow = None
        department = Department.objects.filter(name = request.data.get("department")).last()

        info = request.data.get(department.baton.start_key)
        agents = []
        tasks = []
        
        department_agents = None
        if department.agents.filter(name = request.data.get('agent_name','agent')).exists():
            department_agents = department.agents.filter(name = request.data.get('agent_name'))
        else:
            department_agents = department.agents.exclude(name__icontains='monitoring')
            
        for agent in department_agents:
            print(agent)
            # import pdb;pdb.set_trace()
            if agent.tools.filter().exists():
                agents.append(Agent(
                    role=agent.role.description + " " + agent.role.tone_of_voice if agent.role else department.name,
                    goal=agent.goal,
                    backstory=agent.prompt.last().text_data,
                    tools = [TOOLS.get(tool.name) for tool in agent.tools.all()],
                    allow_delegation=False,
                    verbose=True
                ))
            else:
                agents.append(Agent(
                    role=agent.role.description + " " + agent.role.tone_of_voice if agent.role else department.name,
                    goal=agent.goal,
                    backstory=agent.prompt.last().text_data,
                    allow_delegation=False,
                    verbose=True
                ))
            
        tasks = []
        department_agent_tasks = None
        if department.tasks.filter(agent__name = request.data.get('agent_name')).order_by('index'):
            department_agent_tasks = department.tasks.filter(name = request.data.get('agent_task')).order_by('index')
        else:
            department_agent_tasks = department.tasks.exclude(name__icontains='monitoring').order_by('index')
        
        for task in department_agent_tasks:
            print(task)
            agent_ = None
            for agent in agents:
                if task.agent.goal == agent.goal:
                    agent_ = agent
            if  agent_:
                if task.tools.filter().exists():
                    tasks.append(Task(
                        description=task.prompt.last().text_data if task.prompt.exists() else "perform agents task",
                        expected_output=task.expected_output,
                        tools=[TOOLS.get(tool.name) for tool in task.tools.all()],
 
                       agent=agent_,
                       output_json=GeneratedTextOutput
                    ))
                else:
                    tasks.append(Task(
                        description=task.prompt.last().text_data if task.prompt.exists() else "perform agents task",
                        expected_output=task.expected_output,
                        agent=agent_,
                        output_json=GeneratedTextOutput
                    ))
                
          
        
        crew = Crew(
            agents=agents,
            
            tasks=tasks,
            # process=Process.sequential,
            verbose=True,
            memory=True,
            # output_log_file='scrappinglogs.txt'
        )
        
        # if workflow_data:
            # workflow_tool = TOOLS.get("workflow_tool")
            # response = workflow_tool._run(workflow_data)
            # inputs.update({"workflow_data":workflow_data})
        # import pdb;pdb.set_trace()
        
        result = crew.kickoff(inputs=info)

        # if isinstance(result, dict):
            # kickstart new workflow
                
        return Response({"result":result.json_dict})
        # else:
        #     return Response({"result":result})



class getAgent(APIView):
    def post(self, request, *args,**kwargs):
        transition_prompt = Prompt.objects.filter(name="ED_Stage_Transition_P").latest('created_at')
        template = transition_prompt.text_data
        all_tasks = [{"task_name":task.name,"task_description":task.prompt.last().text_data,"agent_name":task.agent.name,"agent_goal":task.agent.goal} for task in Department.objects.get(name="Engagement Department").tasks.filter(name__icontains="influencer").exclude(name__icontains="quality")]
        prompt = ChatPromptTemplate.from_template(template)
        model = ChatOpenAI(temperature=0)
        output_parser = StrOutputParser()
        chain = RunnableMap({
                "userInput": lambda x: x["userInput"],
                "information": lambda x: x["information"]
            }) | prompt | model | output_parser
        
        data = {"information":
                { 
                    "tasks":all_tasks,
                    "conversations":request.data.get("conversations",""),
                    "active_stage": request.data.get("active_stage","")
                },"userInput":request.data.get("message")}
        chain.invoke(data)
        result = chain.invoke(data)

        return Response(json.loads(result),status=status.HTTP_200_OK)
        




class PromptViewSet(viewsets.ModelViewSet):
    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer

    def get_serializer_class(self):
        if self.action == "update":
            return CreatePromptSerializer
        return super().get_serializer_class()


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def get_serializer_class(self):
        if self.action == "update":
            return CreateRoleSerializer
        return super().get_serializer_class()
