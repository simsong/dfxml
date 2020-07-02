# Does GCC have the diagnostic pragma?
AC_TRY_COMPILE([#pragma GCC diagnostic ignored "-Wredundant-decls"],
    	       [],
	       AC_DEFINE([DFXML_GNUC_HAS_DIAGNOSTIC_PRAGMA],[1],[GCC supports #pragma GCC diagnostic]),
	       )

# Does GCC have the diagnostic pragma ignored -Wshadow?
AC_TRY_COMPILE([#pragma GCC diagnostic ignored "-Wshadow"],
    	       [],
	       AC_DEFINE([DFXML_GNUC_HAS_IGNORED_SHADOW_PRAGMA],[1],[GCC supports #pragma GCC diagnostic ignored -Wshadow]),
	       )

# Does GCC have the diagnostic pragma ignored -WunusedVariable?
AC_TRY_COMPILE([#pragma GCC diagnostic ignored "-Wunused-variable"],
    	       [],
	       AC_DEFINE([DFXML_GNUC_HAS_IGNORED_UNUSED_VARIABLE_PRAGMA],[1],[GCC supports #pragma GCC diagnostic ignored -Wunused-variable]),
	       )

# Does GCC have the diagnostic pragma ignored -Wunused-label?
AC_TRY_COMPILE([#pragma GCC diagnostic ignored "-Wunused-label"],
    	       [],
	       AC_DEFINE([DFXML_GNUC_HAS_IGNORED_UNUSED_LABEL_PRAGMA],[1],[GCC supports #pragma GCC diagnostic ignored -Wunused-label]),
	       )



