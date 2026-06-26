from langchain_classic.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
import os
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import ChatHuggingFace
from retrieve import query_search
from session import get_session_history
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()


def conversation_chain_builder(llm):

    prompt_template = f"""
You are a helpful and precise therapist assistant.

Based ONLY on the retrieved documents and chat history:

1. Relevant concepts
2. Suggested exercises
3. Keep the response strictly conversational and concise

Keep response conversational and do not mention documents.

Do not provide diagnoses. If the user self-identifies with a condition, refer to it using the user's own wording unless the retrieved documents explicitly discuss that condition.
Do not mention therapies not explicitly present in the context.

If the answer is not present in the context or chat history,
say that the information is not available.

Chat history:
{{chat_history}}

Context:
{{context}}
"""

    prompt = ChatPromptTemplate.from_messages(
        [("system", prompt_template), MessagesPlaceholder(variable_name = "chat_history"), ("human", "{question}")]
    )
    parser = StrOutputParser()

    chain = prompt | llm | parser


    conversation_chain = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="chat_history"
    )

    return conversation_chain