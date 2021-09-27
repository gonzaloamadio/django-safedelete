Django safedelete
=================

.. image:: https://github.com/makinacorpus/django-safedelete/workflows/Python%20application/badge.svg
    :target: https://github.com/makinacorpus/django-safedelete/actions?query=workflow%3A%22Python+application%22

.. image:: https://coveralls.io/repos/makinacorpus/django-safedelete/badge.png
    :target: https://coveralls.io/r/makinacorpus/django-safedelete

Why this fork?
------------

This fork is modified son it can be used in a database where safe delete models may be represented with two fields:
a boolean field and a datetime field.

The scenario where there is a boolean field can be because you have created indexes on this field at the database
and would like to continue using them.

So, if this is the case, you can configure this repo to do so. Check comments on `config.py` file.

There is also an extra delete/undelete logic added. See section `delete/undelete logic` in this README
for more information.

What is it ?
------------

For various reasons, you may want to avoid deleting objects from your database.

This Django application provides an abstract model, that allows you to transparently retrieve or delete your objects,
without having them deleted from your database.

You can choose what happens when you delete an object :
 - it can be masked from your database (soft delete, the default behavior)
 - it can be masked from your database and mask any dependent models. (cascading soft delete)
 - it can be normally deleted (hard delete)
 - it can be hard-deleted, but if its deletion would delete other objects, it will only be masked
 - it can be never deleted or masked from your database (no delete, use with caution)


Example
-------

.. code-block:: python

    # imports
    from safedelete.models import SafeDeleteModel
    from safedelete.models import HARD_DELETE_NOCASCADE

    # Models

    # We create a new model, with the given policy : Objects will be hard-deleted, or soft deleted if other objects would have been deleted too.
    class Article(SafeDeleteModel):
        _safedelete_policy = HARD_DELETE_NOCASCADE

        name = models.CharField(max_length=100)

    class Order(SafeDeleteModel):
        _safedelete_policy = HARD_DELETE_NOCASCADE

        name = models.CharField(max_length=100)
        articles = models.ManyToManyField(Article)


    # Example of use

    >>> article1 = Article(name='article1')
    >>> article1.save()

    >>> article2 = Article(name='article2')
    >>> article2.save()

    >>> order = Order(name='order')
    >>> order.save()
    >>> order.articles.add(article1)

    # This article will be masked, but not deleted from the database as it is still referenced in an order.
    >>> article1.delete()

    # This article will be deleted from the database.
    >>> article2.delete()


Compatibilities
---------------

* Branch 0.2.x is compatible with django >= 1.2
* Branch 0.3.x is compatible with django >= 1.4
* Branch 0.4.x is compatible with django >= 1.8
* Branch 0.5.x is compatible with django >= 1.11
* Branch 1.0.x is compatible with django >= 2.2

Current branch (1.0.x) is tested with :

*  Django 2.2 using python 3.5 to 3.9.
*  Django 3.0 using python 3.6 to 3.9.
*  Django 3.1 using python 3.6 to 3.9.
*  Django 3.2 using python 3.6 to 3.9.


Installation
------------

Installing from pypi (using pip). ::

    pip install django-safedelete


Installing from github. ::

    pip install -e git://github.com/makinacorpus/django-safedelete.git#egg=django-safedelete

Add ``safedelete`` in your ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        'safedelete',
        [...]
    ]


The application doesn't have any special requirement.


Configuration
-------------

In the main django settings you can activate the boolean variable ``SAFE_DELETE_INTERPRET_UNDELETED_OBJECTS_AS_CREATED``.
If you do this the ``update_or_create()`` function from django's standard manager class will return ``True`` for
the ``created`` variable if the object was soft-deleted and is now "revived".

By default, the field that indicates a database entry is soft-deleted is ``deleted``, however, you can override the field name
using the ``SAFE_DELETE_FIELD_NAME`` setting.

Some databases also uses a boolean field. There is an option to use this as well. If you would like to use this field, set
to `True` the flag `HAS_BOOLEAN_FIELD` in the `config.py` file.
And set the name for the field in your settings if required with the variable `BOOLEAN_FIELD_NAME`. Default is `is_deleted`

NOTE:
The original package internally only used the datetime field. Boolean field would work for cases
where you have a legacy DB and need to have both fields.
In this fork, we have changed the filters and lookups to use the boolean field if it is defined. Why? Because you may prefer
indexes on a boolean field rather than on a datetime field.

By default, if you do not configure anything in the settings of the project where you install this repo, a datetime field
called `deleted` will be used.

If you would like to use a boolean field and would like also to use it to filter deleted items, you can configure this
in the settings of the project where you install this repo:

.. code-block:: python
    SAFE_DELETE_HAS_BOOLEAN_FIELD = True
    SAFE_DELETE_BOOLEAN_FIELD_NAME = 'is_deleted'
    SAFE_DELETE_USE_BOOLEAN_FIELD_TO_DO_LOGIC = True


Delete/Undelete logic
-------------------------
In the original repository every time a delete operation is performed, the deleted_at field is set
with the value of timezone.now(). This implies that every element has a different timestamp, and if we want to undo an
undelete, but rolling back only elements that were deleted on the same operation, it would not be possible.

Scenario and original behaviour: Assume we have an element `A` and two elements `B` and `C` that have a FK to `A`, and suppose
we do a delete on element `C`. Now we are going to have element `A` and `B` (pointing to `A`). Now we `delete` `A`,
and that operation will delete `B` as well (cascade deletion). If we `undelete` ` A`, then both `B` and `C` will be
undeleted (as they both have a FK to A).

New requirements:
We would like to modified this behaviour and be able to undelete elements that were deleted within the cascade deletion.

In this package, we have modified the original behaviour to meet the new requirements:
Set same timestamp to all deleted elements in order to rollback in an easy way related deleted elements.

For the undelete, if you want to bypass this check and undelete all related elements use the policy:
`some_object.undelete(force_policy=SOFT_DELETE_CASCADE_ALL)`

Documentation
-------------

The documentation is available `here <http://django-safedelete.readthedocs.org>`_. Generate your own documentation using:

    tox -e docs


Licensing
---------

Please see the LICENSE file.
