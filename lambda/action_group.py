import json

def lambda_handler(event, context):
    agent = event['agent']
    actionGroup = event['actionGroup']
    function = event['function']
    parameters = event.get('parameters', [])
    
    
    def Currency_clause():
        prompt = ''' Below are the Common Domain Model (CDM) json generation rules for the Clauses : Base Currency and Eligible Currency. When given a document (ISDA Master Agreement) and asked for CDM json output,strictly apply these rules to generate CDM json output.

<rules>
For the Clauses : Base Currency and Eligible Currency, identify one variant in each clause and produce the Common Domain Model JSON representation for the identified variant. 

Below are the Possible Variants with their example CDM json formats: 
Base Currency:
The base currency in ISDA is usually the United States Dollar (USD), unless otherwise specified.
1)Single Currency: Election of a single currency. 
<json format>
{
  "agreementTerms": {
    "agreement": {
      "creditSupportAgreementElections": {
        "baseAndEligibleCurrency": {
          "baseCurrency": "USD"
        }
      }
    }
  }
}
</json format>

2)Termination Currency: Determined by cross reference to the Termination Currency of the Agreement. 
<json format>
{
  "agreementTerms": {
    "agreement": {
      "creditSupportAgreementElections": {
        "baseAndEligibleCurrency": {
          "baseCurrency": "USD",
          "baseCurrencyTerminationCurrency": true
        }
      }
    }
  }
}
</json format>


Eligible Currency:
1)Base Currency is the only Eligible Currency: Collateral is only permitted in a single currency.

<json format>
{
  "agreementTerms": {
    "agreement": {
      "creditSupportAgreementElections": {
        "baseAndEligibleCurrency": {
          "eligibleCurrency": [
            "USD"
          ],
          "eligibleCurrencyInclBaseCurrency": true
        }
      }
    }
  }
}
</json format>

2)Multiple Eligible Currencies: Collateral is permitted in multiple currencies.
Note: Check carefully for multiple currencies. Do not include any currencies not present in the document. Also if the agreement mentions the same currency multiple times in terms of Treasuries, Securities, Certificates etc, specify that currency only once.
 


<json format>
{
  "agreementTerms": {
    "agreement": {
      "creditSupportAgreementElections": {
        "baseAndEligibleCurrency": {
          "eligibleCurrency": [
            "AED",
            "USD",
            "AFN"
          ],
           "eligibleCurrencyInclBaseCurrency": true
        }
      }
    }
  }
}
</json format>

3)Other Eligible Currency: Any variant not covered by the OtherEligible Currency variants. 
<json format>
{
  "agreementTerms": {
    "agreement": {
      "creditSupportAgreementElections": {
        "baseAndEligibleCurrency": {
          "eligibleCurrencyOther": {
            "value": ""
          }
      }
    }
  }
}
</json format>

*important instructions*: 
a) After concluding, Check again thoroughly for multiple currencies. 
b) Variant 2 (Multiple Eligible Currencies) requires specific currencies to be explicitly listed in the document.
c) Variant 3 (Other Eligible Currency) is used when the eligible currencies are not explicitly listed, but rather defined through some other criteria or left open for future agreement between the parties.
Follow variant 3 json format strictly.



These are the possible CDM fields with their descriptions: 
agreement (1..1): Specification of the standard set of terms that define a legal agreement. (0..1): Specification of the standard set of terms that define a legal agreement. 
baseAndEligibleCurrency (1..1): The base and eligible currency(ies) for the document as specified by the parties to the agreement. 
baseCurrency (1..1): The common agreed currency into which relevant amounts of all collateral arrangements between the parties are converted, or if not an actual currency, the process through which this is determined. Where hardcoded (e.g. under the 1994 ISDA Credit Support Annex (Security Interest NY Law)), the currency that effectively performs this function. [ISO currency code] baseCurrencyTerminationCurrency (1..1): A flag detailing whether the Base Currency is set to the Termination Currency as defined in the related Master Agreement. [boolean - true,false] baseCurrencyOther (0..1): Utilised where the clause data structure is not able to capture a material aspect of the clause. [string] 
eligibleCurrency (0..*): A definition of a currency agreed by the parties, typically to indicate the currencies of eligible cash collateral. [ISO currency code] 
eligibleCurrencyInclBaseCurrency (1..1): A flag detailing whether the Base Currency is included as an Eligible Currency. [boolean - true,false] 
eligibleCurrencyOther (0..1): Utilised where the clause data structure is not able to capture a material aspect of the clause. [string]

</rules>


'''
        
        return prompt


    
    def Rounding_clause():
        prompt = ''' Below are the Common Domain Model (CDM) json generation rules for the Clause: Rounding. When given a document (ISDA Master Agreement) and asked for CDM json output, strictly apply these rules to generate CDM json output.

<rules>
For the Clause: Rounding, identify a variant and produce the Common Domain Model JSON representation for the identified variant. 

Please make sure to thoroughly review the entire document, including all schedules and annexes, even if they appear after the main body of the agreement. Carefully read through each section and paragraph, paying close attention to the headings and subheadings to identify relevant clauses. Before providing your final response, double-check your findings and conclusions to ensure accuracy and completeness.

Below are the Possible Variants of the “Rounding” clause  with example CDM json formats: 
1) Delivery Amount Rounded Up / Return Amount Rounded Down: The Delivery Amount is Rounded Up and the Return Amount is Rounded Down to the nearest multiple of a Fixed Amount in all cases without any conditions.
<json format>
{
  "agreementTerms": {
    "agreement": {
      "creditSupportAgreementElections": {
        "creditSupportObligations": {
          "rounding": {
            "currency": "USD",
            "deliveryAmount": 1000,
            "deliveryDirection": "UP",
            "returnAmount": 2,
            "returnDirection": "DOWN"
          }
        }
      }
    }
  }
}
</json format>

2)Other Rounding: Any variant not covered by the remaining Rounding variants. 
This includes any scenarios where rounding amounts differ based on conditions i.e not integral multiples of a fixed amount irrespective of conditions. Any scenario which does not come under variant 1.

<json format>
{
  "agreementTerms": {
    "agreement": {
      "creditSupportAgreementElections": {
        "creditSupportObligations": {
          "rounding": {
            "other":"relevant provision in full as string"
          }
        }
      }
    }
  }
}
</json format>

Important Notes (follow strictly) :  
1)If the document anywhere states or means that Delivery Amount and the Return Amount will not be rounded, do not give a json structure, instead say they do not fit into any variant.
2) If the delivery amount and return amount are discussed but do not strictly fall in variant 1, then classify them into variant 2. 

                  

These are the possible CDM fields with their descriptions: 
agreement (1..1): Specification of the standard set of terms that define a legal agreement.
  creditSupportAgreementElections: Specification of the standard set of terms that define a legal agreement.
    creditSupportObligations (1..1): The Credit Support Obligations applicable to the agreement.
      rounding (0..1): The rounding methodology applicable to the Delivery Amount and the Return Amount in terms of nearest integral multiple of Base Currency units. ISDA 2016 English Law Credit Support Deed for Initial Margin, paragraph 13, General Principles, (c)(vi)(C): Rounding. | ISDA 2016 Japanese Law Credit Support Annex for Initial Margin, paragraph 13, General Principles, (d)(vi)(C): Rounding. | ISDA 2016 New York Law Credit Support Annex for Initial Margin, paragraph 13, General Principles, (c)(vi)(C): Rounding.
        currency (1..1): The currency in which the Delivery Amount and Return Amount rounding amounts are specified. [ISO currency code]
        deliveryAmount (1..1): The nearest integral multiple of Base Currency units to which the Delivery Amount will be rounded in accordance with the specified rounding direction. [number]
        deliveryDirection (1..1): The rounding rule applicable to the Delivery Amount (which can be (i) up to nearest; (ii) down to nearest). [UP,DOWN]
        other (0..1): Utilised where the clause data structure is not able to capture a material aspect of the clause.
        returnAmount (1..1): The nearest integral multiple of Base Currency units to which the Return Amount will be rounded in accordance with the specified rounding direction. [number]
        returnDirection (1..1): The rounding rule applicable to the Return Amount (which can be (i) up to nearest; (ii) down to nearest). [UP,DOWN]

</rules>

'''
        return prompt

    def Minimum_Transfer_Amount_clause():
        prompt = ''' 
      Below are the Common Domain Model (CDM) json generation rules for the Clause: Minimum Transfer Amount. When given a document (ISDA Master Agreement) and asked for CDM json output, strictly apply these rules to generate CDM json output.

<rules>
For the Clause: Minimum Transfer Amount, identify a variant and produce the Common Domain Model JSON representation for the identified variant. 

Please make sure to thoroughly review the entire document, including all schedules and annexes, even if they appear after the main body of the agreement. Carefully read through each section and paragraph, paying close attention to the headings and subheadings to identify relevant clauses. Before providing your final response, double-check your findings and conclusions to ensure accuracy and completeness. Check important notes provided.


The MTA (Minimum Transfer Amount) may differ between the two parties involved. Follow a step by step approach. Identify for party a first and then party b. Minimum Transfer Amount for each party should be analyzed and classified separately. But finally incorporate both parties into one json format as given below.


*Strictly Follow*: If any party is classified into variant 1(fixed amount), check with important notes again. 


Below are the Possible Variants with their example CDM json formats: 
1) Minimum Transfer Amount is a Fixed Amount: The Minimum Transfer Amount for a Party is a Fixed Amount unconditionally at all times.. If it changes due any event or condition, check with variants 2  and 4. If the MTA is a fixed amount but shall not apply at times, then it comes under variant 4.

<json format>
{
  "agreementTerms": {
    "agreement": {
      "creditSupportAgreementElections": {
        "minimumTransferAmount": [
          {
            "mtaType": {
              "fixedAmount": {
                "amount": 1000,
                "currency": "AED",
                "party": "PARTY_1"
            }
          },
          {
            "mtaType": {
              "fixedAmount": {
                "amount": 1000,
                "currency": "AED",
                "party": "PARTY_2"
              }
            }
          }
        ]
      }
    }
  }
}
</json format>

2)Minimum Transfer Amount is a Fixed Amount Falling to Zero in Certain Circumstances: The Minimum Transfer Amount for a Party is a Fixed Amount but will drop to Zero upon the occurrence of Certain Events (other than ratings related).
Example: if an Event of Default exists with respect to the Party, the Minimum Transfer Amount for the  Party shall be zero.
<json format>
{
  "agreementTerms": {
    "agreement": {
      "creditSupportAgreementElections": {
        "minimumTransferAmount": [
          {
            "mtaType": {
              "other": "relevant provision in full as string"
            }
          },
          {
            "mtaType": {
              "other": "relevant provision in full as string"
            }
          }
        ]
      }
    }
  }
}
</json format>


3)Rating Based Minimum Transfer Amount: A Variable Minimum Transfer Amount is applied to a Party, determined by Reference to a Party's Credit Rating. 
<json format>
{
  "agreementTerms": {
    "agreement": {
      "creditSupportAgreementElections": {
        "minimumTransferAmount": [
          {
            "mtaType": {
              "ratingsBased": {
                "compare": "REFERENCE_AGENCY",
                "currency": "AED",
                "event": [
                  "TERMINATION_EVENT_ALL_AFFECTED_TRANSACTIONS"
                ],
                "namedEntity": "ISDA",
                "noRating": true,
                "notRatedBy": "ONE",
                "numberOfRatingAgencies": "ANY_ONE",
                "party": "PARTY_1",
                "ratedParty": "PARTY",
                "ratingType": "LONG_TERM",
                "variableSet": [
                  {
                    "amount": 1000,
                    "amountIsInfinity": true,
                    "name": "STANDARD_AND_POORS",
                    "value": "AA+"
                  }
                ]
              }
            }
          },
          {
            "mtaType": {
              "ratingsBased": {
                "compare": "HIGHEST",
                "currency": "AED",
                "event": [
                  "TERMINATION_EVENT"
                ],
                "namedEntity": "ISDA 2",
                "noRating": true,
                "notRatedBy": "ONE",
                "numberOfRatingAgencies": "ANY_ONE",
                "party": "PARTY_2",
                "ratedParty": "PARTY",
                "ratingType": "LONG_TERM",
                "variableSet": [
                  {
                    "amount": 1000,
                    "amountIsInfinity": false,
                    "name": "AM_BEST",
                    "value": "BBB-"
                  }
                ]
              }
            }
          }
        ]
      }
    }
  }
}
</json format>
In the variable set if "name" field values are the same , add all the "value" values in the same string separated by commas. 
Example is below:
<example>
{
                "amount": 3000000,
                "name": "STANDARD_AND_POORS",
                "value": "AA-,AA,AA+"
              },
              {
                "amount": 3000000,
                "name": "MOODYS",
                "value": "Aa3,Aa2,Aa1"
              },
              {
                "amount": 1000000,
                "name": "STANDARD_AND_POORS",
                "value": "A-,A,A+"
              },
              {
                "amount": 1000000,
                "name": "MOODYS",
                "value": "A3,A2,A1"
              },
</example>


4)Other Minimum Transfer Amount: Any variant not covered by the Other Minimum Transfer Amount variants. 
<json format>
{
  "agreementTerms": {
    "agreement": {
      "creditSupportAgreementElections": {
        "minimumTransferAmount": [
          {
            "mtaType": {
              "other": "relevant provision in full as string"
            }
          },
          {
            "mtaType": {
              "other": "relevant provision in full as string"
            }
          }
        ]
      }
    }
  }
}
</json format>

Example json format for cases when both parties have different MTA, here variant 3 and variant 2:
<json format>
{
  "agreementTerms": {
    "agreement": {
      "creditSupportAgreementElections": {
        "minimumTransferAmount": [
        {
          "mtaType": {
            "ratingsBased": {
              "currency": "USD",
              "party": "PARTY_1",
              "ratingType": "LONG_TERM",
              "variableSet": [
              {
                "amount": 5000000,
                "name": "STANDARD_AND_POORS",
                "value": "AAA"
              },
              {
                "amount": 5000000,
                "name": "MOODYS",
                "value": "Aaa"
              },
              {
                "amount": 3000000,
                "name": "STANDARD_AND_POORS",
                "value": "AA-,AA,AA+"
              },
              {
                "amount": 3000000,
                "name": "MOODYS",
                "value": "Aa3,Aa2,Aa1"
              },
              {
                "amount": 0,
                "name": "STANDARD_AND_POORS",
                "value": "BBB-"
              },
              {
                "amount": 0,
                "name": "MOODYS",
                "value": "Baa3"
              }]
            }
          }
        },
        {
          "mtaType": {
            "other": ""Minimum Transfer Amount" means with respect to Party B: $100,000. Provided that if an Event of Default exists with respect to Party B, the Minimum Transfer Amount for Party B shall be zero."
          }
        }]
      }
    }
  }
}
</json format>


These are important notes (strictly follow): 
<important notes>
1. Classify the Minimum Transfer Amount (MTA) into variant 1 (Fixed Amount) only if it is a fixed amount that does not depend on any other conditions. The MTA should be fixed unconditionally. If the amount varies with conditions, check variant 4. However, if the MTA becomes  zero due any event or certain conditions, classify to variant 2 .


2. Classify the MTA into variant 2 (Fixed Amount Falling to Zero in Certain Circumstances) if it is a fixed amount but, depending on specific conditions, falls to zero or becomes zero. If the MTA drops to any other lower amount based on conditions, it should be classified into variant 4.
Example condition: MTA is fixed amount but falls to zero if an Event of Default has occurred.

3. Classify the MTA into variant 4 (Other Minimum Transfer Amount) if:
   a) The MTA is a fixed amount but depends on any other conditions not covered by variant  2.
   b) The MTA is fixed but falls to any lower amount (other than zero) depending on conditions.
   c) The MTA is any other arrangement that does not fit into variants 1, 2, or 3. Any unexpected situations should be allocated to variant 4.
</important notes>


These are the possible CDM fields with their descriptions: 
agreement (1..1): Specification of the standard set of terms that define a legal agreement.
  creditSupportAgreementElections: Specification of the standard set of terms that define a legal agreement.
    minimumTransferAmount (0..2): Minimum Transfer Amount clause applicable to 1994 NY CSA, 1995 English Law CSA, 1995 English Law Credit Support Deed, 2016 English Law VM CSA and 2016 New York Law VM CSA.
      mtaType (1..1): Details whether the Minimum Transfer Amount (MTA) is rating based, a fixed amount, or infinity.
        fixedAmount (0..1): Defines that the Minimum Transfer Amount (MTA) is a Fixed Amount
          amount (1..1): The amount value applicable to the Minimum Transfer Amount (MTA). [number]
          currency (1:1): The minimum transfer amount currency code. [ISO currency code]
          party (1..1): The party to which the Minimum Transfer Amount (MTA) applies. [PARTY_1,PARTY_2]
        ratingsBased (0..1): Defines that the Minimum Transfer Amount (MTA) is based on a Ratings condition(s)
          compare (0..1): Where two ratings are specified whether the higher or lower rating prevails. [LOWEST,HIGHEST,REFERENCE_AGENCY,AVERAGE,SECOND_BEST,OTHER]
          currency (1..1): The minimum transfer amount currency code. [ISO currency code]
          event (0..*): The relevant trigger for the mta to fall to zero. [EVENT_OF_DEFAULT,TERMINATION_EVENT,TERMINATION_EVENT_ALL_AFFECTED_TRANSACTIONS,POTENTIAL_EVENT_OF_DEFAULT,ADDITIONAL_TERMINATION_EVENT,OTHER]
          namedAffiliate (0..1): Details the Named Affiliate where the Rated Party is Named Affiliate. [string]
          namedEntity (0..1): Details the Named Entity where the Rated Party is Named Entity. [string]
          noRating (1..1): What conditions apply where a party has no rating. [boolean - true,false]
          notRatedBy (0..1): Defines where conditions apply if no Rating where ratings may not exist. [ALL,ONE,TWO]
          numberOfRatingAgencies (0..1): Defines the number of Rating Agencies that the Party must be rated by. [ALL,ANY_ONE,ANY_TWO,OTHER]
          party (1..1): The party to which the Minimum Transfer Amount (MTA) applies. [PARTY_1,PARTY_2]
          ratedParty (0..1): The party to which a rating applies. [PARTY,CREDIT_SUPPORT_PROVIDER,NAMED_ENTITY,PARTY_OR_CREDIT_SUPPORT_PROVIDER,NAMED_AFFILIATE,ALL_AFFILIATES]
          ratingType (1..1): The relevant rating type. [LONG_TERM,SHORT_TERM]
          variableSet (0..*): Defines a combination of Rating Agency, Rating Value, amount and Currency code.
            amount (0..1): The Minimum Transfer Amount (MTA) applicable to the Rating. [number]
            amountIsInfinity (0..1): A flag that defines the Minimum Transfer Amount (MTA) as Infinity. [boolean - true,false]
            name (0..1): The name of the Rating Agency. [AM_BEST,CBRS,DBRS,FITCH,JAPANAGENCY,MOODYS,RATING_AND_INVESTMENT_INFORMATION,STANDARD_AND_POORS]
            value (0..1): The value assigned to the rating. [string]
          zeroEvent (1..1): Whether a trigger applies for the threshold to fall to zero. [boolean - true,false]
        other (0..1): Utilised where the clause data structure is not able to capture a material aspect of the clause. [string]


</rules>


'''
        return prompt
        
    def Threshold_clause():
        prompt = ''' 
        Below are the Common Domain Model (CDM) json generation rules for the Clause: Threshold. When given a document (ISDA Master Agreement) and asked for CDM json output, strictly apply these rules to generate CDM json output.

<rules>
For the Clause: Threshold, identify a variant and produce the Common Domain Model JSON representation for the identified variant. 

Please make sure to thoroughly review the entire document, including all schedules and annexes, even if they appear after the main body of the agreement. Carefully read through each section and paragraph, paying close attention to the headings and subheadings to identify relevant clauses. Before providing your final response, double-check your findings and conclusions to ensure accuracy and completeness. Check instructions enclosed in <strictly follow> tags before concluding.

*Strictly follow*: If any party is classified into variant 2 (fixed amount), check with variant 3 before concluding. If threshold is a fixed amount but falls to/ becomes  zero under certain circumstances, classify into variant 3 & format json as per variant 3 for that party.


*Strictly follow*: Strictly adhere to the provided definitions and variants, only generate a CDM JSON representation when the relevant information is explicitly available in the document. Do not create new CDM json fields , if the provided information is unclear do not generate a json output. 


The Threshold may differ between the two parties involved. Classify threshold for each party first and then format into one json accordingly.

Below are the Possible Variants with their example CDM json formats: 
1)Zero Threshold: A Threshold of Zero is applied to a Party.
<json format>
{
  "agreementTerms": {
    "agreement": {
      "creditSupportAgreementElections": {
        "threshold": [
          {
            "thresholdType": {
              "fixedAmount": {
                "amount": 0,
                "currency": "AED",
                "party": "PARTY_1"
              }
            }
          },
          {
            "thresholdType": {
              "fixedAmount": {
                "amount": 0,
                "currency": "AED",
                "party": "PARTY_2"
              }
            }
          }
        ]
      }
    }
  }
}
</json format>

2)Threshold is a Fixed Amount: The Threshold for a Party is a Fixed Amount.
<json format>
{
  "agreementTerms": {
    "agreement": {
      "creditSupportAgreementElections": {
        "threshold": [
          {
            "thresholdType": {
              "fixedAmount": {
                "amount": 1000,
                "amountIsInfinity": false,
                "currency": "AED",
                "party": "PARTY_1"
              }
            }
          },
          {
            "thresholdType": {
              "fixedAmount": {
                "amount": 1000,
                "amountIsInfinity": false,
                "currency": "AED",
                "party": "PARTY_2"
              }
            }
          }
        ]
      }
    }
  }
}
</json format>




3)Threshold is a Fixed Amount Falling to Zero in Certain Circumstances: The Threshold for a Party is a Fixed Amount but will drop to Zero upon the occurrence of Certain Events (other than ratings related).


<json format>
    {
  "agreementTerms": {
    "agreement": {
      "creditSupportAgreementElections": {
        "threshold": [
          {
            "thresholdType": {
              "other": "relevant provision in full as string",
            }
          },
          {
            "thresholdType": {
              "other": "relevant provision in full as string",
            }
          },
        ]
      }
    }
  }
}              
</json format>

4)Ratings Based Threshold:  A Variable Threshold is applied to a Party, determined by reference to a Party's Credit Rating. 
<json format>
{
  "agreementTerms": {
    "agreement": {
      "creditSupportAgreementElections": {
        "threshold": [
          {
            "thresholdType": {
              "ratingsBased": {
                "compare": "LOWEST",
                "currency": "AED",
                "event": [
                  "TERMINATION_EVENT"
                ],
                "namedAffiliate": "ISDA 2",
                "namedEntity": "ISDA 1",
                "noRating": false,
                "notRatedBy": "ONE",
                "numberOfRatingAgencies": "ANY_TWO",
                "party": "PARTY_1",
                "ratedParty": "PARTY",
                "ratingType": "LONG_TERM",
                "variableSet": [
                  {
                    "amount": 1000,
                    "name": "AM_BEST",
                    "value": "5"
                  }
                ],
                "zeroEvent": false
              }
            }
          },
          {
            "thresholdType": {
              "ratingsBased": {
                "compare": "HIGHEST",
                "currency": "AED",
                "event": [
                  "TERMINATION_EVENT_ALL_AFFECTED_TRANSACTIONS"
                ],
                "namedAffiliate": "ISDA 2",
                "namedEntity": "ISDA 1",
                "noRating": false,
                "notRatedBy": "ONE",
                "numberOfRatingAgencies": "ANY_ONE",
                "party": "PARTY_2",
                "ratedParty": "CREDIT_SUPPORT_PROVIDER",
                "ratingType": "LONG_TERM",
                "variableSet": [
                  {
                    "amount": 1000,
                    "name": "MOODYS",
                    "value": "8"
                  }
                ],
                "zeroEvent": true
              }
            }
          }
        ]
      }
    }
  }
}
</json format>
In the variable set if "name" field values are the same , add all the "value" values in the same string separated by commas. 
Example is below:
<example>
{
                "amount": 3000000,
                "name": "STANDARD_AND_POORS",
                "value": "AA-,AA,AA+"
              },
              {
                "amount": 3000000,
                "name": "MOODYS",
                "value": "Aa3,Aa2,Aa1"
              },
              {
                "amount": 1000000,
                "name": "STANDARD_AND_POORS",
                "value": "A-,A,A+"
              },
              {
                "amount": 1000000,
                "name": "MOODYS",
                "value": "A3,A2,A1"
              },
</example>

5)Threshold of Infinity: The Threshold for a Party is Infinity.
<json format>
   {
  "agreementTerms": {
    "agreement": {
      "creditSupportAgreementElections": {
        "threshold": [
          {
            "thresholdType": {
              "infinity": {
                "party": "PARTY_1"
              }
            }
          },
          {
            "thresholdType": {
              "infinity": {
                "party": "PARTY_2"
              }
            }
          }
        ]
      }
    }
  }
}
</json format>

6)Other Threshold: Any variant not covered by the Other Threshold variants.
<json format>
   {
  "agreementTerms": {
    "agreement": {
      "creditSupportAgreementElections": {
        "threshold": [
          {
            "thresholdType": {
              "other": "relevant provision in full as string",
            }
          },
          {
            "thresholdType": {
              "other": "relevant provision in full as string",
            }
          },
        ]
      }
    }
  }
}
</json format>

<Strictly follow>
It is common to not have a threshold applicable for both the parties involved in the agreement. Do not infer or assume any values or provide sample information to fill CDM. 
If threshold clause or threshold amount is not explicitly stated do not fit the party into any variant.
follow the below rules:
1) If one of the parties fits into a variant and the other does not, only generate json output for the party that fits into a variant.
2)If both parties don't fit into a variant, do not generate json output and state that both parties do not fit into any variant.
</strictly follow>



These are the possible CDM fields with their descriptions: 
agreement (1..1): Specification of the standard set of terms that define a legal agreement.
  creditSupportAgreementElections: Specification of the standard set of terms that define a legal agreement.
    threshold (0..2): Threshold clause applicable to 1994 NY CSA, 1995 English Law CSA, 1995 English Law Credit Support Deed, 2016 English Law VM CSA and 2016 New York Law VM CSA.
      thresholdType (1..1): Details whether the threshold is rating based, a fixed amount, or infinity.
        fixedAmount (0..1): Defines that the Threshold is a Fixed Amount
          amount (1..1): The amount value applicable to the Threshold [number]
          party (1..1): The party to which the threshold applies. [PARTY_1,PARTY_2]
          currency (1..1): The Threshold currency code. [ISO currency code]
          amountsIsInfinity (0..1): Flag detailing whether the collateral Threshold Amount is set to infinity for a particular party. [boolean - true,false]
          party (1..1): The party to which the threshold applies. [PARTY_1,PARTY_2]
        infinitey (0..1): Defines that the Threshold is Infinity
          party (0..1): Elective Party to which the condition applies [PARTY_1,PARTY_2]
        other (0..1): Utilised where the clause data structure is not able to capture a material aspect of the clause. [string]
        ratingsBased (0.1): Defines that the Threshold is based on a Ratings condition(s)
          compare (0..1): Where two ratings are specified whether the higher or lower rating prevails. [LOWEST,HIGHEST,REFERENCE_AGENCY,AVERAGE,SECOND_BEST,OTHER]
          currency (1..1): The minimum transfer amount currency code. [ISO currency code]
          event (0..*): The relevant trigger for the to fall to zero. [EVENT_OF_DEFAULT,TERMINATION_EVENT,TERMINATION_EVENT_ALL_AFFECTED_TRANSACTIONS,POTENTIAL_EVENT_OF_DEFAULT,ADDITIONAL_TERMINATION_EVENT,OTHER]
          namedAffiliate (0..1): Details the Named Affiliate where the Rated Party is Named Affiliate. [string]
          namedEntity (0..1): Details the Named Entity where the Rated Party is Named Entity. [string]
          noRating (1..1): What conditions apply where a party has no rating. [boolean - true,false]
          notRatedBy (0..1): Defines where conditions apply if no Rating where ratings may not exist. [ALL,ONE,TWO]
          numberOfRatingAgencies (0..1): Defines the number of Rating Agencies that the Party must be rated by. [ALL,ANY_ONE,ANY_TWO,OTHER]
          party (1..1): The party to which the Minimum Transfer Amount (MTA) applies. [PARTY_1,PARTY_2]
          ratedParty (0..1): The party to which a rating applies. [PARTY,CREDIT_SUPPORT_PROVIDER,NAMED_ENTITY,PARTY_OR_CREDIT_SUPPORT_PROVIDER,NAMED_AFFILIATE,ALL_AFFILIATES]
          ratingType (1..1): The relevant rating type. [LONG_TERM,SHORT_TERM]
          variableSet (0..*): Defines a combination of Rating Agency, Rating Value, Threshold amount and Currency code
            amount (0..1): The amount value applicable to the Threshold [number]
            name (0..1): The name of the Rating Agency. [AM_BEST,CBRS,DBRS,FITCH,JAPANAGENCY,MOODYS,RATING_AND_INVESTMENT_INFORMATION,STANDARD_AND_POORS]
            value (0..1): Rating applicable to the party from a given rating agency. [string]
          zeroEvent (1..1): Whether a trigger applies for the threshold to fall to zero. [boolean - true,false]


</rules>

'''
        
        return prompt    
    
    if function == "Currency_clause":
        result = Currency_clause()
        responseBody = {
            "TEXT": {
                "body": result
            }
        }
        
    
    if function == "Rounding_clause":
        result = Rounding_clause()
        responseBody = {
            "TEXT": {
                "body": result
            }
        }

    if function == "Minimum_Transfer_Amount_clause":
        result = Minimum_Transfer_Amount_clause()
        responseBody = {
            "TEXT": {
                "body": result
            }
        }
        
    if function == "Threshold_clause":
        result = Threshold_clause()
        responseBody = {
            "TEXT": {
                "body": result
            }
        }    

    action_response = {
        'actionGroup': actionGroup,
        'function': function,
        'functionResponse': {
            'responseBody': responseBody
        }
    }

    dummy_function_response = {'response': action_response, 'messageVersion': event['messageVersion']}
    print("Response: {}".format(dummy_function_response))

    return dummy_function_response
