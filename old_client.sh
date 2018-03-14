#!/bin/bash
# Use -gt 1 to consume two arguments per pass in the loop (e.g. each
# argument has a corresponding value to go with it).
# Use -gt 0 to consume one or more arguments per pass in the loop (e.g.
# some arguments don't have a corresponding value to go with it such
# as in the --default example).
# note: if this is set to -gt 0 the /etc/hosts part is not recognized ( may be a bug )
while [[ $# -gt 1 ]]
do
key="$1"

case $key in
    -p|--port)
    PORT="$2"
    shift # past argument
    ;;
    -v|--verifier)
    BACKEND="$2"
    shift # past argument
    ;;
    -f|--file)
    FILE="$2"
    shift # past argument
    ;;
    *)
          # unknown option
    ;;
esac
shift # past argument or value
done

curl -i -X POST -H "Content-Type: application/json" -d '{"arg":"'${BACKEND}' '${FILE}'"}' \
               "http://localhost:"${PORT}"/verify"; echo
curl -i -X GET "http://localhost:"${PORT}"/verify/0"; echo
