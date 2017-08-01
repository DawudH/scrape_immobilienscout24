from jinja2 import Environment, PackageLoader, select_autoescape


def construct_html_email(title, results, results_last_7_days):
    """ This function constructs the raw html file that can be send as an email """
    env = Environment(
        loader=PackageLoader('mailer', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template_results = env.get_template('results.html')
    template = env.get_template('main.html')

    # Create the body of the message.
    return template.render(title=title,
                           n_new_apartments=len(results),
                           results=template_results.render(results=results),
                           n_results_last_7_days=len(results_last_7_days),
                           results_last_7_days=template_results.render(results=results_last_7_days))