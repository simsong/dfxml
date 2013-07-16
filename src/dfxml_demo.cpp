#include <iostream>
#include <fstream>
#include <sstream>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <expat.h>
#include <time.h>
#include <netinet/in.h>

#include "dfxml_reader.h"

void process(file_object &fi)
{
    std::cout << "fi.filename: " << fi.filename() << "\n";
    std::cout << "  pieces: " << fi.byte_runs.size() << "\n";
    for(file_object::byte_runs_t::const_iterator it = fi.byte_runs.begin(); it!=fi.byte_runs.end(); it++){
	std::cout << "   " << *it  << "\n";
    }
}


int main(int argc,char **argv)
{

    file_object_reader::read_dfxml(argv[1],process);
    return 0;
}

