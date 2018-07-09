import html

def parser_kiwi(title,data):
    data = html.escape(data)
    output = "<h2>"+title+"</h2>\n"+"<h4>"+data+"</h4>"
    return output
