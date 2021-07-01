/* -*- mode: C++; c-basic-offset: 4; indent-tabs-mode: nil -*- */
/*
 * Simson's XML output class.
 * Include this AFTER your config file with the HAVE statements.
 * Optimized for DFXML generation.
 */

#ifndef DFXML_WRITER_H
#define DFXML_WRITER_H

/* c++ */
#include <cassert>
#include <cinttypes>
#include <cstdio>
#include <cstring>
#include <ctime>
#include <fstream>
#include <iostream>
#include <map>
#include <mutex>
#include <set>
#include <sstream>
#include <stack>
#include <string>
#include <stdexcept>
#include <stdarg.h>

#include <sys/time.h>


#ifdef _MSC_VER
# include <io.h>
#else
# include <unistd.h>
#endif

#ifdef HAVE_SQLITE3_H
#include <sqlite3.h>
#endif

#ifdef HAVE_HASHDB
#include <hashdb.hpp>
#endif

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

#ifdef HAVE_LIBEWF_H
#include <libewf.h>
#endif

#ifdef WIN32
#include <psapi.h>
#endif

#ifdef HAVE_WINSOCK2_H
#include <winsock2.h>
#endif

#ifdef HAVE_BOOST_VERSION_HPP
#include <boost/version.hpp>
#endif

#include "cpuid.h"


class dfxml_writer {
public:
    static inline std::string xml_lt = "&lt;";
    static inline std::string xml_gt = "&gt;";
    static inline std::string xml_am = "&amp;";
    static inline std::string xml_ap = "&apos;";
    static inline std::string xml_qu = "&quot;";

// % encodings
    static inline std::string encoding_null = "%00";
    static inline std::string encoding_r = "%0D";
    static inline std::string encoding_n = "%0A";
    static inline std::string encoding_t = "%09";
    static inline std::string const xml_header = "<?xml version='1.0' encoding='UTF-8'?>\n";


    /* This is the main interface: */
    // defaults to stdout
    dfxml_writer():M(),outf(),out(&std::cout),tags(),tag_stack(),tempfilename(),tempfile_template("/tmp/xml_XXXXXXXX"),
           t0(),t_last_timestamp(),make_dtd(false),outfilename(),oneline() {
        gettimeofday(&t0,0);
        gettimeofday(&t_last_timestamp,0);
        *out << xml_header;
    }

// write to a file, optionally making a DTD
    dfxml_writer(const std::string &outfilename_,bool makeDTD):
        M(),outf(outfilename_.c_str(),std::ios_base::out), out(),tags(),tag_stack(),tempfilename(),tempfile_template(outfilename_+"_tmp_XXXXXXXX"),
        t0(),t_last_timestamp(),make_dtd(false),outfilename(outfilename_),oneline() {
        gettimeofday(&t0,0);
        gettimeofday(&t_last_timestamp,0);
        if(!outf.is_open()){
            perror(outfilename_.c_str());
            exit(1);
        }
        out = &outf;                                                // use this one instead
        *out << xml_header;
    }
    virtual ~dfxml_writer(){};

    // adds the creator, build_environment, and execution environment
    void add_DFXML_creator(const std::string &program,const std::string &version,
                           const std::string &git_commit,
                           int argc,char * const *argv) {
        const std::string command_line = make_command_line(argc,argv);

        push("creator","version='1.0'");
        xmlout("program",program);
        xmlout("version",version);
        if (git_commit.size()>0) xmlout("commit",git_commit);
        add_DFXML_build_environment();
        add_DFXML_execution_environment(command_line);
        pop();                  // creator
    }

    /*** neither copying nor assignment is implemented ***/
    dfxml_writer(const dfxml_writer &) = delete;
    dfxml_writer &operator=(const dfxml_writer &) = delete;

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
    void  write_dtd() {
        *out << "<!DOCTYPE fiwalk\n";
        *out << "[\n";
        for (auto const &it:tags) {
            *out << "<!ELEMENT " << it << "ANY >\n";
        }
        *out << "<!ATTLIST volume startsector CDATA #IMPLIED>\n";
        *out << "<!ATTLIST run start CDATA #IMPLIED>\n";
        *out << "<!ATTLIST run len CDATA #IMPLIED>\n";
        *out << "]>\n";
    }
    /**
     * make sure that a tag is valid and, if so, add it to the list of tags we use
     */
    void  verify_tag(std::string tag) {
        if(tag[0]=='/') tag = tag.substr(1);
        if(tag.find(" ") != std::string::npos){
            std::cerr << "tag '" << tag << "' contains space. Cannot continue.\n";
            exit(1);
        }
        tags.insert(tag);
    }
    void  spaces(){   // print spaces corresponding to tag stack
        for(unsigned int i=0;i<tag_stack.size() && !oneline;i++){
            *out << "  ";
        }
    }


public:
    static std::string make_command_line(int argc,char * const *argv) {
        std::string command_line;
        for(int i=0;i<argc;i++){
            // append space separator between arguments
            if(i>0) command_line.push_back(' ');
            if (strchr(argv[i],' ') != NULL) {
                // the argument has a space, so quote the argument
                command_line.append("\"");
                command_line.append(argv[i]);
                command_line.append("\"");
            } else {
                // the argument has no space, so append as is
                command_line.append(argv[i]);
            }
        }
        return command_line;
    }

