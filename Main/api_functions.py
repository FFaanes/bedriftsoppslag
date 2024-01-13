from config import API_HOST, API_KEY
import requests
from CompanySearch.ComSearch import search_company

# Requests API server for company info or similar companies
# Will use backup solution if connection fails.
def api_request(route, value, validate_emails=False, google_search_results=1):
    try:
        validate_emails_bool = "true" if validate_emails == True else "false"
        company_info = requests.get(f"{API_HOST}{route}{value}", headers={"api-key":API_KEY,"validate-emails":validate_emails_bool}).json()
    except:
        company_info = search_company(value, validate_emails=validate_emails)
    return company_info


