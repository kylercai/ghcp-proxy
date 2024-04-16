# Proxy for GitHub Copilot
Example: http://143.64.163.189:8081/#/flows

## How does it work
- Built on top of MITMProxy and run your logic as Addon to intercept and process the completion requests
- Run as container with Dapr in Kubernetes cluster
- Customers can set the blocking conditions with list of source files and keywords
- If the prompt contains the keywords or contains the contents from source files in the blocking list, the proxy denies the completion request and return 403 code with body “Blocked”


## Architecture
![Architecture](https://github.com/kylercai/ghcp-proxy/blob/main/architecture.png)


## Prerequisites
TBD
## Usage
TBD

## Known Issues
TBD