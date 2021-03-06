#ifndef PY_STATICS_H
#define PY_STATICS_H

typedef struct _statics {
    PyObject *empty;                                  /* ""                   */
    PyObject *nul;                                    /* "\0"                 */
    PyObject *comma;                                  /* ","                  */
    PyObject *space;                                  /* " "                  */
    PyObject *tab;                                    /* "\t"                 */
    PyObject *cr;                                     /* "\r"                 */
    PyObject *lf;                                     /* "\n"                 */

    PyObject *comma_space;                            /* ", "                 */

    PyObject *s_true;                                 /* "true"               */
    PyObject *s_false;                                /* "false"              */
    PyObject *s_null;                                 /* "null"               */

    PyObject *nan;                                    /* "NaN"                */
    PyObject *infinity;                               /* "Infinity"           */
    PyObject *neg_infinity;                           /* "-Infinity"          */

    PyObject *open_dict;                              /* "{"                  */
    PyObject *close_dict;                             /* "}"                  */
    PyObject *empty_dict;                             /* "{}"                 */
    PyObject *ellipsis_dict;                          /* "{...}"              */

    PyObject *open_array;                             /* "["                  */
    PyObject *close_array;                            /* "]"                  */
    PyObject *empty_array;                            /* "[]"                 */
    PyObject *ellipsis_array;                         /* "[...]"              */

    PyObject *open_tuple;                             /* "("                  */
    PyObject *close_tuple;                            /* ")"                  */
    PyObject *empty_tuple;                            /* "()"                 */
    PyObject *ellipsis_tuple;                         /* "(...)"              */
    PyObject *comma_close_tuple;                      /* ",)"                 */
} PyStatics;

PyAPI_DATA(PyStatics) statics;

int _init_statics();

/* If PyObject *o is a static object, return 1, else, return 0.  Index the
 * static was found is written to `index` if non-NULL. */
PyAPI_FUNC(int) _Py_IsStatic(PyObject *o, int *index);

PyAPI_FUNC(PyObject *) Py_Static(PyObject *);

#define Py_STATIC(n) (Py_INCREF(statics.##n), statics.##n)

#endif /* PY_STATICS_H */
