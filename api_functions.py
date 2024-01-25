from config import API_HOST, API_KEY
import requests
from OrgOppslag import search_company

# Requests API server for company info or similar companies
# Will use backup solution if connection fails.
def api_request(route, value, validate_emails=False, google_search_count=1, user="default"):
    try:
        validate_emails_bool = "true" if validate_emails == True else "false"
        company_info = requests.get(f"{API_HOST}{route}{value}", headers={"api-key" : API_KEY,
                                                                          "validate-emails" : validate_emails_bool,
                                                                          "google-search-count" : str(google_search_count),
                                                                          "current-user" : user}).json()
    except:
        print("using local")
        company_info = search_company(value, validate_emails = validate_emails, google_search_count = google_search_count)
    return company_info

def api_updatedata():
    requests.get(f"{API_HOST}/api/oppdaterdata", headers={"api-key" : API_KEY})
    return


def clear_api_cache():
    requests.get(f"{API_HOST}/api/clearcache", headers={"api-key" : API_KEY})
    return

def api_historymanager(mode):
    return requests.get(f"{API_HOST}/api/searchhistory", headers={"api-key" : API_KEY, "mode":mode}).json()

def api_searchcounts():
    return requests.get(f"{API_HOST}/api/searchcounts", headers={"api-key" : API_KEY}).json()