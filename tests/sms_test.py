from twilio.rest import Client

account_sid = 'AC0a28d8b2df04587f7e4ae71d4830c249'
auth_token = '734fbc7c2ebdfe63b5cd7de0deacae52'
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body="Join Earth's mightiest heroes. Like Kevin Bacon.",
                     from_='+12018013260',
                     to='+17153796650'
                 )

print(message.sid)
