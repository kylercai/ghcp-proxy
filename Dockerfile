# use base image mitmproxy/mitmproxy:10.2.0
FROM mitmproxy/mitmproxy:10.2.0

# install the required packages
RUN pip install mitmproxy asyncio requests dapr

# copy the intercept script and the configuration files to the .mitmproxy directory
COPY packetfilter.py /home/mitmproxy/.mitmproxy/packetfilter.py
COPY allowed_users.txt /home/mitmproxy/.mitmproxy/allowed_users.txt
COPY blocklist.ini /home/mitmproxy/.mitmproxy/blocklist.ini
COPY config.ini /home/mitmproxy/.mitmproxy/config.ini

# create directory and copy mitmproxy certs
RUN mkdir -p /home/mitmproxy/.mitmproxy/certs
COPY ./certs /home/mitmproxy/.mitmproxy/certs


# set the working directory
WORKDIR /home/mitmproxy/.mitmproxy

# set the mitmproxy start command, with the addon
CMD ["mitmweb","--set", "confdir=/home/mitmproxy/.mitmproxy/certs","-s", "packetfilter.py", "-p", "8080", "--web-host", "0.0.0.0", "--listen-host", "0.0.0.0", "--set",  "block_global=false"]