from rag.rag import answer_question


question = "How does requests handle authentication?"

answer = answer_question(question)

print("\nAnswer:\n")
print(answer)