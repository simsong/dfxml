#ifndef _DFXML_READER_H_
#define _DFXML_READER_H_

/**
 ** NOTE:
 ** THIS IS NOT A COMPLETE IMPLEMENTATION.
 ** This is a skeletal implementation of a DFXML reader to solve an immediate problem.
 ** For a full implementation, please see ../python/dfxml.py
 **
 ** If you want to add support for a specific DFXML tag, please add it
 ** and submit your patch as a pull request on github.  
 **/
 
/*
 * Revision History:
 * 2012 - Simson L. Garfinkel - Developed as test program. 
 *
 * This file is public domain.
 */



#include <stdio.h>
#include <string>
#include <vector>
#include <stack>
#include <map>
#include <sstream>
#if __cplusplus >= 201103L
#include <functional>
#endif

#include <stdint.h>

#ifdef HAVE_EXPAT_H
#include <expat.h>
#else
#error dfxml_reader.h requires expat.h
#endif


#ifdef HAVE_MD5_H
#include "md5.h"
#endif

namespace dfxml {

    class saxobject {
    public:
        typedef std::map<std::string,std::string> hashmap_t;
        typedef std::map<std::string,std::string> tagmap_t;
        virtual ~saxobject(){}
        saxobject():hashdigest(),_tags(){}
        saxobject(const saxobject &that):hashdigest(that.hashdigest),_tags(that._tags){}
        hashmap_t hashdigest; // any object can have hashes
        tagmap_t _tags; // any object can tags
    };
    std::ostream & operator <<(std::ostream &os,const dfxml::saxobject::hashmap_t &h);


    class no_hash:public std::exception {
        virtual const char *what() const throw() {
            return "requested hash not found";
        }
    };


    class byte_run:public saxobject {
    public:
        virtual ~byte_run(){};
        byte_run():saxobject(),img_offset(0),file_offset(0),len(0),sector_size(0){}
        byte_run(const byte_run &that):saxobject(that),
                                       img_offset(that.img_offset),
                                       file_offset(that.file_offset),
                                       len(that.len),
                                       sector_size(that.sector_size){}

        int64_t img_offset;
        int64_t file_offset;
        int64_t len;
        int64_t sector_size;
#ifdef HAVE_MD5_H
        md5_t md5() const {
            hashmap_t::const_iterator it = hashdigest.find("md5");
            if(it==hashdigest.end()) std::cout << "end found\n";
            if(it!=hashdigest.end()) std::cout << it-> first << "=" /* << it->second */ << "\n";
            if(it!=hashdigest.end()) return md5_t::fromhex(it->second);
            throw new no_hash();
        }
#endif
    };
    std::ostream & operator <<(std::ostream &os,const byte_run &b);



    class imageobject_sax:public saxobject {
    public:
        virtual ~imageobject_sax(){};
    };

    class volumeobject_sax:public saxobject {
    public:;
        volumeobject_sax():saxobject(),block_size(),image(){}
        uint64_t block_size;
        imageobject_sax image;
    };

    class file_object:public saxobject {
    public:;
        file_object():saxobject(),volumeobject(0),byte_runs() { };
        file_object(const file_object &that):saxobject(that),volumeobject(that.volumeobject),
                                             byte_runs(that.byte_runs) {
        };
        const file_object &operator=(const file_object &fo){
            this->hashdigest = fo.hashdigest;
            this->_tags      = fo._tags;
            this->volumeobject = fo.volumeobject;
            this->byte_runs = fo.byte_runs;
            return *this;
        }

        typedef std::vector<byte_run> byte_runs_t;
        volumeobject_sax *volumeobject;
        byte_runs_t byte_runs;

        std::string filename(){return _tags["filename"];}
#ifdef HAVE_MD5_H
        md5_t md5() const {
            std::map<std::string,std::string>::const_iterator it = hashdigest.find("md5");
            if(it!=hashdigest.end()) return md5_t::fromhex(it->second);
            throw new no_hash();
        }
#endif
    };

#if __cplusplus >= 201103L
    typedef std::function<void (file_object&)> fileobject_callback_t;
#else
    typedef void (*fileobject_callback_t)(file_object &);
#endif

    class dfxml_reader {
    public:
        dfxml_reader():tagstack(),cdata(){}
        virtual ~dfxml_reader(){}
        static std::string getattrs(const char **attrs,const std::string &name);
        static uint64_t getattri(const char **attrs,const std::string &name);
        std::stack<std::string> tagstack;
        std::stringstream cdata;
    };

    class file_object_reader:public dfxml_reader{
    private:
        /*** neither copying nor assignment is implemented ***
         *** We do this by making them private constructors that throw exceptions. ***/
        file_object_reader(const file_object_reader &);
        file_object_reader &operator=(const file_object_reader&);
    public:;

        static void startElement(void *userData, const char *name_, const char **attrs);
        static void endElement(void *userData, const char *name_);
        static void read_dfxml(const std::string &fname,fileobject_callback_t process);
        static void characterDataHandler(void *userData,const XML_Char *s,int len);

        virtual ~file_object_reader(){};
        file_object_reader(): dfxml_reader(),volumeobject(),fileobject(),callback(),hashdigest_type(){}
        volumeobject_sax *volumeobject;
        file_object *fileobject;		// the object currently being read
        fileobject_callback_t callback;
        std::string hashdigest_type;
    };
};


#endif
