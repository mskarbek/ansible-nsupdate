# ansible-nsupdate
Like [nsupdate(8)](http://linux.die.net/man/8/nsupdate) ansible-nsupdate is used to submit Dynamic DNS Update requests.

### Requirements
  * [dnspython](http://www.dnspython.org/) - implemented with 1.12.0, it's possible that earlier versions may work
  * enabled and properly configured secure updates in DNS server

### TODO
  * implement remaining of the record types
  * implement proper error handling

#### Pros
  * works (most of the time)

#### Cons
  * crappy implementation
  * only basic error handling

## Options

parameter | required | default | choices | comments
--------- | -------- | ------- | ------- | --------
server | yes | | | DNS master server IP address
key_name | yes | | | TSIG key name
key_secret | yes | | | TSIG key secret
zone | yes | | | DNS zone to update, fo example `example.com.` - dot at the end required
record | yes | | | DNS record to update
type | no | A | A, CNAME | DNS record type, currently available A and CNAME
ttl | no | 60 | | DNS record TTL in seconds
value | no | | | DNS record value
state | no | present | present, absent | Whether the record should exist or not, taking action if the state is different from what is stated

## Example usage

#### Adding record:
    ---
    - hosts: localhost
      connection: local
      tasks:
        - name: add record
          nsupdate: >
            server=10.0.1.2
            key_name=rndc-key
            key_secret="XXXXXXXXXXXXXXXXXXXXXX=="
            zone=example.com.
            record=test
            value=10.0.1.30

#### Removing record:
    ---
    - hosts: localhost
      connection: local
      tasks:
        - name: delete record
          nsupdate: >
            server=10.0.1.2
            key_name=rndc-key
            key_secret="XXXXXXXXXXXXXXXXXXXXXX=="
            zone=example.com.
            record=test
            state=absent
