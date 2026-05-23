import requests
import json

# Test the analyze endpoint
url = "http://localhost:8000/api/analyze"
data = {
    "business_type": "mini-mart",
    "sample_type": "mini-mart"
}

response = requests.post(url, data=data)
print("Status Code:", response.status_code)
print("\nResponse JSON:")
print(json.dumps(response.json(), indent=2))

# Check if metrics exist and what they contain
if response.status_code == 200:
    result = response.json()
    print("\n=== METRICS STRUCTURE ===")
    if "metrics" in result:
        for key, value in result["metrics"].items():
            print(f"\n{key}:")
            if isinstance(value, dict):
                print(f"  Type: dict with keys: {list(value.keys())}")
                if "value" in value:
                    print(f"  Value type: {type(value['value'])}")
                    if isinstance(value['value'], dict):
                        print(f"  Value keys: {list(value['value'].keys())}")
            else:
                print(f"  Type: {type(value)}")

# Made with Bob
