from flask import render_template
from main.docs import docs_bp


@docs_bp.route('/docs')
def docs():
    return render_template('docs/docs.html', title='Documentation')
