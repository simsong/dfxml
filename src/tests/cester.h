
/**
    \copyright MIT License Copyright (c) 2020, Adewale Azeez 
    \author Adewale Azeez <azeezadewale98@gmail.com>
    \date 10 April 2020
    \file cester.h

    Cester is a header only unit testing framework for C. The header 
    file can be downloaded and placed in a project folder or can be 
    used as part of libopen library by including it in the projects 
    like `<libopen/cester.h>`. 
    
    A single test file is considered a test suite in cester, a single 
    test file should contain related tests functions only. 
*/

#ifndef LIBOPEN_CESTER_H
#define LIBOPEN_CESTER_H

/*
    BEFORE YOU SUGGEST ANY EDIT PLEASE TRY TO 
    UNDERSTAND THIS CODE VERY WELL. 
*/

#ifdef __cplusplus
extern "C" {
#endif

/** 
    The inline keyword to optimize the function. In 
    C89 and C90 the inline keyword semantic is 
    different from current C standard semantic hence 
    for compilation targeting C89 or C99 the inline 
    keyword is ommited.
*/
#ifdef __STDC_VERSION__
    #define __CESTER_STDC_VERSION__ __STDC_VERSION__
#else
    #ifdef __cplusplus
        #define __CESTER_STDC_VERSION__ __cplusplus
    #endif
#endif
#ifndef __CESTER_STDC_VERSION__
    #define __CESTER_INLINE__ 
    #define __CESTER_LONG_LONG__ long
    #define __FUNCTION__ "<unknown>"
#else 
    #define __CESTER_INLINE__ inline
    #define __CESTER_LONG_LONG__ long long
    #define __FUNCTION__ __func__
#endif

#ifdef __cplusplus
#ifdef _WIN32
    #define __CESTER_CAST_CHAR_ARRAY__ (unsigned)
#else
    #define __CESTER_CAST_CHAR_ARRAY__ (char*)
#endif
#else
    #define __CESTER_CAST_CHAR_ARRAY__
#endif

#include <stdlib.h>
#include <time.h>
#include <stdio.h>
#include <string.h>
#ifndef CESTER_NO_SIGNAL
#include <signal.h>
#include <signal.h>
#include <setjmp.h>
jmp_buf buf;
#endif

#ifndef __BASE_FILE__
#ifdef _MSC_VER
    #pragma message("__BASE_FILE__ not defined. Define the __BASE_FILE__ directive in Properties -> C/C++ -> Preprocessor -> Preprocessor Definition as __BASE_FILE__=\"%(Filename)%(Extension)\" or register your test cases manually.")
#else
    #pragma message("__BASE_FILE__ not defined. Define __BASE_FILE__ during compilation. -D__BASE_FILE__=\"/the/path/to/yout/testfile.c\" or register your test cases manually.")
#endif
#endif

#ifdef _WIN32
#include <windows.h>
/*
**  Windows 
**  Support Windows XP 
**  To avoid error message : procedure entry point **  InitializeConditionVariable could not be located **  in Kernel32.dll 
*/
#ifdef _WIN32_WINNT
#undef _WIN32_WINNT
#endif
#define _WIN32_WINNT 0x502
#define EXOTICTYPES_WINDLLEXPORT 1
/* Linux */
#else
#define EXOTICTYPES_WINDLLEXPORT 0
#endif
#ifndef __cplusplus
    #if EXOTICTYPES_WINDLLEXPORT
        #define EXOTIC_API __declspec(dllexport) /**< the platform is windows use windows export keyword __declspec(dllexport) */ 
    #else
        #define EXOTIC_API extern                /**< Keyword to export the functions to allow ussage dynamically. NOT USED. IGNORED  */
    #endif
#else
    #define EXOTIC_API
#endif

#ifdef unix
#include <unistd.h>
#include <sys/wait.h>
#endif

#ifdef _WIN32

#define CESTER_RESET_TERMINAL           15                                                /**< reset the terminal color //Nothing     */
#define CESTER_BOLD                     15                                                /**< bold text                //Nothing     */
#define CESTER_FOREGROUND_BLACK         8                                                 /**< gray terminal foreground color         */
#define CESTER_FOREGROUND_RED           4                                                 /**< red terminal foreground color          */
#define CESTER_FOREGROUND_GREEN         2                                                 /**< green foreground color                 */
#define CESTER_FOREGROUND_YELLOW        6                                                 /**< yellow terminal foreground color       */
#define CESTER_FOREGROUND_BLUE          3                                                 /**< blue terminal foreground color         */
#define CESTER_FOREGROUND_MAGENTA       5                                                 /**< magenta terminal foreground color      */
#define CESTER_FOREGROUND_CYAN          11                                                /**< cyan terminal foreground color         */
#define CESTER_FOREGROUND_WHITE         15                                                /**< white terminal foreground color        */
#define CESTER_FOREGROUND_GRAY          8                                                 /**< gray terminal foreground color         */
#define CESTER_BACKGROUND_BLACK         0                                                 /**< black terminal background color        */
#define CESTER_BACKGROUND_RED           64                                                /**< red terminal background color          */
#define CESTER_BACKGROUND_GREEN         39                                                /**< green terminal background color        */
#define CESTER_BACKGROUND_YELLOW        96                                                /**< yellow terminal background color       */
#define CESTER_BACKGROUND_BLUE          48                                                /**< blue terminal background color         */
#define CESTER_BACKGROUND_MAGENTA       87                                                /**< magenta terminal background color      */
#define CESTER_BACKGROUND_CYAN          176                                               /**< cyan terminal background color         */
#define CESTER_BACKGROUND_GRAY          0                                                 /**< gray terminal background color         */
#define CESTER_BACKGROUND_WHITE         10                                                /**< gray terminal background color         */
#define CESTER_RESET_TERMINAL_ATTR()    SetConsoleTextAttribute(hConsole, default_color); /**< reset the terminal color               */

#else
    
#define CESTER_RESET_TERMINAL           "\x1B[0m"     /**< reset the terminal color           */
#define CESTER_BOLD                     "\x1B[1m"     /**< bold text                          */
#define CESTER_FOREGROUND_BLACK         "\x1B[30m"    /**< gray terminal foreground color     */
#define CESTER_FOREGROUND_RED           "\x1B[31m"    /**< red terminal foreground color      */
#define CESTER_FOREGROUND_GREEN         "\x1B[32m"    /**< green foreground color             */
#define CESTER_FOREGROUND_YELLOW        "\x1B[33m"    /**< yellow terminal foreground color   */
#define CESTER_FOREGROUND_BLUE          "\x1B[34m"    /**< blue terminal foreground color     */
#define CESTER_FOREGROUND_MAGENTA       "\x1B[35m"    /**< magenta terminal foreground color  */
#define CESTER_FOREGROUND_CYAN          "\x1B[36m"    /**< cyan terminal foreground color     */
#define CESTER_FOREGROUND_WHITE         "\x1B[37m"    /**< white terminal foreground color    */
#define CESTER_FOREGROUND_GRAY          "\x1B[90m"    /**< gray terminal foreground color     */
#define CESTER_BACKGROUND_BLACK         "\x1B[40m"    /**< black terminal background color    */
#define CESTER_BACKGROUND_RED           "\x1B[41m"    /**< red terminal background color      */
#define CESTER_BACKGROUND_GREEN         "\x1B[42m"    /**< green terminal background color    */
#define CESTER_BACKGROUND_YELLOW        "\x1B[43m"    /**< yellow terminal background color   */
#define CESTER_BACKGROUND_BLUE          "\x1B[44m"    /**< blue terminal background color     */
#define CESTER_BACKGROUND_MAGENTA       "\x1B[45m"    /**< magenta terminal background color  */
#define CESTER_BACKGROUND_CYAN          "\x1B[46m"    /**< cyan terminal background color     */
#define CESTER_BACKGROUND_GRAY          "\x1B[100m"   /**< gray terminal background color     */
#define CESTER_BACKGROUND_WHITE         "\x1B[47m"    /**< gray terminal background color     */
#define CESTER_RESET_TERMINAL_ATTR()    ;             /**< reset the terminal color           */

#endif

/**
    Cester current version
*/
#define CESTER_VERSION "0.3"

/**
    Cester current version
*/
#define CESTER_VERSION_NUM 0.3

/**
    Cester License
*/
#define CESTER_LICENSE "MIT License"

/**
    The hash # symbol for macro directive
*/
#define CESTER_HASH_SIGN #

/**
    Concat two items including C macro directives.
*/
#define CESTER_CONCAT(x, y) x y

/**
    The execution status of a test case that indicates 
    whether a test passes of fails. And also enable the 
    detection of the reason if a test fail.
*/
enum cester_test_status {
    CESTER_RESULT_SUCCESS,        /**< the test case passed                                                       */
    CESTER_RESULT_FAILURE,        /**< the test case failes dues to various reason mostly AssertionError          */
    CESTER_RESULT_TERMINATED,     /**< in isolated test, the test case was termiated by a user or another program */
    CESTER_RESULT_SEGFAULT,       /**< the test case crahses or causes segmentation fault                         */
#ifndef CESTER_NO_MEM_TEST
    CESTER_RESULT_MEMORY_LEAK,    /**< the test case passes or fails but failed to free allocated memory          */
#endif
    CESTER_RESULT_TIMED_OUT,      /**< cester terminated the test case because it running for too long            */
    CESTER_RESULT_UNKNOWN         /**< the test case was never ran                                                */
};

typedef enum cester_test_type {
    CESTER_NORMAL_TEST,             /**< normal test in global or test suite. For internal use only.                                              */
    CESTER_NORMAL_TODO_TEST,        /**< test to be implemented in future. For internal use only.                                                 */
    CESTER_NORMAL_SKIP_TEST,        /**< test to be skipped. For internal use only.                                                               */
    CESTER_BEFORE_ALL_TEST,         /**< test to run before all normal tests in global or test suite. For internal use only.                      */
    CESTER_BEFORE_EACH_TEST,        /**< test to run before each normal tests in global or test suite. For internal use only.                     */
    CESTER_AFTER_ALL_TEST,          /**< test to run after all normal tests in global or test suite. For internal use only.                       */
    CESTER_AFTER_EACH_TEST,         /**< test to run after each normal tests in global or test suite. For internal use only.                      */
    CESTER_OPTIONS_FUNCTION,        /**< the cester function for test, this wil be excuted before running the tests. For internal use only.       */
    CESTER_TESTS_TERMINATOR         /**< the last value in the test cases to terminates the tests. For internal use only.                         */
} TestType;

/**
    The test instance that contains the command line argument 
    length and values, with void* pointer that can be used to 
    share data between unit tests.
*/
typedef struct test_instance {
    unsigned argc;                   /**< the length of the command line arg                            */
    char **argv;                   /**< the command line arguments                                    */
    void *arg;                     /**< pointer to an object that can be passed between unit tests    */
} TestInstance;

/**
    The function signature for each test case and the before after functions. 
    It accepts the ::test_instance as it only argument. 
*/
typedef void (*cester_test)(TestInstance*);

/**
    The function signature for function to execute before and after each test 
    cases. It accepts the ::test_instance, char* and unsigned as parameters. 
*/
typedef void (*cester_before_after_each)(TestInstance*, char * const, unsigned);

/**
    A void function signature with no return type and no parameters.
*/
typedef void (*cester_void)();

typedef struct test_case {
    unsigned execution_status;                        /**< the test execution result status. For internal use only.                                      */
    unsigned line_num;                                /**< the line number where the test case is created. For internal use only.                        */
    enum cester_test_status expected_result;           /**< The expected result for the test case. For internal use only.                                 */
#ifndef CESTER_NO_TIME
    double start_tic;                            /**< the time taken for the test case to complete. For internal use only.                          */
    double execution_time;                            /**< the time taken for the test case to complete. For internal use only.                          */
#endif
    char* execution_output;                           /**< the test execution output in string. For internal use only.                                   */
    char *name;                                       /**< the test function name. For internal use only.                                                */
    cester_test test_function;                       /**< the function that enclosed the tests. For internal use only.                                  */
    cester_before_after_each test_ba_function;       /**< the function that enclosed the tests. For internal use only.                                  */
    cester_void test_void_function;                  /**< the function that enclosed the tests. For internal use only.                                  */
    TestType test_type;                               /**< the type of the test function. For internal use only.                                         */
} TestCase; 

#ifndef CESTER_NO_MEM_TEST

typedef struct allocated_memory {
    unsigned line_num;                 /**< the line number where the memory was allocated. For internal use only.   */
    unsigned allocated_bytes;          /**< the number of allocated bytes. For internal use only.                    */
    char* address;                   /**< the allocated pointer address. For internal use only.                    */
    const char* function_name;       /**< the function where the memory is allocated in. For internal use only.    */
    const char* file_name;           /**< the file name where the memory is allocated. For internal use only.      */
} AllocatedMemory;

#endif

/**
    The initial amount of item the ::CesterArray can accept the first 
    time it initialized.
*/
#define CESTER_ARRAY_INITIAL_CAPACITY 30

/**
    The maximum number of item the ::CesterArray can contain, in case of 
    the Memory manager array reaching this max capacity continous mem 
    test will be disabled.
*/
#define CESTER_ARRAY_MAX_CAPACITY ((size_t) - 5)

typedef struct cester_array_struct {
    size_t size;                        /**< the size of the item in the array                         */
    size_t capacity;                    /**< the number of item the array can contain before expanding */
    void** buffer;                      /**< pointer to the pointers of items added to the array       */
} CesterArray;


#define CESTER_ARRAY_FOREACH(w,x,y,z) for (x = 0; x < w->size; ++x) {\
                                          void* y = w->buffer[x];\
                                          z\
                                      }

/**
    This structure manages the _BEFORE_ and _AFTER_ functions 
    for the test main ::test_instance. And also accounts for all the 
    registered test cases. This is for Cester internal use only.
*/
typedef struct super_test_instance {
    unsigned no_color;                                    /**< Do not print to the console with color if one. For internal use only.                                                            */
    unsigned total_tests_count;                           /**< the total number of tests to run, assert, eval e.t.c. To use in your code call CESTER_TOTAL_TESTS_COUNT                          */
    unsigned total_tests_ran;                             /**< the total number of tests that was run e.t.c. To use in your code call CESTER_TOTAL_TESTS_RAN                                    */
    unsigned total_failed_tests_count;                    /**< the total number of tests that failed. To use in your code call CESTER_TOTAL_FAILED_TESTS_COUNT                                  */
    unsigned total_passed_tests_count;                    /**< the total number of tests that passed. To use in your code call CESTER_TOTAL_FAILED_TESTS_COUNT                                  */
    unsigned verbose;                                     /**< prints as much info as possible into the output stream                                                                           */
    unsigned minimal;                                     /**< prints minimal output into the output stream                                                                                     */
    unsigned print_version;                               /**< prints cester version before running tests                                                                                       */
    unsigned selected_test_cases_size;                    /**< the number of selected test casses from command line. For internal use only.                                                     */
    unsigned selected_test_cases_found;                   /**< the number of selected test casses from command line that is found in the test file. For internal use only.                      */
    unsigned single_output_only;                          /**< display the output for a single test only no summary and syntesis. For internal use only.                                        */
    unsigned mem_test_active;                             /**< Enable or disable memory test at runtime. Enabled by default. For internal use only.                                             */
    unsigned current_execution_status;                    /**< the current test case status. This is used when the test cases run on a single process. For internal use only.                   */
    unsigned isolate_tests;                               /**< Isolate each test case to run in different process to prevent a crashing test case from crahsing others. For internal use only.  */
    unsigned skipped_test_count;                          /**< The number of test cases to be skipped. For internal use only.                                                                   */
    unsigned todo_tests_count;                            /**< The number of test cases that would be implemented in future. For internal use only.                                             */
    unsigned format_test_name;                            /**< Format the test name for fine output e.g. 'test_file_exit' becomes 'test file exist'. For internal use only.                     */
#ifndef CESTER_NO_TIME
    double start_tic;                                   /**< The unix time when the tests starts. For internal use only. */
#endif
    char* flattened_cmd_argv;                           /**< Flattened command line argument for sub process. For internal use only.                                                          */
    char* test_file_path;                               /**< The main test file full path. For internal use only.                                                                             */
    char* output_format;                                /**< The output format to print the test result in. For internal use only.                                                            */
    TestInstance *test_instance ;                       /**< The test instance for sharing datas. For internal use only.                                                            */
    FILE* output_stream;                                /**< Output stream to write message to, stdout by default. For internal use only.                                                     */
    char** selected_test_cases_names;                   /**< selected test cases from command line. For internal use only. e.g. --cester-test=Test2,Test1                                     */
    TestCase* current_test_case;                        /**< The currently running test case. For internal use only.                                                                          */
    CesterArray *registered_test_cases;                 /**< all the manually registered test cases in the instance. For internal use only.                                                   */
#ifndef CESTER_NO_MEM_TEST
    CesterArray* mem_alloc_manager;                     /**< the array of allocated memory. For testing and detecting memory leaks. For internal use only.                                    */
#endif
} SuperTestInstance;

/* CesterArray */
static __CESTER_INLINE__ unsigned cester_array_init(CesterArray**);
static __CESTER_INLINE__ unsigned cester_array_add(CesterArray*, void*);
static __CESTER_INLINE__ void* cester_array_remove_at(CesterArray*, unsigned);

static __CESTER_INLINE__ unsigned cester_run_all_test(unsigned, char **);
static __CESTER_INLINE__ void cester_str_value_after_first(char *, char, char**);


SuperTestInstance superTestInstance = { 
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    1,
    CESTER_RESULT_SUCCESS,
    1,
    0,
    0,
    1,
#ifndef CESTER_NO_TIME
    0.0,
#endif
    (char*)"",
#ifdef __BASE_FILE__
    (char*)__BASE_FILE__,
#else
    (char*)__FILE__,
#endif
    (char*)"text",
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
#ifndef CESTER_NO_MEM_TEST
    NULL
#endif
};

#ifdef _MSC_VER
#define cester_sprintf(x,y,z,a,b,c) sprintf_s(x, y, z, a, b, c);
#define cester_sprintf1(x,y,z,a) cester_sprintf(x,y,z,a,"","")
#define cester_sprintf2(x,y,z,a,b) cester_sprintf(x,y,z,a,b,"")
#define cester_sprintf3(x,y,z,a,b,c) cester_sprintf(x,y,z,a,b,c)
#else
#define cester_sprintf(x,y,z,a,b) sprintf(x, z, a, b);
#define cester_sprintf1(x,y,z,a) sprintf(x, z, a)
#define cester_sprintf2(x,y,z,a,b) sprintf(x, z, a, b)
#define cester_sprintf3(x,y,z,a,b,c) sprintf(x, z, a, b, c)
#endif


/* cester options */

/**
    Change the output stream used by cester to write data. The default is `stdout`. 
    E.g to change the output stream to a file. 
    
    \code{.c} 
    CESTER_CHANGE_STREAM(fopen("./test.txt", "w+"));
    \endcode
    
    The code above changes the stream to a file test.txt, all the output from 
    the test will be written in the file.
**/
#define CESTER_CHANGE_STREAM(x) (superTestInstance.output_stream = x)

/**
    Do not print to the output stream with color. This should be 
    used to prevent writing the color bytes into a file stream (in case).
    
    This option can also be set from the command line with `--cester-nocolor`
*/
#define CESTER_NOCOLOR() (superTestInstance.no_color = 1)

/**
    Print minimal info into the output stream. With this option set the 
    expression evaluated will not be printed in the result output. 
    
    This option can also be set from the command line with `--cester-minimal`
*/
#define CESTER_MINIMAL() (superTestInstance.minimal = 1)

/**
    Print as much info as possible into the output stream. With this option set  
    both passed and failed expression evaluated will be printed in the result. 
    
    This option can also be set from the command line with `--cester-verbose`
*/
#define CESTER_VERBOSE() (superTestInstance.verbose = 1)

/**
    Print cester version before running any test. 
    
    This option can also be set from the command line with `--cester-printversion`
**/
#define CESTER_PRINT_VERSION() (superTestInstance.print_version = 1)

/**
    Display test for a single test case only, skip syntesis and summary.
    
    This option can also be set from the command line with `--cester-singleoutput`
**/
#define CESTER_SINGLE_OUPUT_ONLY() (superTestInstance.single_output_only = 1)

/**
    Do not isolate the tests, run each of the test cases in a single process. 
    The drawback is if a test case causes segfault or crash the entire test 
    crashes and no summary is displayed. No isolation causes a crash one 
    crash all scenerio.
    
    This option can also be set from the command line with `--cester-noisolation`
**/
#define CESTER_NO_ISOLATION() (superTestInstance.isolate_tests = 0)

