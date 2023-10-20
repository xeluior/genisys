import os
import textwrap
from suitable import Api
from pyarchops import helpers
from pyarchops_dnsmasq import dnsmasq

api = Api(
    '127.0.0.1:22',
    connection='smart',
    remote_user='root',
    private_key_file=os.getenv('HOME') + '/.ssh/id_rsa',
    become=True,
    become_user='root',
    sudo=True,
    ssh_extra_args='-o StrictHostKeyChecking=no'
)

dnsmasq_conf = textwrap.dedent('''
    no-poll
    no-resolv
    cache-size=1500
    no-negcache
    server=/core-vpn/10.16.254.1
    server=/core-vpn/10.16.254.2
    server=/core-vpn/10.16.254.3
    server=8.8.4.4
    server=8.8.8.8
''')

resolve_conf = 'nameserver 127.0.0.1'

config = {
    'dnmasq_conf': dnsmasq_conf,
    'resolv_conf': resolve_conf
}

result = dnsmasq.apply(api, config=config)
print(result)
