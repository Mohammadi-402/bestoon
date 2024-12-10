/submit/expense/
POST , returns a json
input: date(optional), text, amount, token
output: status : ok

/submit/income/
POST , returns a json
input: date(optional), text, amount, token
output: status : ok

/q/generalestat/
POST, returns a json
input: from date(optional), to date(optional), token
output: json from some stat related to this user

accounts/login/
POST, returns a json
input: username, password
output: status:ok & token

/accounts/register/
step1:
POST i
nput: username, email, password
output: status:ok
step2:
#click on link with the code in the email 
GET
input: email, code
output: status: ok (shows the token)
