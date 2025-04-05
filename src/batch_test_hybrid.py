import csv
import logging
from travelbot import hybrid_response  # Import the hybrid function

# --- Configuration ---
INPUT_FILE = "test_prompts.txt"
OUTPUT_FILE = "hybrid_results.csv"

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def load_prompts(file_path):
    """Load prompts from the input file."""
    try:
        with open(file_path, "r") as f:
            prompts = [line.strip() for line in f if line.strip()]
        if not prompts:
            logger.warning(f"No prompts found in {file_path}.")
        return prompts
    except FileNotFoundError:
        logger.error(f"Input file not found: {file_path}")
        return []
    except Exception as e:
        logger.error(f"Error reading input file: {e}")
        return []

def write_results(output_file, results):
    """Write results to the output CSV file."""
    try:
        with open(output_file, "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Prompt", "Response"])
            writer.writerows(results)
        logger.info(f"Results saved to {output_file}")
    except Exception as e:
        logger.error(f"Error writing to output file: {e}")

def process_prompts(prompts):
    """Process each prompt using the hybrid_response function."""
    results = []
    for prompt in prompts:
        try:
            logger.info(f"🔍 Processing: {prompt}")
            response = hybrid_response(prompt)
            results.append((prompt, response))
        except Exception as e:
            logger.error(f"Error processing prompt '{prompt}': {e}")
            results.append((prompt, "Error processing prompt"))
    return results

def main():
    """Main function to execute the batch processing."""
    logger.info("🚀 Starting batch processing...")
    prompts = load_prompts(INPUT_FILE)
    if not prompts:
        logger.error("No prompts to process. Exiting.")
        return

    results = process_prompts(prompts)
    write_results(OUTPUT_FILE, results)
    logger.info("✅ Batch processing complete.")

if __name__ == "__main__":
    main()