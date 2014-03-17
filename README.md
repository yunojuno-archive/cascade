Django-Cascade
==============

Test Django project used to explore transaction handling in model deletions.

There has been some discussion within the YunoJuno development team about
the use of signals within the Django model ORM framework, whether it's
good practice, or even safe.

The primary use case is the cascading deletion of models, and how this is
handled internally by the Django ORM. An initial investigation of the Django
source suggested that when calling the `delete()` method of a top-level
object (one that is a parent of a child object), the child's `delete` method
is never called, but its `pre_save` and `post_save` signals are. This
project is a test app used to explore this in more detail.

It consists of a simple Django app with two models - Parent, and Child.
The Child model has a ForeignKey relationship to the Parent model. There
are `pre_save` and `post_save` signal receive handlers for both models.

In both `pre_save` handlers, if the `name` attribute of the model is "Job"
an exception is raised. This is used to force the rollback of any containing
transactions, so that, in theory, if you call `parent.delete()` on a Parent
object that has a Child object with `name=="Job"`, the entire transaction
will rollback to its original state.

In addition to the test coverage, each method contains verbose logging
that can be used to highlight the methods being run at any time.

The suggested test verbosity is '2', e.g.

```bash
$ python manage.py test --verbosity=2
```

##Spoiler

This is the output from calling `delete()` on an object with four child objects:

    DEBUG Enter Parent.delete() method.
    DEBUG Deleting Child object, id=1.  # pre_save
    DEBUG Deleting Child object, id=2.
    DEBUG Deleting Child object, id=3.
    DEBUG Deleting Child object, id=4.
    DEBUG Deleting Parent object, id=1.
    DEBUG Deleted Child object, id=#4.  # post_save
    DEBUG Deleted Child object, id=#3.
    DEBUG Deleted Child object, id=#2.
    DEBUG Deleted Child object, id=#1.
    DEBUG Deleted Parent object, id=#1.
    DEBUG Exit Parent.delete() method.

##Prerequisites

There is a `requirements.txt` file that contains the project dependencies.

**NB** `psycopg2` is only required when running the tests agains a Postgres
database - which is recommended because of the transactional support (given
that that is the whole point of the project). However, you can run the tests
against SQLite if you wish (database settings just need to the uncommented).