    void add_cpuid() {
#ifdef HAVE_ASM_CPUID
#ifndef __WORDSIZE
#define __WORDSIZE 32
#endif
#define BFIX(val, base, end) ((val << (__WORDSIZE-end-1)) >> (__WORDSIZE-end+base-1))
        CPUID  cpuID(0);                     // get CPU vendor
        unsigned long eax = cpuID.EAX();
        unsigned long ebx = cpuID.EBX();
        unsigned long ecx = cpuID.ECX();

        push("cpuid");
        xmlout("identification", CPUID::vendor());
        xmlout("family",   (int64_t) BFIX(eax, 8, 11));
        xmlout("model",    (int64_t) BFIX(eax, 4, 7));
        xmlout("stepping", (int64_t) BFIX(eax, 0, 3));
        xmlout("efamily",  (int64_t) BFIX(eax, 20, 27));
        xmlout("emodel",   (int64_t) BFIX(eax, 16, 19));
        xmlout("brand",    (int64_t) BFIX(ebx, 0, 7));
        xmlout("clflush_size", (int64_t) BFIX(ebx, 8, 15) * 8);
        xmlout("nproc",    (int64_t) BFIX(ebx, 16, 23));
        xmlout("apicid",   (int64_t) BFIX(ebx, 24, 31));

        CPUID cpuID2(0x80000006);
        ecx = cpuID2.ECX();
        xmlout("L1_cache_size", (int64_t) BFIX(ecx, 16, 31) * 1024);
        pop();
#undef BFIX
#endif
    }
    void   set_tempfile_template(const std::string &temp) {
        tempfile_template = temp;
    }
    static std::string xmlescape(const std::string &xml) {
        std::string ret;
        for(auto const &ch: xml){
            switch(ch){
                // XML escapes
            case '>':  ret += xml_gt; break;
            case '<':  ret += xml_lt; break;
            case '&':  ret += xml_am; break;
            case '\'': ret += xml_ap; break;
            case '"':  ret += xml_qu; break;

                // % encodings
            case '\000':  ret += encoding_null; break;      // retain encoded nulls
            case '\r':  ret += encoding_r; break;
            case '\n':  ret += encoding_n; break;
            case '\t':  ret += encoding_t; break;
            default:
                ret += ch;
            }
        }
        return ret;
    }
    static std::string xmlstrip(const std::string &xml) {
        std::string ret;
        for( const auto &ch : xml){
            if(isprint(ch) && !strchr("<>\r\n&'\"",ch)){
                ret += isspace(ch) ? '_' : tolower(ch);
            }
        }
        return ret;
    }

    /** xmlmap turns a map into an XML block */
    static std::string xmlmap(const strstrmap_t &m,const std::string &outer,const std::string &attrs) {
        std::stringstream ss;
        ss << "<" << outer;
        if(attrs.size()>0) ss << " " << attrs;
        ss << ">";
        for(std::map<std::string,std::string>::const_iterator it=m.begin();it!=m.end();it++){
            ss << "<" << (*it).first  << ">" << xmlescape((*it).second) << "</" << (*it).first << ">";
        }
        ss << "</" << outer << ">";
        return ss.str();
    }

