# Proxy for GitHub Copilot
Running instance for example: http://143.64.163.189:8081/#/flows (host on Azure Kubernetes Service)
## Description
A sample to show how to build customized proxy solution on the top of MITMProxy (Man-In-The-Middle) with your addon logic.<br><br>
The sample addon works to intercept GitHub Copilot requests, checking the prompt against the blocking list and denies those requests containing improper contents in the prompt.<br><br>
The typical usage is to mitigate the compliance conerns on GitHub Copilot may send confidential code or information outer to the enterprise. In this scenario, you can define what are the confidential contents look like in the blocking list, and implement your own filtering logic in the addon to allow/block those requests sending to GitHub Copilot.

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
- Install Dapr in Kubernetes cluster  
- Install Dapr component for Pub/Sub  
- Start the proxy in Kubernetes cluster  
- Configure the proxy setting in your IDE
- Review the processing in the proxy web portal  
- Review the published processing detail 
- Further actions on the published processing detail

## Known Issues
TBD