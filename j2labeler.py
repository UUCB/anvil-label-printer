from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
import pdfkit
import string
import random
import os
import barcode

import anvil.server

anvil.server.connect(os.getenv('J2L_ANVIL_KEY'))

debug = bool(os.getenv('J2L_DEBUG'))
printer_name = os.getenv('J2L_PRINTER')


def __init__():
    pass


env = Environment(
    loader=FileSystemLoader("./"),
    autoescape=select_autoescape(),
)

options = {
    'page-width': 1 * 25.4,
    'page-height': 1 * 25.4,
    'margin-top': '0in',
    'margin-bottom': '0in',
    'margin-right': '0in',
    'margin-left': '0in',
}


def generate_barcode(data: str) -> str:
    code = barcode.Code128(data)
    return code.render(
        writer_options={
            'text_distance': 4,
            'module_width': 0.6,
        }
    ).decode('utf-8')


@anvil.server.callable
def print_label(label_vars: dict, template: str, wkhtml_options: dict={},):
    job_id = 'label_temp/' + ''.join(random.choices(string.ascii_letters, k=10))
    template = env.get_template(template)
    if 'barcode' in label_vars.keys():
        label_vars[f'{label_vars["barcode"]}_barcode'] = generate_barcode(label_vars[label_vars['barcode']])
    pdfkit.from_string(
        template.render(label_vars=label_vars), # Returns a string of HTML
        job_id, # Random filename to avoid Weird Crap (tm)
        options=wkhtml_options, # Pass in options from the Anvil app
    )
    os.system(f'lp -d {printer_name} -ofit-to-page {job_id}')
    if not debug:
        os.remove(job_id)
        print(f'printed label {job_id}')


@anvil.server.callable
def ping():
    print('ping')
    return True


anvil.server.wait_forever()

