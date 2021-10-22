"""
Austin Hunt
10/20/2021
basic socket-based web client that connects and sends
HTTP protocol messages to a web server
Execute with: python web_client.py host:port/path [METHOD]
"""
import socket
import sys
import re
import os
import datetime
from pathlib import Path


# Global Configuration
socket.setdefaulttimeout = 1
os.environ['no_proxy'] = '127.0.0.1,localhost'
linkRegex = re.compile('<a\s*href=[\'|"](.*?)[\'"].*?>')
CRLF = "\r\n\r\n"

class HTTPClient:
    def connect(self, host, port):
        """ Shared functionality across all HTTP methods.
        Set up TCP connection, clean up URL path if
        special chars present. """
        # create an INET, STREAMing socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set a timeout of 0.3 seconds
        s.settimeout(0.3)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # set up TCP connection
        s.connect((host, port))
        return s
    def request(self, host, port, path, method, data=None):
        """ Handle HTTP [GET, HEAD] requests """
        s = self.connect(host, port)
        request = (
            f"{method} {path} "
            f"HTTP/1.1\r\n"
            f"Host: {host}{CRLF}"
        )
        print(f"Request: \n{request}")
        s.send(request.encode())
        dataAppend = ''
        # wait for response from server
        try:
            while 1:
                data = (s.recv(4096))
                if not data: break
                else:
                    dataAppend += data.decode()
        except Exception as e:
            if 'timed out' in str(e):
                # Timeout, meaning nothing else is being received from server
                print(e)
            else:
                print(e)

        response = dataAppend
        # shutdown and close tcp connection and socket
        s.shutdown(1)
        s.close()
        # Save request/response pair to files in timestamped folder
        timestamp = datetime.datetime.now().strftime('%H:%m:%s')
        log_folder = f"./log/{timestamp}"
        Path(log_folder).mkdir(parents=True, exist_ok=True)
        with open(f'{log_folder}/request.log', 'w') as f:
            f.write(request)
        with open(f'{log_folder}/response.log', 'w') as f:
            f.write(response)
        return response


def test():
    url_tuple_list = [
          ('www.TaylorTJohnson.com', 80, '/test_cs5283_bad.html'),
          ('www.TaylorTJohnson.com', 80, '/test_cs5283.html')
    ]
    methods = ['GET', 'HEAD']
    client = HTTPClient()
    for url_index, url in enumerate(url_tuple_list):
        for method in methods:
            print(f'Attempting HTTP {method} on URL {url}')
            response = client.request(
                host=url[0],
                port=url[1],
                path=url[2],
                method=method)
            with open(f'responses/{method}/{url_index}.txt', 'w') as f:
                f.write(response)




if __name__ == "__main__":
    args = sys.argv
    if 'test' in args:
        test()
        sys.exit(0)
    try:
        host_port_path = args[1].replace('http://','').replace('https://','')
        if ':' in host_port_path:
            # Port specified
            host = host_port_path.split(':')[0]
            port_path = host_port_path.split(':')[1]
            port = int(port_path[:port_path.find('/')])
            path = port_path[port_path.find('/'):]
        else:
            # Port not specified, default = 80
            port = 80
            if '/' not in host_port_path:
                path = '/'
                print('No path provided, assuming root path /')
                host = host_port_path
            else:
                host = host_port_path[:host_port_path.find('/')]
                path = host_port_path[host_port_path.find('/'):]
        print(
            f'Host = {host}, Port = {port}, Path = {path}'
        )
        if len(args) > 2:
            method = args[2].upper()
        else:
            method = "GET"

        client = HTTPClient()
        response = client.request(host, port, path, method)
        print('Got response: ')
        print(response)

    except Exception as e:
        print(e)
        print(
            'Please execute this script as follows: '
            'python client.py host:port/[path] [METHOD]')
        sys.exit(1)