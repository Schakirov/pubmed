# PubMed Article Sorting by User Preferences

This repository contains a Python script that allows users to download articles from PubMed and rank them based on user-defined preferences, such as keywords, authors, and journals of interest. **The output is an HTML file** that displays the most relevant articles.

---

## Features

- **Customizable Ranking**:
  - Assign positive or negative weights to keywords, authors, and journals.
  - Includes support for regular expressions and advanced ranking criteria (e.g., thresholds and maximum scores).

- **HTML Output**:
  - Generates a user-friendly HTML file (`pubmed-summary.html`) with ranked articles.
  - Highlights relevant keywords, authors, and journals with color-coded tags.

---

## Prerequisites

- **Python Version**: Python 3.6 or higher.
- **Dependencies**: Install the required library with:
  '''bash
  pip install pymed
  '''

---

## Usage

### 1. Edit Preferences

Open the `analyze.py` file and update the parameters in the first few lines:

- **Keywords**:
  - `good_keywords`, `bad_keywords`: Assign scores to keywords based on their importance. Keywords are case-insensitive. Number of occurences doesn't influence the points.
  - `good_keywords_thresh`: Assign scores only if a keyword appears a specified number of times.

- **Authors**:
  - `good_authors`: Prioritize articles by specific authors. +10 points for each author. Usually, it means these articles are in the start of the list.

- **Journals**:
  - `good_journals`: Keywords to prioritize specific journals.
  - `good_journals_strict`: Exact matches for journal names.
  - `bad_journals`: Keywords to deprioritize specific journals.

- **Output Control**:
  - `nArticlesInHtml`: Limits the number of articles in the final HTML file, 5000 by default.

### 2. Run Script

To process articles for a specific day:
```bash
python analyze.py "YYYY-MM-DD"
```

To process articles from a range of dates:
```bash
python analyze.py "YYYY-MM-DD" "YYYY-MM-DD"
```

---

## Example Output

The generated `pubmed-summary.html` includes:

1. **Article ID**:
   - Links to the PubMed entry for each article.

2. **Journal Name and Date**:
   - Displays the name of the journal and the publication date.

3. **Relevance Score**:
   - Indicates the article's score based on your preferences.

4. **Title and Abstract**:
   - Highlights relevant keywords, authors, and journals in color-coded text.

---

## Notes

1. **PubMed Data**:
   - PubMed continuously updates its data. When you query articles for recent days, it is recommended to rerun the script later to get the later updates. If you wish to update the data, you need first to delete the files corresponding to the renewed dates.

2. **Performance**:
   - The script processes around one year of articles in 3 minutes. Performance can be improved by optimizing the substring search in large abstracts.

3. **Custom Regular Expressions**:
   - Use the `re:` prefix in `good_keywords` to define regular expressions. For example:
     - `'re:gene therapy|genetic therapy'`: Matches either "gene therapy" or "genetic therapy."
     - `'re:(?<=[^a-zA-Z])aging(?=[^a-zA-Z])'`: Matches "aging" but not "imaging" or "averaging."

4. **PubMed Query Settings**:
   - Update `your_tool_name` and `your_email` in the script to follow PubMed API policy.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
