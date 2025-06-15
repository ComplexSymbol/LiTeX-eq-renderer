#ifndef _GRAPHER_H
#define _GRAPHER_H
#include <Arduino.h>
#include <Evaluator.h>
#include <LiTeX.h>

extern Render Graph(std::string eq, float scaleX = 0.125f, float scaleY = 0.125f, bool showScale = false, sbyte traceX = -1);

#endif