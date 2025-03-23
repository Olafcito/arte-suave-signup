import os
import json
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup, Comment
import tiktoken
from openai import OpenAI
import yaml
from datetime import datetime, timedelta

load_dotenv()

def load_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)
    
class WebsiteClient:
    def __init__(self, base_url: str):
        self.session = requests.Session()
        self.base_url = base_url
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        })

    def get(self, endpoint: str, params: dict = None) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        return self.session.get(url, params=params, allow_redirects=True)

    def post(self, endpoint: str, data: dict = None, is_json: bool = True) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        if is_json:
            return self.session.post(url, json=data, allow_redirects=True)
        return self.session.post(url, data=data, allow_redirects=True)

    def login(self, login_url: str, credentials: dict) -> requests.Response:
        # Prime cookies by performing a GET first
        self.get(login_url)
        return self.post(login_url, data=credentials, is_json=False)

def clean_html(html: str) -> str:
    """Remove script, style tags and comments, preserving the rest of the HTML structure."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    return str(soup)

def get_token_length(text: str, model: str) -> int:
    """Return the token length of the given text using tiktoken."""
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def extract_classes_with_openai(classes_list: list, html_content: str, model: str) -> dict:
    """
    Use OpenAI's API to extract class parameters.
    The system prompt defines the expected JSON structure.
    """
    system_prompt = """
You are given a list of classes that I want you to extract.
Each class name is the key of the dict, and the value is a dictionary with keys: 'Show', 'action', 'WorkScheduleID', and 'StartDate'.
Example:
{
    "ClassName": {
        "Show": "ShowProfile",
        "action": "SignUpforclasses",
        "WorkScheduleID": "32858", 
        "StartDate": "2025-03-24"
    }
}
"""
    user_prompt = f"Please locate the following classes: {classes_list} in the provided HTML and generate the JSON. Do not include any extra text.\nHTML:\n{html_content}"
    
    client = OpenAI()
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model=model
    )
    result_text = response.choices[0].message.content
    try:
        result_dict = json.loads(result_text)
    except json.JSONDecodeError:
        raise ValueError("OpenAI response is not valid JSON")
    return result_dict

def sign_up_for_classes(client: WebsiteClient, classes_data: dict):
    """For each class entry, execute a GET request with the extracted parameters."""
    for class_name, params in classes_data.items():
        response = client.get(
            "/Account",
            params={
                "Show": params.get("Show"),
                "action": params.get("action"),
                "WorkScheduleID": params.get("WorkScheduleID"),
                "StartDate": params.get("StartDate")
            }
        )
        status = "Success" if response.ok else f"Failure (Status: {response.status_code})"
        print(f"{class_name} - {status}")

def next_tuesday():
    today = datetime.now() + timedelta(hours=1)  # GMT+1
    days_ahead = 1 - today.weekday()  
    if days_ahead <= 0: 
        days_ahead += 7  
    next_tuesday = today + timedelta(days=days_ahead)
    return next_tuesday.date().isoformat()

def main():
    # conf
    credentials = {
        'email': os.getenv('WEBSITE_USERNAME'),
        'password': os.getenv('WEBSITE_PASSWORD')
    }
    base_url = os.getenv('WEBSITE_URL')

    config = load_config()
    model = config['openai']['model']
    classes_list = config["classes"]


    login_endpoint = '?Show=CheckLogIn&AccountID=1'
    
    client = WebsiteClient(base_url)
    login_response = client.login(login_endpoint, credentials)
    if not login_response.ok:
        print("Login failed")
        return

    sign_up_endpoint = "/Account"
    sign_up_params = {
        "Show": "ShowProfile",
        "action": "SignUpforclasses",
        "StartDate": next_tuesday()
    }
    html_response = client.get(sign_up_endpoint, params=sign_up_params)
    if not html_response.ok:
        print("Failed to fetch classes page")
        return
    raw_html = html_response.content.decode('utf-8')
    cleaned_html = clean_html(raw_html)


    token_length = get_token_length(cleaned_html, model)
    print(f"Token length of cleaned HTML: {token_length}")
    

    classes_data = extract_classes_with_openai(classes_list, cleaned_html, model=model)
    print("Extracted classes data:", json.dumps(classes_data, indent=4))

    sign_up_for_classes(client, classes_data)

if __name__ == "__main__":
    main()
