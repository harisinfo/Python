#!/usr/bin/python
import pprint
import re, string
import sys, getopt
import MySQLdb

#connect to DB server
def connectToDbServer( dbServerHost, dbServerUser, dbServerPassword ):
    connection = MySQLdb.connect(
                    host = dbServerHost,
                    user = dbServerUser,
                    passwd = dbServerPassword
                )
    try:
      cursor = connection.cursor()
      return cursor;
    except:
      return "FALSE";

def usage( errorCode ):
    print "/usr/bin/python populate-data.py --source-database <source_database> --target-database <target_database> --input-file <file_name_to_get_data_from>", errorCode 
    return;

def checkIfValExistsInGrid( haystack, needle, bucket ):
      exists = 0
      for ii in range( len( haystack ) ):
        for jj in range( len( haystack[ ii ] ) ):
          if haystack[ ii ][ jj ].find( needle ) != -1:
            exists = bucket[ ii ][ jj ]
      return exists;    
        
          

#initialise variables
sourcedb = ''
targetdb = ''
inputfile = ''
strip_from_table_name = "(),'"
show_create_table = []
constraint_table = []
constraint_table_query = []
constraint_table_name_query = []
constraint_tables_import = []
table_import_list = []

try:
    opts, args = getopt.getopt( sys.argv[1:], "s:t:i:h", [ 'source-database=', 'target-database=', 'input-file=', 'help' ] )
except getopt.GetoptError:
    usage( 1 )
    sys.exit( 1 )


for opt, arg in opts:
  if opt == '--source-database':
    sourcedb = arg
  elif opt == '--target-database':
    targetdb = arg
  elif opt == '--input-file':
    inputfile = arg
  else:
    usage( 2 )
    sys.exit( 2 )
    
try:
  f = open( inputfile, 'r' )
except:
  print "Unknown input file ", inputfile
  sys.exit( 3 )

cursor = connectToDbServer( 'myserver.net', 'my_user', 'my_password' )

try:
    cursor.execute( "USE " + sourcedb )
except:
    print "Could not select ", sourcedb, " access denied or database with the name ", sourcedb, " does not exist"
    sys.exit
  
for line in f:
    newline = line.rstrip('\r\n')
    if newline != '':
      #print newline
      cursor.execute( "SHOW CREATE TABLE " + newline )
      show_create_table.append( cursor.fetchall() ) 
    else:
      newline = line.rstrip( '\r\n' )
      print "Unknown table / incorrect entry for ", newline


for show_create_raw_sql in show_create_table:
  for show_create_table_name, show_create_table_query in show_create_raw_sql:
    if "CONSTRAINT" in  str(show_create_table_query):
      constraint_table_query.append( [ show_create_table_query, show_create_table_name ] )
    else:
      table_import_list.append( show_create_table_name )
                       

outer_index = 0;
for constraint_query, table_name in constraint_table_query:
  if constraint_query != '':
    begin = 0
    inner_index = 0;
    constraint_table_name_query.append( [ ] )
    constraint_tables_import.append( [ ] )
    while begin <= len( constraint_query ) and begin >= 0:
    #begin(start) will loop to -1 when the array is out of bound
      start = constraint_query.find( 'CONSTRAINT', begin )
      end = constraint_query.find( ',', start )
      query = constraint_query[ start:end ]
      
      constraint_table_name_query[ outer_index ].append( [ ] )
      constraint_tables_import[ outer_index ].append( [ ] )
            
      constraint_table_name_query[ outer_index ][ inner_index ] =  query
      constraint_tables_import[ outer_index ][ inner_index ] =  table_name
       
      inner_index += 1
      #extract everything in between start and end, within this loop sets begin with the value of end
      begin = end
    outer_index += 1
  else:
    print "Incorrect constraint_query"
    
table_import_order = 0;   
for i in range( len( constraint_table_name_query ) ):
  for j in range( len( constraint_table_name_query[ i ] ) ):
    v = checkIfValExistsInGrid( constraint_table_name_query, "REFERENCES `" + constraint_tables_import[ i ][ j ], constraint_tables_import )
    if j == 0:
      if v == 0:
        table_import_list.append( constraint_tables_import[ i ][ j ] )
      if v  != 0:
        # position of where the string exists - 1
        xindex = table_import_list.index( v )
        if xindex > 0:
          table_import_list.insert( xindex - 1, constraint_tables_import[ i ][ j ] )
        else:
          table_import_list.insert( 0, constraint_tables_import[ i ][ j ] )
  
# finally print out the tables in the right order to populate data
print ' '.join( str( x ) for x in table_import_list )      
      