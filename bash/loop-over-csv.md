# Looping over comma-separated values in Bash

Given a file (or a process) that produces comma separated values, here's how to split those into separate variables and use them in a bash script.

The trick is to set the Bash `IFS` to a delimiter, then use `my_array=($my_string)` to split on that delimiter.

Create a text file called `data.txt` containing this:
```
first,1
second,2
```
You can create that by doing:
```bash
echo 'first,1
second,2' > /tmp/data.txt
```
To loop over that file and print each line:
```bash
for line in $(cat /tmp/data.txt);
do
  echo $line
done
```
To split each line into two separate variables in the loop, do this:
```bash
for line in $(cat /tmp/data.txt);
do
  IFS=$','; split=($line); unset IFS;
  # $split is now a bash array
  echo "Column 1: ${split[0]}"
  echo "Column 2: ${split[1]}"
done
```
Outputs:
```
Column 1: first
Column 2: 1
Column 1: second
Column 2: 2
```
Here's a script I wrote using this technique for the TIL [Use labels on Cloud Run services for a billing breakdown](https://til.simonwillison.net/til/til/cloudrun_use-labels-for-billing-breakdown.md):
```bash
#!/bin/bash
for line in $(
  gcloud run services list --platform=managed \
    --format="csv(SERVICE,REGION)" \
    --filter "NOT metadata.labels.service:*" \
  | tail -n +2)
do
  IFS=$','; service_and_region=($line); unset IFS;
  service=${service_and_region[0]}
  region=${service_and_region[1]}
  echo "service: $service    region: $region"
  gcloud run services update $service \
    --region=$region --platform=managed \
    --update-labels service=$service
  echo
done
```
