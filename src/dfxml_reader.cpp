/*
 * DFXML reader in C++ using SAX.
 * Revision History:
 * 2012 - SImson L. Garfinkel - Developed as test program. 
 *
 * This file is public domain.
 */


#include <config.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <time.h>
#include <stdint.h>



/* We need netinet/in.h or windowsx.h */
#ifdef HAVE_NETINET_IN_H
# include <netinet/in.h>
#endif

#ifdef HAVE_WINSOCK2_H
#  include <winsock2.h>
#  include <windows.h>
#  include <windowsx.h>
#endif
#include <string.h>
#include <algorithm>

#include "dfxml_reader.h"

std::ostream & operator <<(std::ostream &os,const dfxml::byte_run &b) {
    os << "byte_run[";
    if(b.img_offset) os << "img_offset=" << b.img_offset << ";";
    if(b.file_offset) os << "file_offset=" << b.file_offset << ";";
    if(b.len) os << "len=" << b.len << ";";
    if(b.sector_size) os << "sector_size=" << b.sector_size << ";";
    //os << b.hashdigest;
    os << "]";
    return os;
};

std::ostream & operator <<(std::ostream &os,const dfxml::saxobject::hashmap_t &h)
{
    for(dfxml::saxobject::hashmap_t::const_iterator it = h.begin(); it!=h.end(); it++){
	os << it->first << ":" << it->second << " ";
    }
    return os;
}


std::string dfxml::dfxml_reader::getattrs(const char **attrs,const std::string &name)
{
    for(int i=0;attrs[i];i+=2){
	if(name==attrs[i]) return std::string(attrs[i+1]);
    }
    return std::string("");
}

static uint64_t atoi64(const char *str)
{
    std::stringstream ss;
    ss << str;
    uint64_t val;
    ss >> val;
    return val;
}

uint64_t dfxml::dfxml_reader::getattri(const char **attrs,const std::string &name)
{
    std::stringstream ss;
    for(int i=0;attrs[i];i+=2){
	if(name==attrs[i]){
	    ss << attrs[i+1];
	    uint64_t val;
	    ss >> val;
	    return val;
	}
    }
    return 0;
}


void dfxml::file_object_reader::startElement(void *userData, const char *name_, const char **attrs)
{
    class file_object_reader &self = *(file_object_reader *)userData;
    std::string name(name_);

    self.cdata.str("");
    self.tagstack.push(name);
    if(name=="volume"){
	self.volumeobject = new volumeobject_sax();
	self.volumeobject->block_size = 512; // default
    }
    if(name=="block_size"){
	/* pass */
    }
    if(name=="fileobject"){
	self.fileobject = new file_object();
	self.fileobject->volumeobject = self.volumeobject;
	return;
    }
    if(name=="hashdigest"){
	self.hashdigest_type = getattrs(attrs,"type");
	return;
    }
    if(self.fileobject && (name=="run" || name=="byte_run")){
	byte_run run;
	for(int i=0;attrs[i];i+=2){
	    if(run.img_offset==0 && !strcmp(attrs[i],"img_offset")){run.img_offset = atoi64(attrs[i+1]);continue;}
	    if(run.file_offset==0 && !strcmp(attrs[i],"file_offset")){run.file_offset = atoi64(attrs[i+1]);continue;}
	    if(run.len==0 && !strcmp(attrs[i],"len")){run.len = atoi64(attrs[i+1]);continue;}
	    if(run.sector_size==0 && !strcmp(attrs[i],"sector_size")){run.sector_size = atoi64(attrs[i+1]);continue;}
	}
	self.fileobject->byte_runs.push_back(run); // is there a more efficient way to do this?
    }
}

void dfxml::file_object_reader::endElement(void *userData, const char *name_)
{
    std::string name(name_);

    file_object_reader &self = *(file_object_reader *)userData;
    if(self.tagstack.top() != name){
	std::cout << "close tag '" << name << "' found; '" << self.tagstack.top() << "' expected.\n";
	exit(1);
    }
    self.tagstack.pop();
    std::string cdata = self.cdata.str();
    self.cdata.str("");

    if(name=="volume"){
	self.volumeobject = 0;
	return;
    }
    if(name=="block_size" && self.tagstack.size()>1){
	if(self.tagstack.top()=="volume"){
	    self.volumeobject->block_size = atoi(cdata.c_str());
	}
	return;
    }
    if(name=="fileobject"){
	self.callback(*self.fileobject);
	delete self.fileobject;
	self.fileobject = 0;
	return;
    }
    if(name=="hashdigest" and self.tagstack.size()>0){
	std::string alg = self.hashdigest_type;
	std::transform(alg.begin(), alg.end(), alg.begin(), ::tolower);
	if(self.tagstack.top()=="byte_run"){
	    self.fileobject->byte_runs.back().hashdigest[alg] = cdata;
	}
	if(self.tagstack.top()=="fileobject"){
	    self.fileobject->hashdigest[alg] = cdata;
	}
	return;
    }
    if(self.fileobject){
	self.fileobject->_tags[name] = cdata;
	return;
    }
}

/**
 * Remember - 's' is NOT null-terminated
 */
void dfxml::file_object_reader::characterDataHandler(void *userData,const XML_Char *s,int len)
{
    class file_object_reader &self = *(file_object_reader *)userData;
    self.cdata.write(s,len);
}

void dfxml::file_object_reader::read_dfxml(const std::string &fname,fileobject_callback_t process)
{
    file_object_reader r;

    r.callback = process;

    XML_Parser parser = XML_ParserCreate(NULL);
    XML_SetUserData(parser, &r);
    XML_SetElementHandler(parser, startElement, endElement);
    XML_SetCharacterDataHandler(parser,characterDataHandler);

    std::fstream in(fname.c_str());

    if(!in.is_open()){
	std::cout << "Cannot open " << fname << ": " << strerror(errno) << "\n";
	exit(1);
    }
    try {
	std::string line;
	while(getline(in,line)){
	    if (!XML_Parse(parser, line.c_str(), line.size(), 0)) {
		std::cout << "XML Error: " << XML_ErrorString(XML_GetErrorCode(parser))
			  << " at line " << XML_GetCurrentLineNumber(parser) << "\n";
		XML_ParserFree(parser);
		return;
	    }
	}
	XML_Parse(parser, "", 0, 1);
    }
    catch (const std::exception &e) {
	std::cout << "ERROR: " << e.what() << "\n";
    }
    XML_ParserFree(parser);
}

