import subprocess


def getServiceSelectorTag(serviceName): 
    result = subprocess.check_output("kubectl describe service {serviceName}".format(serviceName=serviceName), shell=True).decode("utf-8")

    lines = result.split("\n")
    print(lines)
    for line in lines:
        split = line.split(": ")
        if len(split) == 2: 
            key, value = split
            if(key == "Selector"):
                #print("Selector is ",  value)
                #tagKey, tagValue = value.split("=")
                #tag = tagKey.strip() + ": " + tagValue.strip()
                #print("tag ", tag)
                return value.strip()

selector = getServiceSelectorTag("minimal-2-service")
print("selector ", selector)
deployment_name = subprocess.check_output("""kubectl get deployments --no-headers -l {selector} | awk '{{print $1}}'""".format(selector = selector), shell = True).decode("utf-8")
print("deployment name:", deployment_name)