from retrieve import query_search
from langchain_core.chat_history import InMemoryChatMessageHistory
from generate import conversation_chain_builder
from session import get_session_history
from langchain_huggingface.chat_models import ChatHuggingFace
import os
import auth
from database import db

llm = ChatHuggingFace.from_model_id(
    model_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation",
    backend="endpoint",
    huggingfacehub_api_token=os.getenv("API_KEY"),
    temperature=0.2,
    max_new_tokens=256,
)
conversation = conversation_chain_builder(llm=llm)

username = str(input("Enter your username:"))
user = db.get_user(username)

if user is None:
    print("Hello! Haven't seen you before. Please register.")
    display_name = str(input("Enter the name you'd like to be addressed by:"))
    password = str(input("Enter Password:"))
    password_hash = auth.hash_password(password)
    db.create_user(username, password_hash, display_name)
    user = db.get_user(username)
    print("Registered Successfully!")

print("Login for:")
print(f"username:{username}")
password = str(input("Password:"))
check = auth.authenticate_user(username, password)
for i in range(3):
    
    if check:
        user_id = user["id"]
        chat_history = db.load_messages(user_id)
        for message in chat_history:
            if message["role"] == "human":
                role = "You"
            elif message["role"] == "ai":
                role =  "AI Assistant"
            else:
                role = message["role"]
            print(f"{role}: {message["content"]}")
        get_session_history(user_id)



        while True:

            user_query = str(input("You:"))
            db.save_message(user_id, "human", user_query)
            if user_query.lower() in ["exit", "close", "quit"]:
                break

            results = query_search(user_query=user_query)
            context = "\n\n".join([
            f"""
            Source: {result.metadata['document']}
            Category: {result.metadata['category']}
            Score: {result.metadata['score']:.4f}
            Content:
            {result.page_content}
            """
                for result in results
            ])
            response = conversation.invoke(
                {
                    "question": user_query,
                    "context": context
                },
                config={
                    "configurable": {
                        "session_id": user_id
                    }
                }
            )

            print(f"AI Assistant:{response}")
            db.save_message(user_id, "ai", response)
        break
    else:
        print(f"Incorrect Password (Attempt: {i+1}/3). Please enter correct password.")
        password = str(input("Password:"))
        check = auth.authenticate_user(username, password)
        if i == 2 and check:
            i -=1

if i == 2 and check is None:
    print("Password Attempts exhausted. Please login again with correct credentials.")