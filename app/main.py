from generate import generate_response
from retrieve import query_search

query = input("Enter your query: ")

results = query_search(query)
answer = generate_response(query, results)
print("\nFinal Answer:\n")
print(answer)