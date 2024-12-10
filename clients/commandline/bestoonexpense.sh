# #!/bin/bash
#
# source config.sh
#
# curl --data "token=$TOKEN&amount=$1&text=$2" $BASE_URL/submit/expense/

#!/bin/bash

source bestoonconfig.sh

print_usage()
{
    echo "Use this script to submit expense reports to ${BASE_URL}"
    echo "Usage: ${0} <Amount> <Description>. Eg:"
    echo "Usage: ${0} 1000 Donation"
}

AMOUNT=$1
shift
TEXT=$*
if [ -z "$TEXT" ]; then
    print_usage
    exit 1
fi

curl --data "token=$TOKEN&amount=$AMOUNT&text=$TEXT" $BASE_URL/submit/expense/
