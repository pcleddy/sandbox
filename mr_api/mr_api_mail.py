from dominate.tags import *

MR_URL = 'https://mr.jpl.nasa.gov'
MR_HISTORY = '%s/requests' % MR_URL

def generate_mail_dom(autostart):

    startmonitor = autostart.startmonitor
    mr_id = 'MR-PR%d' % startmonitor.id

    h = html()
    with h.add(body()).add(div(id='message')) as m:
        mon_req = a('monitor request', href=MR_URL)
        mon_hist = a('your monitor request history')
        m.add(p('The following ', mon_req,
                'has failed automated provisioning for monitoring.'))
        m.add(p('If possible please affect the necessary changes to resolve ',
                'the errors in the table below, then you may "retry" ',
                'the automated provisioning from ', mon_hist, '.'))
