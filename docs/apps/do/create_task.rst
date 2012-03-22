Creating Tasks
==============
If you have task creation privileges, a plus sign will appear near "Tasks" in the heading.

When you click the plus sign, a modal will appear with a TaskForm.

Fill out the following fields:

 * Name (autocompletes against existing TaskPrototype objects)
 * Whether or not it's already complete (boolean)
 * If it is not complete, projected completion date
 * If it is complete, date completed (or will we assume 'now' as the completed date?  Is the task truly completed if it is not marked 'complete?')
 * People who have some authority over this task
 * People who have some interest in this task

==============================================
Create just a new Task or a new TaskPrototype?
==============================================
When you autocomplete the name field and successfully find an existing TaskPrototype, the border of the modal will do something to indicate this, the description will populate, and the ID of the TaskPrototype will be displayed at the top.

The ID of the TaskPrototype will be displayed as a link.  You can click it to be taken to the profile page for the TaskPrototype.

If you modify the name or description, a pre-clicked checkbox will appear prompting you to **evolve** the TaskPrototype object (this is the recommended course of action).

=========================================
Creating Parent, Child, and Sibling Tasks
=========================================
Beneath the form, three plus signs will allow the creation of parent, child, and sibling Tasks.

By clicking the plus sign, an additional TaskForm will appear below and slightly indented the parent TaskForm.

Click "Save" to save the task.  Any validation errors will appear as red borders around the respective fields.

Saved tasks will have a green border.

Once you are finished, you can close the modals.

Evolving TaskPrototypes
=======================
If you autocomplete against a name or description that is close to your desire but not exact, you can *evolve* the TaskPrototype to match your needs.

