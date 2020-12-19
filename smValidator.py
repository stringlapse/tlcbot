# As of usual i do not think I have the brain power to make my own url regex so I stole how Django does it https://github.com/django/django/blob/stable/1.3.x/django/core/validators.py#L45
import re
def validatesURL(url):
    regex = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
    r'localhost|' # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    jury = regex.match(url)
    return jury is not None

def grabsTwitter(url):
    regex = re.compile(r'http(?:s)?:\/\/(?:www\.)?twitter\.com\/([a-zA-Z0-9_]+)')
    result = re.findall(regex,url)
    if len(result) == 0:
        return None
    return result[0]

def grabsTwitch(url):
    regex = re.compile(r'http(?:s)?://(?:www\.)?twitch\.tv/(\w+)')
    result = re.findall(regex,url)
    if len(result) == 0:
        return None
    
    return result[0]

def grabsInstagram(url):
    regex = re.compile(r'http(?:s)?://(?:www\.)?instagram\.com/(\w+)')
    result = re.findall(regex,url)
    if len(result) == 0:
        return None

    return result[0]

def grabsDeviantart(url):
    regex = re.compile(r'http(?:s)?://(?:www\.)?deviantart\.com/(\w+)')
    result = re.findall(regex,url)
    if len(result) == 0:
        return None

    return result[0]

def validatesYoutube(url):
    regex = re.compile(r'http(?:s)?://(?:www\.)?(?:m.)?youtube\.com/[c|channel|user]+/([\w-]+)')
    result = re.findall(regex,url)
    return len(result) != 0

    


    
