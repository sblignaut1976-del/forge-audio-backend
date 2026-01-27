import json
import requests

def get_uvr_models():
    # audio-separator often fetches from this JSON
    url = "https://raw.githubusercontent.com/Anjok07/ultimatevocalremovergui/master/gui_data/mdx_model_data.json"
    try:
        response = requests.get(url)
        data = response.json()
        print("MDX Models found:")
        for model in data:
            if 'guitar' in model.lower():
                print(f"- {model}")
    except Exception as e:
        print(f"Error fetching: {e}")

if __name__ == "__main__":
    get_uvr_models()
