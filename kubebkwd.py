#!/usr/bin/python3

import os
import argparse

parser = argparse.ArgumentParser(description = """
Kubebkwd, a reverse proxy for your local applications into kubernetes.
Note, this will only work with a local kubernetes cluster where your local machine is exposed with host.docker.internal e.g. with docker-desktop.
""")
parser.add_argument('service', type=str, help='The name of your kubernetes service')
parser.add_argument('containerPort', type=int, help='The port your service exposes in the kubernetes cluster')
parser.add_argument('localPort', type=int, help='The port your application is running on on your local machine')
parser.add_argument('--namespace', type=str, help='Kubernetes namespace. Otherwise will default to whatever you have set with kubens')
args = parser.parse_args()

service = args.service
containerPort = args.containerPort
localPort = args.localPort
namespace = args.namespace

print("namespace ", namespace)

template = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {service}-deployment
  labels:
    app: {service}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {service}
  template:
    metadata:
      labels:
        app: {service}
    spec:
      containers:
        - name: {service}
          image: maxmcd/tcp-proxy@sha256:892791987015e408d40c35bfd50e3d15dedbf462b8dc225ae4dcdd2abfd4900e
          command: ["tcp-proxy"]
          args: ["-l", "0.0.0.0:{containerPort}", "-r", "{service}-extname-service:{localPort}"]
          ports:
            - containerPort: {containerPort}
---

apiVersion: v1
kind: Service
metadata:
  name: {service}-extname-service
spec:
  type: ExternalName
  externalName: host.docker.internal
"""

generated_file_name = "generated/{service}-deployment.yaml".format(service=service)
with open(generated_file_name, 'w') as file:
    file_contents = template.format(
        service=service,
        containerPort=containerPort,
        localPort=localPort
    )
    file.write(file_contents)

if namespace == None or namespace == "":
    os.system("""kubectl apply -f ./{generated_file_name}""".format(generated_file_name=generated_file_name))
else:
    os.system("""kubectl apply -n {namespace} -f ./{generated_file_name}""".format(generated_file_name=generated_file_name, namespace=namespace))

