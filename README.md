# LiTeX
LiTeX is a lightweight mathematical equation renderer for low-resolution LCDs built in Python. It is similar to CASIO or Texas Instrument's "V.P.A.M" or "MathPrint".

It contains a customizable rendering engine using a LALR (look-ahead, left-to-right, rightmost derivation) parser. The parser accepts a string formatted similarly to LaTeX. There is also an optional 4-wire SPI library if you want to display LiTeX on a monochrome LCD. Currently, it is set up for the ST-7567 controller.

There is also a customizable, in-place equation evaluator that evaluates any LiTeX equation into a float. The evaluator supports all of the functions included in LiTeX, and also supports implicit multiplication. It cannot solve equations.

## LiTeX features:
- Self-resizing parenthesis
- Self-resizing radicals (nth root)
- Self-aligning fraction bars
- Exponents with smaller font
- Variable base log
- Trigonometric functions: sin cos tan + hyperbolic variants
- Algebreic constants: e, pi, i, theta, x
- Expression Evaluator with implicit multiplication support
- Complex number support

### Example render:
r"1 + e^{2\pi} - (3x \sqrt{ \frac{ sin(4) }{ 5 } log_{6}(7) * 8} / 9)^{ 10 }"
```
                                                                                                                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                                                      ██      ██████  
                                                                                                                                                                                                                                                                                                                                    ████    ██      ██
                                                                                                                                                                                                                                                                                                                                      ██    ██      ██
                                                                                      ██                                ██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████                          ██        ██    ██      ██
                                                                                    ██                                  ██                                                                                                                                                                      ██                            ██      ██    ██      ██
                                        ██████                  ██                ██                                    ██                    ██                    ██  ██    ██    ██                                                                                                          ██                              ██  ██████    ██████  
                                      ██      ██  ██████████                      ██                                    ██        ████████          ██  ████      ██    ██    ██      ██                                                                                                                                        ██                    
                                            ██      ██  ██    ████                ██                                    ██      ██          ████    ████    ██    ██    ██    ██      ██                                                                                                                                        ██                    
      ██                                  ██        ██  ██      ██                ██        ██████                      ██        ██████      ██    ██      ██    ██    ██████████    ██                                                        ██  ██████████  ██                    ██████                      ██████        ██                    
    ████                                ██          ██  ██      ██                ██      ██      ██                    ██              ██    ██    ██      ██    ██          ██      ██      ████                                            ██    ██      ██    ██                ██      ██                  ██      ██      ██                    
  ██  ██          ██          ████    ██████████  ██    ████  ██████              ██      ██      ██    ██    ██        ██      ████████    ██████  ██      ██      ██        ██    ██          ██                                          ██              ██      ██  ██      ██  ██      ██          ██      ██      ██      ██                    
      ██          ██        ██    ██                                              ██              ██  ██  ████          ██                                                                      ██        ██████      ██████                ██            ██        ██    ██  ██    ██      ██                  ██      ██      ██                    
      ██      ██████████  ████  ████                                  ██████████  ██          ████        ██          ██    ██████████████████████████████████████████████████████████████      ██      ██      ██  ██      ██              ██            ██        ██      ██        ██████        ██████████    ████████      ██                    
      ██          ██      ██████                                                  ██              ██      ██          ██                                                                        ██      ██      ██  ██      ██              ██            ██        ██    ██  ██    ██      ██                          ██      ██                    
      ██          ██      ████                                                    ██      ██      ██      ██          ██                              ██████████                                ██      ██      ██    ████████      ████    ██          ██          ██  ██      ██  ██      ██          ██              ██      ██                    
      ██                  ████    ██                                              ██      ██      ██    ████  ██      ██                              ██                                        ██      ██      ██          ██    ██          ██        ██        ██                ██      ██                        ██        ██                    
  ██████████                ██████                                                ██        ██████    ██    ██        ██                              ████████                                ██████      ██████    ████████    ████████        ██      ██      ██                    ██████                      ████          ██                    
                                                                                  ██                              ██  ██                                      ██                                                                ██      ██                                                                                      ██                    
                                                                                    ██                              ████                              ██      ██                                                                ██      ██                                                                                    ██                      
                                                                                      ██                              ██                                ██████                                                                    ██████                                                                                    ██
```