    void close() {                       // writes the output to the file
        const std::lock_guard<std::mutex> lock(M);
        if (!tag_stack.empty()) {
            std::cerr << "dfxml::close(): tag stack not empty!\n";
            while (!tag_stack.empty()){
                auto it = tag_stack.top();
                std::cerr << "   " << it << "\n";
                tag_stack.pop();
            }
            throw std::runtime_error("dfxml: tag stack not empty.");
        }
        outf.close();
        if(make_dtd){
            /* If we are making the DTD, then we should close the file,
             * scan the output file for the tags, write to a temp file, and then
             * close the temp file and have it overwrite the outfile.
             */

            std::ifstream in( tempfilename.c_str());
            if(!in.is_open()){
                std::cerr << tempfilename << strerror(errno) << ":Cannot re-open for input\n";
                exit(1);
            }
            outf.open( outfilename.c_str(),std::ios_base::out);
            if(!outf.is_open()){
                std::cerr << outfilename << " " << strerror(errno)
                          << ": Cannot open for output; will not delete " << tempfilename << "\n";
                exit(1);
            }
            // copy over first line --- the XML header
            std::string line;
            getline(in,line);
            outf << line;

            write_dtd();                    // write the DTD
            while(!in.eof()){
                getline(in,line);
                outf << line << std::endl;
            }
            in.close();
            unlink( tempfilename.c_str());
            outf.close();
        }
    }

    void flush(){ outf.flush(); }
    void tagout( const std::string &tag, const std::string &attribute) {
        verify_tag(tag);
        *out << "<" << tag;
        if(attribute.size()>0) *out << " " << attribute;
        *out << ">";
    }
    void push( const std::string &tag, const std::string &attribute) {
        spaces();
        tag_stack.push(tag);
        tagout(tag,attribute);
        if(!oneline) *out << '\n';
    }
    void push( const std::string &tag) {push(tag,"");}

    // writes a std::string as parsed data
    void puts( const std::string &pdata) {
        *out << pdata;
    }

    // writes a std::string as parsed data
    void printf(const char *fmt,...) __attribute__((format(printf, 2, 3))) { // "2" because this is "1"
        va_list ap;
        va_start(ap, fmt);

        /** printf to stream **/
        char *ret = 0;
        if(vasprintf(&ret,fmt,ap) < 0){
            *out << "dfxml_writer::xmlprintf: " << strerror(errno);
            exit(EXIT_FAILURE);
        }
        *out << ret;
        free(ret);
        /** end printf to stream **/

        va_end(ap);
    }

    void pop() { // close the tag
        assert(tag_stack.size()>0);
        std::string tag = tag_stack.top();
        spaces();
        tagout("/"+tag,"");
        *out << '\n';
        tag_stack.pop();
    }

