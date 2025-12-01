import requests
import json
import time

# CONFIGURATION
BaseUrl = "http://localhost:8000"
Endpoints = {
    "chat": "/chat",
    "extract": "/extract"
}

# HARDCODED TEST CASES (AS REQUIRED BY ASSIGNMENT PART 4)
TestCases = [
    {
        "intent": "chat",
        "query": "What is the fire rating for corridor partitions?",
        "expected_check": "len_answer" 
    },
    {
        "intent": "chat",
        "query": "What is the flooring material in the lobby?",
        "expected_check": "has_sources"
    },
    {
        "intent": "extract",
        "query": "Generate a door schedule",
        "expected_check": "is_json_array"
    },
    {
        "intent": "chat",
        "query": "Who is the architect?",
        "expected_check": "len_answer"
    }
]

def RunEvaluation():
    print("========================================")
    print("   PROJECT BRAIN - AUTOMATED EVALUATION")
    print("========================================")
    print(f"Target API: {BaseUrl}\n")

    PassCount = 0
    FailCount = 0

    for i, Test in enumerate(TestCases):
        print(f"TEST #{i+1}: [{Test['intent'].upper()}] '{Test['query']}'")
        
        # PREPARE PAYLOAD (STANDARD 'message' KEY)
        Payload = {"message": Test['query']}
        Url = f"{BaseUrl}{Endpoints[Test['intent']]}"
        
        StartTs = time.time()
        try:
            # SEND REQUEST
            Resp = requests.post(Url, json=Payload)
            Duration = round(time.time() - StartTs, 2)
            
            if Resp.status_code != 200:
                print(f"   -> FAIL (Status {Resp.status_code})")
                FailCount += 1
                continue

            Data = Resp.json()
            Success = False
            Note = ""

            # HEURISTIC CHECKS
            if Test['intent'] == 'extract':
                # CHECK IF DATA IS A LIST AND NOT EMPTY
                Rows = Data.get("data", [])
                if isinstance(Rows, list) and len(Rows) > 0:
                    Success = True
                    Note = f"Extracted {len(Rows)} rows."
                else:
                    Note = "Returned empty data."

            elif Test['intent'] == 'chat':
                # CHECK IF ANSWER EXISTS AND IS NOT EMPTY
                Ans = Data.get("answer", "")
                Srcs = Data.get("sources", [])
                
                if Test['expected_check'] == "has_sources":
                    Success = len(Srcs) > 0
                    Note = f"Found {len(Srcs)} sources."
                else:
                    Success = len(Ans) > 10
                    Note = "Answer length > 10 chars."

            # PRINT RESULT
            if Success:
                print(f"   -> PASS ({Duration}s) - {Note}")
                PassCount += 1
            else:
                print(f"   -> FAIL ({Duration}s) - Logic check failed. {Note}")
                FailCount += 1

        except Exception as e:
            print(f"   -> CRITICAL ERROR: {e}")
            FailCount += 1
        
        print("-" * 40)

    print(f"\nSUMMARY: {PassCount} PASSED | {FailCount} FAILED")
    print("========================================")

if __name__ == "__main__":
    RunEvaluation()