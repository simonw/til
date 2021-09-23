# Switching between gcloud accounts

I have two different Google Cloud accounts active at the moment. Here's how to list them with `gcloud auth list`:

```
% gcloud auth list
    Credentialed Accounts
ACTIVE  ACCOUNT
        simon@example.com
*       me@gmail.com

To set the active account, run:
    $ gcloud config set account `ACCOUNT`
```
And to switch between them with `gcloud config set account`:

```
% gcloud config set account me@gmail.com
Updated property [core/account].
```
