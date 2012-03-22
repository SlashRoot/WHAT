.. SlashRoot WHAT documentation master file, created by
   sphinx-quickstart on Mon Jun  6 15:57:28 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SlashRoot WHAT documentation
==========================================

The SlashRoot WHAT (Whole House Automation Thing) is designed with two general purposes in mind:

*1. To facilitate the entire automation of SlashRoot business processes, including but by no means limited to accounting, sales, marketing, managing our contacts,
facilitating actual communication (phone, email, SMS, and more), scheduling, power consumption, our website, our network, and so on.

*2. To provide services at various layers to our members, subscribers, clients, and really everybody who has anything to do with SlashRoot.

In particular, we have visualized a barter-driven e-commerce platform that can act as a sort of local currency for New Paltz.

The WHAT is written primarily in Python using the Django framework.  
The search engine is based on Solr, which is written in Java.
The deployment modules use Twisted's WSGI container, which is also written in Python.
The 'push' functionality uses Orbited, which is part of Twisted, and Stomp, an implementation of MorbidQ.

The WHAT is divided up into "apps" - python modules that generally conform to Django conventions.  
The apps are not atomized into independent functions; rather, they are an inter-dependent set of divisions of labor.

The major WHAT apps and their roles
===================================

================   ==================================
App Name           Module Docstring (from __init__.py)
================   ==================================
**accounting**     .. automodule:: accounting
**comm**           .. automodule:: comm
**cms**			   .. automodule:: cms
**commerce**	   .. automodule:: commerce
**contact**		   .. automodule:: contact
**do**			   .. automodule:: do
**hwtrack**		   .. automodule:: hwtrack
**main**		   .. automodule:: main
**meta**		   .. automodule:: meta
**mooncalendar**   .. automodule:: mooncalendar
**people**		   .. automodule:: people
**pigs**		   .. automodule:: pigs
**pos**			   .. automodule:: pos
**power**		   .. automodule:: power
**presence**	   .. automodule:: presence
**products**	   .. automodule:: products
**push**		   .. automodule:: push
**service**		   .. automodule:: service
**social**		   .. automodule:: social
**utility**		   .. automodule:: utility
================   ==================================

Other (less major) apps
=======================

================   ==================================
App Name           Description (not dynamic)
================   ==================================
**checklist**      An app to cover checklists.  Very primitive.  Can probably be tossed or merged with do.
**dajax**          A third-party app designed to facilitate ajax functionality.
**dajaxice**       Handlers to mediate between javascript frameworks and dajax.
**donald**         Our math app.  Once in a while we get REALLY high and do math with Donald Silberger.
**haystack**       A third-party app delivering modular search for Django.
================   ==================================


   
   