/**
    Disable memory leak detection test.
    
    This option can also be set from the command line with `--cester-nomemtest`
**/
#define CESTER_NO_MEMTEST() (superTestInstance.mem_test_active = 0)

/**
    Enable memory allocation. The combination of CESTER_NO_MEMTEST() and 
    CESTER_DO_MEMTEST() is valid only in non isolated tests. 
    
    This togle combined with `CESTER_NO_MEMTEST()` can be used to selectively 
    test memory allocation in a test e.g. Calling CESTER_NO_MEMTEST() before 
    a test case will prevent memory test from the beginning of that function and 
    calling CESTER_DO_MEMTEST() at the end of the test case will ensure memory 
    allocation will be validated in all the other test case that follows.
**/
#define CESTER_DO_MEMTEST() (superTestInstance.mem_test_active = 1)

/**
    Change the output format to text
*/
#define CESTER_OUTPUT_TEXT() superTestInstance.output_format = (char*) "text";

/**
    Change the output format to junitxml
*/
#define CESTER_OUTPUT_JUNITXML() superTestInstance.output_format = (char*) "junitxml";

/**
    Change the output format to TAP (Test Anything Protocol)
*/
#define CESTER_OUTPUT_TAP() superTestInstance.output_format = (char*) "tap";

/**
    Change the output format to TAP (Test Anything Protocol) Version 13
*/
#define CESTER_OUTPUT_TAPV13() superTestInstance.output_format = (char*) "tapV13";

/**
    Format the test case name for output. E.g the test name 
    `modify_test_instance` becomes `modify test instance`. This 
    does not apply to junitxml as the test name remain the way it 
    declared in the test source.
*/
#define CESTER_FORMAT_TESTNAME() superTestInstance.format_test_name = 1;

/**
    Do not format the test case name, it remain the way it 
    declared in the test source.
*/
#define CESTER_DONT_FORMAT_TESTNAME() superTestInstance.format_test_name = 0;

/* test counts */

/**
    The total number of tests that is present in the test file.
*/
#define CESTER_TOTAL_TESTS_COUNT (superTestInstance.total_tests_count)

/**
    The total number of tests that was ran.
*/
#define CESTER_TOTAL_TESTS_RAN (superTestInstance.total_tests_ran)

/**
    The total number of tests that failed.
*/
#define CESTER_TOTAL_FAILED_TESTS_COUNT (superTestInstance.total_failed_tests_count)

/**
    The number of test that was skipped. 
    
    If the selected test_cases_size is 0 then no test was skipped else the 
    number of executed selected test cases minus the total number of test cases 
    is the number of test that was skipped.
*/
#define CESTER_TOTAL_TESTS_SKIPPED (superTestInstance.skipped_test_count)

/**
    The total number of tests that passed. CESTER_TOTAL_TESTS_COUNT - CESTER_TOTAL_FAILED_TESTS_COUNT
*/
#define CESTER_TOTAL_PASSED_TESTS_COUNT (superTestInstance.total_passed_tests_count)

/**
    The total number of tests that passed. CESTER_TOTAL_TESTS_COUNT - CESTER_TOTAL_FAILED_TESTS_COUNT
*/
#define CESTER_TOTAL_TODO_TESTS (superTestInstance.todo_tests_count)

/**
    Run all the test registered in cester, the TestInstance* pointer 
    will be initalized with the pointer to the string arguments from 
    cli and the length of the arguments. The `void* arg` pointer in the 
    TestInstance* can be initalized in the *_BEFORE_* function to share 
    data between the unit tests.
*/
#define CESTER_RUN_ALL_TESTS(x,y) cester_run_all_test(x,y)

#ifdef _WIN32
    int default_color = CESTER_RESET_TERMINAL;
    HANDLE hConsole;
#else
    const char* default_color = CESTER_RESET_TERMINAL;
#endif

static __CESTER_INLINE__ char *cester_extract_name(char const* const file_path) {
    unsigned i = 0, j = 0;
    unsigned found_seperator = 0;
    char *file_name_only = (char*) malloc (sizeof (char) * 30);
    while (file_path[i] != '\0') {
        if (file_path[i] == '\\' || file_path[i] == '/') {
            found_seperator = 1;
            j = 0;
        } else {
            found_seperator = 0;
            file_name_only[j] = file_path[i];
            j++;
        }
        ++i;
    }
    file_name_only[j] = '\0';
    return file_name_only;
}

static __CESTER_INLINE__ char *cester_extract_name_only(char const* const file_path) {
    unsigned i = 0;
    char *file_name = cester_extract_name(file_path);
    while (file_name[i] != '\0') {
        if (file_name[i] == '.') {
            file_name[i] = '\0';
            break;
        }
        ++i;
    }
    return file_name;
}

static __CESTER_INLINE__ unsigned cester_str_after_prefix(const char* arg, char* prefix, unsigned prefix_size, char** out) {
    unsigned i = 0;
    *out = (char*) malloc (sizeof (char) * 200);
    
    while (1) {
        if (arg[i] == '\0') {
            if (i < prefix_size) {
                free(*out);
                return 0;
            } else {
                break;
            }
        }
        if (arg[i] != prefix[i] && i < prefix_size) {
            free(*out);
            return 0;
        }
        if (i >= prefix_size) {
            (*out)[i-prefix_size] = arg[i];
        }
        ++i;
    }
    (*out)[i-prefix_size] = '\0';
    return 1;
}

static __CESTER_INLINE__ char* cester_str_replace(char* str, char old_char, char new_char) {
    char* tmp = (char*) malloc(strlen(str) + 1);
    unsigned index = 0;
    do {
        if (*str == old_char) {
            tmp[index] = new_char;
        } else {
            tmp[index] = *str;
        }
        ++str;
        index++;
    } while (*str != '\0');
    tmp[index] = '\0';
    
    return tmp;
}

static __CESTER_INLINE__ unsigned cester_string_equals(char* arg, char* arg1) {
    unsigned i = 0;
    if (arg == NULL || arg1 == NULL) {
        return 0;
    }
    while (1) {
        if (arg[i] == '\0' && arg1[i] == '\0') {
            break;
        }
        if (arg[i] != arg1[i]) {
            return 0;
        }
        ++i;
    }
    return 1;
}

static __CESTER_INLINE__ unsigned cester_string_starts_with(char* arg, char* arg1) {
    unsigned i = 0;
    while (1) {
        if (arg[i] == '\0' && arg1[i] == '\0') {
            break;
        }
        if (arg[i] != arg1[i]) {
            if (arg1[i] == '\0') {
                break;
            } else {
                return 0;
            }
        }
        ++i;
    }
    return 1;
}

static __CESTER_INLINE__ void unpack_selected_extra_args(char *arg, char*** out, unsigned* out_size) {
    unsigned i = 0;
    unsigned size = 0, current_index = 0;
    char* prefix = (char*) "test=";
    (*out) = (char**) malloc(sizeof(char**));
    
    (*out)[size] = (char*) malloc(sizeof(char*) * 200);
    while (1) {
        if (arg[i] == '\0') {
            ++size;
            break;
        }
        if (arg[i] != prefix[i] && i < 5) {
            break;
        }
        if (arg[i] == ',') {
            (*out)[size][current_index] = '\0';
            current_index = 0;
            ++size;
            (*out)[size] = (char*) malloc(sizeof(char*) * 200);
            goto continue_loop;
        }
        if (i >= 5) {
            (*out)[size][current_index] = arg[i];
            ++current_index;
        }
        continue_loop:
                      ++i;
    }
    (*out)[size-1][current_index] = '\0';
    *out_size = size;
}

static __CESTER_INLINE__ void cester_str_value_after_first(char *arg, char from, char** out) {
    unsigned i = 0, index = 0;
    unsigned found_char = 0;
    *out = (char*) malloc(sizeof(char) * 200);
    while (1) {
        if (arg[i] == '\0') {
            break;
        }
        if (arg[i] == from) {
            found_char = 1;
            goto continue_loop;
        }
        if (found_char == 1) {
            (*out)[index] = arg[i];
            ++index;
        }
        continue_loop:
                      ++i;
    }
    (*out)[index] = '\0';
}

static __CESTER_INLINE__ void cester_concat_str(char **out, const char * extra) {
    size_t i = 0, index = strlen(*out);
    if (index == 0) {
        (*out) = (char*) malloc(sizeof(char) * 80000 );
    }
    if (extra == NULL) {
        extra = "(null)";
    }
    while (1) {
        if (extra[i] == '\0') {
            break;
        }
        (*out)[index] = extra[i];
        ++index;
        ++i;
    }
    (*out)[index] = '\0';
}

/* For some wierd reasons sprintf clears old array first 
before concatenatng in old compiler e.g Turbo C. 
So we first convert int to str then concat it to str*/

static __CESTER_INLINE__ void cester_concat_char(char **out, char extra) {
    char tmp[5] ;
    cester_sprintf1(tmp, 5, "%c", extra);
    cester_concat_str(out, tmp);
}

static __CESTER_INLINE__ void cester_concat_int(char **out, int extra) {
    char tmp[30];
    cester_sprintf1(tmp, 30, "%d", extra);
    cester_concat_str(out, tmp);
}

static __CESTER_INLINE__ void cester_ptr_to_str(char **out, void* extra) {
    unsigned i = 0;
    (*out) = (char*) malloc(sizeof(char) * 30 );
    cester_sprintf1((*out), (30), "%p", extra);
}

static __CESTER_INLINE__ unsigned cester_is_validate_output_option(char *format_option) {
    return (cester_string_equals(format_option, (char*) "junitxml") ||  
	    cester_string_equals(format_option, (char*) "tap") ||
            cester_string_equals(format_option, (char*) "tapV13") ||  
            cester_string_equals(format_option, (char*) "text"));
}

#ifdef _WIN32
#define CESTER_SELECTCOLOR(x) (superTestInstance.no_color == 1 ? default_color : x)
#else 
#define CESTER_SELECTCOLOR(x) (superTestInstance.no_color == 1 ? "" : x)
#endif
#define CESTER_GET_RESULT_AGGR (superTestInstance.total_failed_tests_count == 0 ? "SUCCESS" : "FAILURE")
#define CESTER_GET_RESULT_AGGR_COLOR (superTestInstance.total_failed_tests_count == 0 ? (CESTER_FOREGROUND_GREEN) : (CESTER_FOREGROUND_RED))

#ifdef _WIN32
#define CESTER_DELEGATE_FPRINT_STR(x,y) SetConsoleTextAttribute(hConsole, CESTER_SELECTCOLOR(x)); fprintf(superTestInstance.output_stream, "%s", y)
#define CESTER_DELEGATE_FPRINT_INT(x,y) SetConsoleTextAttribute(hConsole, CESTER_SELECTCOLOR(x)); fprintf(superTestInstance.output_stream, "%d", y)
#define CESTER_DELEGATE_FPRINT_UINT(x,y) SetConsoleTextAttribute(hConsole, CESTER_SELECTCOLOR(x)); fprintf(superTestInstance.output_stream, "%u", y)
#ifndef CESTER_NO_TIME
#define CESTER_DELEGATE_FPRINT_DOUBLE(x,y) SetConsoleTextAttribute(hConsole, CESTER_SELECTCOLOR(x)); fprintf(superTestInstance.output_stream, "%f", y)
#define CESTER_DELEGATE_FPRINT_DOUBLE_2(x,y) SetConsoleTextAttribute(hConsole, CESTER_SELECTCOLOR(x)); fprintf(superTestInstance.output_stream, "%.2f", y)
#endif
#else
#define CESTER_DELEGATE_FPRINT_STR(x,y) fprintf(superTestInstance.output_stream, "%s%s%s", CESTER_SELECTCOLOR(x), y, CESTER_SELECTCOLOR(CESTER_RESET_TERMINAL))
#define CESTER_DELEGATE_FPRINT_INT(x,y) fprintf(superTestInstance.output_stream, "%s%d%s", CESTER_SELECTCOLOR(x), y, CESTER_SELECTCOLOR(CESTER_RESET_TERMINAL))
#define CESTER_DELEGATE_FPRINT_UINT(x,y) fprintf(superTestInstance.output_stream, "%s%u%s", CESTER_SELECTCOLOR(x), y, CESTER_SELECTCOLOR(CESTER_RESET_TERMINAL))
#ifndef CESTER_NO_TIME
#define CESTER_DELEGATE_FPRINT_DOUBLE(x,y) fprintf(superTestInstance.output_stream, "%s%f%s", CESTER_SELECTCOLOR(x), y, CESTER_SELECTCOLOR(CESTER_RESET_TERMINAL))
#define CESTER_DELEGATE_FPRINT_DOUBLE_2(x,y) fprintf(superTestInstance.output_stream, "%s%.2f%s", CESTER_SELECTCOLOR(x), y, CESTER_SELECTCOLOR(CESTER_RESET_TERMINAL))
#endif
#endif

static __CESTER_INLINE__ unsigned cester_string_equals(char* arg, char* arg1);

static __CESTER_INLINE__ void cester_print_version() {
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "CESTER v");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), CESTER_VERSION);
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "\n");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), CESTER_LICENSE);
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "\n");
}

static __CESTER_INLINE__ void cester_print_help() {
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "Usage: ./");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), cester_extract_name_only(superTestInstance.test_file_path));
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), " [-options] [args...]\n");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "\nwhere options include:\n");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "    --cester-minimal         print minimal info into the output stream\n");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "    --cester-verbose         print as much info as possible into the output stream\n");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "    --cester-nocolor         do not print info with coloring\n");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "    --cester-singleoutput    display cester version and exit\n");
#ifndef CESTER_NO_MEM_TEST
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "    --cester-nomemtest       disable memory leak detection in the tests\n");
#endif
#ifdef __CESTER_STDC_VERSION__
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "    --cester-noisolation     run all the test on a single process. Prevents recovery from crash.\n");
#endif
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "    --cester-printversion    display cester version before running the tests\n");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "    --cester-dontformatname  leave the test case name as declared in the source file in the output\n");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "    --cester-test=Test1,...  run only selected tests. Seperate the test cases by comma\n");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "    --cester-output=[FORMAT] change the format in which the test results are printed\n");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "    --cester-version         display cester version and exit\n");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "    --cester-help            display this help info version and exit\n");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "See https://exoticlibraries.github.io/libcester/docs/options.html for more details\n");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "\nSupported output formats. [FORMAT]:\n");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "    text\n");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "    junitxml\n");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "    tap\n");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "    tapV13\n");
}

static __CESTER_INLINE__ void cester_print_assertion(char const* const expression, char const* const file_path, unsigned const line_num) {
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, (superTestInstance.minimal == 0 ? file_path : cester_extract_name(file_path) ));
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, ":");
    cester_concat_int(&(superTestInstance.current_test_case)->execution_output, line_num);
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, ":");
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, " in '");
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, (superTestInstance.current_test_case)->name);
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "' expr => '");
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, expression);
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "'");
    
    /*CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), (superTestInstance.verbose == 1 ? file_path : cester_extract_name(file_path) ));
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), ":");
    CESTER_DELEGATE_FPRINT_INT((CESTER_FOREGROUND_YELLOW), line_num);
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), ":");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), " in '");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), (superTestInstance.current_test_case)->name);
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "' expr => '");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), expression);
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "'");**/
}

static __CESTER_INLINE__ void cester_print_expect_actual(unsigned expecting, char const* const expect, char const* const received, char const* const file_path, unsigned const line_num) {
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, (superTestInstance.minimal == 0 ? file_path : cester_extract_name(file_path) ));
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, ":");
    cester_concat_int(&(superTestInstance.current_test_case)->execution_output, line_num);
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, ":");
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, " in '");
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, (superTestInstance.current_test_case)->name);
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "' =>");
    if (expecting == 0) {
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, " not expecting ");
    } else {
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, " expected ");
    }

    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "'");
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, expect);
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "'");
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, ", received ");
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "'");
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, received);
    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "'");
    
    /*CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), (superTestInstance.verbose == 1 ? file_path : cester_extract_name(file_path) ));
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), ":");
    CESTER_DELEGATE_FPRINT_INT((CESTER_FOREGROUND_YELLOW), line_num);
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), ":");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), " in '");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), (superTestInstance.current_test_case)->name);
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "' =>");
    if (expecting == 0) {
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), " not expecting ");
    } else {
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), " expected ");
    }
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), received);
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), ", received ");
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), expect);*/
}

#ifndef CESTER_NO_TIME
static __CESTER_INLINE__ void print_test_result(double time_spent) {
#else
static __CESTER_INLINE__ void print_test_result() {
#endif
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "\nRan ");
    CESTER_DELEGATE_FPRINT_INT((CESTER_FOREGROUND_WHITE), (superTestInstance.selected_test_cases_size == 0 ? CESTER_TOTAL_TESTS_COUNT : CESTER_TOTAL_TESTS_RAN));
    #ifndef CESTER_NO_TIME
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), " test(s) in ");
        CESTER_DELEGATE_FPRINT_DOUBLE_2((CESTER_FOREGROUND_WHITE), (time_spent > 60 ? (time_spent / 60) : time_spent) );
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), (time_spent > 60 ? " Minutes\n" : " Seconds\n" ));
    #else
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), " test(s)\n");
    #endif
    
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "Synthesis: ");
    CESTER_DELEGATE_FPRINT_STR(CESTER_GET_RESULT_AGGR_COLOR, CESTER_GET_RESULT_AGGR);
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), " Tests: ");
    CESTER_DELEGATE_FPRINT_INT((CESTER_FOREGROUND_YELLOW), CESTER_TOTAL_TESTS_COUNT);
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), " | Passing: ");
    CESTER_DELEGATE_FPRINT_INT((CESTER_FOREGROUND_GREEN), CESTER_TOTAL_PASSED_TESTS_COUNT);
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), " | Failing: ");
    CESTER_DELEGATE_FPRINT_INT((CESTER_FOREGROUND_RED), CESTER_TOTAL_FAILED_TESTS_COUNT);
    if (CESTER_TOTAL_TESTS_SKIPPED > 0) {
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), " | Skipped: ");
        CESTER_DELEGATE_FPRINT_INT((CESTER_FOREGROUND_YELLOW), CESTER_TOTAL_TESTS_SKIPPED);
    }
    if (CESTER_TOTAL_TODO_TESTS > 0) {
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), " | Todo: ");
        CESTER_DELEGATE_FPRINT_INT((CESTER_FOREGROUND_YELLOW), CESTER_TOTAL_TODO_TESTS);
    }
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "\n"); 
}

static __CESTER_INLINE__ void print_test_case_result(TestCase* test_case) {
    #ifdef _WIN32
        unsigned print_color = __CESTER_CAST_CHAR_ARRAY__ CESTER_FOREGROUND_GRAY;
    #else 
        char* print_color = __CESTER_CAST_CHAR_ARRAY__ CESTER_FOREGROUND_GRAY;
    #endif
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), "  ");
    if (test_case->test_type == CESTER_NORMAL_TODO_TEST || test_case->test_type == CESTER_NORMAL_SKIP_TEST) {
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), "o ");
        #ifndef CESTER_NO_TIME
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), "(");
            CESTER_DELEGATE_FPRINT_DOUBLE_2((CESTER_FOREGROUND_GRAY), (test_case->execution_time > 60 ? (test_case->execution_time / 60) : test_case->execution_time));
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), (test_case->execution_time > 60 ? "m" : "s"));
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), ") ");
        #endif
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), (superTestInstance.format_test_name == 1 ? cester_str_replace(test_case->name, '_', ' ') : test_case->name ));
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), (test_case->test_type == CESTER_NORMAL_TODO_TEST ? " TODO " : " SKIP "));
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "\n");
    } else {
    	if (test_case->execution_status == CESTER_RESULT_SUCCESS) {
	        #ifdef _WIN32
                CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GREEN), "+ ");
	        #else
                #ifdef __CESTER_STDC_VERSION__
                    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GREEN), "\u2713 ");
                #else
                    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GREEN), "+ ");
                #endif
	        #endif
	    } else {
	        #ifdef _WIN32
                CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_RED), "- ");
	        #else
                #ifdef __CESTER_STDC_VERSION__
                    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_RED), "X ");
                #else
                    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_RED), "- ");
                #endif
	        #endif
	        print_color = __CESTER_CAST_CHAR_ARRAY__ CESTER_FOREGROUND_RED;
	    }
        #ifndef CESTER_NO_TIME
	        CESTER_DELEGATE_FPRINT_STR((print_color), "(");
	        CESTER_DELEGATE_FPRINT_DOUBLE_2((print_color), (test_case->execution_time > 60 ? (test_case->execution_time / 60) : test_case->execution_time));
	        CESTER_DELEGATE_FPRINT_STR((print_color), (test_case->execution_time > 60 ? "m" : "s"));
            CESTER_DELEGATE_FPRINT_STR((print_color), ") ");
        #endif
            CESTER_DELEGATE_FPRINT_STR((print_color), (superTestInstance.format_test_name == 1 ? cester_str_replace(test_case->name, '_', ' ') : test_case->name ));
            CESTER_DELEGATE_FPRINT_STR((print_color), "\n");
    }
}

