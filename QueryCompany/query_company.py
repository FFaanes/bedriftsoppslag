from googlesearch import search
from validate_email import validate_email
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import numpy as np

def clean_csv(file_path, save_path):
    # Used to split up brreg data into 4 files to reduce size and increase speed.
    brreg_file = pd.read_csv(file_path)
    brreg_1 = pd.DataFrame(brreg_file.iloc[0:250_000])
    brreg_2 = pd.DataFrame(brreg_file.iloc[250_000:500_000])
    brreg_3 = pd.DataFrame(brreg_file.iloc[500_000:750_000])
    brreg_4 = pd.DataFrame(brreg_file.iloc[750_000:])

    pd.DataFrame({"organisasjonsnummer" : brreg_1["organisasjonsnummer"], "navn" : brreg_1["navn"]}, columns=["organisasjonsnummer","navn"]).to_csv(f"{save_path}0", index=False)
    pd.DataFrame({"organisasjonsnummer" : brreg_2["organisasjonsnummer"], "navn" : brreg_2["navn"]}, columns=["organisasjonsnummer","navn"]).to_csv(f"{save_path}1", index=False)
    pd.DataFrame({"organisasjonsnummer" : brreg_3["organisasjonsnummer"], "navn" : brreg_3["navn"]}, columns=["organisasjonsnummer","navn"]).to_csv(f"{save_path}2", index=False)
    pd.DataFrame({"organisasjonsnummer" : brreg_4["organisasjonsnummer"], "navn" : brreg_4["navn"]}, columns=["organisasjonsnummer","navn"]).to_csv(f"{save_path}3", index=False)
    print(f"Reducing Complete, split into 4 files. in {save_path}")




def get_company_name(organisation_number):
    url = f"https://data.brreg.no/enhetsregisteret/api/enheter/{int(str(organisation_number).replace(' ',''))}"
    org_request = requests.get(url).json()
    org_navn = org_request["navn"]
    return org_navn

def get_external_info(company_name):
    try:
        # Perform a Google search for the company name
        company_name = company_name.lower().replace("as", "").strip() # Remove AS
        company_name = company_name.lower().replace("sa", "").strip() # Remove SA
        companyname_stripped = str(company_name).replace(" ", "")
        query = f"{company_name} contact"
        search_results = search(query, num_results=1)
        website = next(search_results)

        # Attempt to find email in homepage
        response = requests.get(website, headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
        soup = BeautifulSoup(response.text, 'html.parser')

        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, soup.get_text())

        # Check if company name is in the url
        if companyname_stripped in website:
            company_name_in_url = True
        else:
            company_name_in_url = False

        # Check if there are none emails
        companyname_in_email = False
        if len(emails) == 0:
            emails = []
        else:
            emails = list(set(emails)) # Remove duplicates from email list

            # Check if company name is within the email
            for email in emails:
                if companyname_stripped in email:
                    companyname_in_email = True
        
        # Check other emails including company name
        email_prefix = ["post", "kontakt", "faktura"]
        email_suffix = ["no","com"]
        email_hosts = ["hotmail", "gmail"]

        # Split email to attempt emails such as name@lastname.no
        company_name_split = company_name.split(" ")
        first_name = ""
        last_name = ""
        if len(company_name_split) == 2:
            first_name = company_name_split[0]
            last_name = company_name_split[1]

        # Loop over prefix, suffix and host and generate email list of possible emails.
        generated_email_list = []
        for prefix in email_prefix:
            for suffix in email_suffix:
                for host in email_hosts:
                    # Format: prefix@firstnamelastname.suffix
                    current_email_adress = f'{prefix}@{companyname_stripped}.{suffix}'
                    generated_email_list.append(current_email_adress)

                    # Format: firstlast@host.suffix
                    current_email_adress = f'{companyname_stripped}@{host}.{suffix}'
                    generated_email_list.append(current_email_adress)
                    
                    # Format: first.last@host.suffix
                    if first_name != "" and last_name != "":
                        current_email_adress = f'{first_name}.{last_name}@{host}.{suffix}'
                        generated_email_list.append(current_email_adress)
        generated_email_list = list(set(generated_email_list))

        # Loop over generated emails to check if they exist.
        validate_emails = False
        if validate_emails == True:
            for email in generated_email_list:
                if validate_email(email) == True:
                    emails.append(email)


        # Remove unwanted emails:
        try:
            unwanted_emails = ["kundeservice@1881.no"]
            for email in unwanted_emails:
                print(f"Popped: {email}")
                emails.remove(email)
        except:
            pass
        
        # Website url only valid if it is not longer than x letters
        if len(str(website)) > 80:
            website = None

        # Check if the request is restricted
        request_restricted = False if response.status_code == 200 else True

        return {"website" : website,
                "valid_emails" : emails,
                "potential_emails": generated_email_list,
                "company_name_in_url" : company_name_in_url,
                "company_name_in_email" : companyname_in_email,
                "request_restricted" : request_restricted}
    except Exception as e:
        print(e)
        return {"website" : None,
                "valid_emails" : None,
                "potential_emails": None,
                "company_name_in_url" : None,
                "company_name_in_email" : None,
                "request_restricted" : None}




# Main function
def query_company(name_or_number):
    try:
        try:
            name_or_number_strip = name_or_number.replace(" ","")
            number_check = int(name_or_number_strip) # Will return Valueerror if it contains letters

            if len(name_or_number_strip) == 9:
                org_nr = int(name_or_number_strip)
                external_info = get_external_info(get_company_name(org_nr))
                print("Found by number.")


        except ValueError:
            # Load csv and search for organisation number
            csv_files_path = os.listdir("./data")

            for csv_path in csv_files_path:
                brreg_file = pd.read_csv(f"./data/{csv_path}")
                search_result = brreg_file[brreg_file["navn"] == name_or_number.upper()]
                try:
                    org_nr = int(search_result.iat[0,0])
                    if len(org_nr) == 9:
                        print(f"Found org_nr in file: {csv_path}")
                        break
                except:
                    pass
                
            external_info = get_external_info(get_company_name(org_nr))
            print("Found by name.")
    
        brreg_url = f"https://data.brreg.no/enhetsregisteret/api/enheter/{org_nr}"
        brreg_request = requests.get(brreg_url).json()

        company_information = {"info" :{"org_nr" : brreg_request["organisasjonsnummer"],
                                        "org_navn" : brreg_request["navn"],
                                        "org_form" : brreg_request["organisasjonsform"]["kode"],
                                        "forretningsadresse" : brreg_request["forretningsadresse"],
                                        "registreringsdatoEnhetsregisteret" : brreg_request["registreringsdatoEnhetsregisteret"],
                                        "registrertIMvaregisteret" : brreg_request["registrertIMvaregisteret"],
                                        "antallAnsatte" : brreg_request["antallAnsatte"],
                                        "registreringsdatoEnhetsregisteret" : brreg_request["registreringsdatoEnhetsregisteret"],
                                        "underAvvikling" : brreg_request["underAvvikling"],
                                        "underTvangsavviklingEllerTvangsopplosning" : brreg_request["underTvangsavviklingEllerTvangsopplosning"]},

                            "external_info" : external_info}
        return company_information
    

    except Exception as e:
        print(f"Something went wrong.\n{e}")
        return None



org_nr = "Frostahallen SA"
print(query_company(org_nr))

#clean_csv("./data/brreg.csv","./data/clean_brreg.csv")



