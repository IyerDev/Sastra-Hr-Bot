import requests 
from bs4 import BeautifulSoup

URL = "https://www.sastra.edu/hrpolicy/"

def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(URL,header=headers, timeout=15)
    print(f"Status Code: {response.status_code}")

    soup=BeautifulSoup(response.text, "html.parser")

    page_title=soup.title.string.strip() if soup.title else "No title Found"
    print(f"Page Title : {page_title}")

    sections = soup.find_all("details")
    
    for i,sec in enumerate(sections,1):
        summary=sec.find("summary")
        title=summary.text.strip() if summary else "No summary"
        print(f"{title}")

if __name__ == "__main__":
    fetch_data()