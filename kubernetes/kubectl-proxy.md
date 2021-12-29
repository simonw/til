# kubectl proxy

Learned about this today as a way of accessing the Kubernetes REST API.

Assuming you have `kubectl` setup and authorized against a cluster (I'm using DigitalOcean K8S) you can start a `localhost` proxy for talking to the API server in the cluster like this:

    kubectl proxy --port 9000

This starts a proxy running on `localhost` port 9000 which can be used to make authenticated API calls to the cluster. The authentication wrapper (which I think defauls to client certificates) is added automatically, so you can just hit `http://localhost:9000/` using `curl`.
```
curl localhost:9000
{
  "paths": [
    "/.well-known/openid-configuration",
    "/api",
    "/api/v1",
    "/apis",
    "/apis/",
    "/apis/admissionregistration.k8s.io",
    "/apis/admissionregistration.k8s.io/v1",
    "/apis/admissionregistration.k8s.io/v1beta1",
    "/apis/apiextensions.k8s.io",
...
```
Absolutely everything in Kubernetes is exposed via the API. Hitting the homepage, as above, shows a list of API paths. Then you can do things like this:
```
% # List nodes in the cluster
% curl localhost:9000/api/v1/nodes
{
  "kind": "NodeList",
  "apiVersion": "v1",
  "metadata": {
    "resourceVersion": "18429049"
  },
  "items": [
    {
      "metadata": {
        "name": "..."

% # List pods (effectively containers) in the cluster:
% curl localhost:9000/api/v1/pods 
{
  "kind": "PodList",
  "apiVersion": "v1",
  "metadata": {
    "resourceVersion": "18429226"
  },
  "items": [
    {
      "metadata": {
        "name": "alpaca-prod",
        "namespace": "default",
        "uid": "50b03bf7-c46d-4ebb-ab93-df089940fa9c",
        "resourceVersion": "1207774",
        "creationTimestamp": "2021-10-31T21:18:08Z",
        "labels": {

% # Show Kubernetes version
% curl localhost:9000/version    
{
  "major": "1",
  "minor": "21",
  "gitVersion": "v1.21.5",
  "gitCommit": "aea7bbadd2fc0cd689de94a54e5b7b758869d691",
  "gitTreeState": "clean",
  "buildDate": "2021-09-15T21:04:16Z",
  "goVersion": "go1.16.8",
  "compiler": "gc",
  "platform": "linux/amd64"
}
```
