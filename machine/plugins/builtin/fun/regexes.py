import re

ip_middle_octet = "(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5]))"
ip_last_octet = "(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"

url_regex = re.compile(
    "<(?P<url>"
    # protocol identifier
    "(?:(?:https?|ftp)://)"
    # user:pass authentication
    "(?:[-a-z\u00a1-\uffff0-9._~%!$&'()*+,;=:]+"
    "(?::[-a-z0-9._~%!$&'()*+,;=:]*)?@)?"
    "(?:"
    "(?:"
    # IP address exclusion
    # private & local networks
    "(?:(?:10|127)" + ip_middle_octet + "{2}" + ip_last_octet + ")|"
    "(?:(?:169\.254|192\.168)" + ip_middle_octet + ip_last_octet + ")|"
    "(?:172\.(?:1[6-9]|2\d|3[0-1])" + ip_middle_octet + ip_last_octet + "))"
    "|"
    # private & local hosts
    "(?:"
    "(?:localhost))"
    "|"
    # IP address dotted notation octets
    # excludes loopback network 0.0.0.0
    # excludes reserved space >= 224.0.0.0
    # excludes network & broadcast addresses
    # (first & last IP address of each class)
    "(?:"
    "(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
    "" + ip_middle_octet + "{2}"
    "" + ip_last_octet + ")"
    "|"
    # host name
    "(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)"
    # domain name
    "(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*"
    # TLD identifier
    "(?:\.(?:[a-z\u00a1-\uffff]{2,}))"
    ")"
    # port number
    "(?::\d{2,5})?"
    # resource path
    "(?:/[-a-z\u00a1-\uffff0-9._~%!$&'()*+,;=:@/]*)?"
    # query string
    "(?:\?\S*)?"
    # fragment
    "(?:#\S*)?"
    ")>",
    re.UNICODE | re.IGNORECASE
)
