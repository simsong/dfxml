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
    //    for ( auto const &it: fi.byte_runs ){
    //std::cout << "   " << it  << "\n";
    //}
}


int main(int argc,char **argv)
{
    dfxml::file_object_reader::read_dfxml(argv[1],process);
    return 0;
}

