#!/usr/bin/env python3

# convert CSV generated by cvent to ldap
# requires python-ldap

# TODO:
# * optimize modifications of ldap database and do it in one go

import argparse
import sys
import csv
import ldap
import threading
import getpass
import datetime

csv_fields = [ 'Name', 'Surname', 'Email', 'Company',
               'Title', 'Registration Type', 'Confirmation Number',
               'Last Registration Date (GMT)',
               'Discount Code', 'Current Voucher Code', 'Amount Paid']


# 'cn' and 'objectClass' are treated separately
ldap_fields = ['givenName', 'sn', 'title', 'organizationName',
               'employeeType', 'userPassword', 'labeledURI', 'mail',
               'pager', 'displayName', 'initials', 'businessCategory']

ldap_modify_fields = ['title', 'organizationName', 'employeeType',
                      'userPassword', 'labeledURI', 'pager',
                      'businessCategory']
#
# LDAP machinery.
#
ldap_search_base = 'dc=users,dc=lpc,dc=events'
ldap_search_filter = '(cn=%s)'
ldap_attrs = ['givenName', 'sn', 'labeledURI', 'businessCategory']
ldap_conn = None
ldap_lock = threading.Lock()


def ldap_connect(passwd):
    LDAP_SERVER = 'ldaps://directory.lpc.events'
    LDAP_USER = 'cn=admin,dc=lpc,dc=events'

    global ldap_conn
    ldap_conn = ldap.initialize(LDAP_SERVER)
    ldap_conn.simple_bind_s(LDAP_USER, passwd)


def ldap_lookup(email):
    with ldap_lock:
        return do_ldap_lookup(email)


def do_ldap_lookup(email):
    #
    # Query the LDAP server.
    #
    ss = ldap_search_filter % (email)
    try:
        results = ldap_conn.search_s(ldap_search_base, ldap.SCOPE_ONELEVEL, ss)
    except ldap.NO_SUCH_OBJECT:
        return None
    if not results:
        return None

    return results[0][1]


def ldap_add(email, dn, ldap_record):
    print("adding %s" % dn)

    mod = []
    for f in ldap_fields:
        mod.append((f, (ldap_record[f] or "none").encode("utf-8")))

    # add the 'cn' fields, one with '@' and another '.' for matrix
    cn = [email.encode("utf-8"), email.replace('@', '.').encode("utf-8")]
    mod.append(('cn', cn))

    # objectClass should be a list rather than string so it is easier to add
    # it manually than bother with conversions
    obj_class = 'inetOrgPerson organizationalPerson person'
    mod.append(('objectClass', obj_class.encode("utf-8").split()))

    ldap_conn.add_s(dn, mod)


def ldap_update(ldap_record):
    email = ldap_record['cn']
    dn = 'cn=%s,%s' % (email, ldap_search_base)

    old = ldap_lookup(email)
    if not old:
        ldap_add(email, dn, ldap_record)
        return

    print("updating %s" % dn)
    mod = []
    op = ldap.MOD_REPLACE
    for f in ldap_modify_fields:
        mod.append((op, f, ldap_record[f].encode("utf-8")))

    ldap_conn.modify(dn, mod)


def ldap_update_field(email, field, value):
    dn = 'cn=%s,%s' % (email, ldap_search_base)

    old = ldap_lookup(email)
    if not old:
        print("%s not found" % email)
        return

    print("updating %s to %s" % (dn, value))
    mod = [(ldap.MOD_REPLACE, field, value.encode("utf-8"))]
    ldap_conn.modify(dn, mod)


def date_convert(csv_date):
    try:
        reg_date = datetime.datetime.strptime(csv_date,
                                              '%Y-%m-%dT%H:%M:%S.000Z')
    except:
        reg_date = datetime.datetime.strptime(csv_date, '%d/%m/%y %H:%M')

    return reg_date


def csv_to_ldap(csv):
    display_name = "%s %s" % (csv['Name'], csv['Surname'])
    reg_date = date_convert(csv['Last Registration Date (GMT)'])
    pager = reg_date.strftime("%Y-%m-%d")
    category = 'Attendee'
    if 'speaker' in csv['Registration Type'].lower():
        category = 'moderator'

    ldap_record = {
        'cn':                   csv['Email'],
        'givenName':            csv['Name'],
        'sn':                   csv['Surname'],
        'title':                csv['Title'],
        'organizationName':     csv['Company'],
        'userPassword':         csv['Confirmation Number'],
        'labeledURI':           csv['Confirmation Number'],
        'mail':                 csv['Email'],
        'employeeType':         csv['Registration Type'],
        'displayName':          display_name,
        'initials':             display_name,
        'pager':                pager,
        'businessCategory':     category,
    }

    return ldap_record


def read_csv(filename):
    with open(filename, "r") as file:
        data = list(csv.reader(file, delimiter=","))

    reg_list = []
    for line in data[1:]:
        reg = dict(zip(csv_fields, line))
        reg_list.append(reg)

    return reg_list


def update_roles(emails, filename, field, value):
    if not emails:
        emails = []

    if filename:
        with open(filename, "r") as file:
            emails += [x.strip() for x in file.readlines()]

    for email in emails:
        ldap_update_field(email, field, value)


def process_csv(csv):
    if not csv:
        return

    reg_list = read_csv(csv)
    ldap_records = [csv_to_ldap(x) for x in reg_list]

    for r in ldap_records:
        try:
            ldap_update(r)
        except:
            print("Failed to process '%s'" % r['cn'], file=sys.stderr)



def get_args(cmd):
    p = argparse.ArgumentParser(cmd)
    p.add_argument("-c", "--csv", help="cvent CSV file")
    p.add_argument("-A", "--admins-file", help="file with admin emails")
    p.add_argument("-a", "--admins", action='append',
                   help="coma separated admin emails")
    p.add_argument("-M", "--moderators-file",
                   help="file with moderators emails")
    p.add_argument("-m", "--moderators", action='append',
                   help="coma separated moderator emails")

    return vars(p.parse_args())


def main(args):
    args = get_args(args[0])
    print(args)

    if not any(args.values()):
        print("Nothing to do")
        return

    passwd = getpass.getpass()
    ldap_connect(passwd)

    process_csv(args['csv'])
    update_roles(args['moderators'], args['moderators_file'],
                 'businessCategory', 'moderator')
    update_roles(args['admins'], args['admins_file'],
                 'businessCategory', 'admin')


if __name__ == '__main__':
    main(sys.argv)
