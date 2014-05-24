#include <iostream>
#include <fstream>
#include <sstream>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <expat.h>
#include <time.h>
#include <netinet/in.h>

#include "config.h"
#include "dfxml_reader.h"

/*
 * DFXML demo program.
 *
 * Simson L. Garfinkel
 * Created for bulk_extractor.
 * This file is public domain.
 */


void process(dfxml::file_object &fi)
{
    std::cout << "fi.filename: " << fi.filename() << "\n";
    std::cout << "  pieces: " << fi.byte_runs.size() << "\n";
    for(dfxml::file_object::byte_runs_t::const_iterator it = fi.byte_runs.begin(); it!=fi.byte_runs.end(); it++){
	//std::cout << "   " << *it  << "\n";
    }
}


int main(int argc,char **argv)
{

    dfxml::file_object_reader::read_dfxml(argv[1],process);
    return 0;
}

