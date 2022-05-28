# Kubebkwd

Kubebkwd (pronounced 'cube backward') is a script which sets up a reverse proxy from your local kubernetes cluster to an application running natively on your machine that you can debug or change out to your heart's content. This allows you to debug your application with the full benefit of having access to having the rest of your applications in a cluster.

Kubebkwd is essentially an attempt at a simplified Telepresence. Telepresence is an amazing tool but one which has a great deal of complexity, we've found has had some compatibility issues with certain verisons of MacOS and such. The trade offs are that Kubebkwd instead uses almost entirely only high-level kubernetes constructs and only a very minimal TCP reverse proxy. Kubebkwd requires no special network manipulation on the host machine outside of what is set up by e.g. docker for desktop already which hopefully should make it more robust to different system configurations. 

This also means that it will only work with local Kubernetes clusters unless you do something special to expose your machine with a host domain from a remote cluster. 

### Usage
The usage is just:

kubebkwd service containerPort localPort [--namespace] [--hostDomain]

Where service is the name of the kubernetes service that you would like to debug.
containerPort is the port that your application listens to in the kubernetes cluster.
localPort is the port that the application running on localhost you would like to debug is running on.
namespace is your kubernetes namespace, this is optional and your life might be easier if you use kubens.
hostDomain defaults to host.docker.internal - but other kubernetes environments use other domains, e.g. minikube uses host.minikube.internal which can be overriden with this argument.


### How this works

There are two major things you need to know in order to understand how this tool works:

One: using an ExternalName Kubernetes Service, we can direct traffic from a pod to an application running on our local by pointing at  host.docker.internal.
Two: We can make it so that it can point at any port by replacing your application's kubernetes deployment with a different one which runs a very simple, light weight TCP reverse proxy.

The script will automatically determine how to name and tag everything such that it should work properly, using the information from your existing service.

Assuming you previously had a kubernetes set up which looked like the following:

[A-deployment] -> [B-service] -:containerPort-> [B-deployment]

After running this script you will now have instead:

[A-deployment] -> [B-service] -:containerPort-> [B-deployment (replaced with reverse proxy)] -:localPort-> [B-service-extname-service] -> [your local application]

An interesting consequence of this method of deployment is that your local service will then end up accessible through kubefwd as B-service as it will have its own pod to make that possible.