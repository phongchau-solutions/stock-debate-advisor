import os
import pandas as pd
import json

def analyze_technical_data(data_dir: str, output_file: str) -> None:
    print("Starting technical analysis...")
    results = []

    for file_name in os.listdir(data_dir):
        if file_name.endswith(".txt"):
            file_path = os.path.join(data_dir, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                data = f.read()

            # Example analysis: Count lines
            analysis_result = {
                "file_name": file_name,
                "line_count": len(data.splitlines())
            }
            results.append(analysis_result)

    # Save results to CSV
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    print(f"Technical analysis completed. Results saved to {output_file}.")

if __name__ == "__main__":
    data_directory = "/home/x1e3/work/vmo/agentic/v4/autogen_debate_poc/data/api_responses"
    output_csv = "../data/technical_analysis_results.csv"
    analyze_technical_data(data_directory, output_csv)