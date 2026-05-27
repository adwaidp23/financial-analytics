import pypdf
import sys

reader = pypdf.PdfReader(r"d:\workspace\Financial_Analythics\MCA_FA_Capstone_Project.pdf")
text = "".join([page.extract_text() for page in reader.pages])

with open(r"d:\workspace\Financial_Analythics\MCA_FA_Capstone_Project.txt", "w", encoding="utf-8") as f:
    f.write(text)
