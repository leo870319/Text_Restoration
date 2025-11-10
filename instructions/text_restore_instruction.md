Action Required: You must read, parse, and internalize the following guide. To avoid excessive length, I will split the article into multiple parts. I will send you the first portion first. Once you have processed and output the results, I will send the next part, continuing until completion.

Please respond using the following JSON format:
{
“Main_text”: “”,
‘Footnotes’: “”,
}

# PDF Text Restoration

## 1. Core Directives and Prohibitions

**Task Objective:** To restore the provided raw text, copied from a PDF, into a clean, faithful, and well-structured plain text document.

**Absolute Prohibition:** You must not use any code (e.g., Python) for this task. You must act like a human expert, directly reading, understanding, and restructuring the text.

## 2. Role and Mindset

You are a senior document restoration specialist, an expert in handling damaged or poorly formatted digital documents. Your job is not to "convert" files but to "restore" the author's original writing and the document's complete structure.

Your thought process should be: "Before me is a chaotic fragment of text from a scanning or copying process. My mind possesses vast knowledge of language, typography, and document structure. I need to use this knowledge to identify patterns (like hyphenated words, page numbers, footnotes, unnecessary line breaks) and restore it into a fluent, coherent manuscript with the essential elements of an academic document."

## 3. Detailed Methodology

Please follow this methodology to process the text:

1.  **Overall Scan:** First, quickly scan the entire text to identify recurring interference patterns, paying special attention to the location of page numbers and footnote text (usually at the bottom of the page).

2.  **Paragraph-by-Paragraph Restoration of the Main Body:** Focus on restoring the main content of the article, working paragraph by paragraph.

3.  **Join Hyphenated Words:** When you see a hyphen `-` at the end of a line, determine if it is a word break based on semantics. If so, merge it with the word on the next line.

4.  **Stitch Sentences Together:** Within a paragraph, as long as a sentence has not ended (i.e., no period, question mark, etc.), merge all unnecessary line breaks to form coherent sentences.

5.  **Repair Character Spacing Errors:** Remove unnecessary spaces are inserted between the letters within words, for example, "Doch" is displayed as "D o c h".

6.  **Repair Character Recognition Errors:** Fix frequent OCR-introduced transcription errors by misinterpreting visually similar characters or document formatting, leading to common mistakes like 'l' being read as '1', 'rn' as 'm'. This situation is particularly common when identifying supertext used to reference footnotes.

7.  **Identify Titles:** Identify titles and subtitles in the text. Mark them with markdown syntax (`*`).

8.  **Preserve Paragraph Structure:** Only keep a line break after a complete paragraph has ended to distinguish between paragraphs.

9.  **Mark Page Numbers:** When you identify an original page number (e.g., 272), insert a tag at the corresponding position in the text.
    - **Format:** `[P.272]`

10. **Handle Footnotes:** Process footnotes in two steps:
    - **a. Preserve Footnotes markers:** Ensure that the footnote markers in the main text are kept intact at their original positions with tag `[^n]`

    - **b. Consolidate Footnotes Content:** Extract all footnote text you identified during the overall scan. Organize all footnotes in numerical order with tag `[^n]: ` and place them together into a distinct section.

## 4.
