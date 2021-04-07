/* -*- mode: C++; c-basic-offset: 4; indent-tabs-mode: nil -*- */
/*
 * Simson's XML output class.
 * Include this AFTER your config file with the HAVE statements.
 * Optimized for DFXML generation.
 */

#ifndef DFXML_WRITER_H
#define DFXML_WRITER_H

#ifdef HAVE_SYS_CDEFS_H
#include <sys/cdefs.h>
#endif

#ifdef HAVE_SYS_RESOURCE_H
#include <sys/resource.h>
#endif

#ifdef HAVE_PWD_H
#include <pwd.h>
#endif

#ifdef HAVE_SYS_UTSNAME_H
#include <sys/utsname.h>
#endif

#ifdef HAVE_LIBTSK3
#include <tsk3/libtsk.h>
#endif

/* c++ */
#include <cinttypes>
#include <cstdio>
#include <cstring>
#include <ctime>
#include <fstream>
#include <map>
#include <mutex>
#include <set>
#include <sstream>
#include <stack>
#include <string>


#ifndef __BEGIN_DECLS
#if defined(__cplusplus)
#define __BEGIN_DECLS   extern "C" {
#define __END_DECLS     }
#else
#define __BEGIN_DECLS
#define __END_DECLS
#endif
#endif

#ifdef __cplusplus
class dfxml_writer {
public:
    /* This is the main interface: */
    dfxml_writer();                                            // defaults to stdout
    dfxml_writer(const std::string &outfilename,bool makeDTD); // write to a file, optionally making a DTD

    // adds the creator, build_environment, and execution environment
    void add_DFXML_creator(const std::string &program,const std::string &version,
                           const std::string &git_commit,
                           int argc, 
                           char * const *argv);
    
private:
    /*** neither copying nor assignment is implemented ***/
    dfxml_writer(const dfxml_writer &) = delete;
    dfxml_writer &operator=(const dfxml_writer &) = delete;

public:
    typedef std::map<std::string,std::string> strstrmap_t;
    typedef std::set<std::string> stringset_t;
    typedef std::set<std::string> tagid_set_t;

private:
    std::mutex     M;
    std::fstream   outf;
    std::ostream   *out;                  // where it is being written; defaults to stdout
    stringset_t    tags;                 // XML tags
    std::stack<std::string>tag_stack;
    std::string    tempfilename;
    std::string    tempfile_template;
    struct timeval t0;
    struct timeval t_last_timestamp;	// for creating delta timestamps
    bool           make_dtd;
    std::string    outfilename;
    bool           oneline;             // output entire DFXML on a single line

    void  write_doctype(std::fstream &out);
    void  write_dtd();
    void  verify_tag(std::string tag);
    void  spaces();                     // print spaces corresponding to tag stack


public:
    static std::string make_command_line(int argc,char * const *argv);
    static void cpuid(uint32_t op, unsigned long *eax, unsigned long *ebx,unsigned long *ecx, unsigned long *edx);
    virtual ~dfxml_writer(){};
    void   set_tempfile_template(const std::string &temp);

    static std::string xmlescape(const std::string &xml);
    static std::string xmlstrip(const std::string &xml);

    /** xmlmap turns a map into an XML block */
    static std::string xmlmap(const strstrmap_t &m,const std::string &outer,const std::string &attrs);

    void close();                       // writes the output to the file
    void flush(){ outf.flush(); }
    void tagout( const std::string &tag,const std::string &attribute);
    void push( const std::string &tag,const std::string &attribute);
    void push( const std::string &tag) {push(tag,"");}

    // writes a std::string as parsed data
    void puts( const std::string &pdata);

    // writes a std::string as parsed data
    void printf(const char *fmt,...) __attribute__((format(printf, 2, 3))); // "2" because this is "1"
    void pop(); // close the tag

    void add_timestamp(const std::string &name);
    void add_DFXML_build_environment();
    void add_cpuid();
    void add_DFXML_execution_environment(const std::string &command_line);
    void add_rusage();
    void set_oneline(bool v);
    const std::string &get_outfilename() const {return outfilename; } ;

    /********************************
     *** THESE ARE ALL THREADSAFE ***
     ********************************/
    void comment(const std::string &comment);
    void xmlprintf(const std::string &tag,const std::string &attribute,const char *fmt,...) 
        __attribute__((format(printf, 4, 5))); // "4" because this is "1";
    void xmlout( const std::string &tag,const std::string &value, const std::string &attribute, const bool escape_value);

    /* These all call xmlout or xmlprintf which already has locking, so these are all threadsafe! */
    void xmlout( const std::string &tag,const std::string &value ){ xmlout(tag,value,"",true); }
    void xmloutl(const std::string &tag,const long value )     { xmlprintf(tag,"","%ld",value); }
#ifdef WIN32
    void xmlout( const std::string &tag,const int32_t value )  { xmlprintf(tag,"","%I32d",value); }
    void xmlout( const std::string &tag,const uint32_t value ) { xmlprintf(tag,"","%I32u",value); }
    void xmlout( const std::string &tag,const int64_t value )  { xmlprintf(tag,"","%I64d",value); }
    void xmlout( const std::string &tag,const uint64_t value ) { xmlprintf(tag,"","%I64u",value); }
#else
    void xmlout( const std::string &tag,const int32_t value )  { xmlprintf(tag,"","%" PRId32,value); }
    void xmlout( const std::string &tag,const uint32_t value ) { xmlprintf(tag,"","%" PRIu32,value); }
    void xmlout( const std::string &tag,const int64_t value )  { xmlprintf(tag,"","%" PRId64,value); }
    void xmlout( const std::string &tag,const uint64_t value ) { xmlprintf(tag,"","%" PRIu64,value); }
#ifdef __APPLE__
    void xmlout( const std::string &tag,const size_t value )   { xmlprintf(tag,"","%" PRIu64,(unsigned long long)value); }
#endif
#endif
    void xmlout( const std::string &tag,const double value )   { xmlprintf(tag,"","%f",value); }
    void xmlout( const std::string &tag,const struct timeval &ts) {
        xmlprintf(tag,"","%d.%06d",(int)ts.tv_sec, (int)ts.tv_usec);
    }
    static std::string to8601(const struct timeval &ts) {
        struct tm tm;
        char buf[64];
#ifdef HAVE_GMTIME_R
        gmtime_r(&ts.tv_sec,&tm);
#else
        time_t t = ts.tv_sec;
        struct tm *tmp;
        tmp = gmtime(&t);
        if(!tmp) return std::string("INVALID");
        tm = *tmp;
#endif
        strftime(buf,sizeof(buf),"%Y-%m-%dT%H:%M:%S",&tm);
        if(ts.tv_usec>0){
            int len = strlen(buf);
            snprintf(buf+len,sizeof(buf)-len,".%06d",(int)ts.tv_usec);
        }
        strcat(buf,"Z");
        return std::string(buf);
    }
};
#endif

#endif
