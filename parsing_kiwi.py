import html

def parser_kiwi(title,data):
    data = html.escape(data)
    output = "<h2>"+title+"</h2>\n<br>"+"<h6>"+data+"</h6>"
    return output
