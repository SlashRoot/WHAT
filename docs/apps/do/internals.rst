Do Module Internals
================

=====
Verbs
=====
Verb objects are action words we use to classify the things we do.

Ideally, they'll be brief and we'll have only a few of them.

Likely examples include "Maintain," "Build," "Develop," "Promote," "Repair," "Triage."

Naturally, each Verb will have a spectrum of difficulty and access in Tasks.

Also, some Verbs, such as "Triage," obviously require generally higher authority.  

======================
TaskPrototype and Task
======================
A **TaskPrototype** is the boilerplate from which Task objects are made.  It has unique information about the task, such as Name and Description.

Some TaskPrototypes, such as "Sweep the Floor," will have hundreds of Task objects associated with them.

A **Task** is a discrete, one-time action.  It is created at a particular DateTime (typically *generated* from a TaskPrototype) and completed at a particular DateTime.

Others, such as "Turn the stage into storage," may have one task in its lifetime.

TaskPrototype objects can never be changed once created; this would corrupt the integrity of the task objects which rely on them for name and description.
Instead, they evolve.  TaskPrototypes have a ManyToMany relationship with their evolutionary ancestors and descendents, ie, a single TaskPrototype might split into several, or many might merge into one.

-------------
Task families
-------------
Many tasks have smaller, "child" tasks that need to be completed as part of the completion of the larger, "parent" task.

This relationship is handled by the model TaskProgeny:

.. autoclass:: do.models.TaskProgeny


TaskPrototype objects use TaskPrototypeProgeny in exactly the same way.

------------------------------------
Generating Tasks from TaskPrototypes
------------------------------------

TaskPrototype has a method, .generate_task(), which creates a Task (in fact an entire Task family) whose prototype property points to the prototype in question. 

.. automethod:: do.models.TaskPrototype.generate_task

In order to create the entire Task family, TaskPrototype.generate_task() iterates through .children.all().

--------------------------------------------------
Categorizing TaskPrototype objects by Verb and Tag
--------------------------------------------------

Tasks are categorized in two ways, but Verb and Tag.  Verbs are very broad, mutually exclusive categories.  Tags are more specific and direct designations.

 * Every Task has one Verb ("Maintain," "Promote," "Develop," "Repair," etc.)
 * Tasks can have one or more tasks ("Tech Service," "Cleaning," "Coffee Bar Stuff," etc.)
 


=======================
Automatic Task Creation
=======================
Every 10 minutes, a cronjob runs the management command **task_generator**.

---------------
Task Generators
---------------
The TaskGenerator model is 

^^^^^^^^^^^^^^^^
Random Recurring
^^^^^^^^^^^^^^^^
.. autoclass:: do.models.RandomRecurringTaskGenerator
When task_generator is run, each RandomRecurringTaskGenerator is iterated through.  

RandomRecurringTaskGenerator has a property, frequency, which is used to determine the likelihood of it being added to the Task queue.

If it is chosen, the  TaskPrototype, .generate_task() is run.