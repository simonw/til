# Only run GitHub Action on push to master

Spotted in [this Cloud Run example](https://github.com/GoogleCloudPlatform/github-actions/blob/20c294aabd5331f9f7b8a26e6075d41c31ce5e0d/example-workflows/cloud-run/.github/workflows/cloud-run.yml):

```yaml
name: Build and Deploy to Cloud Run

on:
  push:
    branches:
    - master
```

Useful if you don't want people opening pull requests against your repo that inadvertantly trigger a deploy action!

An alternative mechanism I've used is to gate the specific deploy steps in the action, [like this](https://github.com/simonw/cryptozoology/blob/8a86ec283823c91ad42c5f737a912d43791d427f/.github/workflows/deploy.yml#L31-L40).

```yaml
    # Only run the deploy if push was to master
    - name: Set up Cloud Run
      if: github.ref == 'refs/heads/master'
      uses: GoogleCloudPlatform/github-actions/setup-gcloud@master
      with:
        version: '275.0.0'
        service_account_email: ${{ secrets.GCP_SA_EMAIL }}
        service_account_key: ${{ secrets.GCP_SA_KEY }}
    - name: Deploy to Cloud Run
      if: github.ref == 'refs/heads/master'
      run: |-
        gcloud config set run/region us-central1
```
