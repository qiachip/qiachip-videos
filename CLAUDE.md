# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The `qiachip-videos` project is an AI-powered system designed to automatically classify YouTube videos based on Qiachip product models. It is also known as `Qiachip YouTube Product Video Smart Classification` for SEO purposes. This system uses a five-layer intelligent classification pipeline to process videos from a YouTube channel, identify product models, and generate a data dashboard. This significantly improves the efficiency of managing video content.

## Codebase Architecture

The project is structured into several key directories:

-   `classifier/`: Contains the core classification logic.
    -   `extract_model.py`: The main five-layer classification pipeline script. This is the heart of the system.
-   `data/`: Stores all data used in the project.
    -   `raw/`: Raw data fetched from external sources, like `raw_videos.json` (from YouTube) and `model_list.json` (product model whitelist).
    -   `processed/`: Processed data, most importantly `videos_with_model.json`, which contains the final classification results.
-   `reports/`: Contains the data visualization dashboard.
    -   `dashboard.html`: A self-contained HTML file for viewing the classification results.
-   `scraper/`: Scripts for fetching data, such as YouTube video information and model documentation.
-   `scripts/`: Utility scripts, such as those for generating the dashboard.
-   `main.py`: The main entry point for running the entire pipeline, offering different modes of operation.

## Common Development Tasks

### 1. Setting Up the Environment

The project has a few Python dependencies. Install them using `pip`:

```bash
pip install -r requirements.txt
```

### 2. Running the Full Pipeline

The `main.py` script orchestrates the entire workflow, from data scraping to classification and report generation. It provides an interactive prompt to select the desired workflow.

To run the full end-to-end process:
```bash
python main.py
# Then select option 1
```

### 3. Running a Specific Part of the Pipeline

You can also run individual scripts for specific tasks.

-   **To run only the classification process:**
    This reads `data/raw/raw_videos.json` and outputs to `data/processed/videos_with_model.json`.
    ```bash
    python classifier/extract_model.py
    ```

-   **To fetch the latest videos:**
    ```bash
    python scraper/fetch_videos.py Qiachip
    ```

### 4. Manually Correcting a Classification

If a video is misclassified, you can manually override the result.

1.  Open `classifier/extract_model.py`.
2.  Find the `VIDEO_ID_MAP` dictionary.
3.  Add an entry with the video's 11-character YouTube ID and the correct model name.

**Example:**
```python
VIDEO_ID_MAP = {
    # format: "video_id": ("correct_model", "manual")
    "7J1MdAHxLdc": ("KR2201-4", "manual"),
}
```

### 5. Viewing the Results

The final results are visualized in a dashboard. Simply open the HTML file in a browser to view it.

```
reports/dashboard.html
```
