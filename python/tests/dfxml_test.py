import py.test

from dfxml import *

def check_equal(a,b,want=None):
    da = dftime(a)
    db = dftime(b)
    result = da==db
    warn = ""
    if result != want:
        warn = " (!)"
    print("a=%s b=%s want=%s equal=%s%s" % (da,db,want,result,warn))

def check_greater(a,b,want=None):
    da = dftime(a)
    db = dftime(b)
    result = da>db
    warn = ""
    if result != want:
        warn = " (!)"
    print("a=%s b=%s want=%s greater=%s%s" % (da,db,want,result,warn))

def test_all():
    print("Testing unicode value parsing.")
    #Test base64 encoding of the "Registered" symbol, encountered in a key name in the M57-Patents corpus.
    test_unicode_string = "\xae"
    if sys.version_info.major == 2:
        #The test string doesn't quite get defined right that way in Python 2
        test_unicode_string = unicode(test_unicode_string, encoding="latin-1")
        test_unicode_string_escaped = test_unicode_string.encode("unicode_escape")
        test_base64_bytes = base64.b64encode(test_unicode_string_escaped)
    elif sys.version_info.major == 3:
        test_unicode_string_escaped = test_unicode_string.encode("unicode_escape")
        test_base64_bytes = base64.b64encode(test_unicode_string_escaped)
    else:
        #Just hard-code value, no examples yet for this language version.
        test_base64_bytes = b'XHhhZQ=='
    test_base64_string = test_base64_bytes.decode("ascii")
    #test_base64_string is the kind of string data you'd expect to encounter in base64-encoded values processing RegXML.
    assert test_unicode_string == safe_b64decode(test_base64_bytes)
    assert test_unicode_string == safe_b64decode(test_base64_string)
    print("Unicode value parsing good!")
    print("Testing time string parsing")
    test_rfc822tdatetime = rfc822Tdatetime("26 Jun 2012 22:34:58 -0700")
    assert test_rfc822tdatetime.tzinfo is not None
    print("Time string parsing good!")
    print("Testing dftime values")
    #check_equal("1900-01-02T02:03:04Z",-2208895016,True) #AJN time.mktime doesn't seem to support old times any more
    a_pacific_dftime = dftime("26 Jun 2012 22:34:58 -0700")
    assert 0.0 == dftime(a_pacific_dftime.iso8601()).timestamp() - a_pacific_dftime.timestamp()
    check_equal("2000-01-02T02:03:04Z","2000-01-02T03:03:04-0100",False)
    check_equal("2000-01-02T02:03:04-0100","2000-01-02T02:03:04-0100",True)
    check_equal("2000-01-02T02:03:04-0100","2000-01-02T02:03:04-0200",False)
    check_equal("2000-01-02T02:03:04-0100","2000-01-02T01:03:04-0200",True)
    check_greater("2000-01-02T04:04:05-0100","2000-01-02T03:04:05-0100",True)
    check_greater("2000-01-02T03:04:05-0200","2000-01-02T03:04:05-0100",True)
    check_greater("2009-11-17T00:33:30.9375Z","2009-11-17T00:33:30Z",True)
    check_equal("2009-11-17T00:33:30.9375Z","2009-11-17T00:33:30Z",False)
    check_equal("2009-11-17T00:33:30.0000Z","2009-11-17T00:33:30Z",True)
    check_equal("27 Jun 2012 06:02:00 -0000","27 Jun 2012 05:02:00 -0100",True)
    check_equal("27 Jun 2012 06:02:00 -0000","2012-06-27T06:02:00Z",True)
    check_equal("26 Jun 2012 22:34:58 -0700","2012-06-27T05:34:58Z", True)
    print("dftime values passed.")
    print("Testing byte_run overlap engine:")
    db = extentdb()
    a = byte_run(img_offset=0,len=5)
    db.add(a)
    b = byte_run(5,5)
    db.add(b)
    try:
        assert db.intersects(byte_run(0,5))==byte_run(0,5)
    except:
        print(type(cmp))
        print(db.intersects(byte_run(0,5)))
        print(byte_run(0,5))
        raise
    assert db.intersects(byte_run(0,1))
    assert db.intersects(byte_run(2,3))
    assert db.intersects(byte_run(4,1))
    assert db.intersects(byte_run(5,1))
    assert db.intersects(byte_run(6,1))
    assert db.intersects(byte_run(9,1))
    assert db.intersects(byte_run(-1,5))
    assert db.intersects(byte_run(-1,10))
    assert db.intersects(byte_run(-1,11))
    assert db.intersects(byte_run(-1,1))==None
    assert db.intersects(byte_run(10,1))==None
    print("Overlap engine good!")
    assert re.sub(rx_xmlns, "", """<fileobject xmlns="http://www.forensicswiki.org/wiki/Category:Digital_Forensics_XML">""") == "<fileobject>"
    assert re.sub(rx_xmlns, "", """<fileobject xmlns:dfxml="http://www.forensicswiki.org/wiki/Category:Digital_Forensics_XML">""") == "<fileobject>"
    assert re.sub(rx_xmlns, "", """<fileobject delta:new_file="1">""") == """<fileobject delta:new_file="1">"""
    assert re.sub(rx_xmlns, "", """<fileobject xmlns="http://www.forensicswiki.org/wiki/Category:Digital_Forensics_XML" attr="1">""") == """<fileobject attr="1">"""
    print("XML namespace regex good!")
