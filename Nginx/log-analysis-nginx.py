#!/usr/bin/python
import pprint
import re, string
import sys, getopt
import gzip


def usage( errorCode ):
	print "/usr/bin/python perform-analysis-i.py --input-file <input_file> --search-param-optional <field_1:field_2> --search-param-strict <field_1:field_2> --extract-field"
	print "allowed values for ---search-param-strict"
	print "remote_address, time_local, status_code, referrer, ua, request"
	return;


try:
    opts, args = getopt.getopt( sys.argv[1:], "i:f:s:e:h", [ 'input-file=', 'search-param-optional=', 'search-param-strict=', 'extract-field=', 'help' ] )
except getopt.GetoptError:
    usage( 1 )
    sys.exit( 1 )

inputfile = ''
allowed_delimiters_list =[ '\s', '\t' ]
searchparamstrict = ''
fieldsyntax = ''
extractfield = ''



for opt, arg in opts:
	if opt == '--input-file':
		inputfile = arg
	elif opt == '--search-param-optional':
		fieldsyntax = str( arg ).strip()
	elif opt == '--search-param-strict':
		searchparamstrict = str( arg ).strip()
	elif opt == '--extract-field':
		extractfield = str( arg ).strip()
	else:
		print "do nothing"
		usage( 2 )
		sys.exit( 2 )

try:
        if ".gz" in str( inputfile ):
                f = gzip.open( inputfile )
        else:
                f = open( inputfile, 'r' )
except:
        usage( 1 )
        sys.exit( 3 )

'''

Nginx Log rule: $remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent" "$http_x_forwarded_for"

Example: 88.5.132.162 - - [16/Jul/2013:03:20:12 +0100] "GET /json/my/get/request HTTP/1.1" 200 2313 "http://www.harisinfo.co.uk/" "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)"

Pattern to match:string\s-\sstring\s[string]\s"string"\sstring\sstring\s"string"\s"string"\s"string"

'''

if extractfield != "":
        arrExtractField = extractfield.split( ":" )

extractedLine = ""
extractedVariable = ""
for extractedField in arrExtractField:
        extractedVariable = extractedVariable + "$" + extractedField + "\t"

print extractedVariable
t = string.Template( extractedVariable )

regularExpressionSearchParam = searchparamstrict.strip().replace( ":", "|" )

patternToMatchIP = "^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\s"
patternToMatchTimeLocal = re.compile( r"\s\[\S+\s*\S*\]" )
patternToMatchStatusCode = re.compile( r"\"\s[0-9]{3}\s" )
patternToMatchRequest = re.compile( r"\]\s\"\S+\s\S+\s\S+\"\s" )
patternToMatchReferer = re.compile( r"\d{1}\s\"\S+\"" )
patternToMatchUserAgent = re.compile( r"\"{1}\s{1}\"[\s\S]*\"{1}$" )

for line in f:
        newline = line.strip().rstrip('\r\n')

        if re.compile( r"%s" % regularExpressionSearchParam ).search( newline, 0 ):
                ip = re.match( patternToMatchIP, newline )
                s = patternToMatchStatusCode.search( newline, 0 )
                d = patternToMatchTimeLocal.search( newline, 0 )
                req = patternToMatchRequest.search( newline, 0 )
                ref = patternToMatchReferer.search( newline, 0 )
                useragent = patternToMatchUserAgent.search( newline, 0 )

                v_remote_address = newline[ ip.start():ip.end() ].replace( '"','' ).strip()
                v_time_local = newline[ d.start():d.end() ].replace( "]", "" ).replace( "[", "" ).strip()
                v_status_code = newline[ s.start():s.end() ].replace( '"','' ).replace( ']', '' ).replace( '[', '' ).strip()
                v_referrer = newline[ ref.start() + 1:ref.end() ].replace( '"','' ).replace( ']', '' ).replace( '[', '' ).strip()
                v_ua = newline[ useragent.start():useragent.end() ].replace( '"','' ).replace( ']', '' ).replace( '[', '' ).strip()

                if req:
                                v_request = newline[ req.start():req.end() ].replace( '"', '' ).replace( ']', '' ).strip()
                else:
                                v_request = ""

                print t.substitute( remote_address=v_remote_address, time_local=v_time_local, status_code=v_status_code, referrer=v_referrer, ua=v_ua, request=v_request )