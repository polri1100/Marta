import json 
# import ast

# a = '{"type": "service_account", \
# "project_id": "martacostura", \
# "private_key_id": "fce6e0f0d0d4688261fd3f40b6fba53e87089c3d", \
# "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDB9OSC+qecw0fM\nSCwvtb2csdpSQS/Pgw+qNSHG7lGsegFDiYz6JcD5WIoKqu96iuQTv3bJIPfyQ19i\n8jXPLjjX9NPhKTNdisQxT2mRNfW3KZzEAd+PNySKtS/KBy+4AOV1zAumR2NMM5I5\nCA/MFWnO9I3lSXzEZjWpdX+AjSYYzsOep3Vy1g5ZMtcGmjuHAp+Nk44LtF2bcpys\nzQwoDuZoQkaNm8kd8WRP3cfPvru/usyzCGTnStbCHFfBnxqOnZ037cYzCXoOmL7E\n4GuFk5vznRXmCC69mm/pUYU9Q7KRD99xYZFl/9hD57233HVCoi/gR6YjJPwH/MCp\nqBBBklsXAgMBAAECggEADux7ng27UoyUEbExSoUpZHfVh063Zw176b981y8Eicjk\nIADiyryXme1Tcc6v7os7/BOsstJz7D19hsIsRxdqDZ6A+b+PJuYZLSd3GqfpktZY\n1vFt9ORr+LWdn7s902Ko7+TAtg1NeVIz22o2DPX41jvAT0wq6tG9KfTTLV5Zor7j\nrqelH7RAF/XSO/dXfBko0KRylquGu/kC4uJcURsZT9K6xAbwI28lMufl88iXEXE0\nRRuKVrDTsvko2jiBz0UDScb1ELf39THnvRH45e7hcQFi72sm/Jzo8gBXE6M+6aha\noGmmHngqYWArd1302ubpSOBphGatS5iW/n62Di8fAQKBgQDw2EusdElpmuv6qD+u\ndFxYOqElQO/jJY5a1rNOJWpBp/c7UEow9oi0s6J/6akYcdy1X7CdIvBOZiAzCjry\nYYBP/+35rz4Xbk+nqzOPj4qeLtuhnSVSFYHNpJoPCXo/FgworS4Dn6nI4S/tQ5iK\nljAzViRNjmyPQwb2NxgXkHYgUQKBgQDOKUlRN76butziPAXmYhVyAxPRr+xGotme\nx1lGbkxjwbZnFsjr98rNj2H0lvZbLgo0hH6pduRckxugr721QGXerR9ml3CDIB+M\nqRbT+oOKS/1/WEfvWckFJlOiIjSKhEHn3qdgasW0MqoqgQ3SZbjY8ihebbi+sXAK\nhx74cX2S5wKBgCiGDD2JF20Ybwou0wA0ffEudDzDb1mF0S0BoQvOCdHgRB4LxV/1\nq0zUSMxC8Xu2dM9juWDHJy3ZyyMrXn234BIV2uG/FbB1lBt/F97Y5Rb2hWfs/AGS\nstN6FZ3gF1yUBhm2Ad8EN1ogYaMHU5xF5vhMTzFpfGSif4JgBMK6QNXxAoGAb1b4\n07YpaO14UW5dOVkLf/GNiJdcIaHdqdS7sD/tXYrGudIiXN4MVwvyuSe2kPPCay6L\nQXaGSkDgkN2YtQS8f5A7/yoWh5qXr126iG0pEU2M8HN7FhcFa5SRYmTav1xCQ7mJ\n55aCg5lBMYdVMaXiOLg/eRAE0Gf/vI/Q+BhC200CgYEAsrKvJeDYp0PR5LrE18Zj\n/SNc/rh1OJjYvV9FAF+4bWQe7qaihh6gD4kKGEp4sgBp1e6kBymkEQwY3dH9G8wo\nAeGwQg9Y3dfaQZ4U+wxnuyQdPulnj/IBEn5pfesljdZklfq6nNN2243Zw72uEuYp\nZzSetL1lB9KXlcN2CBcc9oo=\n-----END PRIVATE KEY-----\n", "client_email": "marta-costura-sheets@martacostura.iam.gserviceaccount.com", "client_id": "116789383299631603165", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/marta-costura-sheets%40martacostura.iam.gserviceaccount.com", "universe_domain": "googleapis.com"}'
# print(a)

# b = json.loads(a, strict=False)
# print(b['private_key'])

a = json.loads('streamlit/secrets.toml', strict=False)

print(a)