    void add_timestamp(const std::string &name) {
        struct timeval t1, t;

        // timestamp delta against t_last_timestamp
        gettimeofday(&t1,0);
        t.tv_sec = t1.tv_sec - t_last_timestamp.tv_sec;
        if(t1.tv_usec > t_last_timestamp.tv_usec){
            t.tv_usec = t1.tv_usec - t_last_timestamp.tv_usec;
        } else {
            t.tv_sec--;
            t.tv_usec = (t1.tv_usec+1000000) - t_last_timestamp.tv_usec;
        }
        char delta[16];
        snprintf(delta, 16, "%d.%06d", (int)t.tv_sec, (int)t.tv_usec);

        // reset t_last_timestamp for the next invocation
        gettimeofday(&t_last_timestamp,0);

        // timestamp total
        t.tv_sec = t1.tv_sec - t0.tv_sec;
        if(t1.tv_usec > t0.tv_usec){
            t.tv_usec = t1.tv_usec - t0.tv_usec;
        } else {
            t.tv_sec--;
            t.tv_usec = (t1.tv_usec+1000000) - t0.tv_usec;
        }
        char total[16];
        snprintf(total, 16, "%d.%06d", (int)t.tv_sec, (int)t.tv_usec);

        // prepare attributes and add the timestamp
        std::stringstream ss;
        ss << "name='" << name << "' delta='" << delta << "' total='" << total << "'";
        xmlout("timestamp", "",ss.str(), true);
    }
    void add_DFXML_build_environment() {
        /* __DATE__ formats as: Apr 30 2011 */
        struct tm tm;
        memset(&tm,0,sizeof(tm));
        push("build_environment");
#ifdef __GNUC__
        // See http://gcc.gnu.org/onlinedocs/cpp/Common-Predefined-Macros.html
        xmlprintf("compiler","","%d.%d.%d (%s)",__GNUC__, __GNUC_MINOR__,__GNUC_PATCHLEVEL__,__VERSION__);
#endif
#ifdef CPPFLAGS
        xmlout("CPPFLAGS",CPPFLAGS,"",true);
#endif
#ifdef CFLAGS
        xmlout("CFLAGS",CFLAGS,"",true);
#endif
#ifdef CXXFLAGS
        xmlout("CXXFLAGS",CXXFLAGS,"",true);
#endif
#ifdef LDFLAGS
        xmlout("LDFLAGS",LDFLAGS,"",true);
#endif
#ifdef LIBS
        xmlout("LIBS",LIBS,"",true);
#endif
#if defined(__DATE__) && defined(__TIME__) && defined(HAVE_STRPTIME)
        if(strptime(__DATE__,"%b %d %Y",&tm)){
            char buf[64];
            snprintf(buf,sizeof(buf),"%4d-%02d-%02dT%s",tm.tm_year+1900,tm.tm_mon+1,tm.tm_mday,__TIME__);
            xmlout("compilation_date",buf);
        }
#endif
#ifdef BOOST_VERSION
        {
            char buf[64];
            snprintf(buf,sizeof(buf),"%d",BOOST_VERSION);
            xmlout("library", "", std::string("name=\"boost\" version=\"") + buf + "\"",false);
        }
#endif
#ifdef HAVE_LIBTSK3
        xmlout("library", "", std::string("name=\"tsk\" version=\"") + tsk_version_get_str() + "\"",false);
#endif
#ifdef HAVE_LIBEWF
        xmlout("library", "", std::string("name=\"libewf\" version=\"") + libewf_get_version() + "\"",false);
#endif
#ifdef HAVE_EXIV2
        xmlout("library", "", std::string("name=\"exiv2\" version=\"") + Exiv2::version() + "\"",false);
#endif
#ifdef HAVE_HASHDB
        xmlout("library", "", std::string("name=\"hashdb\" version=\"") + hashdb_version() + "\"",false);
#endif
#ifdef SQLITE_VERSION
        xmlout("library", "", "name=\"sqlite\" version=\"" SQLITE_VERSION "\" source_id=\"" SQLITE_SOURCE_ID "\"",false);
#endif
#ifdef HAVE_GNUEXIF
        // gnuexif does not have a programmatically obtainable version.
        xmlout("library","","name=\"gnuexif\" version=\"?\"",false);
#endif
#ifdef GIT_COMMIT
        xmlout("git", "", "commit=\"" GIT_COMMIT "\"",false);
#endif
        pop();
    }
    void add_DFXML_execution_environment(const std::string &command_line) {
        push("execution_environment");
#if defined(HAVE_ASM_CPUID)
        add_cpuid();
#endif

#ifdef HAVE_SYS_UTSNAME_H
        struct utsname name;
        if(uname(&name)==0){
            xmlout("os_sysname",name.sysname);
            xmlout("os_release",name.release);
            xmlout("os_version",name.version);
            xmlout("host",name.nodename);
            xmlout("arch",name.machine);
        }
#else
#ifdef UNAMES
        xmlout("os_sysname",UNAMES,"",false);
#endif
#ifdef HAVE_GETHOSTNAME
        {
            char hostname[1024];
            if(gethostname(hostname,sizeof(hostname))==0){
                xmlout("host",hostname);
            }
        }
#endif
#endif

        xmlout("command_line", command_line); // quote it!
#ifdef HAVE_GETUID
        xmlprintf("uid","","%d",getuid());
#ifdef HAVE_GETPWUID
        xmlout("username",getpwuid(getuid())->pw_name);
#endif
#endif

#define TM_FORMAT "%Y-%m-%dT%H:%M:%SZ"
        char buf[256];
        time_t t = time(0);
        strftime(buf,sizeof(buf),TM_FORMAT,gmtime(&t));
        xmlout("start_time",buf);
        pop();                      // <execution_environment>
    }
    void set_oneline(bool v) {
        if (v){
            spaces();
        } else {
            *out << "\n";
        }
        oneline = v;
    }

    const std::string &get_outfilename() const {return outfilename; } ;

