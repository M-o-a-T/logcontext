"""
The `logcontext` module helps to solve the following problem:

You have an async program. It does lots of things in parallel.
You don't really know what's happening. Then you get a deadlock,
or a cancellation whose initial trigger is masked by another error
or an unprotected async call within a `finally:` block.

You now have no idea what's happening, and low-level instrumentation
of your code causes the error to get lost in the noise.

Here's how `logcontext` can help.

First, wrap your main code::

	from logcontext import main_context
	def main():
		with main_context():
			... # whatever your program does
	
Then you wrap each possibly-interesting block, nursery, async context, …
with

	from logcontext import context_of
	...
	async def code_of_interest(arg):
		with context_of("interesting: %s", arg) as ctx:
		    ... # start some subtask

			# display what my subcontexts are doing, if anything
			ctx.log_tree()  


Text and positional arguments will be passed to `logging.log`.

Reporting on the current state of your code is then as easy as::

	from logcontext import log_backtrace, log_tree

	...
	log_tree()  # reports the whole program's context tree
	log_backtrace()  # reports the contexts leading to the current code

Both `context_of` and `log_tree` accept a log level. This way you can
selectively attach higher log levels to possibly-interesting code.
"Uninteresting" subtrees are skipped.

"""

from ._main import main_context, context_of, log_backtrace, log_tree
