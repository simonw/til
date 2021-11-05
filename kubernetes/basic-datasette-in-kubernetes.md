# Basic Datasette in Kubernetes

This recipe for deploying the official `datasetteproject/datasette` container in Kubernetes just worked for me. It uses an interesting (possibly nasty?) trick to install plugins and download a SQLite database file on container startup, without needing to bake a brand new container image.

I'm running 2 replicas, to experiment with the cluster.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: datasette-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: datasette
  template:
    metadata:
      labels:
        app: datasette
    spec:
      containers:
      - name: datasette
        image: datasetteproject/datasette
        command:
        - sh
        - -c
        args:
        - |-
          # Install some plugins
          pip install \
            datasette-debug-asgi \
            datasette-cluster-map \
            datasette-psutil
          # Download a DB (using Python because curl/wget are not available)
          python -c 'import urllib.request; urllib.request.urlretrieve("https://global-power-plants.datasettes.com/global-power-plants.db", "/home/global-power-plants.db")'
          # Start Datasette, on 0.0.0.0 to allow external traffic
          datasette -h 0.0.0.0 /home/global-power-plants.db
        ports:
        - containerPort: 8001
          protocol: TCP
```
The devious trick here is to use `command` and `args` to specify a multi-line shell script to run on startup, which installs some plugins with `pip install`, then downloads a database file using `urllib.request.urlretrieve()` in Python (because `wget` and `curl` are not included in the official image), then starts Datasette against that downloaded file.
