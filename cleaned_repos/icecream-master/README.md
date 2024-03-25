# IceCream — Never use print() to debug again

Do you ever use `print()` or `log()` to debug your code? Of course you
do. IceCream, or `ic` for short, makes print debugging a little sweeter.

`ic()` is like `print()`, but better:

  1. It prints both expressions/variable names and their values.
  2. It's 60% faster to type.
  3. Data structures are pretty printed.
  4. Output is syntax highlighted.
  5. It optionally includes program context: filename, line number, and
     parent function.

IceCream is well tested, [permissively licensed](LICENSE.txt), and
supports Python 2, Python 3, PyPy2, and PyPy3.