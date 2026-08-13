from evals.dataset import EVAL_DATASET
from rag.embeddings import embeddings
from rag.vector_store import search_documents


def evaluate_ast_retrieval():
    correct_top_1 = 0
    correct_top_5 = 0

    print("=" * 70)
    print("🚀 EVALUATING AST RETRIEVAL & LINE CITATIONS")
    print("=" * 70 + "\n")

    for index, item in enumerate(EVAL_DATASET, 1):
        question = item["question"]
        expected_file = item["expected_file"]

        results = search_documents(
            query=question,
            embeddings=embeddings,
            limit=5,
            repository="requests",
            collection_name="code_chunks_ast",
        )

        retrieved_files = []
        retrieved_details = []

        for res in results:
            payload = res.payload
            file_path = payload.get("file_path", "unknown")
            node_type = payload.get("node_type", "n/a")
            start_line = payload.get("start_line", "?")
            end_line = payload.get("end_line", "?")

            retrieved_files.append(file_path)
            retrieved_details.append(
                {
                    "file": file_path,
                    "citation": f"{file_path}#L{start_line}-L{end_line}",
                    "node_type": node_type,
                    "score": round(res.score, 4),
                }
            )

        top_1_match = len(retrieved_files) > 0 and retrieved_files[0] == expected_file
        top_5_match = expected_file in retrieved_files

        if top_1_match:
            correct_top_1 += 1
        if top_5_match:
            correct_top_5 += 1

        status = "PASS" if top_5_match else "FAIL"

        print(f"[{index}/{len(EVAL_DATASET)}] [{status}] Q: \"{question}\"")
        print(f"   Expected File : {expected_file}")
        print("   Retrieved Chunks & Line Citations:")

        for rank, detail in enumerate(retrieved_details, 1):
            indicator = "🎯" if detail["file"] == expected_file else "  "
            print(
                f"   {indicator} #{rank} {detail['citation']} "
                f"| node: {detail['node_type']} | score: {detail['score']}"
            )
        print("-" * 70)

    top_1_acc = correct_top_1 / len(EVAL_DATASET)
    top_5_acc = correct_top_5 / len(EVAL_DATASET)

    print("\n" + "=" * 70)
    print("📊 EVALUATION RESULTS SUMMARY")
    print("=" * 70)
    print(f"Hit@1 Accuracy : {top_1_acc:.2%}")
    print(f"Hit@5 Accuracy : {top_5_acc:.2%}")
    print("=" * 70)


if __name__ == "__main__":
    evaluate_ast_retrieval()