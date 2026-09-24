import json
import urllib.request
import subprocess

def deploy_rules():
    token = subprocess.check_output(["gcloud", "auth", "print-access-token"]).decode("utf-8").strip()
    project_id = "qwiklabs-gcp-02-e73129932fd9"
    
    rules_content = """rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}"""

    # 1. Create Ruleset
    url_ruleset = f"https://firebaserules.googleapis.com/v1/projects/{project_id}/rulesets"
    body_ruleset = {
        "source": {
            "files": [
                {
                    "name": "firestore.rules",
                    "content": rules_content
                }
            ]
        }
    }
    
    req = urllib.request.Request(url_ruleset, data=json.dumps(body_ruleset).encode('utf-8'), headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            ruleset_name = res["name"]
            print("Created ruleset:", ruleset_name)
    except Exception as e:
        print("Failed creating ruleset:", e)
        return

    # 2. Release Ruleset to cloud.firestore
    url_release = f"https://firebaserules.googleapis.com/v1/projects/{project_id}/releases/cloud.firestore"
    body_release = {
        "name": f"projects/{project_id}/releases/cloud.firestore",
        "rulesetName": ruleset_name
    }
    
    req_patch = urllib.request.Request(url_release, data=json.dumps(body_release).encode('utf-8'), method='PATCH', headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    
    try:
        with urllib.request.urlopen(req_patch) as response:
            res = json.loads(response.read().decode('utf-8'))
            print("Updated Firestore release:", res)
    except Exception as e:
        print("Failed patching release, trying PUT/POST...", e)
        req_put = urllib.request.Request(f"https://firebaserules.googleapis.com/v1/projects/{project_id}/releases", data=json.dumps(body_release).encode('utf-8'), headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })
        with urllib.request.urlopen(req_put) as response:
            res = json.loads(response.read().decode('utf-8'))
            print("Created release:", res)

if __name__ == "__main__":
    deploy_rules()
