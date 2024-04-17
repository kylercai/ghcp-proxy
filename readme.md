# Proxy for GitHub Copilot
A sample to show how to build customized proxy solution on the top of MITMProxy (Man-In-The-Middle) with your addon logic.<br><br>
The typical usage is to mitigate the compliance conerns on GitHub Copilot may send confidential code or information outer to the enterprise. The proxy with the addon works to intercept GitHub Copilot requests, checking the prompt against the blocking list and denies those requests containing improper prompt contents.<br>

## Description

<!-- files description in table -->
| File | Description |
| --------------- | --------------- |
| packetfilter.py | Addon implementation script. Run with the mitmproxy |
| prompts-pubsub.yml | Dapr component definition, using Redis as the Pub/Sub broker to publish the events |
| cplproxy.yml | Yaml definiton to run this proxy in Kubernetes cluster |
| Dockerfile | Used to build container image when you update the addon logic/configuration/certifications |
| blocklist.ini | Define the blocking conditions (now it includes source files and keywords) |
| allowed_users.txt | Define the allowed users to be authenticated on the proxy |
| config.ini | Other configurations need for the addon logic |

## How does it work
- Built on top of MITMProxy and run your logic as Addon to intercept and process the completion requests
- Run as container with Dapr in Kubernetes cluster
- Customers can set the blocking conditions with list of source files and keywords
- If the prompt contains the keywords or contains the contents from source files in the blocking list, the proxy denies the completion request and return 403 code with body “Blocked”

## Architecture
![Architecture](./imgs/architecture.png)

## Prerequisites
- Dapr is installed in your Kubernetes cluster  
- Redis or other brokers with Pub/Sub support  

## Usage
- Install Dapr in Kubernetes cluster<br>
```
dapr init -k
```
```
λ dapr status -k
NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
dapr-placement-server  dapr-system  True     Running  1         1.13.2   1d   2024-04-15 15:27.05
dapr-sidecar-injector  dapr-system  True     Running  1         1.13.2   1d   2024-04-15 15:27.05
dapr-sentry            dapr-system  True     Running  1         1.13.2   1d   2024-04-15 15:27.05
dapr-operator          dapr-system  True     Running  1         1.13.2   1d   2024-04-15 15:27.05
``` 

- Install Dapr component for Pub/Sub  
```
λ kubectl apply -f prompts-pubsub.yml
component.dapr.io/promptpubsub configured
```

- Start the proxy in Kubernetes cluster  
```
kubectl apply -f cplproxy.yml
```
- Check the proxy services status:
  - cplproxy: the proxy service listening on port 8080. Sits in the middle of clients and the GitHub Copilot service to intercept and process the request
  - cplproxyweb: the web console of the cplproxy service listening on port 8081
```
λ kubectl get service -o wide
NAME               TYPE           CLUSTER-IP     EXTERNAL-IP       PORT(S)                               AGE    SELECTOR
cplproxy           LoadBalancer   20.0.163.163   143.64.163.184    8080:32651/TCP                        15h    app=cplproxy
cplproxy-dapr      ClusterIP      None           <none>            80/TCP,50001/TCP,50002/TCP,9090/TCP   15h    app=cplproxy
cplproxyweb        LoadBalancer   20.0.70.142    143.64.163.189    8081:32701/TCP                        15h    app=cplproxy
```
Visit the cplproxyweb and you will see the web console of the cplproxy like below:
![UI](./imgs/webConsole.png)

- Configure the proxy setting in your IDE
- Review the processing in the proxy web portal
In the web portal you will see the flows detail and how the proxy do the processing
![UI](./imgs/proxyUI.png)

- Review the published processing detail 
Use the console of your pub/sub broker to view the messages in the "prompts" topic

- Further actions on the published processing detail

## Known Issues
TBD