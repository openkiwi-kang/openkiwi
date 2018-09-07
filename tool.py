def check_ip( str_ip_addr, str_start_ip, subnetmask):

    ipaddr = list(str_ip_addr.split("."))
    ipaddr[0] = int(ipaddr[0])
    ipaddr[1] = int(ipaddr[1])
    ipaddr[2] = int(ipaddr[2])
    ipaddr[3] = int(ipaddr[3])
    startip = list(str_start_ip.split("."))
    startip[0] = int(startip[0])
    startip[1] = int(startip[1])
    startip[2] = int(startip[2])
    startip[3] = int(startip[3])
    if startip[0] > 255 or startip[1] > 255 or startip[2] > 255 or startip[3] > 255:
        return False
    if ipaddr[0] > 255 or ipaddr[1] > 255 or ipaddr[2] > 255 or ipaddr[3] > 255:
        return False
    if ipaddr[0] < 0 or ipaddr[1] < 0 or ipaddr[2] < 0 or ipaddr[3] < 0:
        return False
    if startip[0] < 0 or startip[1] < 0 or startip[2] < 0 or startip[3] < 0:
        return False
    print(ipaddr)
    print(startip)

    #temp1 = int(ipaddr[0])<<24 + int(ipaddr[1])<<16 + int(ipaddr[2])<<8 + int(ipaddr[3])
    #temp2 = int(startip[0])<<24 + int(startip[1])<<16 + int(startip[2])<<8 + int(startip[3])
    temp1 = int(ipaddr[0])*(2**24) + int(ipaddr[1])*(2**16) + int(ipaddr[2])*(2**8) + int(ipaddr[3])
    temp2 = int(startip[0])*(2**24) + int(startip[1])*(2**16) + int(startip[2])*(2**8) + int(startip[3])
    print(hex(temp1))
    print(hex(temp2))

    if int(temp1)>>(32-subnetmask) == int(temp2)>>(32-subnetmask):
       return True
    else:
       return False
