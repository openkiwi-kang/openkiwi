import html
import re

def parser_kiwi(title,data):
    data = html.escape(data)
    data = re.sub('\r\n','\n',data)
    data = re.sub('\n', '<br>', data)
    data = re.sub("&#x27;","'",data)
    data = textprocessing(data)
    print(data)
    output = "<h2>"+title+"</h2>\n"+"<p>"+data+"<p>"
    #output is output_html
    return output

def textprocessing(data):
    temp = data
    #Bold
    temp = re.sub('''[']{3}(?P<text>[^']*)[']{3}''',"<strong>\g<text></strong>",temp)
    #italic
    temp = re.sub('''[']{2}(?P<text>[^']*)[']{2}''',"<em>\g<text></em>",temp)
    #strikethrough1
    temp = re.sub('''[-]{2}(?P<text>[^-]*)[-]{2}''',"<del>\g<text></del>",temp)
    #strikethrough2
    temp = re.sub('''[~]{2}(?P<text>[^~]*)[~]{2}''',"<del>\g<text></del>",temp)
    #underline
    temp = re.sub('''[_]{2}(?P<text>[^_]*)[_]{2}''',"<u>\g<text></u>",temp)
    return temp
