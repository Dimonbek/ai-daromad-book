import docx
import sys
import os

# Set output to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def extract_text(file_path):
    doc = docx.Document(file_path)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText).strip()

files = ["AI_Daromad_Kirish.docx", "AI_Daromad_Bob1.docx", "AI_Daromad_Bob2.docx"]
downloads = "C:\\Users\\Lenovo\\Downloads"

for f in files:
    path = os.path.join(downloads, f)
    if os.path.exists(path):
        print(f"--- {f} ---")
        text = extract_text(path)
        print(text if text else "[Empty File]")
        print("\n" + "="*50 + "\n")
    else:
        print(f"File {f} not found.")
