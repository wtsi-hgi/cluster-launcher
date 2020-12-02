from aiohttp import web
import os
import subprocess

async def handler(request):
    print(dir(request))
    print(await request.read())
    return web.Response(text="Received")





'''    path = "../clusters/" + user
    if (os.path.isdir(path)):
        #If cluster file for user exists, do something
        pass
    else:
        subprocess.Popen(['bash', 'user-creation.sh', path])
        #os.mkdir(path)
        #os.mkdir(path + "terraform")


if __name__ == "__main__":
    username="an12"
    num_workers="2"
    public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSIYcwRdIM5Ny4I6613oSWsyQtnurMqwzMDFUxpz6fLPbg7+MoEfmetLoMgMywayS6rSF+GkFoG6zPMJoV0EnDlLwmWGjvCkwywtVo93mjtwkfdvEqgw5FOBG+UNumlwZI/kLLUSh9rD+5wIZXAWHRJ9n42XuQWDvadB4IOLlpS8M2YQVHnwcDQLb3fV4nBLpHOXuFQA6wNnwQjI1Fk5OXtmLPl9PkX5GGX3C9sPC81SDlO/gmtvWE33zF2/DYamAFU4BXOdrT3S6vHpmb7ihTwWu634BHPWA6iEPis3LOVsbzw9TC6RjMUomlvPWBkglovEXEf9RXIExF+wTi4XiB an12@mib114726i"
    flavor="m1.small"
    image_name="bionic-WTSI-docker_49930_38ab07e9"
    vol_name="NA"
    vol_size="1"
    device_name="NA"

    #1. Read username from cookie
    #2. Check if user already has a cluster
    #3a If yes, launch Jupter Notebook
    #3b. If no, let user create cluster
    startup(username, num_workers, public_key, flavor, image_name, vol_name, vol_size, device_name)
'''
