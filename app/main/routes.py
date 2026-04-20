from flask import render_template, redirect, url_for, session, request
from app.main import main
from app.main.forms import ContactForm


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/how-it-works')
def how_it_works():
    return render_template('main/how_it_works.html')


@main.route('/about')
def about():
    return render_template('main/about.html')


@main.route('/faq')
def faq():
    return render_template('main/faq.html')


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # TODO: send email via Flask-Mail
        return redirect(url_for('main.contact', sent=1))
    return render_template('main/contact.html', form=form)


@main.route('/set-lang/<lang>')
def set_lang(lang):
    from flask import current_app
    if lang in current_app.config['LANGUAGES']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('main.index'))
