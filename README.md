# LiTeX
LiTeX is a lightweight mathematical equation renderer for low-resolution LCDs built in Python or c++ with Arduino (developed for Teensy 4.0). It is similar to CASIO or Texas Instrument's "V.P.A.M" or "MathPrint".

It contains a customizable rendering engine using a LALR (look-ahead, left-to-right, rightmost derivation) parser. The parser accepts a string formatted similarly to LaTeX. There is also an optional 4-wire SPI library if you want to display LiTeX on a monochrome LCD. Currently, it is set up for an ST-7567 display.

There is also a customizable, in-place equation evaluator that evaluates any LiTeX equation into a complex number. The evaluator supports all of the functions included in LiTeX, and also supports implicit multiplication. It can solve single variable equations with x using newton's method. (Solver is currently Python-only)

## LiTeX features:
- Self-resizing parenthesis
- Self-resizing radicals (nth root)
- Self-aligning fraction bars
- Exponents with smaller font
- Variable base log (using subscript) 
- All 6 basic trigonometric functions: sin cos tan sec, etc..
- Inverse trig function of sin, cos, and tan
- Algebreic constants: e, pi, i, x
- Expression Evaluator with implicit multiplication support
- Complex number support with all functions

## Inputting expressions:
Expression syntax differs slightly from regular LaTeX when it comes to a few functions. To make the expression less ambiguous, easier for the parser to understand, and to make the code more lightweight, extra braces are required around a few functions. Functions that are not in this list are the same as in LaTeX.
### Negative sign (python):
Negative sign, which is shorter than the minus operator, can be specified by using the tilde (~). e.g. "~4+3" Using the minus _operator_ in that example ("-4+3") does not yield an error, but it may cause unexpected errors if placed in other parts of the expression. It is best to use the tilde when specifying a negative number.
### Negative sign (c++):
After realizing that the python implementation of negative sign is really bad, the ~ character is only recognized by the rendering engine. It is immediately replaced with - in the evaluator.
### Exponents:
Exponents should look like this when they are inputted into both the renderer and the evaluator. e.g. "a^{b}" Braces are required even if there is only 1 digit in the exponent.
### Subscript:
Like with exponents, braces are required around the contents of the subexpression. e.g. "a_{b}"
### Radicals:
Radicals require the index of the root to be specified in braces before the radicand. e.g. "\sqrt{2}{3}" Renders and evaluates as the square root of 3.
### Trig Functions:
To specify a trigonometric function, just type it out in the expression, followed by a set of parenthesis to indicate the contents. e.g. "sin(3)"
### Inverse Trig Functions:
Inverse trig functions can be specified by adding "^{~1}" after specifying a trig function. e.g "sin^{~1} Default units for trig functions are radians.
### Complex Numbers:
Complex numbers are not specified with the letter i: "4+3i", but rather with the escape sequence "\im". Using "i" will print the letter i, as used in sine, not the imaginary number. e.g. "4+3\im"
### Special constants:
All special constants: pi, e, etc.. require an escape sequence to render and evaluate properly. eg: "\e^{2\im\pi}"

## Example render:
r"1 + \e^{2\pi\im} - (3\sqrt{2}{\frac{sin(4)}{5}log_{6^{2}}(7) * 8} / 9)^{10}"
```
                                                                                                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                                                ██      ██████  
                                                                                                                                                                                                                                                                                                                              ████    ██      ██
                                                                                                                                                                                                                                                                                                                                ██    ██      ██
                                                                                      ██                    ████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████                          ██        ██    ██      ██
                                                                                    ██                      ██                                                                                                                                                                            ██                            ██      ██    ██      ██
                                        ██████                  ██                ██                        ██                ██                  ██  ██    ██    ██                                                                                                                      ██                              ██  ██████    ██████  
                                      ██      ██  ██████████                      ██                        ██    ████████          ██  ████    ██    ██    ██      ██                                                                                                                                                    ██                    
                                            ██      ██  ██    ████                ██                        ██  ██          ████    ████    ██  ██    ██    ██      ██                                                                                                                                                    ██                    
      ██                                  ██        ██  ██      ██                ██        ██████          ██    ██████      ██    ██      ██  ██    ██████████    ██                                                                    ██  ██████████  ██                    ██████                      ██████        ██                    
    ████                                ██          ██  ██      ████              ██      ██      ██        ██          ██    ██    ██      ██  ██          ██      ██      ████                                                        ██    ██      ██    ██                ██      ██                  ██      ██      ██                    
  ██  ██          ██          ████    ██████████  ██    ████    ██                ██      ██      ██        ██  ████████    ██████  ██      ██    ██        ██    ██          ██                                                      ██              ██      ██  ██      ██  ██      ██          ██      ██      ██      ██                    
      ██          ██        ██    ██                                              ██              ██        ██                                                                ██        ██████      ██████                            ██            ██        ██    ██  ██    ██      ██                  ██      ██      ██                    
      ██      ██████████  ████  ████                                  ██████████  ██          ████          ██  ████████████████████████████████████████████████████████      ██      ██      ██  ██      ██                          ██            ██        ██      ██        ██████        ██████████    ████████      ██                    
      ██          ██      ██████                                                  ██              ██        ██                                                                ██      ██      ██  ██      ██                          ██            ██        ██    ██  ██    ██      ██                          ██      ██                    
      ██          ██      ████                                                    ██      ██      ██      ██                          ██████████                              ██      ██      ██    ████████                ██████    ██          ██          ██  ██      ██  ██      ██          ██              ██      ██                    
      ██                  ████    ██                                              ██      ██      ██      ██                          ██                                      ██      ██      ██          ██              ██      ██    ██        ██        ██                ██      ██                        ██        ██                    
  ██████████                ██████                                                ██        ██████        ██                          ████████                              ██████      ██████    ████████                      ██        ██      ██      ██                    ██████                      ████          ██                    
                                                                                  ██                      ██                                  ██                                                                              ██                                                                                          ██                    
                                                                                  ██                      ██                          ██      ██                                                                  ████      ██                                                                                            ██                    
                                                                                  ██                      ██                            ██████                                                                  ██        ██████████                                                                                      ██                    
                                                                                  ██                      ██                                                                                                  ████████                                                                                                    ██                    
                                                                                  ██                  ██  ██                                                                                                  ██      ██                                                                                                  ██                    
                                                                                    ██                  ████                                                                                                  ██      ██                                                                                                ██                      
                                                                                      ██                  ██                                                                                                    ██████                                                                                                ██                        
                                                                                                      
                ██████            ██████      ██████      ██████      ██████      ██████      ██████  
              ██      ██        ██      ██  ██      ██  ██      ██  ██      ██  ██      ██  ██      ██
              ██      ██        ██      ██  ██      ██  ██      ██  ██      ██  ██      ██  ██      ██
  ██████████          ██        ██      ██  ██      ██  ██      ██  ██      ██  ██      ██          ██
                    ██          ██      ██  ██      ██  ██      ██  ██      ██  ██      ██        ██  
  ██████████      ██            ██      ██  ██      ██  ██      ██  ██      ██  ██      ██      ██    
                ██              ██      ██  ██      ██  ██      ██  ██      ██  ██      ██    ██      
              ██          ████  ██      ██  ██      ██  ██      ██  ██      ██  ██      ██  ██        
              ██████████  ████    ██████      ██████      ██████      ██████      ██████    ██████████
--PRERENDER--
```
![Screenshot 2025-04-18 at 8 51 45 AM](https://github.com/user-attachments/assets/bb581813-ec44-4efc-8a0f-ed50f9659bd7)
