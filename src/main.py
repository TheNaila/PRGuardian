import os
import azure.functions as func
import logging
import os

from .integration import run_pr_audit

app = func.FunctionApp()

@app.route(route="webhook", methods=["POST"])
def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.info('GitHub Webhook received.')

    try:
        # 1. Get the PR data from the request
        payload = req.get_json()

        labels = [l["name"] for l in payload.get("pull_request", {}).get("labels", [])]
        
        TRIGGER_LABEL = "audit-requested" 
        if TRIGGER_LABEL not in labels: 
            return func.HttpResponse(f"Skipping: Label '{TRIGGER_LABEL}' not found.", status_code=200)
        # 2. Call your existing AI logic here
        run_pr_audit(
            payload["repository"]["full_name"],
            pr_number=int(payload["number"]),
        )
    
        
        return func.HttpResponse("PRGuardian is auditing...", status_code=200)
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

 

   


if __name__ == "__main__":
    main()