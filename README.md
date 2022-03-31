buildroot-cooker
================

This is a command line interface to enhance `buildroot` for complex
recipes.

It combines the `BR_EXTERNAL` approach, which is an upper layer 
of `buildroot` and a wrapper to operate `buildroot.

With the `br-external` feature, we can enhance buildroot with custom packages
that are not officially supported.  

With the provided `cooker` wrapper, we operate a buildroot according to a
`recipe` descriptor to build an image on several architectures.  
By default, buildroot approach is one Buildroot per Architecture.   
With this wrapper we can build one buildroot for multiple architectures.

### Getting started

Set up environment
```shell
╰─$ source sourceme.sh 
```

`cooker` is the command line tool

List all recipes
```shell
╰─$ cooker --list
```

List known architectures
```shell
╰─$ cooker --list-boards
```

Cook a recipe:
```shell
╰─$ cooker --recipe my-recipe
```

Cook several recipes at once:
```shell
╰─$ cooker --recipe recipe1 --recipe recipe2 
```

### Build management

All requirements are downloaded and managed in
arbitrary ~/br2-downloads folder.  
Use the `dl-dir` option if you want to use a different location :

```shell
╰─$ cooker --dl-dir /tmp --recipe recipe1 
```

Maintaining dl-dir folder accross cooking sessions, 
allows faster cooking processes.

All temporary and build results are created where `cooker` is
summoned but you can change that behavior with the `work-dir` option:
```shell
╰─$ cooker --work-dir /tmp --dl-dir /tmp --recipe recipe1 
```

Print buildroot revision to be used :
```shell
╰─$ cooker --br2-revision
```

### Developments and special opmodes 

+ Test a newer buildroot revision with

```shell
╰─$ cooker --br2-tag 2020.01.1 --recipe my-recipe
```

+ use specific buildroot tree
```shell
╰─$ cooker --br2-url https://custom-buildroot.git --recie my-recipe
```
