# mitmweb --web-host 0.0.0.0 --listen-host 0.0.0.0 --set block_global=false -s <your script path>/sample.py 
# mitmweb --web-host 0.0.0.0 --listen-host 0.0.0.0 --set block_global=false -s /home/liczha/copilot-usage/sample-myself.py

import asyncio
from mitmproxy import http,ctx,connection,proxy
#from elasticsearch import Elasticsearch, exceptions
from datetime import datetime
import base64
import re
import os
# import functools 
import configparser
import json
#import requests
from dapr.clients import DaprClient

config = configparser.ConfigParser()
config.read('/home/mitmproxy/.mitmproxy/blocklist.ini')
BLOCKLIST_FILES = config.get('files', 'list')
BLOCKLIST_KEYWORDS = config.get('keywords', 'list')

class PacketFilter:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.proxy_authorizations = {} 
        # allowed_users.txt only contains a list of username 
        self.user_list = self.load_users("/home/mitmproxy/.mitmproxy/allowed_users.txt")
        self.blocklist_files = self.load_blocklist(BLOCKLIST_FILES)
        ctx.log.debug(f"Blocklist files: {self.blocklist_files}")
        self.blocklist_keyword = self.load_blocklist(BLOCKLIST_KEYWORDS)
        ctx.log.debug(f"Blocklist keywords: {self.blocklist_keyword}")
    
    def load_users(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Users file '{file_path}' not found")
        users = []
        with open(file_path, "r") as f:
            for line in f:
                users.append(line.strip())
        return users

    #接受字符串输入，用','为分隔符分割成多个子字符串，把子字符串去掉空格，存储在数组中
    def load_blocklist(self, blocklist_str):
        return [x.strip() for x in blocklist_str.split(",")]

    # verify whether the request is allowed 
    def http_connect(self, flow: http.HTTPFlow):
        # get proxy-authorization http://username@proxy_address:port
        proxy_auth = flow.request.headers.get("Proxy-Authorization", "")

        
        # verify username whether exist and be in user_list
        if not proxy_auth:
            flow.response = http.Response.make(401)
            return

        auth_type, auth_string = proxy_auth.split(" ", 1)
        username = base64.b64decode(auth_string).decode("utf-8").replace(":", "")
        
        if not (username in self.user_list):
            flow.response = http.Response.make(401)
            return
        
        ctx.log.info("Authenticated User: " + username + "@" + flow.client_conn.address[0])
        self.proxy_authorizations[(flow.client_conn.address[0])] = username

    # check if the request is allowed
    def is_allowed(self, prompt):
        # check if the request is allowed
        for keyword in self.blocklist_keyword:
            if prompt.find(keyword) != -1:
                return False
        for file in self.blocklist_files:
            if prompt.find(file) != -1:
                return False
        return True
    
    async def record_debug(self, username, prompt, is_allowed):
        #daprPort = 3500
        #stateStoreName = "statestore"
        #stateUrl = f"http://localhost:{daprPort}/v1.0/state/{stateStoreName}"
        daprPort = os.getenv("DAPR_HTTP_PORT", 3500)
        PUBSUB_NAME = 'promptpubsub'
        TOPIC_NAME = 'prompts'        
        dapr_url = f"http://localhost:{daprPort}/v1.0/publish/{PUBSUB_NAME}/{TOPIC_NAME}"
        data=json.dumps({
            'user': username,
            'time': datetime.utcnow().isoformat(),
            'allowed': is_allowed,
            'prompt': prompt
        })
        try:
            ctx.log.debug(f"Record: {data}")
            ctx.log.debug(f"Record: {dapr_url}")
            # response = requests.post(dapr_url, json=data, timeout=5, headers = {'Content-Type': 'application/json'} )
            # if not response.ok:
            #     print('HTTP %d => %s' % (response.status_code,
            #                             response.content.decode('utf-8')), flush=True)
        except Exception as e:
            print(e, flush=True)

    async def record(self, username, prompt, is_allowed):
        PUBSUB_NAME = 'promptpubsub'
        TOPIC_NAME = 'prompts'
        data_to_record=json.dumps({
                    'user': username,
                    'time': datetime.utcnow().isoformat(),
                    'allowed': is_allowed,
                    'prompt': prompt
                })
        ctx.log.debug(f"Record: {data_to_record}")
        
        try:
            with DaprClient() as client:
                #Using Dapr SDK to publish a topic
                result = client.publish_event(
                    pubsub_name=PUBSUB_NAME,
                    topic_name=TOPIC_NAME,
                    data=data_to_record,
                    data_content_type='application/json',
                )
            ctx.log.debug('Published.')
        except Exception as e:
            print(e, flush=True)
    
    def request(self, flow: http.HTTPFlow):
        if flow.request.url.find("completions") == -1:
            return
        # get username from proxy_authorizations
        username = self.proxy_authorizations.get(flow.client_conn.address[0])
        
        try:
            # convert flow.request.content into json object
            data = json.loads(flow.request.content)
            #is_allowed = self.is_allowed(flow.request.content.decode('utf-8', 'ignore'))
            is_allowed = self.is_allowed(data['prompt'])
            #ctx.log.debug( f"Prompt: {data['prompt']}")
            # record the request
            #asyncio.ensure_future(self.record_debug(username, data['prompt'], is_allowed))
            asyncio.ensure_future(self.record(username, data['prompt'], is_allowed))

            # if is_allowed is false, then drop the request, set the response body to "Blocked"
            # and set the response code to 403
            if not is_allowed:
                flow.response = http.Response.make(403, b"Blocked")
                return

        except json.JSONDecodeError as e:
            ctx.log.error(f'Failed to decode request content: {e}')
            return

        return

addons = [
    PacketFilter()
]