static __CESTER_INLINE__ void print_test_case_outputs(TestCase* test_case) {
    if (test_case->execution_status == CESTER_RESULT_SEGFAULT || test_case->execution_status == CESTER_RESULT_TERMINATED) {
        if (test_case->execution_status == CESTER_RESULT_SEGFAULT) {
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "SegfaultError ");
        } else {
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "PrematureTermination ");
        }
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), (superTestInstance.minimal == 0 ? superTestInstance.test_file_path : cester_extract_name(superTestInstance.test_file_path) ));
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), ":");
        CESTER_DELEGATE_FPRINT_INT((CESTER_FOREGROUND_WHITE), test_case->line_num);
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), ": ");
        if (test_case->execution_status == CESTER_RESULT_SEGFAULT) {
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "Segmentation fault ");
        } else {
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "Premature Termination ");
        }
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "in '");
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), test_case->name);
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "' \n");
        
    }
    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), test_case->execution_output);
}

static __CESTER_INLINE__ void write_testcase_tap(TestCase *a_test_case, char* file_name, int index) {
    #ifdef _WIN32
        unsigned print_color = __CESTER_CAST_CHAR_ARRAY__ CESTER_FOREGROUND_YELLOW;
    #else 
        char* print_color = __CESTER_CAST_CHAR_ARRAY__ CESTER_FOREGROUND_YELLOW;
    #endif
    if (a_test_case->execution_status == CESTER_RESULT_SUCCESS || 
        a_test_case->test_type == CESTER_NORMAL_SKIP_TEST || 
        a_test_case->test_type == CESTER_NORMAL_TODO_TEST) {
            
        if (a_test_case->execution_status == CESTER_RESULT_SUCCESS) {
            print_color = __CESTER_CAST_CHAR_ARRAY__ CESTER_FOREGROUND_GREEN;
        }
        CESTER_DELEGATE_FPRINT_STR((print_color), "ok ");
        
    } else {
        print_color = __CESTER_CAST_CHAR_ARRAY__ CESTER_FOREGROUND_RED;
        CESTER_DELEGATE_FPRINT_STR((print_color), "not ok ");
    }
    CESTER_DELEGATE_FPRINT_INT((print_color), index);
    CESTER_DELEGATE_FPRINT_STR((print_color), " - ");
    if (a_test_case->test_type == CESTER_NORMAL_SKIP_TEST) {
        CESTER_DELEGATE_FPRINT_STR((print_color), "# SKIP ");
        
    } else if (a_test_case->test_type == CESTER_NORMAL_TODO_TEST) {
        CESTER_DELEGATE_FPRINT_STR((print_color), "# TODO ");
        
    }
    CESTER_DELEGATE_FPRINT_STR((print_color), (superTestInstance.format_test_name == 1 ? cester_str_replace(a_test_case->name, '_', ' ') : a_test_case->name ));
    CESTER_DELEGATE_FPRINT_STR((print_color), ", ");
    switch (a_test_case->execution_status) {
        case CESTER_RESULT_SUCCESS:
            CESTER_DELEGATE_FPRINT_STR((print_color), "Passed");
            break;
        case CESTER_RESULT_SEGFAULT:
            CESTER_DELEGATE_FPRINT_STR((print_color), "Failed: Segmentation fault ");
            break;
        case CESTER_RESULT_TERMINATED:
            CESTER_DELEGATE_FPRINT_STR((print_color), "Failed: Premature Termination ");
            break;
#ifndef CESTER_NO_MEM_TEST
        case CESTER_RESULT_MEMORY_LEAK:
            CESTER_DELEGATE_FPRINT_STR((print_color), "Failed: Memory leak");
            break;
#endif
        default:
            if (a_test_case->test_type != CESTER_NORMAL_SKIP_TEST && 
                a_test_case->test_type != CESTER_NORMAL_TODO_TEST) {
                
                CESTER_DELEGATE_FPRINT_STR((print_color), "Failed");
            }
            break;
    }
    CESTER_DELEGATE_FPRINT_STR((print_color), "\n");
    if (superTestInstance.verbose == 1) {
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), a_test_case->execution_output);
    }
}

static __CESTER_INLINE__ void write_testcase_tap_v13(TestCase *a_test_case, char* file_name, int index) {
    #ifdef _WIN32
        unsigned print_color = __CESTER_CAST_CHAR_ARRAY__ CESTER_FOREGROUND_YELLOW;
    #else 
        char* print_color = __CESTER_CAST_CHAR_ARRAY__ CESTER_FOREGROUND_YELLOW;
    #endif
    if (a_test_case->execution_status == CESTER_RESULT_SUCCESS || 
        a_test_case->test_type == CESTER_NORMAL_SKIP_TEST || 
        a_test_case->test_type == CESTER_NORMAL_TODO_TEST) {
            
        if (a_test_case->execution_status == CESTER_RESULT_SUCCESS) {
            print_color = __CESTER_CAST_CHAR_ARRAY__ CESTER_FOREGROUND_GREEN;
        }
        CESTER_DELEGATE_FPRINT_STR((print_color), "ok ");
        
    } else {
        print_color = __CESTER_CAST_CHAR_ARRAY__ CESTER_FOREGROUND_RED;
        CESTER_DELEGATE_FPRINT_STR((print_color), "not ok ");
    }
    CESTER_DELEGATE_FPRINT_INT((print_color), index);
    CESTER_DELEGATE_FPRINT_STR((print_color), " - ");
    if (a_test_case->test_type == CESTER_NORMAL_SKIP_TEST) {
        CESTER_DELEGATE_FPRINT_STR((print_color), "# SKIP ");
        
    } else if (a_test_case->test_type == CESTER_NORMAL_TODO_TEST) {
        CESTER_DELEGATE_FPRINT_STR((print_color), "# TODO ");
        
    }
    CESTER_DELEGATE_FPRINT_STR((print_color), (superTestInstance.format_test_name == 1 ? cester_str_replace(a_test_case->name, '_', ' ') : a_test_case->name ));
    CESTER_DELEGATE_FPRINT_STR((print_color), "\n");
    if (superTestInstance.verbose == 1 && a_test_case->test_type != CESTER_NORMAL_SKIP_TEST && 
        a_test_case->test_type != CESTER_NORMAL_TODO_TEST) {
        if (a_test_case->execution_status == CESTER_RESULT_SUCCESS && superTestInstance.minimal == 1) {
            return;
        }
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), "  ---\n");
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), "  at:\n");
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), "    file: ");
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), (superTestInstance.minimal == 0 ? superTestInstance.test_file_path : cester_extract_name(superTestInstance.test_file_path)));
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), "\n    test_case: ");
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), a_test_case->name);
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), "\n    line: ");
        CESTER_DELEGATE_FPRINT_INT((CESTER_FOREGROUND_GRAY), a_test_case->line_num);
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), "\n    column: 1");
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), "\n");
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), "  outputs:\n");
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), a_test_case->execution_output);
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), "  message: ");
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), (superTestInstance.format_test_name == 1 ? cester_str_replace(a_test_case->name, '_', ' ') : a_test_case->name ));
        switch (a_test_case->execution_status) {
            case CESTER_RESULT_SUCCESS:
                CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), " passed");
                break;
            case CESTER_RESULT_SEGFAULT:
                CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), " failed: Segmentation fault ");
                break;
            case CESTER_RESULT_TERMINATED:
                CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), " failed: Premature termination ");
                break;
#ifndef CESTER_NO_MEM_TEST
            case CESTER_RESULT_MEMORY_LEAK:
                CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), " failed: Memory leak");
                break;
#endif
            default:
                if (a_test_case->test_type != CESTER_NORMAL_SKIP_TEST && 
                    a_test_case->test_type != CESTER_NORMAL_TODO_TEST) {
                    
                    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), " failed");
                }
                break;
        }
        #ifndef CESTER_NO_TIME
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), "\n  time: ");
            CESTER_DELEGATE_FPRINT_DOUBLE_2((CESTER_FOREGROUND_GRAY), a_test_case->execution_time);
        #endif
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), "\n  ...\n");
    }
}

static __CESTER_INLINE__ void write_testcase_junitxml(TestCase *a_test_case, char* file_name) {
    CESTER_DELEGATE_FPRINT_STR((default_color), "    <testcase classname=\"");
    CESTER_DELEGATE_FPRINT_STR((default_color), file_name);
    CESTER_DELEGATE_FPRINT_STR((default_color), "\" name=\"");
    CESTER_DELEGATE_FPRINT_STR((default_color), a_test_case->name);
    #ifndef CESTER_NO_TIME
        CESTER_DELEGATE_FPRINT_STR((default_color), "\" time=\"");
        CESTER_DELEGATE_FPRINT_DOUBLE_2((default_color), a_test_case->execution_time);
    #endif
        CESTER_DELEGATE_FPRINT_STR((default_color), "\"");
    switch (a_test_case->execution_status) {
        case CESTER_RESULT_SUCCESS:
            CESTER_DELEGATE_FPRINT_STR((default_color), "/>\n");
            break;
        case CESTER_RESULT_SEGFAULT:
        case CESTER_RESULT_TERMINATED:
            if (a_test_case->execution_status == CESTER_RESULT_SEGFAULT) {
                CESTER_DELEGATE_FPRINT_STR((default_color), ">\n        <failure message=\"the test case crashed\" type=\"SegmentationFault\">");
                CESTER_DELEGATE_FPRINT_STR((default_color), "SegfaultError ");
            } else {
                CESTER_DELEGATE_FPRINT_STR((default_color), ">\n        <failure message=\"the test case was terminated\" type=\"PrematureTermination\">");
                CESTER_DELEGATE_FPRINT_STR((default_color), "PrematureTermination ");
            }
            CESTER_DELEGATE_FPRINT_STR((default_color), (superTestInstance.minimal == 0 ? superTestInstance.test_file_path : cester_extract_name(superTestInstance.test_file_path)));
            CESTER_DELEGATE_FPRINT_STR((default_color), ":");
            CESTER_DELEGATE_FPRINT_INT((default_color), a_test_case->line_num);
            CESTER_DELEGATE_FPRINT_STR((default_color), ": ");
            if (a_test_case->execution_status == CESTER_RESULT_SEGFAULT) {
                CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "Segmentation fault ");
            } else {
                CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "Premature Termination ");
            }
            CESTER_DELEGATE_FPRINT_STR((default_color), "in '");
            CESTER_DELEGATE_FPRINT_STR((default_color), a_test_case->name);
            CESTER_DELEGATE_FPRINT_STR((default_color), "' \n");
            CESTER_DELEGATE_FPRINT_STR((default_color), a_test_case->execution_output);
            CESTER_DELEGATE_FPRINT_STR((default_color), "        </failure>\n    </testcase>\n");
            break;
#ifndef CESTER_NO_MEM_TEST
        case CESTER_RESULT_MEMORY_LEAK:
            CESTER_DELEGATE_FPRINT_STR((default_color), ">\n        <failure message=\"the test case leaks memory\" type=\"MemoryLeakError\">");
            CESTER_DELEGATE_FPRINT_STR((default_color), a_test_case->execution_output);
            CESTER_DELEGATE_FPRINT_STR((default_color), "        </failure>\n    </testcase>\n");
            break;
#endif
        default:
            CESTER_DELEGATE_FPRINT_STR((default_color), ">\n        <failure message=\"the test case failed\" type=\"TestFailed\">");
            CESTER_DELEGATE_FPRINT_STR((default_color), a_test_case->execution_output);
            CESTER_DELEGATE_FPRINT_STR((default_color), "        </failure>\n    </testcase>\n");
            break;
    }
    
}

static __CESTER_INLINE__ int cester_print_result(TestCase cester_test_cases[], TestInstance* test_instance) {
    unsigned index_sub;
    unsigned i, index4, index5, index6, index7, index8;
    #ifndef CESTER_NO_TIME
        clock_t tok;
        double time_spent;

        tok = clock();
        time_spent = (double)(tok - superTestInstance.start_tic) / CLOCKS_PER_SEC;
    #endif
    if (superTestInstance.registered_test_cases->size == 0) {
        for (i=0;cester_test_cases[i].test_type != CESTER_TESTS_TERMINATOR;++i) {
            if (cester_test_cases[i].test_type == CESTER_AFTER_ALL_TEST && superTestInstance.single_output_only == 0) {
                ((cester_test)cester_test_cases[i].test_function)(test_instance);
            }
        }
    }
    CESTER_ARRAY_FOREACH(superTestInstance.registered_test_cases, index4, test_case, {
        if (((TestCase*)test_case)->test_type == CESTER_AFTER_ALL_TEST && superTestInstance.single_output_only == 0) {
            ((cester_test)((TestCase*)test_case)->test_function)(test_instance);
        }
    })
    if (superTestInstance.single_output_only == 0) {
        if (cester_string_equals(superTestInstance.output_format, (char*) "junitxml") == 1) {
            CESTER_DELEGATE_FPRINT_STR((default_color), "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n");
            CESTER_DELEGATE_FPRINT_STR((default_color), "<testsuite tests=\"");
            CESTER_DELEGATE_FPRINT_INT((default_color), (superTestInstance.selected_test_cases_size == 0 ? CESTER_TOTAL_TESTS_COUNT : CESTER_TOTAL_TESTS_RAN));
            CESTER_DELEGATE_FPRINT_STR((default_color), "\" failures=\"");
            CESTER_DELEGATE_FPRINT_INT((default_color), superTestInstance.total_failed_tests_count);
            CESTER_DELEGATE_FPRINT_STR((default_color), "\" name=\"");
            CESTER_DELEGATE_FPRINT_STR((default_color), cester_extract_name_only(superTestInstance.test_file_path));
            CESTER_DELEGATE_FPRINT_STR((default_color), "\" errors=\"0\" skipped=\"");
            CESTER_DELEGATE_FPRINT_INT((default_color), CESTER_TOTAL_TESTS_SKIPPED + CESTER_TOTAL_TODO_TESTS);
            #ifndef CESTER_NO_TIME
                CESTER_DELEGATE_FPRINT_STR((default_color), "\" time=\"");
                CESTER_DELEGATE_FPRINT_DOUBLE_2((default_color), time_spent);
            #endif
            CESTER_DELEGATE_FPRINT_STR((default_color), "\">\n");
            if (superTestInstance.registered_test_cases->size == 0) {
                for (i=0;cester_test_cases[i].test_type != CESTER_TESTS_TERMINATOR;++i) {
                    if (cester_test_cases[i].test_type == CESTER_NORMAL_TEST && cester_test_cases[i].execution_status != CESTER_RESULT_UNKNOWN) {
                        write_testcase_junitxml(&cester_test_cases[i], cester_extract_name_only(superTestInstance.test_file_path));
                    }
                }
            }
            CESTER_ARRAY_FOREACH(superTestInstance.registered_test_cases, index5, test_case, {
                if (((TestCase*)test_case)->test_type == CESTER_NORMAL_TEST && ((TestCase*)test_case)->execution_status != CESTER_RESULT_UNKNOWN) {
                    write_testcase_junitxml(((TestCase*)test_case), cester_extract_name_only(superTestInstance.test_file_path));
                }
            })
            CESTER_DELEGATE_FPRINT_STR((default_color), "</testsuite>\n");
            
        } else if (cester_string_equals(superTestInstance.output_format, (char*) "tap") == 1) {
            CESTER_DELEGATE_FPRINT_INT((CESTER_FOREGROUND_WHITE), 1);
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "..");
            CESTER_DELEGATE_FPRINT_INT((CESTER_FOREGROUND_WHITE), (superTestInstance.selected_test_cases_size == 0 ? CESTER_TOTAL_TESTS_COUNT : CESTER_TOTAL_TESTS_RAN));
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "\n");
            index_sub = 1;
            if (superTestInstance.registered_test_cases->size == 0) {
                for (i=0;cester_test_cases[i].test_type != CESTER_TESTS_TERMINATOR;++i) {
                    if ((cester_test_cases[i].test_type == CESTER_NORMAL_TEST || cester_test_cases[i].test_type == CESTER_NORMAL_TODO_TEST || 
                        cester_test_cases[i].test_type == CESTER_NORMAL_SKIP_TEST)) {
                        
                        if (superTestInstance.selected_test_cases_size > 0 && cester_test_cases[i].execution_status == CESTER_RESULT_UNKNOWN) {
                            continue;
                        }
                        write_testcase_tap(&cester_test_cases[i], cester_extract_name_only(superTestInstance.test_file_path), index_sub);
                        ++index_sub;
                    }
                }
            }
            CESTER_ARRAY_FOREACH(superTestInstance.registered_test_cases, index5, test_case, {
                if (((TestCase*)test_case)->test_type == CESTER_NORMAL_TEST || ((TestCase*)test_case)->test_type == CESTER_NORMAL_TODO_TEST || 
                    ((TestCase*)test_case)->test_type == CESTER_NORMAL_SKIP_TEST) {
                        
                    if (superTestInstance.selected_test_cases_size > 0 && ((TestCase*)test_case)->execution_status == CESTER_RESULT_UNKNOWN) {
                        continue;
                    }
                    write_testcase_tap(((TestCase*)test_case), cester_extract_name_only(superTestInstance.test_file_path), index_sub);
                    ++index_sub;
                }
            })
            if (superTestInstance.verbose == 1) {
                CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), "# Failed ");
                CESTER_DELEGATE_FPRINT_INT((CESTER_FOREGROUND_GRAY), CESTER_TOTAL_FAILED_TESTS_COUNT);
                CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), " of ");
                CESTER_DELEGATE_FPRINT_INT((CESTER_FOREGROUND_GRAY), (superTestInstance.selected_test_cases_size == 0 ? CESTER_TOTAL_TESTS_COUNT : CESTER_TOTAL_TESTS_RAN));
                #ifndef CESTER_NO_TIME
                    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), " tests\n# Time ");
                    CESTER_DELEGATE_FPRINT_DOUBLE_2((CESTER_FOREGROUND_GRAY), (time_spent > 60 ? (time_spent / 60) : time_spent));
                    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), (time_spent > 60 ? " Minutes\n" : " Seconds\n" ));
                #else
                    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), " tests\n");
                #endif
            }
            
        } else if (cester_string_equals(superTestInstance.output_format, (char*) "tapV13") == 1) {
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_CYAN), "TAP version 13");
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_CYAN), "\n");
            CESTER_DELEGATE_FPRINT_INT((CESTER_FOREGROUND_CYAN), 1);
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_CYAN), "..");
            CESTER_DELEGATE_FPRINT_INT((CESTER_FOREGROUND_CYAN), (superTestInstance.selected_test_cases_size == 0 ? CESTER_TOTAL_TESTS_COUNT : CESTER_TOTAL_TESTS_RAN));
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_CYAN), "\n");
            index_sub = 1;
            if (superTestInstance.registered_test_cases->size == 0) {
                for (i=0;cester_test_cases[i].test_type != CESTER_TESTS_TERMINATOR;++i) {
                    if ((cester_test_cases[i].test_type == CESTER_NORMAL_TEST || cester_test_cases[i].test_type == CESTER_NORMAL_TODO_TEST || 
                        cester_test_cases[i].test_type == CESTER_NORMAL_SKIP_TEST)) {
                        
                        if (superTestInstance.selected_test_cases_size > 0 && cester_test_cases[i].execution_status == CESTER_RESULT_UNKNOWN) {
                            continue;
                        }
                        write_testcase_tap_v13(&cester_test_cases[i], cester_extract_name_only(superTestInstance.test_file_path), index_sub);
                        ++index_sub;
                    }
                }
            }
            CESTER_ARRAY_FOREACH(superTestInstance.registered_test_cases, index5, test_case, {
                if (((TestCase*)test_case)->test_type == CESTER_NORMAL_TEST || ((TestCase*)test_case)->test_type == CESTER_NORMAL_TODO_TEST || 
                    ((TestCase*)test_case)->test_type == CESTER_NORMAL_SKIP_TEST) {
                    
                    if (superTestInstance.selected_test_cases_size > 0 && ((TestCase*)test_case)->execution_status == CESTER_RESULT_UNKNOWN) {
                        continue;
                    }
                    write_testcase_tap_v13(((TestCase*)test_case), cester_extract_name_only(superTestInstance.test_file_path), index_sub);
                    ++index_sub;
                }
            })
            if (superTestInstance.verbose == 1) {
                CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), "# Failed ");
                CESTER_DELEGATE_FPRINT_INT((CESTER_FOREGROUND_GRAY), CESTER_TOTAL_FAILED_TESTS_COUNT);
                CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), " of ");
                CESTER_DELEGATE_FPRINT_INT((CESTER_FOREGROUND_GRAY), (superTestInstance.selected_test_cases_size == 0 ? CESTER_TOTAL_TESTS_COUNT : CESTER_TOTAL_TESTS_RAN));
                #ifndef CESTER_NO_TIME
                    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), " tests\n# Time ");
                    CESTER_DELEGATE_FPRINT_DOUBLE_2((CESTER_FOREGROUND_GRAY), (time_spent > 60 ? (time_spent / 60) : time_spent));
                    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), (time_spent > 60 ? " Minutes\n" : " Seconds\n" ));
                #else
                    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_GRAY), " tests\n");
                #endif
            }
            
        } else {
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "\n");
            if (superTestInstance.registered_test_cases->size == 0) {
                for (i=0;cester_test_cases[i].test_type != CESTER_TESTS_TERMINATOR;++i) {
                    if (superTestInstance.selected_test_cases_size > 0 && cester_test_cases[i].execution_status != CESTER_RESULT_UNKNOWN) {
                        print_test_case_result(&cester_test_cases[i]);
                        
                    } else if (((cester_test_cases[i].test_type == CESTER_NORMAL_TEST && cester_test_cases[i].execution_status != CESTER_RESULT_UNKNOWN) || 
                            (cester_test_cases[i].test_type == CESTER_NORMAL_TODO_TEST || cester_test_cases[i].test_type == CESTER_NORMAL_SKIP_TEST)) && 
                            superTestInstance.selected_test_cases_size == 0) {
                            
                        print_test_case_result(&cester_test_cases[i]);
                    }
                }
            }
            CESTER_ARRAY_FOREACH(superTestInstance.registered_test_cases, index6, test_case_delegate, {
                TestCase* test_case = (TestCase*) test_case_delegate;
                if (superTestInstance.selected_test_cases_size > 0 && test_case->execution_status != CESTER_RESULT_UNKNOWN) {
                    print_test_case_result(test_case);
                    
                } else if (((test_case->test_type == CESTER_NORMAL_TEST && test_case->execution_status != CESTER_RESULT_UNKNOWN) || 
                        (test_case->test_type == CESTER_NORMAL_TODO_TEST || test_case->test_type == CESTER_NORMAL_SKIP_TEST)) && 
                        superTestInstance.selected_test_cases_size == 0) {
                        
                    print_test_case_result(test_case);
                }
            })
            
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "\n");
            if (superTestInstance.registered_test_cases->size == 0) {
                for (i=0;cester_test_cases[i].test_type != CESTER_TESTS_TERMINATOR;++i) {
                    if (cester_test_cases[i].test_type == CESTER_NORMAL_TEST && cester_test_cases[i].execution_status != CESTER_RESULT_UNKNOWN) {
                        print_test_case_outputs(&cester_test_cases[i]);
                    }
                }
            }
            CESTER_ARRAY_FOREACH(superTestInstance.registered_test_cases, index7, test_case_delegate1, {
                TestCase* test_case1 = (TestCase*) test_case_delegate1;
                if (test_case1->test_type == CESTER_NORMAL_TEST && test_case1->execution_status != CESTER_RESULT_UNKNOWN) {
                    print_test_case_outputs(test_case1);
                }
            })
            
            #ifndef CESTER_NO_TIME
                print_test_result(time_spent);
            #else
                print_test_result();
            #endif
        }
    }
    
    CESTER_RESET_TERMINAL_ATTR();
    if (CESTER_TOTAL_FAILED_TESTS_COUNT != 0 && superTestInstance.current_execution_status == CESTER_RESULT_SUCCESS) {
        return CESTER_RESULT_FAILURE;
    }
    return superTestInstance.current_execution_status;
}

