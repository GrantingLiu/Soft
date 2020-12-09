
xrange = "c1 fe 09 ce 00 00 00 00 00 00 00 00 00 00 00"

def data_change(str):      #发送指令
    inp_s = str
    if inp_s != "":
        inp_s = inp_s.strip()
        print("hex inp_s", inp_s)
        get_list = []
        while inp_s != '':
            try:
                numb = int(inp_s[0:2], 16)
            except ValueError:
                return None
            inp_s = inp_s[2:].strip()
            get_list.append(numb)
        inp_s = bytes(get_list)
        print("byte inp_s", inp_s) 
    return inp_s

string = data_change(str=xrange)
t = None
for i in range(len(string)):
    if i:
        t ^= string[i]
    else:
        t = string[i] ^ 0
print(hex(t))