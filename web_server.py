"""
Austin Hunt
10/20/2021
Simple HTTP web server using socket programming,
execute with: python server.py PORT DIRECTORY
"""
import sys
import socket
from socket import *
from os.path import exists
from PIL import Image
import datetime
import io
from time import mktime
from wsgiref.handlers import format_date_time

SERVER_NAME = 'Austin Hunt'
CRLF = '\r\n\r\n'

class HTTPServer:

    def __init__(self, document_root="~"):
        """ Create an HTTPServer object and initialize its document root
        (where it will look for requested files) """
        self.document_root = document_root

    def listen(self, host='localhost', port=80, buffer_size=1024 ):
        """ Starts an HTTP Server that begins listening at specified port
        and makes files available in specified directory """
        s = socket(AF_INET, SOCK_STREAM)
        s.bind((host, port))
        print(f'Address bound {host}:{port}, server now listening')
        s.listen(1)
        try:
            while True:
                connection, address = s.accept()
                print('\n\n')
                print(f'TCP Connection Established with {address}')
                with connection:
                    message = connection.recv(buffer_size)
                    if not message: break
                    print(message)

                    method = self.get_method(message)
                    print(f'Method = {method}')
                    if method == 'GET':
                        self.handle_get_request(connection, host, message)
                    elif method == 'HEAD':
                        self.handle_head_request(connection, host, message)
                    else:
                        # Functionality apart from GET/HEAD not supported
                        self.handle_other_methods(connection, host)

        except Exception as e:
            print(e)
            connection.shutdown(1)
            connection.close()
            sys.exit(1)

    def get_method(self, msg):
        """ Get the method from a request message """
        return msg.decode().split()[0]

    def handle_other_methods(self, connection, host):
        """ Handle 501 response (i.e. response to non-GET,
            non-HEAD requests, not supported """
        required_headers = {
            'Host': host,
            'Date': format_date_time(mktime(datetime.datetime.now().timetuple())),
            'Server': SERVER_NAME,
            # Don't send Content-Length for HEAD response
        }
        required_headers_string = ''.join(f'{k}: {v}\r\n' for k, v in required_headers.items())
        response_proto = 'HTTP/1.1'
        response_status = '501'
        response_status_descr = 'Not Implemented'
        full_msg = (
            f'{response_proto} {response_status} {response_status_descr}\r\n'
            f'{required_headers_string}{CRLF}'
        )
        connection.send(full_msg.encode())

    def handle_head_request(self, connection, host, message):
        """ Handle a HTTP HEAD request """
        print('Handling HEAD request')
        required_headers = {
            'Host': host,
            'Date': format_date_time(mktime(datetime.datetime.now().timetuple())),
            'Server': SERVER_NAME,
            # Don't send Content-Length for HEAD response
        }
        required_headers_string = ''.join(f'{k}: {v}\r\n' for k, v in required_headers.items())
        try:
            filepath = self.get_full_requested_path(message)
            response_proto = 'HTTP/1.1'
            if self.file_exists(filepath):
                response_status = '200'
                response_status_descr = 'OK'
            else:
                response_status = '404'
                response_status_descr = 'NOT FOUND'
        except Exception as e:
            response_status = '500'
            response_status_descr = f'Internal Server Error: {str(e)}'

        full_msg = (
            f'{response_proto} {response_status} {response_status_descr}\r\n'
            f'{required_headers_string}{CRLF}'
        )
        connection.send(full_msg.encode())

    def handle_get_request(self, connection, host, message):
        """ Handle a HTTP GET Request """
        print('Handling GET request')

        filepath = self.get_full_requested_path(message)
        response_proto = 'HTTP/1.1'

        if self.file_exists(filepath):
            response_status = '200'
            response_status_descr = 'OK'
            response_body = self.get_file_contents(filepath)
        else:
            response_status = '404'
            response_status_descr = 'NOT FOUND'
            response_body = f'File not found'

        required_headers = {
            'Host': host,
            'Date': format_date_time(mktime(datetime.datetime.now().timetuple())),
            'Server': SERVER_NAME,
            'Content-Length': len(response_body)
        }
        required_headers_string = ''.join(f'{k}: {v}\r\n' for k, v in required_headers.items())

        full_msg = (
            f'{response_proto} {response_status} {response_status_descr}\r\n'
            f'{required_headers_string}\n'
            f'{response_body}{CRLF}'
        )
        connection.send(full_msg.encode())


    def get_full_requested_path(self, msg):
        """ Translate the relative path in the request to the
        full path using the server's document root """
        requested_file = msg.decode().split()[1]
        # Client pre-converts '' to '/', will always at least be '/' here
        if requested_file == '/':
            requested_file = '/index.html'
        full_requested_path = f'{self.document_root}{requested_file}'
        if full_requested_path.startswith('//'):
            full_requested_path = full_requested_path[1:]
        print(f'File requested: {full_requested_path}')
        return full_requested_path

    def get_file_contents(self, filename):
        """ Get the contents of a file (existence is pre-verified) """
        if any([x in filename for x in ['jpg','JPG','png','PNG']]):
            img = Image.open(filename)
            output = io.BytesIO()
            img.save(output, format="png")
            return output.getvalue()

        with open(filename, 'r') as f:
            return f.read()

    def file_exists(self, filepath):
        """ Determine whether a request is valid (if a requested file exists) """
        return exists(filepath)

if __name__ == "__main__":
    args = sys.argv
    try:
        port = int(args[1])
        document_root = args[2]

        server = HTTPServer(document_root=document_root)
        server.listen(host='localhost', port=port, buffer_size=1024)
    except Exception as e:
        print(e)
        sys.exit(1)

