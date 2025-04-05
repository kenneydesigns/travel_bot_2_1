# filepath: [compare_batch_results.py](http://_vscodecontentref_/9)
import csv
from difflib import unified_diff

def load_results(file_path):
    """Load results from a CSV file."""
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        return {row[0]: row[1] for row in reader}

def save_comparison(output_file, comparisons):
    """Save comparison results to a CSV file."""
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Prompt", "qa_chain Response", "hybrid_response Response", "Difference"])
        writer.writerows(comparisons)
    print(f"✅ Comparison results saved to {output_file}")

def compare_results(file1, file2, output_file="comparison_results.csv"):
    """Compare results from two CSV files."""
    results1 = load_results(file1)
    results2 = load_results(file2)
    comparisons = []

    for prompt in results1:
        qa_response = results1[prompt]
        hybrid_response = results2.get(prompt, "No response")
        diff = "\n".join(unified_diff(qa_response.splitlines(), hybrid_response.splitlines(), lineterm=""))
        comparisons.append((prompt, qa_response, hybrid_response, diff))

        print(f"Prompt: {prompt}")
        print(f"qa_chain Response: {qa_response}")
        print(f"hybrid_response Response: {hybrid_response}")
        if diff:
            print("Difference:")
            print(diff)
        print("-" * 50)

    save_comparison(output_file, comparisons)

if __name__ == "__main__":
    compare_results("results.csv", "hybrid_results.csv")