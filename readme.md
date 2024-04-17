# Local Proxy for GitHub Copilot
A sample to show how to build customized proxy solution on the top of MITMProxy (Man-In-The-Middle) with your addon logic.<br><br>
The typical usage is to mitigate the compliance conerns on that GitHub Copilot may send confidential information to outer of the enterprise. Using the proxy sitting in the middle of your clients and the GitHub Copilot service, to intercept requests, checking the prompt against the blocking list and denies those requests containing improper prompt contents.<br>

## Description

<!-- files description in table -->
| File | Description |
| --------------- | --------------- |
| packetfilter.py | Addon implementation script. Run with the mitmproxy |
| prompts-pubsub.yml | Dapr component definition, using Redis as the Pub/Sub broker to publish the events |
| cplproxy.yml | Yaml definiton to run this proxy in Kubernetes cluster |
| Dockerfile | Used to build your own container image when you update the addon logic/configuration/certifications |
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
- Dapr (version 1.13.2 or above) is installed in your Kubernetes cluster
- Redis or other brokers with Pub/Sub support
- Build your own container image if you update the logic and configuration. In the "Deployment" definition of "cplproxy.yml", point your container image to the right image repository link

## Usage
- Install Dapr in Kubernetes cluster<br>
```
dapr init -k
```
Check the status and make sure Dapr is up and running:
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
This tells the Dapr use your broker to publish the flow processing events. Benefit from Dapr, you can many choices for your favorite brokers, for example Kafka, RabbitMQ, RocketMQ, Azure Event Hubs, etc. For the up-to-date list of supported Pub/Sub brokers, please visit Dapr links: https://docs.dapr.io/reference/components-reference/supported-pubsub/.

- Start the proxy in Kubernetes cluster  
```
kubectl apply -f cplproxy.yml
```
This install the deployments and services to run the proxy in Kubernetes cluster.<br>
After the installation, check the proxy services status:
```
λ kubectl get deployments -l app=cplproxy -o wide
NAME       READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS   IMAGES                     SELECTOR
cplproxy   1/1     1            1           16h   cplproxy     kylerdocker/cplproxy:2.1   app=cplproxy

λ kubectl get services cplproxy cplproxyweb -o wide
NAME          TYPE           CLUSTER-IP     EXTERNAL-IP      PORT(S)          AGE   SELECTOR
cplproxy      LoadBalancer   20.0.163.163   143.64.163.184   8080:32651/TCP   16h   app=cplproxy
cplproxyweb   LoadBalancer   20.0.70.142    143.64.163.189   8081:32701/TCP   16h   app=cplproxy

λ kubectl get pods -l app=cplproxy -o wide
NAME                        READY   STATUS    RESTARTS   AGE   IP          NODE                                NOMINATED NODE   READINESS GATES
cplproxy-66f8f985d5-ccvhl   2/2     Running   0          16h   10.0.4.28   aks-agentpool-38020763-vmss000000   <none>           <none>
```

There are two services:<br>
    - cplproxy: the proxy service listening on port 8080. Sits in the middle of clients and the GitHub Copilot service to intercept and process the request.<br>
    - cplproxyweb: the web console of the cplproxy service listening on port 8081.<br>

In the deployment definition we set the container replica as 1, and you should see 2 containers when you run "kubectl get pods" like below:
```
λ kubectl get pods -l app=cplproxy -o wide
NAME                        READY   STATUS    RESTARTS   AGE   IP          NODE                                NOMINATED NODE   READINESS GATES
cplproxy-66f8f985d5-ccvhl   2/2     Running   0          16h   10.0.4.28   aks-agentpool-38020763-vmss000000   <none>           <none>
```
This is our expectation because Dapr automatically inject a side-car containers into the pod of the cplproxy container. You can use command "kubectl describe pod xxx" to view the detail.

Visit the cplproxyweb service and you will see the web console of the cplproxy like below:<br>
![UI](./imgs/webConsole.png)
<br>

- Configure the proxy setting in your IDE
You set the proxy using the cplproxy service address.<br>
When you configure the proxy setting in IDE, make sure using URL in the form of "http://<your_id>@<your_proxy_domain_name>:8080". <your_id> should be list in the "allowed_users.txt", and <your_proxy_domain_name> should be a resolvable domain name pointing to the cplproxy service IP address. For example: http://kacai@mitmproxy.kylerc.it:8080 (_I add a recode in local host file point "mitmproxy.kylerc.it" to the cplproxy service IP run in my Kubernetes cluster_).
<br>

- Review the processing in the proxy web portal
In the web portal you will see the flows detail and how the proxy do the processing
![UI](./imgs/proxyUI.png)
<br>

- Review the published processing detail 
Use the console of your pub/sub broker to view the messages in the "prompts" topic
<br>

- Further actions on the published processing detail
<br>

## Known Issues
TBD