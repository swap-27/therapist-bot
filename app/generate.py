from langchain_classic.prompts import PromptTemplate
from dotenv import load_dotenv
import os
from huggingface_hub import InferenceClient


load_dotenv()
client = InferenceClient(
token=os.getenv("API_KEY")
)
def generate_response(user_query, results):
    
    context = "\n\n".join([
        f"""
    Source: {result['document']}
    Category: {result['category']}

    Content:
    {result['text']}
    """
        for result in results
    ])

    prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a helpful and precise therapist assistant.

Based ONLY on the retrieved documents:

1. Relevant concepts
2. Suggested exercises
3. Supporting evidence from the documents
4. Keep the response strictly conversational and concise

Do not provide diagnoses.
Do not mention therapies not explicitly present in the context.

If the answer is not present in the context,
say that the information is not available.

Context:
{context}

Question:
{question}

Answer:
"""
)
    prompt = prompt_template.format(context=context, question=user_query)
    print(f"Prompt: {prompt}")




    response = client.chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct",
        temperature=0.2,
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    response_text = response.choices[0].message.content.strip()
    
    print(f"Response: {response_text}")
    return response_text

