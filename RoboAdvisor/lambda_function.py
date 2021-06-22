### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")

def parse_float(n):
    """
    Securely converts a non-numeric value to float.
    """
    try:
        return float(n)
    except ValueError:
        return float("nan")


    
def portfolioRecommendation(investmentAmount,risklevel):
    investmentAmount = parse_float(investmentAmount)
    AGG = 0
    SPY = 0
    if risklevel == 'None':
        AGG = 1          
    elif risklevel == 'Very Low':
        AGG = 0.8
        SPY = 0.2        
    elif risklevel == 'Low':
        AGG = 0.6
        SPY = 0.4
    elif risklevel == 'Medium':
        AGG = 0.4
        SPY = 0.6
    elif risklevel == 'High':
        AGG = 0.2
        SPY = 0.8    
    elif risklevel == 'Very High':
        AGG = 0
        SPY = 1
        
    if risklevel == 'Very High':
        return f"{SPY * 100}% - ${investmentAmount} in Equity (SPY)"
    elif risklevel == 'None':
        return f"{AGG * 100}% - ${investmentAmount} in Bonds(AGG)"
    else:
        return f"{AGG * 100}% - ${round(AGG * investmentAmount,2)} in Bond (AGG) and {SPY * 100}% - ${round(SPY * investmentAmount,2)} in Equities (SPY)"
        
        

    
    
        

def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }

def validate_data(age,investment_amount):
    #Validating the age
    if age is not None:
        if age <=0 and age > 65:
            return build_validation_result(
            False,
            "Age",
            "The age should be less than 65",
            "Please provide a different age"
            )
    #validating the investment amount
    if investment_amount is not None:
        if investment_amount < 5000:
            return build_validation_result(
            "Investment Amount",
            "The amount should be greater than 5000",
            "Please provide a different amount")
        
    return build_validation_result(True,None,None)
        


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response


### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """

    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        # Perform basic validation on the supplied input slots.
        validation_result = validate_data(age,investment_amount)
        
        # Use the elicitSlot dialog action to re-prompt
        # for the first violation detected.
        
        if not validation_result["isValid"]:
            slots[validation_result["violatedSlot"]] = None
            
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validation_result["violatedSlot"],
                validation_result["message"],
            )

        # Fetch current session attibutes
        output_session_attributes = intent_request["sessionAttributes"]

        return delegate(output_session_attributes, get_slots(intent_request))

    # Get the initial investment recommendation
    
    initial_recommendation = portfolioRecommendation(investment_amount,risk_level)

    
    
    # Return a message with the initial recommendation based on the risk level.
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """{} thank you for your information;
            based on the risk level you defined, my recommendation is to choose an investment portfolio with {}
            """.format(
                first_name, initial_recommendation
            ),
        },
    )


### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "RecommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)
