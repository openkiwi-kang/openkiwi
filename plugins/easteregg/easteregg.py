from flask import Blueprint,redirect,flash

plugin = Blueprint('easteregg',__name__)

@plugin.route('/easteregg')
def index():
    return """
<!DOCTYPE html>
<html>
<h2>The Zen of Openkiwi, by openkiwi kang</h2>
<br>
<p>Beautiful is better than ugly.</p>
<p>Comfortable is better than uncomfortable.</p>
<p>Extension is important.</p>
<p>We should always keep security in mind.</p>
<p>Performance should be considered after security.</p>
</html>
    """