/* Assertions, Tests */


/**
    Does nothing just an empty placeholder. Can be used in the 
    CESTER_SKIP_TEST and CESTER_TODO_TEST when compiling with 
    -ansi and -pedantic-errors flag
*/
#define cester_assert_nothing() 

/**
    Compare two argument using the provided operator
    Prints the expression as in the source code
    
    \param w a value to compare to y
    \param x the operator to use for the comparison. One of ==, !=, <, >, <=, >=
    \param y a value to compare to w
    \param z the expression to print in output
*/
#define cester_assert_cmp_msg(w,x,y,z) cester_evaluate_expression(w x y, z, __FILE__, __LINE__)

/**
    Compare two argument using the provided operator
    Prints the expression as in the source code
    
    \param x a value to compare to z
    \param y the operator to use for the comparison. One of ==, !=, <, >, <=, >=
    \param z a value to compare to x
*/
#define cester_assert_cmp(x,y,z) cester_assert_cmp_msg(x, y, z, "(" #x " " #y " " #z ")")

/**
    Check if the expression evaluates to true. 
    Prints the expression as in the source code.
    
    \param x the expression to check if true
*/
#define cester_assert_true(x) cester_assert_cmp_msg(x, ==, 1, "(" #x ")")

/**
    Check if the expression evaluates to false. 
    Prints the expression as in the source code.
    
    \param x the expression to check if false
*/
#define cester_assert_false(x) cester_assert_cmp_msg(x, ==, 0, "(" #x ")")

/**
    Assertion macro that passes if an expression is NULL. 
    Prints the expression as in the source code.
    
    \param x the expression to check if it NULL.
*/
#define cester_assert_null(x) cester_assert_cmp_msg(x, ==, NULL, "(" #x ")")

/**
    Assertion macro that passes if an expression is not NULL. 
    Prints the expression as in the source code.
    
    \param x the expression to check if it not NULL.
*/
#define cester_assert_not_null(x) cester_assert_cmp_msg(x, !=, NULL, "!(" #x ")")

/**
    Assertion macro that passes if the two expression is equal. 
    Prints the expression as in the source code
    
    \param x the first expression to compare
    \param y the second expression to compare to the first expression
*/
#define cester_assert_equal(x,y) cester_evaluate_expect_actual(x==y, 1, #x, #y, __FILE__, __LINE__)

/**
    Assertion macro that passes if the two expression is not equal. 
    Prints the expression as in the source code
    
    \param x the first expression to compare
    \param y the second expression to compare to the first expression
*/
#define cester_assert_not_equal(x,y) cester_evaluate_expect_actual(x!=y, 0, #x, #y, __FILE__, __LINE__)

/**
    Compare two strings. If the comparison fails the test case 
    is marked as failed. The advantage of this macro is that it display 
    the actual values of the two strings.
    
    \param x a string to compare
    \param y another string to compare with the first string
*/
#define cester_assert_str_equal(x,y) cester_evaluate_expect_actual_str(x, y, 1, __FILE__, __LINE__)

/**
    Compare two strings. If the comparison passes the test case 
    is marked as failed. The advantage of this macro is that it display 
    the actual values of the two strings.
    
    \param x a string to compare
    \param y another string to compare with the first string
*/
#define cester_assert_str_not_equal(x,y) cester_evaluate_expect_actual_str(x, y, 0, __FILE__, __LINE__)

/**
    Compare two pointers. If the comparison fails the test case 
    is marked as failed. The advantage of this macro is that it display 
    the actual values of the two pointers.
    
    \param x a pointer to compare
    \param y another pointer to compare with the first pointer
*/
#define cester_assert_ptr_equal(x,y) cester_evaluate_expect_actual_ptr(x, y, 1, __FILE__, __LINE__)

/**
    Compare two pointers. If the comparison passes the test case 
    is marked as failed. The advantage of this macro is that it display 
    the actual values of the two pointers.
    
    \param x a pointer to compare
    \param y another pointer to compare with the first pointer
*/
#define cester_assert_ptr_not_equal(x,y) cester_evaluate_expect_actual_ptr(x, y, 0, __FILE__, __LINE__)

/* document the following, add 'compile time only' */
#define __internal_cester_assert_cmp(w,x,y,z) (w x y, z, w, y, #x, __FILE__, __LINE__)
#define __internal_cester_assert_eq(x,y,z) (x == y, "expected " #z ",%s received " #z, y, x, "", __FILE__, __LINE__)
#define __internal_cester_assert_ne(x,y,z) (x != y, "not expecting " #z ",%s found " #z, x, y, "", __FILE__, __LINE__)
#define __internal_cester_assert_gt(x,y,z) (x > y, "expected value to be greater than " #z ",%s received " #z, x, y, "", __FILE__, __LINE__)
#define __internal_cester_assert_ge(x,y,z) (x >= y, "expected value to be greater than or equal to " #z ",%s received " #z, x, y, "", __FILE__, __LINE__)
#define __internal_cester_assert_lt(x,y,z) (x < y, "expected value to be lesser than " #z ",%s received " #z, x, y, "", __FILE__, __LINE__)
#define __internal_cester_assert_le(x,y,z) (x <= y, "expected value to be lesser than or equal to " #z ",%s received " #z, x, y, "", __FILE__, __LINE__)

/**
    Compare two char using the provided operator
    This macro prints out the actual values of the two 
    chars.
    
    \param w a char
    \param x the operator to use for the comparison. One of ==, !=, <, >, <=, >=
    \param y another char
    \param z the string formated for output
*/
#define cester_assert_cmp_char(w,x,y,z) CESTER_CONCAT(cester_compare_char, __internal_cester_assert_cmp(w,x,y,z))

/**
    Check if the two characters are the same.
    This macro prints out the actual values of the two 
    characters.
    
    \param x a char
    \param y another char
*/
#define cester_assert_char_eq(x,y) CESTER_CONCAT(cester_compare_char, __internal_cester_assert_eq(x,y,%c))

/**
    Check if the two char are not the same.
    This macro prints out the actual values of the two 
    chars.
    
    \param x a char
    \param y another char
*/
#define cester_assert_char_ne(x,y) CESTER_CONCAT(cester_compare_char, __internal_cester_assert_ne(x,y,%c))

/**
    Check if the a char is greater than the other.
    This macro prints out the actual values of the two 
    chars.
    
    \param x a char
    \param y another char
*/
#define cester_assert_char_gt(x,y) CESTER_CONCAT(cester_compare_char, __internal_cester_assert_gt(x,y,%c))

/**
    Check if the a char is greater than or equal to the other.
    This macro prints out the actual values of the two 
    chars.
    
    \param x a char
    \param y another char
*/
#define cester_assert_char_ge(x,y) CESTER_CONCAT(cester_compare_char, __internal_cester_assert_ge(x,y,%c))

/**
    Check if the a char is lesser than the other.
    This macro prints out the actual values of the two 
    chars.
    
    \param x a char
    \param y another char
*/
#define cester_assert_char_lt(x,y) CESTER_CONCAT(cester_compare_char, __internal_cester_assert_lt(x,y,%c))

/**
    Check if the a char is lesser than or equal to the other.
    This macro prints out the actual values of the two 
    chars.
    
    \param x a char
    \param y another char
*/
#define cester_assert_char_le(x,y) CESTER_CONCAT(cester_compare_char, __internal_cester_assert_le(x,y,%c))

/**
    Compare two unsigned char using the provided operator
    This macro prints out the actual values of the two 
    unsigned char.
    
    \param w an unsigned char
    \param x the operator to use for the comparison. One of ==, !=, <, >, <=, >=
    \param y another unsigned char
    \param z the string formated for output
*/
#define cester_assert_cmp_uchar(w,x,y,z) CESTER_CONCAT(cester_compare_uchar, __internal_cester_assert_cmp(w,x,y,z))

/**
    Check if the two unsigned char are the same.
    This macro prints out the actual values of the two 
    unsigned char.
    
    \param x an unsigned char
    \param y another unsigned char
*/
#define cester_assert_uchar_eq(x,y) CESTER_CONCAT(cester_compare_uchar, __internal_cester_assert_eq(x,y,%c))

/**
    Check if the two unsigned char are not the same.
    This macro prints out the actual values of the two 
    unsigned char.
    
    \param x an unsigned char
    \param y another unsigned char
*/
#define cester_assert_uchar_ne(x,y) CESTER_CONCAT(cester_compare_uchar, __internal_cester_assert_ne(x,y,%c))

/**
    Check if the a unsigned char is greater than the other.
    This macro prints out the actual values of the two 
    unsigned char.
    
    \param x an unsigned char
    \param y another unsigned char
*/
#define cester_assert_uchar_gt(x,y) CESTER_CONCAT(cester_compare_uchar, __internal_cester_assert_gt(x,y,%c))

/**
    Check if the a unsigned char is greater than or equal to the other.
    This macro prints out the actual values of the two 
    unsigned char.
    
    \param x an unsigned char
    \param y another unsigned char
*/
#define cester_assert_uchar_ge(x,y) CESTER_CONCAT(cester_compare_uchar, __internal_cester_assert_ge(x,y,%c))

/**
    Check if the a unsigned char is lesser than the other.
    This macro prints out the actual values of the two 
    unsigned char.
    
    \param x an unsigned char
    \param y another unsigned char
*/
#define cester_assert_uchar_lt(x,y) CESTER_CONCAT(cester_compare_uchar, __internal_cester_assert_lt(x,y,%c))

/**
    Check if the a unsigned char is lesser than or equal to the other.
    This macro prints out the actual values of the two 
    unsigned char.
    
    \param x an unsigned char
    \param y another unsigned char
*/
#define cester_assert_uchar_le(x,y) CESTER_CONCAT(cester_compare_uchar, __internal_cester_assert_le(x,y,%c))

/**
    Compare two short using the provided operator
    This macro prints out the actual values of the two 
    short.
    
    \param w a short
    \param x the operator to use for the comparison. One of ==, !=, <, >, <=, >=
    \param y another short
    \param z the string formated for output
*/
#define cester_assert_cmp_short(w,x,y,z) CESTER_CONCAT(cester_compare_short, __internal_cester_assert_cmp(w,x,y,z))

/**
    Check if the two short are the same.
    This macro prints out the actual values of the two 
    short.
    
    \param x a short
    \param y another short
*/
#define cester_assert_short_eq(x,y) CESTER_CONCAT(cester_compare_short, __internal_cester_assert_eq(x,y,%hi))

/**
    Check if the two short are not the same.
    This macro prints out the actual values of the two 
    short.
    
    \param x a short
    \param y another short
*/
#define cester_assert_short_ne(x,y) CESTER_CONCAT(cester_compare_short, __internal_cester_assert_ne(x,y,%hi))

/**
    Check if the a short is greater than the other.
    This macro prints out the actual values of the two 
    short.
    
    \param x a short
    \param y another short
*/
#define cester_assert_short_gt(x,y) CESTER_CONCAT(cester_compare_short, __internal_cester_assert_gt(x,y,%hi))

/**
    Check if the a short is greater than or equal to the other.
    This macro prints out the actual values of the two 
    short.
    
    \param x a short
    \param y another short
*/
#define cester_assert_short_ge(x,y) CESTER_CONCAT(cester_compare_short, __internal_cester_assert_ge(x,y,%hi))

/**
    Check if the a short is lesser than the other.
    This macro prints out the actual values of the two 
    short.
    
    \param x a short
    \param y another short
*/
#define cester_assert_short_lt(x,y) CESTER_CONCAT(cester_compare_short, __internal_cester_assert_lt(x,y,%hi))

/**
    Check if the a short is lesser than or equal to the other.
    This macro prints out the actual values of the two 
    short.
    
    \param x a short
    \param y another short
*/
#define cester_assert_short_le(x,y) CESTER_CONCAT(cester_compare_short, __internal_cester_assert_le(x,y,%hi))

/**
    Compare two unsigned short using the provided operator
    This macro prints out the actual values of the two 
    unsigned short.
    
    \param w an unsigned short
    \param x the operator to use for the comparison. One of ==, !=, <, >, <=, >=
    \param y another unsigned short
    \param z the string formated for output
*/
#define cester_assert_cmp_ushort(w,x,y,z) CESTER_CONCAT(cester_compare_ushort, __internal_cester_assert_cmp(w,x,y,z))

/**
    Check if the two unsigned short are the same.
    This macro prints out the actual values of the two 
    unsigned short.
    
    \param x an unsigned short
    \param y another unsigned short
*/
#define cester_assert_ushort_eq(x,y) CESTER_CONCAT(cester_compare_ushort, __internal_cester_assert_eq(x,y,%hu))

/**
    Check if the two unsigned short are not the same.
    This macro prints out the actual values of the two 
    unsigned short.
    
    \param x an unsigned short
    \param y another unsigned short
*/
#define cester_assert_ushort_ne(x,y) CESTER_CONCAT(cester_compare_ushort, __internal_cester_assert_ne(x,y,%hu))

/**
    Check if the a unsigned short is greater than the other.
    This macro prints out the actual values of the two 
    unsigned short.
    
    \param x an unsigned short
    \param y another unsigned short
*/
#define cester_assert_ushort_gt(x,y) CESTER_CONCAT(cester_compare_ushort, __internal_cester_assert_gt(x,y,%hu))

/**
    Check if the a unsigned short is greater than or equal to the other.
    This macro prints out the actual values of the two 
    unsigned short.
    
    \param x an unsigned short
    \param y another unsigned short
*/
#define cester_assert_ushort_ge(x,y) CESTER_CONCAT(cester_compare_ushort, __internal_cester_assert_ge(x,y,%hu))

/**
    Check if the a unsigned short is lesser than the other.
    This macro prints out the actual values of the two 
    unsigned short.
    
    \param x an unsigned short
    \param y another unsigned short
*/
#define cester_assert_ushort_lt(x,y) CESTER_CONCAT(cester_compare_ushort, __internal_cester_assert_lt(x,y,%hu))

/**
    Check if the a unsigned short is lesser than or equal to the other.
    This macro prints out the actual values of the two 
    unsigned short.
    
    \param x an unsigned short
    \param y another unsigned short
*/
#define cester_assert_ushort_le(x,y) CESTER_CONCAT(cester_compare_ushort, __internal_cester_assert_le(x,y,%hu))

/**
    Compare two int using the provided operator
    This macro prints out the actual values of the two 
    int.
    
    \param w an int
    \param x the operator to use for the comparison. One of ==, !=, <, >, <=, >=
    \param y another int
    \param z the string formated for output
*/
#define cester_assert_cmp_int(w,x,y,z) CESTER_CONCAT(cester_compare_int, __internal_cester_assert_cmp(w,x,y,z))

/**
    Check if the two int are the same.
    This macro prints out the actual values of the two 
    int.
    
    \param x an int
    \param y another int
*/
#define cester_assert_int_eq(x,y) CESTER_CONCAT(cester_compare_int, __internal_cester_assert_eq(x,y,%d))

/**
    Check if the two int are not the same.
    This macro prints out the actual values of the two 
    int.
    
    \param x an int
    \param y another int
*/
#define cester_assert_int_ne(x,y)  CESTER_CONCAT(cester_compare_int, __internal_cester_assert_ne(x,y,%d))

/**
    Check if the a int is greater than the other.
    This macro prints out the actual values of the two 
    int.
    
    \param x an int
    \param y another int
*/
#define cester_assert_int_gt(x,y) CESTER_CONCAT(cester_compare_int, __internal_cester_assert_gt(x,y,%d))

/**
    Check if the a int is greater than or equal to the other.
    This macro prints out the actual values of the two 
    int.
    
    \param x an int
    \param y another int
*/
#define cester_assert_int_ge(x,y) CESTER_CONCAT(cester_compare_int, __internal_cester_assert_ge(x,y,%d))

/**
    Check if the a int is lesser than the other.
    This macro prints out the actual values of the two 
    int.
    
    \param x an int
    \param y another int
*/
#define cester_assert_int_lt(x,y) CESTER_CONCAT(cester_compare_int, __internal_cester_assert_lt(x,y,%d))

/**
    Check if the a int is lesser than or equal to the other.
    This macro prints out the actual values of the two 
    int.
    
    \param x an int
    \param y another int
*/
#define cester_assert_int_le(x,y) CESTER_CONCAT(cester_compare_int, __internal_cester_assert_le(x,y,%d))

/**
    Compare two unsigned int using the provided operator
    This macro prints out the actual values of the two 
    unsigned int.
    
    \param w an unsigned int
    \param x the operator to use for the comparison. One of ==, !=, <, >, <=, >=
    \param y another unsigned int
    \param z the string formated for output
*/
#define cester_assert_cmp_uint(w,x,y,z) CESTER_CONCAT(cester_compare_uint, __internal_cester_assert_cmp(w,x,y,z))

/**
    Check if the two unsigned int are the same.
    This macro prints out the actual values of the two 
    unsigned int.
    
    \param x an unsigned int
    \param y another unsigned int
*/
#define cester_assert_uint_eq(x,y) CESTER_CONCAT(cester_compare_uint, __internal_cester_assert_eq(x,y,%u))

