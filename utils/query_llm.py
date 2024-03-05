
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


from openai import OpenAI
from langchain import hub
import dotenv
import os

# Loads the latest version
prompt = hub.pull("rlm/rag-prompt", api_url="https://api.hub.langchain.com")


dotenv.load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPEN_AI_KEY")

OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")
client = OpenAI(api_key=OPEN_AI_KEY)

MONGODB_ATLAS_CLUSTER_URI = os.getenv("MONGODB_STRING")
DB_NAME = "properties_datacomm"
COLLECTION_NAME =  "properties_chunk_for_rag"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "vector_index_chunked"

# Loads the database locally and connects to the cluster
vector_search = MongoDBAtlasVectorSearch.from_connection_string(
    MONGODB_ATLAS_CLUSTER_URI,
    DB_NAME + "." + COLLECTION_NAME,
    OpenAIEmbeddings(disallowed_special=()),
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    

)

# parameters for the query
qa_retriever = vector_search.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 25},
)

# will need to experiment with the prompt
prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Refer to the database collection when answering the questions. If no properties match the query say you do not know.

Context: you are a real estate agent and you have been asked to provide some property locations in the database. 1

Question: {question}
"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)


llm = ChatOpenAI(model_name="gpt-4-turbo-preview", temperature=0.8)

"""
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=qa_retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt},
)
"""


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    {"context": qa_retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


question = "what is a good property for me if i have kids? from the properties in the database (return the best 3 (three) properties in your answer and RETURN their LOCATION as well!! AND the list of ammentities for each property.  as well as PRICE for each available unit listed in the database"

print()
print("> query:", question)
result = rag_chain.invoke(question)
print(f"> answer: {result}")

input('----- init second phase -----')

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)
contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()


from langchain_core.messages import AIMessage, HumanMessage

qa_system_prompt = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise.\

{context}"""
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)


def contextualized_question(input: dict):
    if input.get("chat_history"):
        return contextualize_q_chain
    else:
        return input["question"]


rag_chain = (
    RunnablePassthrough.assign(
        context=contextualized_question | qa_retriever | format_docs
    )
    | qa_prompt
    | llm
)



chat_history = []

print('human msg')
question = "What are some properties near the dubai marina? ?"
ai_msg = rag_chain.invoke({"question": question, "chat_history": chat_history})
chat_history.extend([HumanMessage(content=question), ai_msg])

print('ai msg: ', ai_msg)

second_question = "what is the price and square footage of this property?"
print('human msg: ', second_question)
ai_msg2 = rag_chain.invoke({"question": second_question, "chat_history": chat_history})

print('ai msg: ', ai_msg2)