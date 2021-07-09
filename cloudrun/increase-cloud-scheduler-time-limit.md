# Increasing the time limit for a Google Cloud Scheduler task

In [VIAL issue 724](https://github.com/CAVaccineInventory/vial/issues/724) a Cloud Scheduler job which triggered a Cloud Run hosted export script - by sending an HTTP POST to an endpoint - was returning an error. The logs showed the error happened exactly three minutes after the task started executing.

Turns out the HTTP endpoint (which does a lot of work) was taking longer than three minutes, which is the undocumented default time limit for Cloud Scheduler jobs.

Unfortunately it's not possible to increase this time limit using the Cloud Scheduler web console, but it IS possible to increase the limit using the CLI `gcloud` tool.

To list the scheduler jobs:
```
~ % gcloud beta scheduler jobs list --project django-vaccinateca
ID                                        LOCATION  SCHEDULE (TZ)                                                    TARGET_TYPE  STATE
api-export-production                     us-west2  every 1 minutes (America/Los_Angeles)                            HTTP         ENABLED
api-export-staging                        us-west2  every 1 minutes (America/Los_Angeles)                            HTTP         ENABLED
mapbox-export                             us-west2  0 2,9,10,11,12,13,14,15,16,17,18,21 * * * (America/Los_Angeles)  HTTP         ENABLED
resolve-missing-counties-production       us-west2  */10 * * * * (America/Los_Angeles)                               HTTP         ENABLED
resolve-missing-counties-staging          us-west2  */10 * * * * (America/Los_Angeles)                               HTTP         ENABLED
vaccinatethestates-api-export-production  us-west2  */10 * * * * (America/Los_Angeles)                               HTTP         ENABLED
vaccinatethestates-api-export-staging     us-west2  */10 * * * * (America/Los_Angeles)                               HTTP         ENABLED
```
To increase the limit for one of them by name:
```
gcloud beta scheduler jobs update http \
  vaccinatethestates-api-export-production \
  --attempt-deadline=540s \
  --project django-vaccinateca
```
You can see the limit using `describe`:
```
~ % gcloud beta scheduler jobs describe vaccinatethestates-api-export-production --project django-vaccinateca
attemptDeadline: 180s
description: Hit /api/exportVaccinateTheStates to export to api.vaccinatethestates.com
  bucket
httpTarget:
  headers:
    Authorization: Bearer 27:...
    User-Agent: Google-Cloud-Scheduler
  httpMethod: POST
  uri: https://vial.calltheshots.us/api/exportVaccinateTheStates
lastAttemptTime: '2021-07-08T23:40:00.992830Z'
name: projects/django-vaccinateca/locations/us-west2/jobs/vaccinatethestates-api-export-production
retryConfig:
  maxBackoffDuration: 3600s
  maxDoublings: 5
  maxRetryDuration: 0s
  minBackoffDuration: 5s
schedule: '*/10 * * * *'
scheduleTime: '2021-07-08T23:50:00.061563Z'
state: ENABLED
status:
  code: 2
timeZone: America/Los_Angeles
userUpdateTime: '2021-06-10T23:34:48Z'
```
