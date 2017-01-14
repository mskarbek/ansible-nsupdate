#!/usr/bin/python

from binascii import Error as binascii_error

try:
    import dns.update
    import dns.query
    import dns.tsigkeyring
    import dns.message
    import dns.resolver
    HAVE_DNSPYTHON=True
except:
    HAVE_DNSPYTHON=False


class Record(object):
    def __init__(self, module):
        self.module         = module
        self.state          = module.params['state']
        self.server         = module.params['server']
        if module.params['zone'][-1] != '.':
            self.zone       = module.params['zone'] + '.'
        else:
            self.zone       = module.params['zone']
        self.record         = module.params['record']
        self.type           = module.params['type']
        self.ttl            = module.params['ttl']
        self.value          = module.params['value']
        if module.params['key_name']:
            try:
                self.keyring    = dns.tsigkeyring.from_text({
                    module.params['key_name'] : module.params['key_secret']
                })
            except TypeError:
                module.fail_json(msg='Missing key_secret')
            except binascii_error as kre:
                module.fail_json(msg='TSIG key error: {}'.format(str(kre)))
        else:
            self.keyring    = None
        if module.params['key_algorithm'] == 'hmac-md5':
            self.algorithm  = 'HMAC-MD5.SIG-ALG.REG.INT'
        else:
            self.algorithm  = module.params['key_algorithm']

    def create_record(self):
        update = dns.update.Update(self.zone, keyring=self.keyring, keyalgorithm=self.algorithm)
        update.add(self.record, self.ttl, self.type, self.value)

        try:
            response = dns.query.tcp(update, self.server, timeout=10)
            if dns.message.Message.rcode(response) == 0:
                return True
            else:
                return False
        except:
            self.module.fail_json(msg='Connection to DNS server failed')

    def modify_record(self):
        update = dns.update.Update(self.zone, keyring=self.keyring, keyalgorithm=self.algorithm)
        update.replace(self.record, self.ttl, self.type, self.value)

        try:
            response = dns.query.tcp(update, self.server, timeout=10)
            if dns.message.Message.rcode(response) == 0:
                return True
            else:
                return False
        except:
            self.module.fail_json(msg='Connection to DNS server failed')

    def remove_record(self):
        update = dns.update.Update(self.zone, keyring=self.keyring, keyalgorithm=self.algorithm)
        update.delete(self.record, self.type)

        try:
            response = dns.query.tcp(update, self.server, timeout=10)
            if dns.message.Message.rcode(response) == 0:
                return True
            else:
                return False
        except:
            self.module.fail_json(msg='Connection to DNS server failed')

    def record_exists(self):
        update = dns.update.Update(self.zone, keyring=self.keyring, keyalgorithm=self.algorithm)
        update.present(self.record, self.type)

        try:
            response = dns.query.tcp(update, self.server, timeout=10)
            if dns.message.Message.rcode(response) == 0:
                if self.state == 'absent':
                    return True
                update.present(self.record, self.type, self.value)
                response = dns.query.tcp(update, self.server, timeout=10)
                if dns.message.Message.rcode(response) == 0:
                    return True
                else:
                    return 2
            else:
                return False
        except:
            self.module.fail_json(msg='Connection to DNS server failed')

def main():
    tsig_algs = ['HMAC-MD5.SIG-ALG.REG.INT', 'hmac-md5', 'hmac-sha1', 'hmac-sha224',
                 'hmac-sha256', 'hamc-sha384', 'hmac-sha512']

    module = AnsibleModule(
        argument_spec = dict(
            state=dict(required=False, default='present', choices=['present', 'absent'], type='str'),
            server=dict(required=True, type='str'),
            key_name=dict(required=False, type='str'),
            key_secret=dict(required=False, type='str'),
            key_algorithm=dict(required=False, default='hmac-md5', choices=tsig_algs, type='str'),
            zone=dict(required=True, type='str'),
            record=dict(required=True, type='str'),
            type=dict(required=False, default='A', type='str'),
            ttl=dict(required=False, default=3600, type='int'),
            value=dict(required=False, default=None, type='str')
        ),
        supports_check_mode=True
    )

    if not HAVE_DNSPYTHON:
        module.fail_json(msg='python library dnspython required: pip install dnspython')

    record = Record(module)

    success = None
    result = {}
    result['server'] = record.server
    result['zone'] = record.zone
    result['record'] = record.record
    result['type'] = record.type
    result['ttl'] = record.ttl
    result['value'] = record.value
    result['state'] = record.state

    exists = record.record_exists()

    if record.state == 'absent':
        if exists:
            if module.check_mode:
                module.exit_json(changed=True)
            success = record.remove_record()
            if success != True:
                module.fail_json(msg='Failed to delete DNS record')
            result['changed'] = True
    elif record.state == 'present':
        if not exists:
            if module.check_mode:
                module.exit_json(changed=True)
            success = record.create_record()
            result['changed'] = True
        elif exists == 2:
            success = record.modify_record()
            result['changed'] = True
        else:
            result['changed'] = False
        if success is not None and success != True:
            module.fail_json(msg='Failed to update DNS record')

    module.exit_json(**result)

# import module snippets
from ansible.module_utils.basic import *
main()
