# Parrot

Parrot is a tool for faking command line tools for testing scripts that depend
on command line tools to do their work, but don't want to execute, or can't
rely on proper behavior during testing.

This is accomplished by placing Parrot, renamed or symlinked to the command you
want to fake, ahead of the real command in the PATH. Parrot will then compare
how it is called to a specified list of behaviors and will report to stderr and
stdout what is defined in the proper behavior.

Parrot will look for the file that contains the behaviors it can fake first if
the environment variable "PARROT_BEHAVIORS_FILE" is set it will use the file
given. If the environment variable is not set then Parrot will look in the
directory where Parrot is located for a file named: "parrot_behaviors" If
either file doesn't exist Parrot will throw a "ParrotMissingBehaviorFile"
exception. Parrot will not fall back to the parrot_behaviors file if
PARROT_BEHAVIORS_FILE is not set. This is because Parrot cannot properly report
any issues since stdout and stderr are used by behaviors. Any error reporting
done there could be mistaken as output for the expected behavior.


## Why use Parrot?

Parrot was conceived because of issues I've had trying to properly test bash
scripts. It is an unfortunate, but also desirable, fact of life that running a
command in a script causes side effects such as creating files, opening sockets,
changing state of a machine. This is, after all, what you want the scripts to do
in production. However, it is also very useful to do dry runs of scripts to make
sure that logic is correct without accidentally running commands like
"rm -rf $temp_install/bin" only to find out temp_install hasn't been set making
the command be run as "rm -rf /bin". Which could be disasterous if run with admin
privileges. Of course you could make your own dry run option and wrap every
command with some logic to not run the command. But, if you rely on some output
from the command, an exit code, stdout, etc. you now have to provide that logic
with your dry run option which can make your script hard to write and even harder
to read later when you need to make changes.

Parrot seeks to solve this by moving the dry run logic outside your script and
onto the PATH by making false commands you can call instead and that will
provide some user defined expected behavior so your script can still rely on
this for its operation. This should allow your script to skip a dry run option
and just define the necessary commands through Parrot making yor script easier
to maintain while, hopefully, making it easier to test at the same time.

Despite the fact that Parrot was intended for bash script testing, since it
just replaces executables on the PATH it should be usable in the same way by
any language that can call other programs.


## Behaviors

Parrot behaviors are defined in a JSON file that will be provided to Parrot
either by an environment variable or a file located adjacent to the command(s)
that are being parroted.

The parrot behaviors file can be given by the environment variable:  
**PARROT_BEHAVIORS_FILE** which should be the path to your behaviors file. If
you intend to use multiple behavior files for your testing this is the
preferred method of setting the behaviors file.

You can also provide a file called **parrot_behaviors** which is located in 
the same directory as the command(s) you are parroting and not where parrot.py
may exist.

This JSON file should take the form:

    [
      {"command": <command>,
       "args": [<arg1>, <arg2>, ...],
       "stdout": <expected output for stdout>,
       "stderr": <expected output for stderr>,
       "return_code": <expected return code>
      },
      ...
    ]

Where:
|Key         | Meaning |
-------------|---------|
|command     | Is the name of the program you want to "parrot". Eg. ls, awk, cat. |
|args        | Is the full set of arguments expected for command as a JSON list. |
|stdout      | Is the output command should "parrot" back. |
|stderr      | Is the output command should "parrot" back on the stderr stream. |
|return_code | Is the expected exit code from command. |

Parrot uses the command and args to create a unique id which it will then use
to find the unique behavior to mimic when it is run. Because some programs care
about the order of arguments (such as find) Parrot necessarily has to care as
well. Which means Parrot will need to be called exactly as the behavior is
defined for it to work. See the limitations for a detailed explanation.

Example behaviors file can be found in tests/integration/parrot_behaviors.*

### Behavior Limitations

The order of arguments is important to how Parrot determines which behavior to
mimic. This is because a single command could have multiple ways of being used
that would behave differently and could easily be in the same behaviors file.
However, there are many commands where the order of arguments is unimportant to
its behavior. For example the commands "ls -lh", "ls -hl", and "ls -l -h" all 
produce exactly the same output if run as their true programs. In Parrot,
however, these are all unique behaviors. This means if you want to call the same
parroted command multiple times in your script you will need to make sure that
the arguments are provided the same way each time, or provide behaviors for each
way that you will call the command.

Aliases could cause Parrot to become confused. This too is a side effect of the
way Parrot determines unique behaviors. All arguments passed are used to
determine the correct behavior, including arguments that are added by aliases.
For example a very common alias is "ls=ls --color=auto" which could make the
command "ls -lh" in your script actually be "ls --color=auto -lh" be called by
the system. The later is what Parrot will see.

Some common "commands" can often be both a program and a builtin for a scripting 
language. The best example of this is "echo." It is very difficult to use Parrot
for these commands as the builtin will usually take precedent over the program
on the PATH. You can get around this by using a fully qualifed path to the
command, however, this makes it very difficult to then have Parrot replace that
command since you can no longer rely on path resolution to pick Parrot over the
real command.

Be aware that most systems rely on the commands on the system too. This can lead
to situations where you may want to parrot a command that is relied on by the
system in a way you need the system to work. This can be a complex situation to
resolve and there is no good generic solution that I can offer.


## How to Use Parrot

1. Install "parrot.py" somewhere in your source repository that makes sense for
your build/test system. Where parrot.py is installed will not affect its
operation, but it is recommended to install and distribute it with your tests.
2. Create symlinks to parrot.py for each of the commands you want to replace
during testing. You can link multiple commands to the same parrot.py without
worrying about the various commands interfering with each other. This is
because all of the information about what to do is located in a behaviors file
which can contain as many behaviors as you want. You can also use multiple
behavior files if you wish, but you will have to manage when to change behavior
files through the environment variable **PARROT_BEHAVIORS_FILE**
3. Your tests should set the environment **PATH** variable such that the
symlinked commands are in front of their real counterparts. This will allow
Parrot to override the real command.


## License
Parrot uses the 3 clause BSD license. You can find the full text in license.txt.

