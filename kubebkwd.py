#!/usr/bin/python3

import os
import argparse
import subprocess

parser = argparse.ArgumentParser(description = """
Kubebkwd - a reverse proxy from your kubernetes cluster to your local
Note, this will only work with a local kubernetes cluster where your local machine is exposed with host.docker.internal e.g. with docker-desktop.
To revert, simply re-deploy your container to the cluster as you normally would using kubectl apply. This will also litter a service postfixed with 'extname' which you can remove manually.
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

namespaceArg = ""
if namespace != None:
    namespaceArg = "-n {namespace}".format(namespace=namespace)

print("namespace ", namespace)

def getServiceSelectorTag(serviceName): 
    result = subprocess.check_output("kubectl describe {namespaceArg} service {serviceName}".format(serviceName=serviceName, namespaceArg=namespaceArg), shell=True).decode("utf-8")

    lines = result.split("\n")
    print(lines)
    for line in lines:
        split = line.split(": ") #could use a yaml parser? meh
        if len(split) == 2: 
            key, value = split
            if(key == "Selector"):
                return value.strip()

selector = getServiceSelectorTag(service)
print("selector ", selector)
deploymentName = subprocess.check_output("""kubectl get deployments --no-headers -l {selector} | awk '{{print $1}}'""".format(selector = selector), shell = True).decode("utf-8")
print("deployment name:", deploymentName)
print("Selector is ",  selector)
tagKey, tagValue = selector.split("=")
tag = tagKey.strip() + ": " + tagValue.strip()


template = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {deployment}
  labels:
    {tag}
spec:
  replicas: 1
  selector:
    matchLabels:
      {tag}
  template:
    metadata:
      labels:
        {tag}
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
os.system("mkdir generated")
with open(generated_file_name, 'w') as file:
    file_contents = template.format(
        service=service,
        containerPort=containerPort,
        localPort=localPort,
        deployment=deploymentName,
        tag=tag
    )
    file.write(file_contents)


os.system("""kubectl apply {namespaceArg} -f ./{generated_file_name}""".format(generated_file_name=generated_file_name, namespaceArg=namespaceArg))

