from __future__ import print_function

__author__ = 'Mark'

import urllib2
import cookielib
import re



codes = [ "8967", #Processor
             "8090", #HDD
             "9374", #RAM 1333
             "9375", #RAM 1600
             "8988", #Motherboard
             "8705", #Blu-Ray writer
             "9748", #Wireless Network
             "2746", #TPLink Switch
             "8595"] #Netgear Switch

cookies = cookielib.LWPCookieJar()
handlers = [
    urllib2.HTTPHandler(),
    urllib2.HTTPSHandler(),
    urllib2.HTTPCookieProcessor(cookies)
]

opener = urllib2.build_opener(*handlers)

def multikeysort(items, columns):
    from operator import itemgetter
    comparers = [ ((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1)) for col in columns]
    def comparer(left, right):
        for fn, mult in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return mult * result
        else:
            return 0
    return sorted(items, cmp=comparer)

def fetch (uri):
    req = urllib2.Request(uri)
    return opener.open(req)

def main():
    print("Watching MSY products\n")

    uri = "http://www.msy.com.au/index.jsp"
    fetch(uri)

    data = "7|0|7|http://www.msy.com.au/SelectMethod/|D2FE8D58D5A8C97208FC7AEB987FF4B1|au.com.msy.web.gwt.client.SessionService|orderForPickup|java.lang.String/2004016611|ACT|Fyshwick|1|2|3|4|2|5|5|6|7|"
    headers = {"Content-Type": "text/x-gwt-rpc; charset=utf-8",
               "X-GWT-Permutation": "A1BF40EE68ED4796AD73BE1AC0A98E27",
               "X-GWT-Module-Base": "http://www.msy.com.au/SelectMethod/",
               "Referer": "http://www.msy.com.au/selectMethod.jsp"}

    uri = "http://www.msy.com.au/SessionService"

    print("Initialising ...", end=" ")

    req = urllib2.Request(uri, data, headers)
    res = opener.open(req)
    if "OK" in res.read():
        print("ok")
    else:
        print("failed")

    res.close()

    p = re.compile(r"^.*<span>(.*)</span>.*$")
    p2 = re.compile(r"^.*<span class=.+?>(.*)</span>.*$")

    products = []

    for code in codes:
        print("%s ..." % code, end=" ")
        uri = "http://www.msy.com.au/product.jsp?productId=%s" % code
        res = fetch(uri)

        maxNameLen = 50

        name = ""
        stock = ""
        price = ""
        lines = res.read().split("\n")
        for line in lines:
            if "Name:" in line:
                name = p.match(line).group(1).strip()
                if len(name) > maxNameLen:
                    name = name[:maxNameLen-3] + "..."
            elif "Our Price:" in line:
                price = p2.match(line).group(1).strip()
            elif "Stock" in line:
                stock = p.match(line).group(1).strip()
                break

        if name:
            print("ok")
            products.append({"name":name, "stock":stock, "price":price})
        else:
            print("failed")

        res.close()

    products = multikeysort(products, ['-stock', 'name'])

    print()
    for product in products:
        print("%s: %s - %s" % (product['stock'].rjust(13), product['name'].ljust(50), product['price']))

if __name__ == "__main__":
    main()