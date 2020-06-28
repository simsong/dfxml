// Uses cester
// doc: https://github.com/exoticlibraries/libcester/blob/master/docs/docs/macros.rst

// cester generates some GCC warnings. Ignore them.
#pragma GCC diagnostic ignored "-Wshadow"
#pragma GCC diagnostic ignored "-Wunused-variable"

// get cester!
#include "cester.h"

// define stuff I need in the global environment. Only read it once.
#ifndef GUARD_BLOCK
#include "config.h"
#include "../hash_t.h"
#define GUARD_BLOCK
const uint8_t nulls[512] = {0};

int count_wrongs(void) {
    /* First test the operation of the digest function */
    uint8_t buf20[20] = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19};
    int wrongs = 0;
    sha1_t v20(buf20);
    for(int i=0;i<20;i++){
        if (v20.digest[i] != i) wrongs += 1;
    }
    return wrongs;
}
#endif

CESTER_TEST(test_sha1_t, inst,
            cester_assert_equal( count_wrongs(), 0 );
    )

CESTER_TEST(test_md5_generator, inst, 
            cester_assert_equal( md5_generator::hash_buf(nulls,0).hexdigest(),
                                 "d41d8cd98f00b204e9800998ecf8427e");
    )

CESTER_TEST(test_sha1_generator, inst, 
            cester_assert_equal( sha1_generator::hash_buf(nulls,0).hexdigest(),
                                 "da39a3ee5e6b4b0d3255bfef95601890afd80709");
    )

CESTER_TEST(test_sha256_generator, inst, 
            cester_assert_equal( sha256_generator::hash_buf(nulls,0).hexdigest(),
                                 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    )

CESTER_TEST(test_sha512_generator, inst, 
            cester_assert_equal( sha512_generator::hash_buf(nulls,0).hexdigest(),
                                 "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e");
    )
