# ansible-nsupdate
Like [nsupdate(8)](http://linux.die.net/man/8/nsupdate) ansible-nsupdate is used to submit Dynamic DNS Update requests.
Used with the recent versions of BIND and Knot DNS servers.

### Requirements
  * [dnspython](http://www.dnspython.org/) - implemented with 1.12.0, it's possible that earlier versions may work

### TODO
  * implement proper error handling

#### Pros
  * works

#### Cons
  * crappy implementation - don't expect any input validation
  * only basic error handling

## Options

parameter | required | default | choices | comments
--------- | -------- | ------- | ------- | --------
server | yes | | | DNS master server IP address
key_name | no | | | TSIG key name
key_secret | no | | | TSIG key secret
zone | yes | | | DNS zone to update, for example `test.com`, can be ended with dot
record | yes | | | DNS record to update
type | no | A | | DNS record type
ttl | no | 3600 | | DNS record TTL in seconds
value | no | | | DNS record value
state | no | present | present, absent | Whether the record should exist or not, taking action if the state is different from what is stated

## Example usage

#### Adding A record:
    ---
    - hosts: localhost
      connection: local
      tasks:
        - name: add A record
          nsupdate:
            server: 10.0.1.2
            key_name: rndc-key
            key_secret: "XXXXXXXXXXXXXXXXXXXXXX=="
            zone: example.com.
            record: test
            value: 10.0.1.30

#### Adding PTR record:
    ---
    - hosts: localhost
      connection: local
      tasks:
        - name: add PTR record
          nsupdate:
            server: 10.0.1.2
            zone: 13.168.192.in-addr.arpa.
            type: PTR
            record: 13.13.168.192.in-addr.arpa.
            value: test-13.test.com.

#### Removing record:
    ---
    - hosts: localhost
      connection: local
      tasks:
        - name: delete record
          nsupdate:
            server: 10.0.1.2
            zone: example.com
            record: test
            state: absent
