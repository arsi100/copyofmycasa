from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
import dotenv
import os

def get_retreiver():
    """
    This function returns a retriever object that can be used to query the database
    @ return: retreiver object
    """
    dotenv.load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv("OPEN_AI_KEY")
    
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

    return qa_retriever


def generate_rag__chain():
    """
    This function returns a LANGCHAIN chain object that can be used to query the database via llm 
    @ return: runnable chain object
    """
    dotenv.load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv("OPEN_AI_KEY")

    llm = ChatOpenAI(model_name="gpt-4-turbo-preview", temperature=0)

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

    qa_system_prompt = """You are an DUBAI based real-estate assistant for question-answering tasks based on properties in the database. \
    Use the following pieces of retrieved context to answer the question. \
    If you don't know the answer, just say that you don't know. \
    Keep a professional and helpful tone. \
    If they ask for a price return the prices for the individual units. If no prices are listed do not answer. \
    Do not provide any information that is not directly relevant to the question, including agent information. \
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

    retriever = get_retreiver()

    # define the chain
    rag_chain = (
        RunnablePassthrough.assign(
            context=contextualized_question | retriever | format_docs
        )
        | qa_prompt
        | llm
    )

    return rag_chain


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def ask_question(q, rag_chain, chat_history): 
    """
    This function takes a question as input and returns the answer to the question
    @ param: q: str: question
    @ return: str: answer
    """
    ai_msg = rag_chain.invoke({"question": q, "chat_history": chat_history})
    chat_history.extend([HumanMessage(content=q), ai_msg])
    return ai_msg.content


if __name__ == "__main__":


    rag_chain = generate_rag__chain()
    
    chat_history = []

    question = "Are there any properties in JVC?"
    print('>human msg: ' , question + "\n")

    ai_msg = ask_question(question, rag_chain, chat_history)

    print('ai msg: ', ai_msg)

    second_question = "What is the price of the property in JVC"
    print('>human msg: ', second_question)

    ai_msg2 = ask_question(second_question, rag_chain, chat_history)

    print('ai msg: ', ai_msg2)
    

    '''
    question = "Are there any properties in JVC?"
    print('>human msg: ' , question + "\n")
    ai_msg = rag_chain.invoke({"question": question, "chat_history": chat_history})
    chat_history.extend([HumanMessage(content=question), ai_msg])

    print(ai_msg)
    input()
    
    print('>ai msg: ', ai_msg.content + "\n")
    #print('chat history1: ', chat_history)
    
    second_question = "What is the price of the property in JVC"
    print('>human msg: ', second_question)
    ai_msg2 = rag_chain.invoke({"question": second_question, "chat_history": chat_history})
    chat_history.extend([HumanMessage(content=second_question), ai_msg2])
    
    print('>ai msg: ', ai_msg2.content + "\n" )
    #print('chat history2: ', chat_history)
    
    third_question = input(">")
    print('human msg: ', third_question + "\n")
    ai_msg3 = rag_chain.invoke({"question": third_question, "chat_history": chat_history})
    chat_history.extend([HumanMessage(content=third_question), ai_msg3])

    
    
    print('ai msg: ', ai_msg3.content + "\n")
    #print('chat history3: ', chat_history)
    
    while(True):
        q = input(">")
        print('human msg: ', q + "\n")
        ai = rag_chain.invoke({"question": q, "chat_history": chat_history})
        print('ai msg: ', ai.content + "\n")
        chat_history.extend([HumanMessage(content=q), ai])
    '''