/**
    Check if the two unsigned int are not the same.
    This macro prints out the actual values of the two 
    unsigned int.
    
    \param x an unsigned int
    \param y another unsigned int
*/
#define cester_assert_uint_ne(x,y) CESTER_CONCAT(cester_compare_uint, __internal_cester_assert_ne(x,y,%u))

/**
    Check if the a unsigned int is greater than the other.
    This macro prints out the actual values of the two 
    unsigned int.
    
    \param x an unsigned int
    \param y another unsigned int
*/
#define cester_assert_uint_gt(x,y) CESTER_CONCAT(cester_compare_uint, __internal_cester_assert_gt(x,y,%u))

/**
    Check if the a unsigned int is greater than or equal to the other.
    This macro prints out the actual values of the two 
    unsigned int.
    
    \param x an unsigned int
    \param y another unsigned int
*/
#define cester_assert_uint_ge(x,y) CESTER_CONCAT(cester_compare_uint, __internal_cester_assert_ge(x,y,%u))

/**
    Check if the a unsigned int is lesser than the other.
    This macro prints out the actual values of the two 
    unsigned int.
    
    \param x an unsigned int
    \param y another unsigned int
*/
#define cester_assert_uint_lt(x,y) CESTER_CONCAT(cester_compare_uint, __internal_cester_assert_lt(x,y,%u))

/**
    Check if the a unsigned int is lesser than or equal to the other.
    This macro prints out the actual values of the two 
    unsigned int.
    
    \param x an unsigned int
    \param y another unsigned int
*/
#define cester_assert_uint_le(x,y) CESTER_CONCAT(cester_compare_uint, __internal_cester_assert_le(x,y,%u))

/**
    Compare two long using the provided operator
    This macro prints out the actual values of the two 
    long.
    
    \param w a long
    \param x the operator to use for the comparison. One of ==, !=, <, >, <=, >=
    \param y another long
    \param z the string formated for output
*/
#define cester_assert_cmp_long(w,x,y,z) CESTER_CONCAT(cester_compare_long, __internal_cester_assert_cmp(w,x,y,z))

/**
    Check if the two long are the same.
    This macro prints out the actual values of the two 
    long.
    
    \param x a long
    \param y another long
*/
#define cester_assert_long_eq(x,y) CESTER_CONCAT(cester_compare_long, __internal_cester_assert_eq(x,y,%li))

/**
    Check if the two long are not the same.
    This macro prints out the actual values of the two 
    long.
    
    \param x a long
    \param y another long
*/
#define cester_assert_long_ne(x,y) CESTER_CONCAT(cester_compare_long, __internal_cester_assert_ne(x,y,%li))

/**
    Check if the a long is greater than the other.
    This macro prints out the actual values of the two 
    long.
    
    \param x a long
    \param y another long
*/
#define cester_assert_long_gt(x,y) CESTER_CONCAT(cester_compare_long, __internal_cester_assert_gt(x,y,%li))

/**
    Check if the a long is greater than or equal to the other.
    This macro prints out the actual values of the two 
    long.
    
    \param x a long
    \param y another long
*/
#define cester_assert_long_ge(x,y) CESTER_CONCAT(cester_compare_long, __internal_cester_assert_ge(x,y,%li))

/**
    Check if the a long is lesser than the other.
    This macro prints out the actual values of the two 
    long.
    
    \param x a long
    \param y another long
*/
#define cester_assert_long_lt(x,y) CESTER_CONCAT(cester_compare_long, __internal_cester_assert_lt(x,y,%li))

/**
    Check if the a long is lesser than or equal to the other.
    This macro prints out the actual values of the two 
    long.
    
    \param x a long
    \param y another long
*/
#define cester_assert_long_le(x,y) CESTER_CONCAT(cester_compare_long, __internal_cester_assert_le(x,y,%li))

/**
    Compare two unsigned long using the provided operator
    This macro prints out the actual values of the two 
    unsigned long.
    
    \param w a unsigned long
    \param x the operator to use for the comparison. One of ==, !=, <, >, <=, >=
    \param y another unsigned long
    \param z the string formated for output
*/
#define cester_assert_cmp_ulong(w,x,y,z) CESTER_CONCAT(cester_compare_ulong, __internal_cester_assert_cmp(w,x,y,z))

/**
    Check if the two unsigned long are the same.
    This macro prints out the actual values of the two 
    unsigned long.
    
    \param x a unsigned long
    \param y another unsigned long
*/
#define cester_assert_ulong_eq(x,y) CESTER_CONCAT(cester_compare_ulong, __internal_cester_assert_eq(x,y,%lu))

/**
    Check if the two unsigned long are not the same.
    This macro prints out the actual values of the two 
    unsigned long.
    
    \param x a unsigned long
    \param y another unsigned long
*/
#define cester_assert_ulong_ne(x,y) CESTER_CONCAT(cester_compare_ulong, __internal_cester_assert_ne(x,y,%lu))

/**
    Check if the a unsigned long is greater than the other.
    This macro prints out the actual values of the two 
    unsigned long.
    
    \param x a unsigned long
    \param y another unsigned long
*/
#define cester_assert_ulong_gt(x,y) CESTER_CONCAT(cester_compare_ulong, __internal_cester_assert_gt(x,y,%lu))

/**
    Check if the a unsigned long is greater than or equal to the other.
    This macro prints out the actual values of the two 
    unsigned long.
    
    \param x a unsigned long
    \param y another unsigned long
*/
#define cester_assert_ulong_ge(x,y) CESTER_CONCAT(cester_compare_ulong, __internal_cester_assert_ge(x,y,%lu))

/**
    Check if the a unsigned long is lesser than the other.
    This macro prints out the actual values of the two 
    unsigned long.
    
    \param x a unsigned long
    \param y another unsigned long
*/
#define cester_assert_ulong_lt(x,y) CESTER_CONCAT(cester_compare_ulong, __internal_cester_assert_lt(x,y,%lu))

/**
    Check if the a unsigned long is lesser than or equal to the other.
    This macro prints out the actual values of the two 
    unsigned long.
    
    \param x a unsigned long
    \param y another unsigned long
*/
#define cester_assert_ulong_le(x,y) CESTER_CONCAT(cester_compare_ulong, __internal_cester_assert_le(x,y,%lu))

/**
    Compare two long long using the provided operator
    This macro prints out the actual values of the two 
    long long.
    
    \param w a long long
    \param x the operator to use for the comparison. One of ==, !=, <, >, <=, >=
    \param y another long long
    \param z the string formated for output
*/
#define cester_assert_cmp_llong(w,x,y,z) CESTER_CONCAT(cester_compare_llong, __internal_cester_assert_cmp(w,x,y,z))

/**
    Check if the two long long are the same.
    This macro prints out the actual values of the two 
    long long.
    
    \param x a long long
    \param y another long long
*/
#ifndef __CESTER_STDC_VERSION__
#define cester_assert_llong_eq(x,y) CESTER_CONCAT(cester_compare_llong, __internal_cester_assert_eq(x,y,%li))
#else
#define cester_assert_llong_eq(x,y) CESTER_CONCAT(cester_compare_llong, __internal_cester_assert_eq(x,y,%lli))
#endif

/**
    Check if the two long long are not the same.
    This macro prints out the actual values of the two 
    long long.
    
    \param x a long long
    \param y another long long
*/
#ifndef __CESTER_STDC_VERSION__
#define cester_assert_llong_ne(x,y) CESTER_CONCAT(cester_compare_llong, __internal_cester_assert_ne(x,y,%li))
#else
#define cester_assert_llong_ne(x,y) CESTER_CONCAT(cester_compare_llong, __internal_cester_assert_ne(x,y,%lli))
#endif

/**
    Check if the a long long is greater than the other.
    This macro prints out the actual values of the two 
    long long.
    
    \param x a long long
    \param y another long long
*/
#ifndef __CESTER_STDC_VERSION__
#define cester_assert_llong_gt(x,y) CESTER_CONCAT(cester_compare_llong, __internal_cester_assert_gt(x,y,%li))
#else
#define cester_assert_llong_gt(x,y) CESTER_CONCAT(cester_compare_llong, __internal_cester_assert_gt(x,y,%lli))
#endif

/**
    Check if the a long long is greater than or equal to the other.
    This macro prints out the actual values of the two 
    long long.
    
    \param x a long long
    \param y another long long
*/
#ifndef __CESTER_STDC_VERSION__
#define cester_assert_llong_ge(x,y) CESTER_CONCAT(cester_compare_llong, __internal_cester_assert_ge(x,y,%li))
#else
#define cester_assert_llong_ge(x,y) CESTER_CONCAT(cester_compare_llong, __internal_cester_assert_ge(x,y,%lli))
#endif

/**
    Check if the a long long is lesser than the other.
    This macro prints out the actual values of the two 
    long long.
    
    \param x a long long
    \param y another long long
*/
#ifndef __CESTER_STDC_VERSION__
#define cester_assert_llong_lt(x,y) CESTER_CONCAT(cester_compare_llong, __internal_cester_assert_lt(x,y,%li))
#else
#define cester_assert_llong_lt(x,y) CESTER_CONCAT(cester_compare_llong, __internal_cester_assert_lt(x,y,%lli))
#endif

/**
    Check if the a long long is lesser than or equal to the other.
    This macro prints out the actual values of the two 
    long long.
    
    \param x a long long
    \param y another long long
*/
#ifndef __CESTER_STDC_VERSION__
#define cester_assert_llong_le(x,y) CESTER_CONCAT(cester_compare_llong, __internal_cester_assert_ge(x,y,%li))
#else
#define cester_assert_llong_le(x,y) CESTER_CONCAT(cester_compare_llong, __internal_cester_assert_ge(x,y,%lli))
#endif

/**
    Compare two unsigned long long using the provided operator
    This macro prints out the actual values of the two 
    unsigned long long.
    
    \param w a unsigned long long
    \param x the operator to use for the comparison. One of ==, !=, <, >, <=, >=
    \param y another unsigned long long
    \param z the string formated for output
*/
#define cester_assert_cmp_ullong(w,x,y,z) CESTER_CONCAT(cester_compare_ullong, __internal_cester_assert_cmp(w,x,y,z))

/**
    Check if the two unsigned long long are the same.
    This macro prints out the actual values of the two 
    unsigned long long.
    
    \param x a unsigned long long
    \param y another unsigned long long
*/
#define cester_assert_ullong_eq(x,y) CESTER_CONCAT(cester_compare_ullong, __internal_cester_assert_eq(x,y,%llu))

/**
    Check if the two unsigned long long are not the same.
    This macro prints out the actual values of the two 
    unsigned long long.
    
    \param x a unsigned long long
    \param y another unsigned long long
*/
#define cester_assert_ullong_ne(x,y) CESTER_CONCAT(cester_compare_ullong, __internal_cester_assert_ne(x,y,%llu))

/**
    Check if the a unsigned long long is greater than the other.
    This macro prints out the actual values of the two 
    unsigned long long.
    
    \param x a unsigned long long
    \param y another unsigned long long
*/
#define cester_assert_ullong_gt(x,y) CESTER_CONCAT(cester_compare_ullong, __internal_cester_assert_gt(x,y,%llu))

/**
    Check if the a unsigned long long is greater than or equal to the other.
    This macro prints out the actual values of the two 
    unsigned long long.
    
    \param x a unsigned long long
    \param y another unsigned long long
*/
#define cester_assert_ullong_ge(x,y) CESTER_CONCAT(cester_compare_ullong, __internal_cester_assert_ge(x,y,%llu))

/**
    Check if the a unsigned long long is lesser than the other.
    This macro prints out the actual values of the two 
    unsigned long long.
    
    \param x a unsigned long long
    \param y another unsigned long long
*/
#define cester_assert_ullong_lt(x,y) CESTER_CONCAT(cester_compare_ullong, __internal_cester_assert_lt(x,y,%llu))

/**
    Check if the a unsigned long long is lesser than or equal to the other.
    This macro prints out the actual values of the two 
    unsigned long long.
    
    \param x a unsigned long long
    \param y another unsigned long long
*/
#define cester_assert_ullong_le(x,y) CESTER_CONCAT(cester_compare_ullong, __internal_cester_assert_le(x,y,%llu))

/**
    Compare two float using the provided operator
    This macro prints out the actual values of the two 
    float.
    
    \param w a float
    \param x the operator to use for the comparison. One of ==, !=, <, >, <=, >=
    \param y another float
    \param z the string formated for output
*/
#define cester_assert_cmp_float(w,x,y,z) CESTER_CONCAT(cester_compare_float, __internal_cester_assert_cmp(w,x,y,z))

/**
    Check if the two float are the same.
    This macro prints out the actual values of the two 
    float.
    
    \param x a float
    \param y another float
*/
#define cester_assert_float_eq(x,y) CESTER_CONCAT(cester_compare_float, __internal_cester_assert_eq(x,y,%f))

/**
    Check if the two float are not the same.
    This macro prints out the actual values of the two 
    float.
    
    \param x a float
    \param y another float
*/
#define cester_assert_float_ne(x,y) CESTER_CONCAT(cester_compare_float, __internal_cester_assert_ne(x,y,%f))

/**
    Check if the a float is greater than the other.
    This macro prints out the actual values of the two 
    float.
    
    \param x a float
    \param y another float
*/
#define cester_assert_float_gt(x,y) CESTER_CONCAT(cester_compare_float, __internal_cester_assert_gt(x,y,%f))

/**
    Check if the a float is greater than or equal to the other.
    This macro prints out the actual values of the two 
    float.
    
    \param x a float
    \param y another float
*/
#define cester_assert_float_ge(x,y) CESTER_CONCAT(cester_compare_float, __internal_cester_assert_ge(x,y,%f))

/**
    Check if the a float is lesser than the other.
    This macro prints out the actual values of the two 
    float.
    
    \param x a float
    \param y another float
*/
#define cester_assert_float_lt(x,y) CESTER_CONCAT(cester_compare_float, __internal_cester_assert_lt(x,y,%f))

/**
    Check if the a float is lesser than or equal to the other.
    This macro prints out the actual values of the two 
    float.
    
    \param x a float
    \param y another float
*/
#define cester_assert_float_le(x,y) CESTER_CONCAT(cester_compare_float, __internal_cester_assert_le(x,y,%f))

/**
    Compare two double using the provided operator
    This macro prints out the actual values of the two 
    double.
    
    \param w a double
    \param x the operator to use for the comparison. One of ==, !=, <, >, <=, >=
    \param y another double
    \param z the string formated for output
*/
#define cester_assert_cmp_double(w,x,y,z) CESTER_CONCAT(cester_compare_double, __internal_cester_assert_cmp(w,x,y,z))

/**
    Check if the two double are the same.
    This macro prints out the actual values of the two 
    double.
    
    \param x a double
    \param y another double
*/
#define cester_assert_double_eq(x,y) CESTER_CONCAT(cester_compare_double, __internal_cester_assert_eq(x,y,%lf))

/**
    Check if the two double are not the same.
    This macro prints out the actual values of the two 
    double.
    
    \param x a double
    \param y another double
*/
#define cester_assert_double_ne(x,y) CESTER_CONCAT(cester_compare_double, __internal_cester_assert_ne(x,y,%lf))

/**
    Check if the a double is greater than the other.
    This macro prints out the actual values of the two 
    double.
    
    \param x a double
    \param y another double
*/
#define cester_assert_double_gt(x,y) CESTER_CONCAT(cester_compare_double, __internal_cester_assert_gt(x,y,%lf))

/**
    Check if the a double is greater than or equal to the other.
    This macro prints out the actual values of the two 
    double.
    
    \param x a double
    \param y another double
*/
#define cester_assert_double_ge(x,y) CESTER_CONCAT(cester_compare_double, __internal_cester_assert_ge(x,y,%lf))

/**
    Check if the a double is lesser than the other.
    This macro prints out the actual values of the two 
    double.
    
    \param x a double
    \param y another double
*/
#define cester_assert_double_lt(x,y) CESTER_CONCAT(cester_compare_double, __internal_cester_assert_lt(x,y,%lf))

/**
    Check if the a double is lesser than or equal to the other.
    This macro prints out the actual values of the two 
    double.
    
    \param x a double
    \param y another double
*/
#define cester_assert_double_le(x,y) CESTER_CONCAT(cester_compare_double, __internal_cester_assert_le(x,y,%lf))

/**
    Compare two long double using the provided operator
    This macro prints out the actual values of the two 
    long double.
    
    \param w a long double
    \param x the operator to use for the comparison. One of ==, !=, <, >, <=, >=
    \param y another long double
    \param z the string formated for output
*/
#define cester_assert_cmp_ldouble(w,x,y,z) CESTER_CONCAT(cester_compare_ldouble, __internal_cester_assert_cmp(w,x,y,z))

/**
    Check if the two long double are the same.
    This macro prints out the actual values of the two 
    long double.
    
    \param x a long double
    \param y another long double
*/
#define cester_assert_ldouble_eq(x,y) CESTER_CONCAT(cester_compare_ldouble, __internal_cester_assert_eq(x,y,%e))

/**
    Check if the two long double are not the same.
    This macro prints out the actual values of the two 
    long double.
    
    \param x a long double
    \param y another long double
*/
#define cester_assert_ldouble_ne(x,y) CESTER_CONCAT(cester_compare_ldouble, __internal_cester_assert_ne(x,y,%e))

/**
    Check if the a long double is greater than the other.
    This macro prints out the actual values of the two 
    long double.
    
    \param x a long double
    \param y another long double
*/
#define cester_assert_ldouble_gt(x,y) CESTER_CONCAT(cester_compare_ldouble, __internal_cester_assert_gt(x,y,%e))

/**
    Check if the a long double is greater than or equal to the other.
    This macro prints out the actual values of the two 
    long double.
    
    \param x a long double
    \param y another long double
*/
#define cester_assert_ldouble_ge(x,y) CESTER_CONCAT(cester_compare_ldouble, __internal_cester_assert_ge(x,y,%e))

/**
    Check if the a long double is lesser than the other.
    This macro prints out the actual values of the two 
    long double.
    
    \param x a long double
    \param y another long double
*/
#define cester_assert_ldouble_lt(x,y) CESTER_CONCAT(cester_compare_ldouble, __internal_cester_assert_lt(x,y,%e))

/**
    Check if the a long double is lesser than or equal to the other.
    This macro prints out the actual values of the two 
    long double.
    
    \param x a long double
    \param y another long double
*/
#define cester_assert_ldouble_le(x,y) CESTER_CONCAT(cester_compare_ldouble, __internal_cester_assert_le(x,y,%e))

static __CESTER_INLINE__ void cester_evaluate_expression(unsigned eval_result, char const* const expression, char const* const file_path, unsigned const line_num) {
    if (cester_string_equals(superTestInstance.output_format, (char*) "tap") == 1) {
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "# ");
        
    } else if (cester_string_equals(superTestInstance.output_format, (char*) "tapV13") == 1) {
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "    - ");
    }
    if (eval_result == 0) {
        superTestInstance.current_execution_status = CESTER_RESULT_FAILURE;
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "EvaluationError ");
    } else if (superTestInstance.verbose == 1) {
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "Passed ");
    }
    if (eval_result == 0 || superTestInstance.verbose == 1) {
        cester_print_assertion(expression, file_path, line_num);
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "\n");
    }
}

static __CESTER_INLINE__ void cester_evaluate_expect_actual(unsigned eval_result, unsigned expecting, char const* const expected, char const* const actual, 
                                                char const* const file_path, unsigned const line_num) {
                                                    
    
    if (cester_string_equals(superTestInstance.output_format, (char*) "tap") == 1) {
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "# ");
        
    } else if (cester_string_equals(superTestInstance.output_format, (char*) "tapV13") == 1) {
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "    - ");
    }
    if (eval_result == 0) {
        superTestInstance.current_execution_status = CESTER_RESULT_FAILURE;
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "AssertionError ");
    } else if (superTestInstance.verbose == 1) {
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "Passed ");
    }
    if (eval_result == 0 || superTestInstance.verbose == 1) {
        cester_print_expect_actual(expecting, expected, actual, file_path, line_num);
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "\n");
    }
}

static __CESTER_INLINE__ void cester_evaluate_expect_actual_str(char const* const expected, char const* const actual, unsigned expecting, char const* const file_path, unsigned const line_num) {
    unsigned eval_result = cester_string_equals((char*)expected, (char*)actual);  
    if (cester_string_equals(superTestInstance.output_format, (char*) "tap") == 1) {
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "# ");
        
    } else if (cester_string_equals(superTestInstance.output_format, (char*) "tapV13") == 1) {
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "    - ");
    }
    if (eval_result != expecting) {
        superTestInstance.current_execution_status = CESTER_RESULT_FAILURE;
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "AssertionError ");
    } else if (superTestInstance.verbose == 1) {
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "Passed ");
    }  
    if (eval_result != expecting || superTestInstance.verbose == 1) {
        cester_print_expect_actual(expecting, expected, actual, file_path, line_num);
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "\n");
    }
}

