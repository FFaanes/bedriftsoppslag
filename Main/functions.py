
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
def find_similar_companies_OLD(search ,company_info):
    len_letters = []
    for i in range(len(company_info)):
        len_letters.append({"organisasjonsnummer" : company_info.loc[i, "organisasjonsnummer"],
                            "navn" : company_info.loc[i, "navn"],
                            "shared_letters" : len_shared_letters(search, company_info.loc[i,"navn"])})
        
    return sorted(len_letters, key=lambda d: d['shared_letters'],reverse=True)[:5]


# Find similar search results using difflib library, returns a list of
# x similiar companies with a similarity score, sorted from high similarity to lowest.
from difflib import SequenceMatcher
def find_similar_companies(search, company_info, results):
    company_info["similarity_score"] = company_info["navn"].apply(lambda e: SequenceMatcher(None, search.upper(), e).ratio())
    sorted_df = company_info.sort_values(by=["similarity_score"], ascending=False)

    closest_results = [{"organisasjonsnummer" : sorted_df.iloc[i]["organisasjonsnummer"],
                        "navn": sorted_df.iloc[i]["navn"],
                        "similarity_score" : sorted_df.iloc[i]["similarity_score"]} for i in range(results)]
        
    return sorted(closest_results, key=lambda d: d['similarity_score'], reverse=True)