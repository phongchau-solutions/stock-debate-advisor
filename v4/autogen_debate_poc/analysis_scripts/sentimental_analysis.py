import os
import pandas as pd
import json

def analyze_sentimental_data(data_dir: str, output_file: str) -> None:
    print("Starting sentimental analysis...")
    results = []

    for file_name in os.listdir(data_dir):
        if file_name.endswith(".txt"):
            file_path = os.path.join(data_dir, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                data = f.read()

            # Example analysis: Count sentiment words (placeholder logic)
            positive_words = ["good", "great", "positive", "excellent"]
            negative_words = ["bad", "poor", "negative", "terrible"]

            positive_count = sum(data.lower().count(word) for word in positive_words)
            negative_count = sum(data.lower().count(word) for word in negative_words)

            analysis_result = {
                "file_name": file_name,
                "positive_count": positive_count,
                "negative_count": negative_count
            }
            results.append(analysis_result)

    # Save results to CSV
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    print(f"Sentimental analysis completed. Results saved to {output_file}.")

if __name__ == "__main__":
    data_directory = "/home/x1e3/work/vmo/agentic/v4/autogen_debate_poc/data/mbb_news"
    output_csv = "../data/sentimental_analysis_results.csv"
    analyze_sentimental_data(data_directory, output_csv)