static __CESTER_INLINE__ void cester_evaluate_expect_actual_ptr(void* ptr1, void* ptr2, unsigned expecting, char const* const file_path, unsigned const line_num) {
    unsigned eval_result;
    char* expected;
    char* actual;
    
    eval_result = ptr1 == ptr2; 
    cester_ptr_to_str(&expected, ptr1);
    cester_ptr_to_str(&actual, ptr2);
    if (cester_string_equals(superTestInstance.output_format, (char*) "tap") == 1) {
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "# ");
        
    } else if (cester_string_equals(superTestInstance.output_format, (char*) "tapV13") == 1) {
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "    - ");
    }
    if (eval_result != expecting) {
        superTestInstance.current_execution_status = CESTER_RESULT_FAILURE;
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "AssertionError ");
    } else if (superTestInstance.verbose == 1) {
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "Passed ");
    }  
    if (eval_result != expecting || superTestInstance.verbose == 1) {
        cester_print_expect_actual(expecting, expected, actual, file_path, line_num);
        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "\n");
    }
}

static __CESTER_INLINE__ void cester_compare_char(int eval_result, char const* const expr, char first, char second, char const* const op, char const* const file_path, unsigned const line_num) {
    char expression[2048] = "";
    cester_sprintf3(expression, 2048, expr, second, op, first);
    cester_evaluate_expression(eval_result, (char*)expression, file_path, line_num);
}

static __CESTER_INLINE__ void cester_compare_uchar(int eval_result, char const* const expr, unsigned char first, unsigned char second, char const* const op, char const* const file_path, unsigned const line_num) {
    char expression[2048] ;
    cester_sprintf3(expression, 2048, expr, second, op, first);
    cester_evaluate_expression(eval_result, (char*)expression, file_path, line_num);
}

static __CESTER_INLINE__ void cester_compare_int(int eval_result, char const* const expr, int first, int second, char const* const op, char const* const file_path, unsigned const line_num) {
    char expression[2048] ;
    cester_sprintf3(expression, 2048, expr, second, op, first);
    cester_evaluate_expression(eval_result, (char*)expression, file_path, line_num);
}

static __CESTER_INLINE__ void cester_compare_uint(int eval_result, char const* const expr, unsigned int first, unsigned int second, char const* const op, char const* const file_path, unsigned const line_num) {
    char expression[2048] ;
    cester_sprintf3(expression, 2048, expr, second, op, first);
    cester_evaluate_expression(eval_result, (char*)expression, file_path, line_num);
}

static __CESTER_INLINE__ void cester_compare_short(int eval_result, char const* const expr, short first, short second, char const* const op, char const* const file_path, unsigned const line_num) {
    char expression[2048] ;
    cester_sprintf3(expression, 2048, expr, second, op, first);
    cester_evaluate_expression(eval_result, (char*)expression, file_path, line_num);
}

static __CESTER_INLINE__ void cester_compare_ushort(int eval_result, char const* const expr, unsigned short first, unsigned short second, char const* const op, char const* const file_path, unsigned const line_num) {
    char expression[2048] ;
    cester_sprintf3(expression, 2048, expr, second, op, first);
    cester_evaluate_expression(eval_result, (char*)expression, file_path, line_num);
}

static __CESTER_INLINE__ void cester_compare_long(int eval_result, char const* const expr, long first, long second, char const* const op, char const* const file_path, unsigned const line_num) {
    char expression[2048] ;
    cester_sprintf3(expression, 2048, expr, second, op, first);
    cester_evaluate_expression(eval_result, (char*)expression, file_path, line_num);
}

static __CESTER_INLINE__ void cester_compare_ulong(int eval_result, char const* const expr, unsigned long first, unsigned long second, char const* const op, char const* const file_path, unsigned const line_num) {
    char expression[2048] ;
    cester_sprintf3(expression, 2048, expr, second, op, first);
    cester_evaluate_expression(eval_result, (char*)expression, file_path, line_num);
}

static __CESTER_INLINE__ void cester_compare_llong(int eval_result, char const* const expr, __CESTER_LONG_LONG__ first, __CESTER_LONG_LONG__ second, char const* const op, char const* const file_path, unsigned const line_num) {
    char expression[2048] ;
    cester_sprintf3(expression, 2048, expr, second, op, first);
    cester_evaluate_expression(eval_result, (char*)expression, file_path, line_num);
}

static __CESTER_INLINE__ void cester_compare_ullong(int eval_result, char const* const expr, unsigned __CESTER_LONG_LONG__ first, unsigned __CESTER_LONG_LONG__ second, char const* const op, char const* const file_path, unsigned const line_num) {
    char expression[2048] ;
    cester_sprintf3(expression, 2048, expr, second, op, first);
    cester_evaluate_expression(eval_result, (char*)expression, file_path, line_num);
}

static __CESTER_INLINE__ void cester_compare_float(int eval_result, char const* const expr, float first, float second, char const* const op, char const* const file_path, unsigned const line_num) {
    char expression[2048] ;
    cester_sprintf3(expression, 2048, expr, second, op, first);
    cester_evaluate_expression(eval_result, (char*)expression, file_path, line_num);
}

static __CESTER_INLINE__ void cester_compare_double(int eval_result, char const* const expr, double first, double second, char const* const op, char const* const file_path, unsigned const line_num) {
    char expression[2048] ;
    cester_sprintf3(expression, 2048, expr, second, op, first);
    cester_evaluate_expression(eval_result, (char*)expression, file_path, line_num);
}

static __CESTER_INLINE__ void cester_compare_ldouble(int eval_result, char const* const expr, long double first, long double second, char const* const op, char const* const file_path, unsigned const line_num) {
    char expression[2048] ;
    cester_sprintf3(expression, 2048, expr, second, op, first);
    cester_evaluate_expression(eval_result, (char*)expression, file_path, line_num);
}

#ifndef __CESTER_STDC_VERSION__
/**
    Create a test case, this uses the first arguments as the test
    case name and identifier and the body of the test.
*/
#define CESTER_TEST(x,y,z) static void cester_test_##x(TestInstance* y);

/**
    Create a test case that has not been implemented, It is skipped and
    generates warning. This macro will print message in output to remind
    the developer of it implementation. Good for TDD.

    This uses the first arguments as the test case name and identifier
    and the body of the test.
*/
#define CESTER_TODO_TEST(x,y,z) static void cester_test_##x(TestInstance* y);

/**
    Create a test case that is not run.

    This uses the first arguments as the test case name and identifier
    and the body of the test.
*/
#define CESTER_SKIP_TEST(x,y,z) static void cester_test_##x(TestInstance* y);

/**
    The function that would be invoked once before running
    any test in the test file. You can only have one of this function
    in a test file.
*/
#define CESTER_BEFORE_ALL(x,y) void cester_before_all_test(TestInstance* x);

/**
    The function that would be invoked before each test. You can only 
    have one of this function in a test file.
*/
#define CESTER_BEFORE_EACH(w,x,y,z) void cester_before_each_test(TestInstance* w, char * const x, unsigned y);

/**
    The function that would be invoked once after running 
    all the tests in the test file. You can only have one of this function 
    in a test file.
*/
#define CESTER_AFTER_ALL(x,y) void cester_after_all_test(TestInstance* x);

/**
    The functions that would be invoked after each test is 
    ran. You can only have one of this function in a test file.
*/
#define CESTER_AFTER_EACH(w,x,y,z) void cester_after_each_test(TestInstance* w, char * const x, unsigned y);

/**
    Set the options for cester, anything in this macro will be executed before 
    the tests starts running.
*/
#define CESTER_OPTIONS(x) void cester_options_before_main();

/**
    Absorb the statements and logic in a test file before re including 
    the __BASE_FILE__. This way code can be written in the global space of the 
    test file. 
    
    \note do not put other CESTER_ macros inside this one, this should contain 
    only your C or C++ code.
*/
#define CESTER_BODY(x)

/**
    A multiline comment macro everything in the macro is totally 
    ignored during macro expansion.
*/
#define CESTER_COMMENT(x)

#ifndef CESTER_NO_MOCK
/**
    Mock a function to just return a value. the first argument is the name 
    of the function to mock, the second argument is the return type of the 
    function, the third parameter is the value that is returned when the 
    function is called. 
    
    This still requires using the -Wl,--wrap option to wrap the parameter 
    to override the initial function. E.g. if the function `multiply_by` 
    is mocked the option `-Wl,--wrap=multiply_by` should be added during 
    compilation. 
    
    Th mocking features only works on GCC for now.
*/
#define CESTER_MOCK_SIMPLE_FUNCTION(x,y,z)  __attribute__((weak)) y x; y __real_##x;

/**

*/
#define CESTER_MOCK_FUNCTION(x,y,z) __attribute__((weak)) y x; extern y __real_##x;
#else 
#define CESTER_MOCK_SIMPLE_FUNCTION(x,y,z)
#define CESTER_MOCK_FUNCTION(x,y,z)
#endif

#else
    
#define CESTER_TEST(x,y,...) static void cester_test_##x(TestInstance* y);
#define CESTER_TODO_TEST(x,y,...) static void cester_test_##x(TestInstance* y);
#define CESTER_SKIP_TEST(x,y,...) static void cester_test_##x(TestInstance* y);
#define CESTER_BEFORE_ALL(x,...) void cester_before_all_test(TestInstance* x);
#define CESTER_BEFORE_EACH(w,x,y,...) void cester_before_each_test(TestInstance* w, char * const x, unsigned y);
#define CESTER_AFTER_ALL(x,...) void cester_after_all_test(TestInstance* x);
#define CESTER_AFTER_EACH(w,x,y,...) void cester_after_each_test(TestInstance* w, char * const x, unsigned y);
#define CESTER_OPTIONS(...) void cester_options_before_main();
#define CESTER_BODY(...)
#define CESTER_COMMENT(...)
#ifndef CESTER_NO_MOCK
#define CESTER_MOCK_SIMPLE_FUNCTION(x,y,...)  __attribute__((weak)) y x; y __real_##x;
#define CESTER_MOCK_FUNCTION(x,y,...) __attribute__((weak)) y x; extern y __real_##x;
#else 
#define CESTER_MOCK_SIMPLE_FUNCTION(x,y,...)
#define CESTER_MOCK_FUNCTION(x,y,...)
#endif
#endif

#ifdef __BASE_FILE__
#ifdef __cplusplus
}
#endif
    #include __BASE_FILE__
#ifdef __cplusplus
extern "C" {
#endif
#else 
    
#endif

#undef CESTER_TEST
#undef CESTER_TODO_TEST
#undef CESTER_SKIP_TEST
#undef CESTER_BEFORE_ALL
#undef CESTER_BEFORE_EACH
#undef CESTER_AFTER_ALL
#undef CESTER_AFTER_EACH
#undef CESTER_OPTIONS
#undef CESTER_BODY
#undef CESTER_MOCK_SIMPLE_FUNCTION
#undef CESTER_MOCK_FUNCTION

#ifdef __CESTER_STDC_VERSION__
#ifndef CESTER_NO_TIME
#define CESTER_TEST(x,y,...) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, 0.000, 0.000, (char*) "", (char*) #x, (cester_test_##x), NULL, NULL, CESTER_NORMAL_TEST },
#define CESTER_TODO_TEST(x,y,...) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, 0.000, 0.000, (char*) "", (char*) #x, (cester_test_##x), NULL, NULL, CESTER_NORMAL_TODO_TEST },
#define CESTER_SKIP_TEST(x,y,...) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, 0.000, 0.000, (char*) "", (char*) #x, (cester_test_##x), NULL, NULL, CESTER_NORMAL_SKIP_TEST },
#define CESTER_BEFORE_ALL(x,...) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, 0.000, 0.000, (char*) "", (char*) "cester_before_all_test", (cester_before_all_test), NULL, NULL, CESTER_BEFORE_ALL_TEST },
#define CESTER_BEFORE_EACH(w,x,y,...) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, 0.000, 0.000, (char*) (char*) "", (char*) "cester_before_each_test", NULL, (cester_before_each_test), NULL, CESTER_BEFORE_EACH_TEST },
#define CESTER_AFTER_ALL(x,...) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, 0.000, 0.000, (char*) "", (char*) "cester_after_all_test", (cester_after_all_test), NULL, NULL, CESTER_AFTER_ALL_TEST },
#define CESTER_AFTER_EACH(w,x,y,...) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, 0.000, 0.000, (char*) "", (char*) "cester_after_each_test", NULL, (cester_after_each_test), NULL, CESTER_AFTER_EACH_TEST },
#define CESTER_OPTIONS(...) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, 0.000, 0.000, (char*) "", (char*) "cester_options_before_main", NULL, NULL, (cester_options_before_main), CESTER_OPTIONS_FUNCTION },
#else
#define CESTER_TEST(x,y,...) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, (char*) "", (char*) #x, (cester_test_##x), NULL, NULL, CESTER_NORMAL_TEST },
#define CESTER_TODO_TEST(x,y,...) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, (char*) "", (char*) #x, (cester_test_##x), NULL, NULL, CESTER_NORMAL_TODO_TEST },
#define CESTER_SKIP_TEST(x,y,...) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, (char*) "", (char*) #x, (cester_test_##x), NULL, NULL, CESTER_NORMAL_SKIP_TEST },
#define CESTER_BEFORE_ALL(x,...) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, (char*) "", (char*) "cester_before_all_test", (cester_before_all_test), NULL, NULL, CESTER_BEFORE_ALL_TEST },
#define CESTER_BEFORE_EACH(w,x,y,...) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, (char*) (char*) "", (char*) "cester_before_each_test", NULL, (cester_before_each_test), NULL, CESTER_BEFORE_EACH_TEST },
#define CESTER_AFTER_ALL(x,...) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, (char*) "", (char*) "cester_after_all_test", (cester_after_all_test), NULL, NULL, CESTER_AFTER_ALL_TEST },
#define CESTER_AFTER_EACH(w,x,y,...) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, (char*) "", (char*) "cester_after_each_test", NULL, (cester_after_each_test), NULL, CESTER_AFTER_EACH_TEST },
#define CESTER_OPTIONS(...) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, (char*) "", (char*) "cester_options_before_main", NULL, NULL, (cester_options_before_main), CESTER_OPTIONS_FUNCTION },
#endif
#define CESTER_BODY(...)
#define CESTER_MOCK_SIMPLE_FUNCTION(x,y,...) 
#define CESTER_MOCK_FUNCTION(x,y,...)
#else
#ifndef CESTER_NO_TIME
#define CESTER_TEST(x,y,z) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, 0.000, 0.000, (char*) "", (char*) #x, (cester_test_##x), NULL, NULL, CESTER_NORMAL_TEST },
#define CESTER_TODO_TEST(x,y,z) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, 0.000, 0.000, (char*) "", (char*) #x, (cester_test_##x), NULL, NULL, CESTER_NORMAL_TODO_TEST },
#define CESTER_SKIP_TEST(x,y,z) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, 0.000, 0.000, (char*) "", (char*) #x, (cester_test_##x), NULL, NULL, CESTER_NORMAL_SKIP_TEST },
#define CESTER_BEFORE_ALL(x,y) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, 0.000, 0.000, (char*) "", (char*) "cester_before_all_test", (cester_before_all_test), NULL, NULL, CESTER_BEFORE_ALL_TEST },
#define CESTER_BEFORE_EACH(w,x,y,z) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, 0.000, 0.000, (char*) (char*) "", (char*) "cester_before_each_test", NULL, (cester_before_each_test), NULL, CESTER_BEFORE_EACH_TEST },
#define CESTER_AFTER_ALL(x,y) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, 0.000, 0.000, (char*) "", (char*) "cester_after_all_test", (cester_after_all_test), NULL, NULL, CESTER_AFTER_ALL_TEST },
#define CESTER_AFTER_EACH(w,x,y,z) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, 0.000, 0.000, (char*) "", (char*) "cester_after_each_test", NULL, (cester_after_each_test), NULL, CESTER_AFTER_EACH_TEST },
#define CESTER_OPTIONS(x) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, 0.000, 0.000, (char*) "", (char*) "cester_options_before_main", NULL, NULL, (cester_options_before_main), CESTER_OPTIONS_FUNCTION },
#else
#define CESTER_TEST(x,y,z) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, (char*) "", (char*) #x, (cester_test_##x), NULL, NULL, CESTER_NORMAL_TEST },
#define CESTER_TODO_TEST(x,y,z) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, (char*) "", (char*) #x, (cester_test_##x), NULL, NULL, CESTER_NORMAL_TODO_TEST },
#define CESTER_SKIP_TEST(x,y,z) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, (char*) "", (char*) #x, (cester_test_##x), NULL, NULL, CESTER_NORMAL_SKIP_TEST },
#define CESTER_BEFORE_ALL(x,y) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, (char*) "", (char*) "cester_before_all_test", (cester_before_all_test), NULL, NULL, CESTER_BEFORE_ALL_TEST },
#define CESTER_BEFORE_EACH(w,x,y,z) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, (char*) (char*) "", (char*) "cester_before_each_test", NULL, (cester_before_each_test), NULL, CESTER_BEFORE_EACH_TEST },
#define CESTER_AFTER_ALL(x,y) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, (char*) "", (char*) "cester_after_all_test", (cester_after_all_test), NULL, NULL, CESTER_AFTER_ALL_TEST },
#define CESTER_AFTER_EACH(w,x,y,z) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, (char*) "", (char*) "cester_after_each_test", NULL, (cester_after_each_test), NULL, CESTER_AFTER_EACH_TEST },
#define CESTER_OPTIONS(x) { CESTER_RESULT_UNKNOWN, __LINE__, CESTER_RESULT_SUCCESS, (char*) "", (char*) "cester_options_before_main", NULL, NULL, (cester_options_before_main), CESTER_OPTIONS_FUNCTION },
#endif
#define CESTER_BODY(x)
#define CESTER_MOCK_SIMPLE_FUNCTION(x,y,z) 
#define CESTER_MOCK_FUNCTION(x,y,z)
#endif

#ifdef __cplusplus
}
#endif
static TestCase cester_test_cases[] = {
#ifdef __BASE_FILE__
    #include __BASE_FILE__
#endif
#ifndef CESTER_NO_TIME
{ CESTER_RESULT_UNKNOWN, 0, CESTER_RESULT_SUCCESS, 0.000, 0.000, NULL, NULL, NULL, NULL, NULL, CESTER_TESTS_TERMINATOR }
#else
{ CESTER_RESULT_UNKNOWN, 0, CESTER_RESULT_SUCCESS, NULL, NULL, NULL, NULL, NULL, CESTER_TESTS_TERMINATOR }
#endif
};
#ifdef __cplusplus
extern "C" {
#endif

#undef CESTER_TEST
#undef CESTER_TODO_TEST
#undef CESTER_SKIP_TEST
#undef CESTER_BEFORE_ALL
#undef CESTER_BEFORE_EACH
#undef CESTER_AFTER_ALL
#undef CESTER_AFTER_EACH
#undef CESTER_OPTIONS
#undef CESTER_BODY
#undef CESTER_MOCK_SIMPLE_FUNCTION
#undef CESTER_MOCK_FUNCTION

#ifdef __CESTER_STDC_VERSION__
#define CESTER_TEST(x,y,...) static void cester_test_##x(TestInstance* y) { __VA_ARGS__  } 
#define CESTER_TODO_TEST(x,y,...) static void cester_test_##x(TestInstance* y) { __VA_ARGS__ }
#define CESTER_SKIP_TEST(x,y,...) static void cester_test_##x(TestInstance* y) { __VA_ARGS__ } 
#define CESTER_BEFORE_ALL(x,...) void cester_before_all_test(TestInstance* x) { __VA_ARGS__ CESTER_NO_ISOLATION(); } 
#define CESTER_BEFORE_EACH(w,x,y,...) void cester_before_each_test(TestInstance* w, char * const x, unsigned y) { __VA_ARGS__ CESTER_NO_ISOLATION(); }
#define CESTER_AFTER_ALL(x,...) void cester_after_all_test(TestInstance* x) { __VA_ARGS__ CESTER_NO_ISOLATION(); }
#define CESTER_AFTER_EACH(w,x,y,...) void cester_after_each_test(TestInstance* w, char * const x, unsigned y) { __VA_ARGS__ CESTER_NO_ISOLATION(); }
#define CESTER_OPTIONS(...) void cester_options_before_main() { __VA_ARGS__ }
#define CESTER_BODY(...) __VA_ARGS__
#ifndef CESTER_NO_MOCK
#define CESTER_MOCK_SIMPLE_FUNCTION(x,y,...) y __wrap_##x { return __VA_ARGS__; }
#define CESTER_MOCK_FUNCTION(x,y,...) y __wrap_##x { __VA_ARGS__ }
#else
#define CESTER_MOCK_SIMPLE_FUNCTION(x,y,...) 
#define CESTER_MOCK_FUNCTION(x,y,...) 
#endif

#else
    
#define CESTER_TEST(x,y,z) static void cester_test_##x(TestInstance* y) { z } 
#define CESTER_TODO_TEST(x,y,z) static void cester_test_##x(TestInstance* y) { z }
#define CESTER_SKIP_TEST(x,y,z) static void cester_test_##x(TestInstance* y) { z } 
#define CESTER_BEFORE_ALL(x,y) void cester_before_all_test(TestInstance* x) { y CESTER_NO_ISOLATION(); } 
#define CESTER_BEFORE_EACH(w,x,y,z) void cester_before_each_test(TestInstance* w, char * const x, unsigned y) { z CESTER_NO_ISOLATION(); }
#define CESTER_AFTER_ALL(x,y) void cester_after_all_test(TestInstance* x) { y CESTER_NO_ISOLATION(); }
#define CESTER_AFTER_EACH(w,x,y,z) void cester_after_each_test(TestInstance* w, char * const x, unsigned y) { z CESTER_NO_ISOLATION(); }
#define CESTER_OPTIONS(x) void cester_options_before_main() { x }
#define CESTER_BODY(x) x
#ifndef CESTER_NO_MOCK
#define CESTER_MOCK_SIMPLE_FUNCTION(x,y,z) y __wrap_##x { return z; }
#define CESTER_MOCK_FUNCTION(x,y,z) y __wrap_##x { z }
#else
#define CESTER_MOCK_SIMPLE_FUNCTION(x,y,z) 
#define CESTER_MOCK_FUNCTION(x,y,z) 
#endif
#endif

/**
    Manually register a test case in situation where the the test 
    are not auto detected or selected test cases want to be run. 
    
    If a test is registered manually all auto detected test will not 
    be executed. 
*/
#define CESTER_REGISTER_TEST(x) cester_register_test((char*)#x, (cester_test_##x), NULL, NULL, __LINE__, CESTER_NORMAL_TEST)

/**
    Manually register a test case as a skip test which cases the test case 
    not to run but it will be reported in result and logged under skipped tests.
    
    Reason for skipping a test can be unavailability of resources or any other 
    reason.
*/
#define CESTER_REGISTER_SKIP_TEST(x) cester_register_test((char*)#x, (cester_test_##x), NULL, NULL, __LINE__, CESTER_NORMAL_SKIP_TEST)

/**
    Manually register a test case that is yet to be implemented so it will be 
    skipped but it will be reported in result and logged under todo tests.
*/
#define CESTER_REGISTER_TODO_TEST(x) cester_register_test((char*)#x, (cester_test_##x), NULL, NULL, __LINE__, CESTER_NORMAL_TODO_TEST)

/**
    Manually notify cester to execute the BEFORE_ALL function to execute 
    before all the test case are run.
*/
#define CESTER_REGISTER_BEFORE_ALL() cester_register_test("cester_before_all_test", (cester_before_all_test), NULL, NULL, __LINE__, CESTER_BEFORE_ALL_TEST)

/**
    Manually notify cester to execute the BEFORE_EACH function to execute 
    every time before a test case is run.
*/
#define CESTER_REGISTER_BEFORE_EACH() cester_register_test("cester_before_each_test", NULL, (cester_before_each_test), NULL, __LINE__, CESTER_BEFORE_EACH_TEST)

/**
    Manually notify cester to execute the AFTER_ALL function to execute 
    after all the test case are run.
*/
#define CESTER_REGISTER_AFTER_ALL() cester_register_test("cester_after_all_test", (cester_after_all_test), NULL, NULL, __LINE__, CESTER_AFTER_ALL_TEST)

/**
    Manually notify cester to execute the AFTER_EACH function to execute 
    every time after a test case is run.
*/
#define CESTER_REGISTER_AFTER_EACH() cester_register_test("cester_after_each_test", NULL, (cester_after_each_test), NULL, __LINE__, CESTER_AFTER_EACH_TEST)

/**
    Manually notify cester to execute the CESTER_OPTIONS block before running 
    the tests.
*/
#define CESTER_REGISTER_OPTIONS() cester_register_test("cester_options_before_main", NULL, NULL, (cester_options_before_main), __LINE__, CESTER_OPTIONS_FUNCTION)

/**
    Set the expected result of a test case. 
    
    \param x the test case name
    \param y the expected result. Can be one of the ::cester_test_status enum
*/
#define CESTER_TEST_SHOULD(x,y) cester_expected_test_result(#x, y);

/**
    Change the expected result of a test case to Segfault. 
    If the test segfault then it passes. If it does not segfault 
    it is marked as failed.
    
    \param x the test case name
*/
#define CESTER_TEST_SHOULD_SEGFAULT(x) CESTER_TEST_SHOULD(x, CESTER_RESULT_SEGFAULT);

/**
    Change the expected result of a test case to failure. 
    If the test case passed then it marked as failure. If it failed 
    then it consider as passed.
    
    \param x the test case name
*/
#define CESTER_TEST_SHOULD_FAIL(x) CESTER_TEST_SHOULD(x, CESTER_RESULT_FAILURE);

/**
    Change the expected test case result. If the test case is terminated by user 
    or another program then it passes ortherwise it fails.
    
    \param x the test case name
*/
#define CESTER_TEST_SHOULD_BE_TERMINATED(x) CESTER_TEST_SHOULD(x, CESTER_RESULT_TERMINATED);

#ifndef CESTER_NO_MEM_TEST
/**
    Change the expected test case result to leak memory. If the test case does not 
    leak any memory then the test case is marked as failure.
    
    \param x the test case name
*/
#define CESTER_TEST_SHOULD_LEAK_MEMORY(x) CESTER_TEST_SHOULD(x, CESTER_RESULT_MEMORY_LEAK);
#endif

/**
    Manually register a test case
*/
static __CESTER_INLINE__ void cester_register_test(char *test_name, cester_test f1, cester_before_after_each f2, cester_void f3, unsigned line_num, TestType test_type) {
    TestCase* test_case ;
    if (superTestInstance.registered_test_cases == NULL) {
	if (cester_array_init(&superTestInstance.registered_test_cases) == 0) {
	    if (superTestInstance.output_stream==NULL) {
            superTestInstance.output_stream = stdout;
	    }
	    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), "Unable to initialize the test cases array. Cannot run manually registered tests.\n");
	    return;
	}
    }
    test_case = (TestCase*) malloc(sizeof(TestCase));
    test_case->execution_status = CESTER_RESULT_UNKNOWN;
    test_case->line_num = line_num;
    test_case->expected_result = CESTER_RESULT_SUCCESS;
    #ifndef CESTER_NO_TIME
        test_case->start_tic = 0.000;
        test_case->execution_time = 0.000;
    #endif
    test_case->execution_output = (char*) "";
    test_case->test_function = f1;
    test_case->test_ba_function = f2;
    test_case->test_void_function = f3;
    test_case->name = test_name;
    test_case->test_type = test_type;
    if (cester_array_add(superTestInstance.registered_test_cases, test_case) == 0) {
        if (superTestInstance.output_stream==NULL) {
            superTestInstance.output_stream = stdout;
        }
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), "Failed to register '");
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), test_name);
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), "' \n");
        superTestInstance.mem_test_active = 0;
    }
}

