
# Compare company name to name in dataframe to find len of shared letters
# Used to find closest search result.
def len_shared_letters(search, other):
    if len(other) > len(search) + 2 or len(other) < len(search) -2:
        return 0
    shared_letters = []
    for letter in search:
        other.replace(letter,"")
        if letter.upper() in str(other).upper():
            shared_letters.append(letter)
    return len(shared_letters)

# Uses shared letters to calculate how many letters each company shares
# This is then sorted with the top 5 companies that shares the most letters.
def find_similar_companies(search ,company_info):
    len_letters = []
    for i in range(len(company_info)):
        len_letters.append({"organisasjonsnummer" : company_info.loc[i, "organisasjonsnummer"],
                            "navn" : company_info.loc[i, "navn"],
                            "shared_letters" : len_shared_letters(search, company_info.loc[i,"navn"])})
        
    return sorted(len_letters, key=lambda d: d['shared_letters'],reverse=True)[:5]


