# html-parsing-project
Replica of a Python code that I wrote for my previous employer to parse an html file and extract content with specific characteristics.

Project goal: Python 3.x code that reads an HTML file, looks for key strings and writes the strings to a CSV file. 

- Open html file, “terminology.html.”
- Search for terminology words, defined by specified colour codes, and their accompanying definition, example(s), and/or usage strings. 
- Output to a “terminology.csv” file with the headers, “Term”, “Definition”, “Example(s)”, and “Usage”.


20230515 
- First version of my recreated parser. 
- Poor error handling on unexpected string patterns.

20230516
- Corrections and much improved error handling. The code no longer crashes on sample HTML... successful .csv conversion.
- Corrected this pattern:
<span style="color: rgb(0,0,255);"><strong>1%</stong>
Followed by any strings with "Definition:" (ending with </span>, "Example(s)" (ending with </span>, and "Usage:" (ending with </span>)
- Ignore other unexpected strings.
- Omit "&nbsp" and "<span>" when saving the string pattern to the csv.

Future issues to improve?
- All content must be inside a main <div>
- String patterns hard coded. 