static __CESTER_INLINE__ void cester_expected_test_result(const char* const test_name, enum cester_test_status expected_result) {
    unsigned i,index;
    if (superTestInstance.registered_test_cases->size == 0) {
        for (i=0;cester_test_cases[i].test_type != CESTER_TESTS_TERMINATOR;++i) {
            if ((cester_test_cases[i].test_type == CESTER_NORMAL_TEST || 
                       cester_test_cases[i].test_type == CESTER_NORMAL_TODO_TEST || 
                       cester_test_cases[i].test_type == CESTER_NORMAL_SKIP_TEST) &&
                       cester_string_equals(cester_test_cases[i].name, (char*)test_name) == 1) {
                           
                cester_test_cases[i].expected_result = expected_result;
            }
            
        }
    }
    
    CESTER_ARRAY_FOREACH(superTestInstance.registered_test_cases, index, test_case, {
        if ((((TestCase*)test_case)->test_type == CESTER_NORMAL_TEST || 
                   ((TestCase*)test_case)->test_type == CESTER_NORMAL_TODO_TEST || 
                   ((TestCase*)test_case)->test_type == CESTER_NORMAL_SKIP_TEST) && 
                   cester_string_equals(((TestCase*)test_case)->name, (char*)test_name) == 1) {
            
            ((TestCase*)test_case)->expected_result = expected_result;
        }
    })
}

static __CESTER_INLINE__ unsigned cester_run_test_no_isolation(TestInstance *, TestCase *, unsigned);

static __CESTER_INLINE__ void cester_report_single_test_result(unsigned last_status, TestCase *a_test_case) {
    #ifndef CESTER_NO_TIME
        clock_t tok ;
    
        tok = clock();
        a_test_case->execution_time = (double)(((double)tok) - ((double)a_test_case->start_tic)) / CLOCKS_PER_SEC;
    #endif
    if ((a_test_case->expected_result == last_status || a_test_case->expected_result == CESTER_RESULT_FAILURE) && last_status != CESTER_RESULT_SUCCESS) {
        a_test_case->execution_status = CESTER_RESULT_SUCCESS;
        cester_concat_str(&a_test_case->execution_output, "Passed ");
        cester_concat_str(&a_test_case->execution_output, (superTestInstance.minimal == 0 ? superTestInstance.test_file_path : cester_extract_name(superTestInstance.test_file_path) ));
        cester_concat_str(&a_test_case->execution_output, ":");
        cester_concat_int(&a_test_case->execution_output, a_test_case->line_num);
        cester_concat_str(&a_test_case->execution_output, ":");
        cester_concat_str(&a_test_case->execution_output, " in '");
        cester_concat_str(&a_test_case->execution_output, a_test_case->name);
        cester_concat_str(&a_test_case->execution_output, "' => ");
        switch (a_test_case->expected_result) {
            case CESTER_RESULT_FAILURE:
                cester_concat_str(&a_test_case->execution_output, "Failed as expected");
                break;
            case CESTER_RESULT_SEGFAULT:
                cester_concat_str(&a_test_case->execution_output, "Segfault as expected");
                break;
            case CESTER_RESULT_TERMINATED:
                cester_concat_str(&a_test_case->execution_output, "Prematurely terminated as expected");
                break;
            case CESTER_RESULT_TIMED_OUT:
                cester_concat_str(&a_test_case->execution_output, "Timed out as expected");
                break;
#ifndef CESTER_NO_MEM_TEST
            case CESTER_RESULT_MEMORY_LEAK:
                cester_concat_str(&a_test_case->execution_output, "Leaked memory as expected");
                break;
#endif
            case CESTER_RESULT_SUCCESS:
            case CESTER_RESULT_UNKNOWN:
                break;
        }
        cester_concat_str(&a_test_case->execution_output, "\n");
    } else {
        a_test_case->execution_status = last_status;
    }
    if (a_test_case->execution_status == CESTER_RESULT_SUCCESS) {
        ++superTestInstance.total_passed_tests_count;
    } else {
        ++superTestInstance.total_failed_tests_count;
    }
    superTestInstance.current_execution_status = a_test_case->execution_status;
}

static __CESTER_INLINE__ void cester_run_test(TestInstance *test_instance, TestCase *a_test_case, unsigned index) {
    unsigned last_status;

    last_status = CESTER_RESULT_UNKNOWN;
    superTestInstance.current_test_case = a_test_case;
#ifndef CESTER_NO_SIGNAL
    if (setjmp(buf) == 1) {
        goto check_isolation;
    }
#endif
#ifndef CESTER_NO_TIME
    a_test_case->start_tic = clock();
#endif
#ifndef __CESTER_STDC_VERSION__
    #pragma message("Isolated tests not supported in C version less than C99. cester will rely of signal for crash reporting")
    superTestInstance.isolate_tests = 0;
#endif
    if (superTestInstance.isolate_tests == 1 && last_status == CESTER_RESULT_UNKNOWN) {
#ifdef __CESTER_STDC_VERSION__
#ifdef _WIN32
        SECURITY_ATTRIBUTES sa;
        sa.nLength = sizeof(SECURITY_ATTRIBUTES);
        sa.bInheritHandle = TRUE;
        sa.lpSecurityDescriptor = NULL;

        HANDLE stdout_pipe_read;
        HANDLE stdout_pipe_write;
        CreatePipe(&stdout_pipe_read, &stdout_pipe_write, &sa, 0);

        STARTUPINFO si = {
            .cb = sizeof(STARTUPINFO),
            .dwFlags = STARTF_USESTDHANDLES,
            .hStdOutput = stdout_pipe_write
        };

        PROCESS_INFORMATION pi = {0};

        CHAR command[1500];
        snprintf(command, 1500, "%s --cester-test=%s  --cester-singleoutput --cester-noisolation %s %s %s %s %s %s %s",
                    test_instance->argv[0],
                    a_test_case->name,
                    (superTestInstance.mem_test_active == 0 ? "--cester-nomemtest" : ""),
                    (superTestInstance.minimal == 1 ? "--cester-minimal" : ""),
                    (superTestInstance.verbose == 1 ? "--cester-verbose" : ""),
                    (superTestInstance.format_test_name == 0 ? "--cester-dontformatname" : ""),
                    (cester_string_equals(superTestInstance.output_format, (char*) "tap") == 1 ? "--cester-output=tap" : ""),
                    (cester_string_equals(superTestInstance.output_format, (char*) "tapV13") == 1 ? "--cester-output=tapV13" : ""),
                    superTestInstance.flattened_cmd_argv);

        CreateProcess(
            NULL,
            command,
            NULL,
            NULL,
            TRUE,
            0,
            NULL,
            NULL,
            &si,
            &pi);

        CloseHandle(stdout_pipe_write);

        DWORD len;
        DWORD maxlen = 700;
        CHAR buffer[700];

        do {
            ReadFile(stdout_pipe_read, buffer, maxlen, &len, NULL);
            buffer[len] = '\0';
            cester_concat_str(&a_test_case->execution_output, buffer);
        } while (len > 0);

        WaitForSingleObject(pi.hProcess, INFINITE);

        DWORD status;
        GetExitCodeProcess(pi.hProcess, &status);

        if ((status & 0x80000000)) {
            last_status = CESTER_RESULT_SEGFAULT;
        } else if (status == 1 && strlen(a_test_case->execution_output) == 0) {
            last_status = CESTER_RESULT_TERMINATED;
        } else {
            last_status = status;
        }

        end_sub_process:
            CloseHandle(pi.hProcess);
            CloseHandle(pi.hThread);
#elif defined unix
        pid_t pid;
        int pipefd[2];
        char *selected_test_unix = (char*) "";

        pipe(pipefd);
        pid = fork();

        if (pid == -1) {
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), "Unable to create a seperate process for the '");
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), a_test_case->name);
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), "'. Running the test on main process.");
            last_status = cester_run_test_no_isolation(test_instance, a_test_case, index);

        } else if (pid == 0) {
            cester_concat_str(&selected_test_unix, "--cester-test=");
            cester_concat_str(&selected_test_unix, a_test_case->name);
            close(pipefd[0]);
            dup2(pipefd[1], STDOUT_FILENO);
            execl(test_instance->argv[0],
                    test_instance->argv[0],
                    selected_test_unix,
                    "--cester-singleoutput",
                    "--cester-noisolation",
                    (superTestInstance.mem_test_active == 0 ? "--cester-nomemtest" : ""),
                    (superTestInstance.minimal == 1 ? "--cester-minimal" : ""),
                    (superTestInstance.verbose == 1 ? "--cester-verbose" : ""),
                    (superTestInstance.format_test_name == 0 ? "--cester-dontformatname" : ""),
                    (superTestInstance.no_color == 1 ? "--cester-nocolor" : ""),
                    (cester_string_equals(superTestInstance.output_format, (char*) "tap") == 1 ? "--cester-output=tap" : ""),
                    (cester_string_equals(superTestInstance.output_format, (char*) "tapV13") == 1 ? "--cester-output=tapV13" : ""),
                    superTestInstance.flattened_cmd_argv,
                    (char*)NULL);
            exit(CESTER_RESULT_FAILURE);

        } else {
            int status;
            char buffer[700];
            size_t len;

            close(pipefd[1]);
            while ((len = read(pipefd[0], buffer, 700)) != 0) {
                buffer[len] = '\0';
                cester_concat_str(&a_test_case->execution_output, buffer);
            }
            waitpid(pid, &status, 0);
            close(pipefd[0]);
            last_status = WEXITSTATUS(status);
            end_sub_process:
                kill(pid, SIGTERM);
        }
#else
        #pragma message("Isolated tests not supported in this environment. The tests will be run on the main process")
        last_status = cester_run_test_no_isolation(test_instance, a_test_case, index);
#define CESTER_NO_SUBPROCESS 1
#endif
#endif
    } else if (last_status == CESTER_RESULT_UNKNOWN) {
        last_status = cester_run_test_no_isolation(test_instance, a_test_case, index);
    }
    resolve_test_result:
        cester_report_single_test_result(last_status, a_test_case);
        return;
    
    check_isolation:
        last_status = superTestInstance.current_execution_status;
#ifdef __CESTER_STDC_VERSION__
#ifndef __cplusplus
#ifndef CESTER_NO_SUBPROCESS
        if (superTestInstance.isolate_tests == 1) {
            goto end_sub_process;
        }
#endif
#endif
#endif
        goto resolve_test_result;
}

static __CESTER_INLINE__ unsigned cester_run_test_no_isolation(TestInstance *test_instance, TestCase *a_test_case, unsigned index) {
    unsigned i, index1, index2, mem_index;
    #ifndef CESTER_NO_TIME
        clock_t tok;
    #endif
    superTestInstance.current_execution_status = CESTER_RESULT_SUCCESS;
    if (superTestInstance.registered_test_cases->size == 0) {
        for (i=0;cester_test_cases[i].test_type != CESTER_TESTS_TERMINATOR;++i) {
            if (cester_test_cases[i].test_type == CESTER_BEFORE_EACH_TEST) {
                ((cester_before_after_each)cester_test_cases[i].test_ba_function)(test_instance, a_test_case->name, index);
            }
        }
    }
    CESTER_ARRAY_FOREACH(superTestInstance.registered_test_cases, index1, test_case, {
        if (((TestCase*)test_case)->test_type == CESTER_BEFORE_EACH_TEST) {
            ((cester_before_after_each)((TestCase*)test_case)->test_ba_function)(test_instance, a_test_case->name, index);
        }
    })
    ((cester_test)a_test_case->test_function)(test_instance);
    if (superTestInstance.registered_test_cases->size == 0) {
        for (i=0;cester_test_cases[i].test_type != CESTER_TESTS_TERMINATOR;++i) {
            if (cester_test_cases[i].test_type == CESTER_AFTER_EACH_TEST) {
                ((cester_before_after_each)cester_test_cases[i].test_ba_function)(test_instance, a_test_case->name, index);
            }
        }
    }
    CESTER_ARRAY_FOREACH(superTestInstance.registered_test_cases, index2, test_case, {
        if (((TestCase*)test_case)->test_type == CESTER_AFTER_EACH_TEST) {
           ((cester_before_after_each)((TestCase*)test_case)->test_ba_function)(test_instance, a_test_case->name, index);
        }
    })
    ++superTestInstance.total_tests_ran;
#ifndef CESTER_NO_MEM_TEST
    if (superTestInstance.mem_test_active == 1) {
        unsigned leaked_bytes = 0;
        CESTER_ARRAY_FOREACH(superTestInstance.mem_alloc_manager, mem_index, alloc_mem, {
            if (cester_string_equals((char*)((AllocatedMemory*)alloc_mem)->function_name, a_test_case->name)) {
                leaked_bytes += ((AllocatedMemory*)alloc_mem)->allocated_bytes;
                if (superTestInstance.current_test_case != NULL) {
                    if (cester_string_equals(superTestInstance.output_format, (char*) "tap") == 1) {
                        cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "# ");
                    }
                    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "MemoryLeakError ");
                    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, (superTestInstance.minimal == 0 ? superTestInstance.test_file_path : cester_extract_name(superTestInstance.test_file_path) ));
                    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, ":");
                    cester_concat_int(&(superTestInstance.current_test_case)->execution_output, ((AllocatedMemory*)alloc_mem)->line_num);
                    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, ": ");
                    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "in '");
                    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, (superTestInstance.current_test_case)->name);
                    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "' => Memory allocated in line '");
                    cester_concat_int(&(superTestInstance.current_test_case)->execution_output, ((AllocatedMemory*)alloc_mem)->line_num);
                    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "' not freed. Leaking '");
                    cester_concat_int(&(superTestInstance.current_test_case)->execution_output, ((AllocatedMemory*)alloc_mem)->allocated_bytes);
                    cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "' Bytes \n");
                }
            }
        })
        
        if (leaked_bytes > 0) {
            superTestInstance.current_execution_status = CESTER_RESULT_MEMORY_LEAK;
        }
    }
