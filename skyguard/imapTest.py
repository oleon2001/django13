# Copyright (c) 2014, Menno Smits
# Released subject to the New BSD License
# Please see http://en.wikipedia.org/wiki/BSD_licenses

from __future__ import unicode_literals

from imapclient import IMAPClient

HOST = 'imap.zoho.com'
USERNAME = 'admin@ensambles.net'
PASSWORD = 'l6moSa5mgCpg'
ssl = True

server = IMAPClient(HOST, use_uid=True, ssl=ssl)
server.login(USERNAME, PASSWORD)

select_info = server.select_folder('INBOX')
print('%d messages in INBOX' % select_info['EXISTS'])

messages = server.search(['NOT', 'DELETED'])
print("%d messages that aren't deleted" % len(messages))

print
print("Messages:")
# Can be ALL BODY
# http://james.apache.org/server/rfclist/imap4/rfc2060.txt Section 6.4.5 FETCH command
response = server.fetch(messages, ['ENVELOPE','BODY[TEXT]'])
imeis = []
for msgid, data in response.iteritems():
	if data[b'ENVELOPE'].from_[0].name =='Bonafont':
		strs = data[b'BODY[TEXT]'].split()
		#print strs[-4],strs[-2],strs[-1]
		imeis.append("{0},{1},{2}".format(strs[0],strs[2],strs[3]))
		#print data[b'ENVELOPE'].subject
		
imeis.sort()
if imeis:
	a = [ imeis[0] ]
	for i in imeis[1:]:
		if i!= a[-1]:
			a.append(i)
else:
	a = []
		
server = IMAPClient(HOST, use_uid=True, ssl=ssl)
server.login(USERNAME, PASSWORD)

select_info = server.select_folder('Trash')
print('%d messages in TRASH' % select_info['EXISTS'])

messages = server.search(['NOT', 'DELETED'])
print("%d messages that aren't deleted" % len(messages))
response = server.fetch(messages, ['ENVELOPE','BODY[TEXT]'])
printeds = []
for msgid, data in response.iteritems():
	if data[b'ENVELOPE'].from_[0].name =='Bonafont':
		strs = data[b'BODY[TEXT]'].split()
		printeds.append("{0},{1},{2}".format(strs[0],strs[2],strs[3]))

printeds.sort()
if imeis:
	b = [ imeis[0] ]
	for i in imeis[1:]:
		if i!= b[-1]:
			b.append(i)
else:
	b= []
	
#for i in b:
#	try:
#		a.remove(i)
#	except:
#		pass
		
print ("Remaining items:"), len(a)
for i in a:
	print i
	
