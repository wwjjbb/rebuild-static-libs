# rebuild-static-libs
Find and rebuild all packages with static libraries (Gentoo)

```
usage: rebuild-static-libs.py [-h] [-a] [-p] [-P]

Remerge packages containing static libraries

optional arguments:
  -h, --help     show this help message and exit
  -a, --ask      Stop and ask before starting emerge
  -p, --pretend  Just pretend, do not carry out any builds
  -P, --pump     Use pump (distcc)
```
## Problems

It's not good with packages that have been masked or gone away. You need to deal with
these manually.

You can either carefully unmerge such packages, or edit the generated emerge command
to remove them from the list.