#endif
    if (superTestInstance.single_output_only == 1) {
        CESTER_DELEGATE_FPRINT_STR((default_color), a_test_case->execution_output);
    }
    return superTestInstance.current_execution_status;
}

#ifndef CESTER_NO_SIGNAL  
void (*signal(int , void (*)(int)))(int);
void cester_claim_signals();
void cester_recover_on_signal(int sig_num);
#endif

/* use start param to save the state index instead of starting 
loop again or super var */ 
static __CESTER_INLINE__ void cester_run_all_test_iterator(int start) {
    unsigned i, j, index, index1, index2, index3, test_index;
    unsigned found_test;
    char* selected_test_case_name;
    
    found_test = 0;
    test_index = 0;
    if (superTestInstance.selected_test_cases_size == 0) {
        if (superTestInstance.registered_test_cases->size == 0) {
            for (i=0;cester_test_cases[i].test_type != CESTER_TESTS_TERMINATOR;++i) {
                if (cester_test_cases[i].test_type == CESTER_NORMAL_TEST && cester_test_cases[i].execution_status == CESTER_RESULT_UNKNOWN) {
                    cester_run_test(superTestInstance.test_instance, &cester_test_cases[i], ++test_index);

                } else if (cester_test_cases[i].test_type == CESTER_NORMAL_TODO_TEST) {
                    ++superTestInstance.todo_tests_count;

                } else if (cester_test_cases[i].test_type == CESTER_NORMAL_SKIP_TEST) {
                    ++superTestInstance.skipped_test_count;

                }
            }
        }
        CESTER_ARRAY_FOREACH(superTestInstance.registered_test_cases, index2, test_case, {
            if (((TestCase*)test_case)->test_type == CESTER_NORMAL_TEST && ((TestCase*)test_case)->execution_status == CESTER_RESULT_UNKNOWN) {
                cester_run_test(superTestInstance.test_instance, ((TestCase*)test_case), ++test_index);

            } else if (((TestCase*)test_case)->test_type == CESTER_NORMAL_TODO_TEST) {
                ++superTestInstance.todo_tests_count;

            } else if (((TestCase*)test_case)->test_type == CESTER_NORMAL_SKIP_TEST) {
                ++superTestInstance.skipped_test_count;

            }
        })

    } else {
        for (j = superTestInstance.selected_test_cases_found; j < superTestInstance.selected_test_cases_size; ++j) {
            selected_test_case_name = superTestInstance.selected_test_cases_names[j];
            found_test = 0;
            if (superTestInstance.registered_test_cases->size == 0) {
                for (i=0;cester_test_cases[i].test_type != CESTER_TESTS_TERMINATOR;++i) {
                    if ((cester_test_cases[i].test_type == CESTER_NORMAL_TEST || cester_test_cases[i].test_type == CESTER_NORMAL_TODO_TEST ||
                        cester_test_cases[i].test_type == CESTER_NORMAL_SKIP_TEST) &&
                        cester_string_equals(cester_test_cases[i].name, selected_test_case_name) == 1 &&  
                        cester_test_cases[i].execution_status == CESTER_RESULT_UNKNOWN) {

                        found_test = 1;
                        if (cester_test_cases[i].test_type == CESTER_NORMAL_TEST) {
                            ++superTestInstance.selected_test_cases_found;
                            cester_run_test(superTestInstance.test_instance, &cester_test_cases[i], ++test_index);
                        } else {
                            cester_test_cases[i].execution_status = CESTER_RESULT_SUCCESS;
                            if (cester_test_cases[i].test_type == CESTER_NORMAL_SKIP_TEST) {
                                ++superTestInstance.skipped_test_count;
                            } else {
                                ++superTestInstance.todo_tests_count;
                            }
                        }
                    }
                }
            }
            if (found_test == 0) {
                CESTER_ARRAY_FOREACH(superTestInstance.registered_test_cases, index3, test_case, {
                    if ((((TestCase*)test_case)->test_type == CESTER_NORMAL_TEST || ((TestCase*)test_case)->test_type == CESTER_NORMAL_TODO_TEST ||
                        ((TestCase*)test_case)->test_type == CESTER_NORMAL_SKIP_TEST) &&
                        cester_string_equals(((TestCase*)test_case)->name, selected_test_case_name) == 1 && 
                        ((TestCase*)test_case)->execution_status == CESTER_RESULT_UNKNOWN) {

                        found_test = 1;
                        if (((TestCase*)test_case)->test_type == CESTER_NORMAL_TEST) {
                            ++superTestInstance.selected_test_cases_found;
                            cester_run_test(superTestInstance.test_instance, ((TestCase*)test_case), ++test_index);
                        } else {
                            ((TestCase*)test_case)->execution_status = CESTER_RESULT_SUCCESS;
                            if (((TestCase*)test_case)->test_type == CESTER_NORMAL_SKIP_TEST) {
                                ++superTestInstance.skipped_test_count;
                            } else {
                                ++superTestInstance.todo_tests_count;
                            }
                        }
                    }
                })
                if (found_test == 0) {
                    if (superTestInstance.minimal == 0 && cester_string_equals(superTestInstance.output_format, (char*) "text") == 1) {
                        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), "Warning: the '");
                        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), superTestInstance.selected_test_cases_names[j]);
                        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), "' was not found! \n");
                    }
                }
            }
        }
    }
}

static __CESTER_INLINE__ unsigned cester_run_all_test(unsigned argc, char **argv) {
    char* cester_option;
    char* arg;
    unsigned i, j, index, index1;
#ifdef _WIN32
	CONSOLE_SCREEN_BUFFER_INFO info;
	if (GetConsoleScreenBufferInfo(GetStdHandle(STD_OUTPUT_HANDLE), &info)) {
	    default_color = info.wAttributes;
	}
	hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
#endif

#ifndef CESTER_NO_SIGNAL    
    cester_claim_signals();
#endif

    i = 0; 
    j = 0;
    if (superTestInstance.output_stream==NULL) {
        superTestInstance.output_stream = stdout;
    }
#ifndef CESTER_NO_MEM_TEST
	if (superTestInstance.mem_alloc_manager == NULL) {
	    if (cester_array_init(&superTestInstance.mem_alloc_manager) == 0) {
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), "Unable to initialize the memory management array. Memory test disabled.\n");
            superTestInstance.mem_test_active = 0;
	    }
	}
#endif
    if (superTestInstance.registered_test_cases == NULL) {
        if (cester_array_init(&superTestInstance.registered_test_cases) == 0) {
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_RED), "Unable to initialize the registered test cases array. Cannot continue tests.\n");
            return CESTER_RESULT_FAILURE;
        }
    }

    /* resolve command line options */
    for (;j < argc; ++j) {
        arg = argv[j];
        if (cester_str_after_prefix(arg, (char*) "--cester-", 9, &cester_option) == 1) {
            if (cester_string_equals(cester_option, (char*) "minimal") == 1) {
                superTestInstance.minimal = 1;

            } else if (cester_string_equals(cester_option, (char*) "verbose") == 1) {
                superTestInstance.verbose = 1;

            } else if (cester_string_equals(cester_option, (char*) "nocolor") == 1) {
                superTestInstance.no_color = 1;

            } else if (cester_string_equals(cester_option, (char*) "printversion") == 1) {
                superTestInstance.print_version = 1;

            } else if (cester_string_equals(cester_option, (char*) "singleoutput") == 1) {
                superTestInstance.single_output_only = 1;

            } else if (cester_string_equals(cester_option, (char*) "noisolation") == 1) {
                superTestInstance.isolate_tests = 0;

            } else if (cester_string_equals(cester_option, (char*) "dontformatname") == 1) {
                superTestInstance.format_test_name = 0;
#ifndef CESTER_NO_MEM_TEST
            } else if (cester_string_equals(cester_option, (char*) "nomemtest") == 1) {
                superTestInstance.mem_test_active = 0;
#endif
            } else if (cester_string_equals(cester_option, (char*) "version") == 1) {
                CESTER_NOCOLOR();
                cester_print_version();
                return EXIT_SUCCESS;

            } else if (cester_string_equals(cester_option, (char*) "help") == 1) {
                CESTER_NOCOLOR();
                cester_print_version();
                cester_print_help();
                return EXIT_SUCCESS;

            } else if (cester_string_starts_with(cester_option, (char*) "test=") == 1) {
                unpack_selected_extra_args(cester_option, &superTestInstance.selected_test_cases_names, &superTestInstance.selected_test_cases_size);

            } else if (cester_string_starts_with(cester_option, (char*) "output=") == 1) {
                cester_str_value_after_first(cester_option, '=', &superTestInstance.output_format);
                if (cester_is_validate_output_option(superTestInstance.output_format) == 0) {
                    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_RED), "Invalid cester output format: ");
                    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_RED), superTestInstance.output_format);
                    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_RED), "\n");
                    if (cester_string_starts_with(superTestInstance.output_format, (char*) "tap")) {
                        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), "Did you mean 'tap' or 'tapV13?'\n");
                    }
                    CESTER_RESET_TERMINAL_ATTR()
                    return EXIT_FAILURE;
                }

            } else {
                CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_RED), "Invalid cester option: --cester-");
                CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_RED), cester_option);
                CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_RED), "\n");
                CESTER_RESET_TERMINAL_ATTR()
                return EXIT_FAILURE;
            }
        } else {
            cester_concat_str(&superTestInstance.flattened_cmd_argv, argv[j]);
            cester_concat_str(&superTestInstance.flattened_cmd_argv, " ");
        }
    }

    if (superTestInstance.print_version == 1) {
        cester_print_version();
        CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_WHITE), "\n");
        CESTER_RESET_TERMINAL_ATTR();
    }

    superTestInstance.test_instance = (TestInstance*) malloc(sizeof(TestInstance*));
    superTestInstance.test_instance->argc = argc;
    superTestInstance.test_instance->argv = argv;

    /* execute options */
    for (i=0;cester_test_cases[i].test_type != CESTER_TESTS_TERMINATOR;++i) {
        if (cester_test_cases[i].test_type == CESTER_OPTIONS_FUNCTION && superTestInstance.single_output_only == 0) {
            ((cester_void)cester_test_cases[i].test_void_function)();

        } else if ((cester_test_cases[i].test_type == CESTER_NORMAL_TEST ||
               cester_test_cases[i].test_type == CESTER_NORMAL_TODO_TEST ||
               cester_test_cases[i].test_type == CESTER_NORMAL_SKIP_TEST) &&
               superTestInstance.registered_test_cases->size == 0) {

            ++superTestInstance.total_tests_count;
        }

    }

    CESTER_ARRAY_FOREACH(superTestInstance.registered_test_cases, index, test_case, {
        if (((TestCase*)test_case)->test_type == CESTER_OPTIONS_FUNCTION && superTestInstance.single_output_only == 0) {
            ((cester_void)((TestCase*)test_case)->test_void_function)();

        } else if (((TestCase*)test_case)->test_type == CESTER_NORMAL_TEST ||
               ((TestCase*)test_case)->test_type == CESTER_NORMAL_TODO_TEST ||
               ((TestCase*)test_case)->test_type == CESTER_NORMAL_SKIP_TEST) {

            ++superTestInstance.total_tests_count;
        }
    })

    /* before all */
    if (superTestInstance.registered_test_cases->size == 0) {
        for (i=0;cester_test_cases[i].test_type != CESTER_TESTS_TERMINATOR;++i) {
            if (cester_test_cases[i].test_type == CESTER_BEFORE_ALL_TEST && superTestInstance.single_output_only == 0) {
                ((cester_test)cester_test_cases[i].test_function)(superTestInstance.test_instance);
            }
        }
    }
    CESTER_ARRAY_FOREACH(superTestInstance.registered_test_cases, index1, test_case, {
        if (((TestCase*)test_case)->test_type == CESTER_BEFORE_ALL_TEST && superTestInstance.single_output_only == 0) {
            ((cester_test)((TestCase*)test_case)->test_function)(superTestInstance.test_instance);
        }
    })
    
    #ifndef CESTER_NO_TIME
        superTestInstance.start_tic = clock();
    #endif
    cester_run_all_test_iterator(0);
    
    
    return cester_print_result(cester_test_cases, superTestInstance.test_instance);
}

#ifndef CESTER_NO_MAIN
int main(int argc, char **argv) {
    return CESTER_RUN_ALL_TESTS(argc, argv);
}
#endif

#ifndef CESTER_NO_SIGNAL
void cester_claim_signals() {
    signal(SIGINT , cester_recover_on_signal);
    signal(SIGABRT , cester_recover_on_signal);
    signal(SIGILL , cester_recover_on_signal);
    signal(SIGFPE , cester_recover_on_signal);
    signal(SIGSEGV, cester_recover_on_signal);
    signal(SIGTERM , cester_recover_on_signal);
}

/* This is still faulty it works for SIGSEGV 
but SIGINT just crash to my face. So I will 
manually try to recover the test instead of using 
longjmp and setjmp which is behaving 
inconsistently. This still messes up for more 
than 2 crashes 
 */
void cester_recover_on_signal(int sig_num) {
    cester_claim_signals();
    switch (sig_num) {
#ifndef CESTER_NO_MEM_TEST
        case SIGILL:
            superTestInstance.current_execution_status = CESTER_RESULT_MEMORY_LEAK;
            break;
#endif
        case SIGSEGV:
            superTestInstance.current_execution_status = CESTER_RESULT_SEGFAULT;
            break;
        case SIGINT: /* this is one crazy kill signal */
            if (superTestInstance.isolate_tests == 1) {
                return;
            }
            superTestInstance.current_execution_status = CESTER_RESULT_TERMINATED;
            cester_report_single_test_result(superTestInstance.current_execution_status, superTestInstance.current_test_case);
            cester_run_all_test_iterator(0);
            exit(cester_print_result(cester_test_cases, superTestInstance.test_instance));
            break;
        case SIGFPE:
        case SIGTERM:
        case SIGABRT:
            superTestInstance.current_execution_status = CESTER_RESULT_FAILURE;
            break;
    }
    longjmp(buf, 1);
    
}
#endif

/* CesterArray */

static __CESTER_INLINE__ unsigned cester_array_init(CesterArray** out) {
    void **buffer;
    CesterArray* array_local = (CesterArray*) malloc(sizeof(CesterArray));
    if (!array_local) {
        return 0;
    }
    array_local->size = 0;
    array_local->capacity = CESTER_ARRAY_INITIAL_CAPACITY;
    buffer = (void**) malloc(sizeof(void*) * array_local->capacity);
    if (!buffer) {
        free(array_local);
        return 0;
    }
    array_local->buffer = buffer;
    *out = array_local;
    return 1;
}

static __CESTER_INLINE__ unsigned cester_array_add(CesterArray* array, void* item) {
    void** new_buffer;
    if (array->size >= array->capacity) {
        if (array->capacity >= CESTER_ARRAY_MAX_CAPACITY) {
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), "Max managable memory allocation reached, cannot expand array. Further Memory test disabled.\n");
            superTestInstance.mem_test_active = 0;
            return 0;
        }
        array->capacity = array->capacity + CESTER_ARRAY_INITIAL_CAPACITY;
        new_buffer = (void**) malloc(sizeof(void*) * array->capacity);
        if (!new_buffer) {
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), "Failed to expand the memory allocation array. Further Memory test disabled.\n");
            superTestInstance.mem_test_active = 0;
            return 0;
        }
        memcpy(new_buffer, array->buffer, array->size * sizeof(void*));
        free(array->buffer);
        array->buffer = new_buffer;
    }
    array->buffer[array->size] = item;
    ++array->size;
    return 1;
}

static __CESTER_INLINE__ void* cester_array_remove_at(CesterArray* array, unsigned index) {
    void* item = array->buffer[index];
    if (index != array->size - 1) {
        unsigned block_size = (array->size - 1 - index) * sizeof(void*);
        memmove(&(array->buffer[index]),
                &(array->buffer[index + 1]),
                block_size);
    }
    return item;
}

/* Memory leak Detection procedures */

#ifndef CESTER_NO_MEM_TEST

static __CESTER_INLINE__ void* cester_malloc(unsigned size, const char *file, unsigned line, const char *func) {
    void* p;
    const char* actual_function_name;
#ifndef __CESTER_STDC_VERSION__
    if (superTestInstance.current_test_case != NULL) {
        actual_function_name = superTestInstance.current_test_case->name;
    } else {
        actual_function_name = func;
    }
#else 
    actual_function_name = func;
#endif
    if (superTestInstance.mem_test_active == 1) {
        if (superTestInstance.mem_alloc_manager == NULL) {
            if (cester_array_init(&superTestInstance.mem_alloc_manager) == 0) {
                if (superTestInstance.output_stream==NULL) {
                    superTestInstance.output_stream = stdout;
                }
                CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), "Unable to initialize the memory management array. Memory test disabled.\n");
                superTestInstance.mem_test_active = 0;
            }
        }
    }
    p = malloc(size);
    if (superTestInstance.mem_test_active == 1) {
        AllocatedMemory* allocated_mem = (AllocatedMemory*) malloc(sizeof(AllocatedMemory));
        allocated_mem->line_num = line;
        allocated_mem->allocated_bytes = size;
        if (cester_str_after_prefix(actual_function_name, (char*) "cester_test_", 12, (char **) &(allocated_mem->function_name)) == 0) {
            allocated_mem->function_name = actual_function_name;
        }
        allocated_mem->file_name = file;
        cester_ptr_to_str(&allocated_mem->address, p);
        if (cester_array_add(superTestInstance.mem_alloc_manager, allocated_mem) == 0) {
            CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), "Failed to register allocated memory. Memory test disabled.\n");
            superTestInstance.mem_test_active = 0;
        }
    }
    return p;
}

static __CESTER_INLINE__ void cester_free(void *pointer, const char *file, unsigned line, const char *func) {
    unsigned index;
    const char* actual_function_name;
#ifndef __CESTER_STDC_VERSION__
    if (superTestInstance.current_test_case != NULL) {
        actual_function_name = superTestInstance.current_test_case->name;
    } else {
        actual_function_name = func;
    }
#else 
    actual_function_name = func;
#endif
    if (pointer == NULL) {
        if (superTestInstance.mem_test_active == 1 && superTestInstance.current_test_case != NULL) {
            cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "InvalidOperation ");
            cester_concat_str(&(superTestInstance.current_test_case)->execution_output, (superTestInstance.minimal == 0 ? superTestInstance.test_file_path : cester_extract_name(superTestInstance.test_file_path) ));
            cester_concat_str(&(superTestInstance.current_test_case)->execution_output, ":");
            cester_concat_int(&(superTestInstance.current_test_case)->execution_output, line);
            cester_concat_str(&(superTestInstance.current_test_case)->execution_output, ": ");
            cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "in '");
            cester_concat_str(&(superTestInstance.current_test_case)->execution_output, (superTestInstance.current_test_case)->name);
            cester_concat_str(&(superTestInstance.current_test_case)->execution_output, "' => Attempting to free a NULL pointer \n");
            superTestInstance.current_execution_status = CESTER_RESULT_MEMORY_LEAK;
        }
        return;
    }
    if (superTestInstance.mem_test_active == 1) {
        char* address;
        cester_ptr_to_str(&address, pointer);
        CESTER_ARRAY_FOREACH(superTestInstance.mem_alloc_manager, index, alloc_mem, {
            if (cester_string_equals(((AllocatedMemory*)alloc_mem)->address, address) == 1) {
                if (!cester_array_remove_at(superTestInstance.mem_alloc_manager, index)) {
                    CESTER_DELEGATE_FPRINT_STR((CESTER_FOREGROUND_YELLOW), "Memory allocation array corrupted. Further Memory test disabled.\n");
                    superTestInstance.mem_test_active = 0;
                }
                free(alloc_mem);
                --superTestInstance.mem_alloc_manager->size;
                break;
            }
        })
    }
    free(pointer);
}

#define malloc(x) cester_malloc( x, __FILE__, __LINE__, __FUNCTION__) /**< Override the default malloc function for mem test */
#define free(x) cester_free( x, __FILE__, __LINE__, __FUNCTION__)     /**< Override the default free function for mem test   */
#endif

#ifdef __cplusplus
}
#endif

#endif
