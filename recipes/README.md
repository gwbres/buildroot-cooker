recipe
======

Contains all known recipes

recipe architecture
===================

This is the basic architecture to follow for one recipe

+ recipes/$recipe/$recipe_defconfig : recipe minimum configuration file
+ recipes/$recipe/overlay : optionnal recipe rootfile system overlay
+ recipes/$recipe/post-image : optionnal post-image task to run once recipe compilation has completed 
+ recipes/$recipe/post-build : optionnal post-build task to run once recipe has been built 
+ recipes/$recipe/patches : buildroot global patch directory for given recipe
+ recipes/$recipe/uboot-fragments : optionnal recipe uboot fragments file 
+ recipes/$recipe/linux-fragments : optionnal recipe uboot fragments file 
+ recipes/$recipe/\* : all other recipe specific files, might not be integrated

minimal recipe definition
=========================

Single board recipe : to be declined on a single platform:

Multi platform recipe : to decline on several platforms at once:

recipes hooks
=============

TODO
