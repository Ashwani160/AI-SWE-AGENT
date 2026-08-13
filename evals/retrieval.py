from evals.dataset import EVAL_DATASET

from rag.embeddings import embeddings
from rag.vector_store import search_documents


def evaluate_retrieval():
    correct = 0

    for item in EVAL_DATASET:
        results = search_documents(
            query=item["question"],
            embeddings=embeddings,
            limit=5,
            repository="requests",
            collection_name="code_chunks_lang",
        )

        retrieved_files = {
            result.payload["file_path"]
            for result in results
        }
        retrieved_score = {
            result.score
            for result in results
        }

        expected_file = item["expected_file"]

        if expected_file in retrieved_files:
            correct += 1
            status = "PASS"
        else:
            status = "FAIL"

        print(f"{status}: {item['question']}")
        print(f"Expected: {expected_file}")
        print(f"Retrieved: {retrieved_files}")
        print(f"Retrieved Score: {retrieved_score}")
        print()

    accuracy = correct / len(EVAL_DATASET)

    print(f"Retrieval Accuracy: {accuracy:.2%}")


if __name__ == "__main__":
    evaluate_retrieval()