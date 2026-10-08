import os
import re
import json
import requests
from bs4 import BeautifulSoup

URL = "https://www.sastra.edu/hrpolicy/"
DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "chunks.json")

def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()

def build_chunks():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    
    sections = soup.find_all("details")
    print(f" Found {len(sections)} sections")
    
    heading_pattern = re.compile(r"^\s*(\d+(\.\d+)+)\s*(.*)")
    
    all_chunks = []
    
    for sec_idx, sec in enumerate(sections, start=1):
        summary = sec.find("summary")
        sec_title = clean_text(summary.get_text()) if summary else f"Section {sec_idx}"
        
        # Check if this section has numbered subsections (like Section 10 does)
        bold_tags = sec.find_all(["strong", "b"])
        has_subsections = any(heading_pattern.match(clean_text(b.get_text())) for b in bold_tags)
        
        if not has_subsections:
            paragraphs = []
            for tag in sec.find_all(["p", "li"]):
                text = clean_text(tag.get_text())
                if text:
                    prefix = "- " if tag.name == "li" else ""
                    paragraphs.append(prefix + text)
                    
            # Combine into chunks of max ~1000 characters
            combined_text = "\n".join(paragraphs)
            all_chunks.append({
                "id": f"sec_{sec_idx}",
                "section_number": sec_idx,
                "section_title": sec_title,
                "full_heading": sec_title,
                "content": combined_text,
                "char_count": len(combined_text)
            })
        else:
            curr_code = None
            curr_title = None
            curr_lines = []
            
            def save_current_subsection():
                if curr_lines:
                    content_str = "\n".join(curr_lines)
                    heading_str = f"{sec_title} > {curr_code} {curr_title or ''}".strip()
                    code_id = curr_code.replace(".", "_") if curr_code else "intro"
                    all_chunks.append({
                        "id": f"sec_{sec_idx}_{code_id}",
                        "section_number": sec_idx,
                        "section_title": sec_title,
                        "subsection_code": curr_code,
                        "subsection_title": curr_title,
                        "full_heading": heading_str,
                        "content": content_str,
                        "char_count": len(content_str)
                    })
            
            # Iterate through all paragraph and list elements
            for el in sec.find_all(["p", "li"]):
                text = clean_text(el.get_text())
                if not text:
                    continue
                
                # Check if this element starts a new subsection
                strong = el.find(["strong", "b"])
                if strong:
                    st_text = clean_text(strong.get_text())
                    match = heading_pattern.match(st_text)
                    if match:
                        # Save the previous subsection chunk before starting a new one
                        save_current_subsection()
                        curr_lines = []
                        curr_code = match.group(1)
                        curr_title = clean_text(match.group(3))
                        
                        # Add remaining text after the bold title if any
                        remainder = clean_text(text.replace(st_text, "", 1))
                        if remainder:
                            prefix = "- " if el.name == "li" else ""
                            curr_lines.append(prefix + remainder)
                        continue
                
                prefix = "- " if el.name == "li" else ""
                curr_lines.append(prefix + text)
                
            # Don't forget to save the last subsection
            save_current_subsection()
            
    # Create the data folder if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Save to JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
        
    print(f"\n3. SUCCESS! Saved {len(all_chunks)} chunks to {OUTPUT_FILE}")

if __name__ == "__main__":
    build_chunks()