from .models import Interest, PageobjectInterest, Visit, Website, SecureAuth, Page, Profile, ProfileInterest, PageObject, ProfilePageobject, PageobjectLog 
from neomodel import (StructuredNode, StringProperty, IntegerProperty,
        RelationshipTo, RelationshipFrom)
from .models import PageN, WebsiteN, ProfileN

def UI_UU_mixed_filtering(base_uri, token, pageobjectIndex_tokens, itemIndex_distance):
    """ User_Item and User-User mixing Method
    Args:
        token (string): Profile Token
        base_uri(string): Website hostname
        pageobjectIndex_tokens(Dictionary<Integer,Array<tokens>>): Tokens for a pageobject
        itemIndex_distance(Integer,Float): given value for an index of the pageobject within the received list.
        
    Returns:
        Ordered array of recommended received clickables indexs
    """
    itemIndex_UU_Distance = {}
    # If neo4j wasn't accessible warn the User.
    error_flag = ""
    try: 
        pageobjectIndex_UUValues = {}
        for e in pageobjectIndex_tokens.keys():
            # Initialise the value of the User-User website based filtering
            uuweb_pageobject_val = 0.0
            # Retrieve Dictionary value corresponding visited the users webpage
            UU_w = UU_websites(token, base_uri)
            if(pageobjectIndex_tokens[e] == None):
                pageobjectIndex_UUValues[e] = 0.0
            else:
                # we add all the values retrieve from UU_websites
                for t in pageobjectIndex_tokens[e]:
                    if not UU_websites(token, base_uri).get(t) == None:
                        uuweb_pageobject_val = uuweb_pageobject_val + float(UU_w[t])
                pageobjectIndex_UUValues[e] = uuweb_pageobject_val

        for i in itemIndex_distance.keys():
            # As the Stronger the User-User value for one page object the more it should contribute
            # to a smaller itemIndex_value
            itemIndex_UU_Distance[i] = itemIndex_distance[i]*(1.0-pageobjectIndex_UUValues[i])
            # As the list might no longer be sorted we, sort the list once more
        # UI_UU base filtering.
        recommendation = itemIndex_UU_Distance
    except:
        # If the developer has not connected the neo4j server
        # We do not compromise minimum service.
        error_flag = 1
        recommendation = itemIndex_distance
    # Sorted list of distances
    sorted_index = sorted(recommendation, key=itemIndex_distance.get)
    sent_recommendation = []
    for item_index in sorted_index:
        if  item_index not in sent_recommendation:
            sent_recommendation.append(item_index)
    return (sent_recommendation, error_flag)

def UU_websites(token, base_uri):
    """ User-User Demographic based method
    
    Args:
        token (string): Profile Token
        base_uri(string): Web page href

    Returns:
        Dictionary {token: rank/(profile_number) }
    """
    # Array of tokens, values and Dictionary of the matching items.
    uu_tokens = []
    uu_vals = []
    UU_map = {}
    # Using the cypher query in ProfileN giving for each returing token a number of common websites
    matching_profile_website_query = ProfileN.nodes.get(token=token).get_tokens_from_common_Websites(page=base_uri)[0]
    # Number of profiles
    profile_numbers= len(matching_profile_website_query)
    # Converting to arrays so that we can hold indexs while applying a simple normalisation
    for o in matching_profile_website_query:
        tok = o[0].properties['token']
        nb = o[1]
        uu_tokens.append(tok)
        uu_vals.append(nb)

    # Normalising the array of values
    if(len(uu_vals) != 0):
        uu_vals = [uu_vals]
        uu_vals = normalize(uu_vals, axis=1)
        uu_vals = uu_vals[0]

    # Mapping a normalised and standardaised value
    for idx, token in enumerate(uu_tokens):
        # As it may be possible to have more than one profile for the same pageobject
        # To keep a normalised structure (value in the range of [0.0,1.0] )
        # WE devide by the number of existing profiles.
        tp = uu_vals[idx]*(1.0/float(profile_numbers))
        UU_map[token] = tp
    return UU_map
