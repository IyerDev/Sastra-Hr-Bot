import requests
from bs4 import BeautifulSoup

URL = "https://www.sastra.edu/hrpolicy/" 

def inspect_sec():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response= requests.get(URL,headers=headers)
    soup=BeautifulSoup(response.text ,"html.parser")

    sections=soup.find_all("details")
    target_sec= None 
    for sec in sections:
        summary=sec.find("summary")
        if summary and "Types of Leave" in summary.get_text():
            target_sec=sec
            break
    print("Section not found") if not target_sec else print("Section :")
    summary_tg=target_sec.find("summary").get_text(strip=True)

    print(f"{summary_tg}")

    bold_tags = target_sec.find_all(["strong","b"])
    print(f"Subheadings : {len(bold_tags)}")
    for b in bold_tags:
        text = b.get_text(strip=True)
        print(text) if text else print("")
        
if __name__=="__main__":
    inspect_sec()