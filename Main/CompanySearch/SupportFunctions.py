import re
import os

import requests
import pandas as pd
import numpy as np

from googlesearch import search
from validate_email import validate_email
from bs4 import BeautifulSoup

#base_path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
base_path = os.path.realpath(os.path.dirname(__file__))
# ------------------------------ updating of new company information from brreg file --------------------------------------

def generate_new_data(path_full_csv = os.path.join(base_path, "./data/alle_enheter.csv")):
    all = pd.read_csv(path_full_csv).replace(np.NaN, None)
    grouped = all.groupby(all.navn.str[0])
    for group in grouped:
        pd.DataFrame(group[1], columns=["organisasjonsnummer","navn"]).to_csv(f"./data/{ord(group[0].lower())}.csv", index=False)
    



# ------------------------------------ Checking and returning org nr --------------------------------------
def get_org_nr(value):
    value = str(value)
    if len(value) == 9:
        try:
            org_nr = int(value)
            return org_nr
        except ValueError:
            pass
    else:
        org_df = pd.read_csv(os.path.join(base_path, f"./data/{ord(value[0].lower())}.csv"))
        try:
            return int(org_df[org_df["navn"] == value.upper()].iat[0,0])
        except IndexError:
            pass
    return None
    


# ------------------------------------ Request information from brreg --------------------------------------
def get_brreg_info(org_nr):
    brreg_url = f"https://data.brreg.no/enhetsregisteret/api/enheter/{org_nr}"
    brreg_request = requests.get(brreg_url).json()
    if "feilmelding" not in brreg_request:

        return {"org_nr" : brreg_request["organisasjonsnummer"],
                "org_navn" : brreg_request["navn"],
                "org_form_beskrivelse" : brreg_request["organisasjonsform"]["beskrivelse"],
                "org_form_kode" : brreg_request["organisasjonsform"]["kode"],
                "forretningsadresse" : brreg_request["forretningsadresse"],
                "registreringsdatoEnhetsregisteret" : brreg_request["registreringsdatoEnhetsregisteret"],
                "registrertIMvaregisteret" : brreg_request["registrertIMvaregisteret"],
                "antallAnsatte" : brreg_request["antallAnsatte"],
                "registreringsdatoEnhetsregisteret" : brreg_request["registreringsdatoEnhetsregisteret"],
                "underAvvikling" : brreg_request["underAvvikling"],
                "underTvangsavviklingEllerTvangsopplosning" : brreg_request["underTvangsavviklingEllerTvangsopplosning"]}
    return None




# ------------------------------------ Format Company name --------------------------------------
def format_company_name(brreg_info):
    name_formats = {}
    name_formats["original_name"] = brreg_info["org_navn"]
    name_formats["clean_name"] = brreg_info["org_navn"].replace(" KONKURSBO","").replace(" AS","").replace(" SA","").replace(" DA","").replace(" ASA","")

    if len(name_formats["original_name"].split(" ")) == 2:
        name_formats["split_name"] = name_formats["original_name"].split(" ")
        return name_formats
    else:
        name_formats["split_name"] = None
        return name_formats



# ------------------------------------ Generate Suggested Emails --------------------------------------
def generate_suggested_emails(formatted_names):
    # Split email to attempt emails such as name@lastname.no
    company_name = formatted_names["clean_name"].replace(" ","").lower()
    first_name = ""
    last_name = ""
    if formatted_names["split_name"]:
        first_name = formatted_names["split_name"][0].lower()
        last_name = formatted_names["split_name"][1].lower()

    # Check emails including company name
    email_prefix = ["post", "kontakt", "faktura"]
    email_suffix = ["no","com"]
    email_hosts = ["hotmail", "gmail"]

    # Loop over prefix, suffix and host and generate email list of possible emails.
    generated_email_list = []
    for prefix in email_prefix:
        for suffix in email_suffix:
            for host in email_hosts:
                # Format: prefix@firstnamelastname.suffix
                generated_email_list.append(f'{prefix}@{company_name}.{suffix}')

                # Format: firstlast@host.suffix
                generated_email_list.append(f'{company_name}@{host}.{suffix}')
                
                # Format: first.last@host.suffix
                if first_name != "" and last_name != "":
                    generated_email_list.append(f'{first_name}.{last_name}@{host}.{suffix}')
    return list(set(generated_email_list))



# ------------------------------------ Validate Emails --------------------------------------
def check_emails(email_list):
    valid_emails = []
    for email in email_list:
        if validate_email(email):
            valid_emails.append(email)
    return valid_emails
        


# ----------------------------- Use google to gather external info --------------------------------------
def get_external_info(clean_name):
    g_search = next(search(f"{clean_name} contact", num_results=1))
    req = requests.get(g_search, headers={"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
    soup = BeautifulSoup(req.text, 'html.parser')
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    # Return webiste, list of emails and response code
    return {"website":g_search, "emails": list(set(re.findall(email_pattern, soup.get_text()))), "restricted": False if req.status_code == 200 else True}





#generate_new_data()