    /********************************
     *** THESE ARE ALL THREADSAFE ***
     ********************************/
    void add_rusage() {
#ifdef WIN32
        /* Note: must link -lpsapi for this */
        PROCESS_MEMORY_COUNTERS_EX pmc;
        memset(&pmc,0,sizeof(pmc));
        GetProcessMemoryInfo(GetCurrentProcess(), (PROCESS_MEMORY_COUNTERS *)&pmc, sizeof(pmc));
        push("PROCESS_MEMORY_COUNTERS");
        xmlout("cb",(int64_t)pmc.cb);
        xmlout("PageFaultCount",(int64_t)pmc.PageFaultCount);
        xmlout("WorkingSetSize",(int64_t)pmc.WorkingSetSize);
        xmlout("QuotaPeakPagedPoolUsage",(int64_t)pmc.QuotaPeakPagedPoolUsage);
        xmlout("QuotaPagedPoolUsage",(int64_t)pmc.QuotaPagedPoolUsage);
        xmlout("QuotaPeakNonPagedPoolUsage",(int64_t)pmc.QuotaPeakNonPagedPoolUsage);
        xmlout("PagefileUsage",(int64_t)pmc.PagefileUsage);
        xmlout("PeakPagefileUsage",(int64_t)pmc.PeakPagefileUsage);
        xmlout("PrivateUsage",(int64_t)pmc.PrivateUsage);
        pop();
#endif
#ifdef HAVE_GETRUSAGE
        struct rusage ru;
        memset(&ru,0,sizeof(ru));
        if(getrusage(RUSAGE_SELF,&ru)==0){
            push("rusage");
            xmlout("utime",ru.ru_utime);
            xmlout("stime",ru.ru_stime);
            xmlout("maxrss",(long)ru.ru_maxrss);
            xmlout("minflt",(long)ru.ru_minflt);
            xmlout("majflt",(long)ru.ru_majflt);
            xmlout("nswap",(long)ru.ru_nswap);
            xmlout("inblock",(long)ru.ru_inblock);
            xmlout("oublock",(long)ru.ru_oublock);

            struct timeval t1;
            gettimeofday(&t1,0);
            struct timeval t;

            t.tv_sec = t1.tv_sec - t0.tv_sec;
            if(t1.tv_usec > t0.tv_usec){
                t.tv_usec = t1.tv_usec - t0.tv_usec;
            } else {
                t.tv_sec--;
                t.tv_usec = (t1.tv_usec+1000000) - t0.tv_usec;
            }
            xmlout("clocktime",t);
            pop();
        }
#endif
    }

    /***************************************
     *** ALL THAT FOLLOWS ARE THREADSAFE ***
     ***************************************/
    void comment(const std::string &comment) {
        const std::lock_guard<std::mutex> lock(M);
        *out << "<!-- " << comment << " -->\n";
        out->flush();
    }
    void xmlprintf(const std::string &tag,const std::string &attribute,const char *fmt,...) __attribute__((format(printf, 4, 5))) {
        // "4" because this is "1";
        const std::lock_guard<std::mutex> lock(M);
        spaces();
        tagout(tag,attribute);
        va_list ap;
        va_start(ap, fmt);

        /** printf to stream **/
        char *ret = 0;
        if(vasprintf(&ret,fmt,ap) < 0){
            std::cerr << "dfxml_writer::xmlprintf: " << strerror(errno) << "\n";
            exit(EXIT_FAILURE);
        }
        *out << ret;
        free(ret);
        /** end printf to stream **/

        va_end(ap);
        tagout("/"+tag,"");
        *out << '\n';
        out->flush();
    }
    void xmlout( const std::string &tag,const std::string &value, const std::string &attribute, const bool escape_value) {
        const std::lock_guard<std::mutex> lock(M);
        spaces();
        if(value.size()==0){
            if(tag.size()) tagout(tag,attribute+"/");
        } else {
            if(tag.size()) tagout(tag,attribute);
            *out << (escape_value ? xmlescape(value) : value);
            if(tag.size()) tagout("/"+tag,"");
        }
        *out << "\n";
        out->flush();
    }

    /* These all call xmlout or xmlprintf which already has locking, so these are all threadsafe! */
    void xmlout( const std::string &tag,const std::string &value )       { xmlout(tag,value,"",true); }
    void xmlout( const std::string &tag,const signed char value )        { xmlprintf(tag,"","%hhd",value); }
    void xmlout( const std::string &tag,const short value )              { xmlprintf(tag,"","%hd", value); }
    void xmlout( const std::string &tag,const int value )                { xmlprintf(tag,"","%d",  value); }
    void xmlout( const std::string &tag,const long value )               { xmlprintf(tag,"","%ld", value); }
    void xmlout( const std::string &tag,const long long value )          { xmlprintf(tag,"","%lld",value); }
    void xmlout( const std::string &tag,const unsigned char value )      { xmlprintf(tag,"","%hhu",value); }
    void xmlout( const std::string &tag,const unsigned short value )     { xmlprintf(tag,"","%hu", value); }
    void xmlout( const std::string &tag,const unsigned int value )       { xmlprintf(tag,"","%u",  value); }
    void xmlout( const std::string &tag,const unsigned long value )      { xmlprintf(tag,"","%lu", value); }
    void xmlout( const std::string &tag,const unsigned long long value ) { xmlprintf(tag,"","%llu",value); }
    void xmlout( const std::string &tag,const double value )             { xmlprintf(tag,"","%f",value); }
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
