import html

def parser_kiwi(title,data):
    data = html.escape(data)
    output = "<h2>"+title+"</h2>\n"+"<p>"+data+"<p>"
    #output is output_html
    return output
