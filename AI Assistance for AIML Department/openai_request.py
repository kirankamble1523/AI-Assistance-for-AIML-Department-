from openai import OpenAI
import os

client = OpenAI(api_key="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")

#def send_request(query):


#    completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {
#             "role": "user",
#            "content": query
#           }
#   
# 
#  ]
# )

#return completion.choices[0].message.content

def send_request(query):


    completion = client.chat.completions.create(
         model="gpt-4o-mini",
         messages=query
    )

    return completion.choices[0].message.content