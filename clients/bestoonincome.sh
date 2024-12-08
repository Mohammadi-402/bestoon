#!/bin/bash

# please set your variable
TOKEN=blhcafryehw
BASE_URL=http://localhost:8000
curl --data "token=$mytoken&amount=$1&text=$2" $BASE_URL/submit/income/
