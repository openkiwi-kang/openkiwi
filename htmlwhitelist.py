from bleach.sanitizer import Cleaner

cleaner = Cleaner(tags=['blockquote','a', 'b', 'blockquote', 'code', 'del', 'dd', 'dl', 'dt', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'i', 'img', 'kbd', 'li', 'ol', 'p', 'pre', 's', 'sub', 'strong', 'strike', 'ul', 'br', 'hr', 'span', 'div', 'big']
, attributes={'a': ['href', 'title'],'img': ['src','width','height'],'span': ['style','class'],'div': ['style','class']}
, styles=['font-size','font-family','font-weight','background-color','color','text-align','text-decoration','text-transform','margin','display','border-top','border-bottom','border-left','border-right','border-width']
, protocols=['http', 'https']
, strip=False, strip_comments=True)

def parser_kiwi(title,input):
    return cleaner.clean(input)
