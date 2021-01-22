# Bloom Brackets

Bloom brackets is an internal scripting solution for storing user defined behaviours.
It functions as a scripting language without the need of a parser or tokenizer to do its work.

The language is baded around arrays to hold the scripting structure. There are only a couple of rules for bloom brackets to be writte:

- An array is considered a code block when its first element doesn't contain a string.
- An array which its first element is a string is considered an expression and it can be though of as a function call.

Here is an example of an IF THEN ELSE statement:

```json
[
	["IF", ["==", 1, 1],
		[
			["print", "true"]
		],
		[
			["print", "false"]
		]
	]
]
```

The key take aways from this example is that every expression is a function. This means that extending the scripting features is as simple as adding more commands.

For example the "print" statement on the above example could be implemented as follows:

```python
context["#CALLS']["print"] = lambda args, ctx: print(*args)
```

Notice the context argument passed to the lambda that implements the "print" statement. Bloom brackets holds a global context while running a script. All variables and functions are stored here and available for any commands/statements to use for their implementations.
## Expression

```
["SET", "myvar", "myvalue"]
   ^       ^         ^
   |       |         +-- Second argument
   |       +-- First argument
   +-- The expression command

```

## Block

```python
[
  # first statement in the block
  ["SET", "myvar", "myvalue"],
  # second statement in the block
  ["SET", "myvar", "myvalue"],
  # third statement in the block
  ["SET", "myvar", "myvalue"],
  # forth statement in the block
  ["SET", "myvar", "myvalue"],
  # etc...
  ...
]
```

## Built in commands

### IF THEN ELSE

The IF statement executes conditional code based on a value of boolean expression.

|Argument|Type|Description|
|:-|:-:|:-|
|condition|boolean|A boolean value which will trigger code execution on the true or false branches|
|then|block|A sub script which runs if the condition resolves to true|
|else|block|A sub script which runs if the condition resolves to false|

```python
["IF", 
  # Condition
  true, 
  # Then
  ["print", true], 
  # Else
  ["print", false]
]
```
### SET

The set statement both defines and assigns a value to variable.

|Argument|Type|Description|
|:-|:-:|:-|
|variable|string|The variable name|
|value|any|The variable value|

```python
["SET", 
  # variable
  "myvar", 
  # value
  "myvalue"
]
```

