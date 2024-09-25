#pragma once

#include <chrono>
#include <ctime>
#include <iomanip>
#include <cassert>

#include <cmath>
#include <iostream>
#include <cstring>
#include <algorithm>
#include <vector>
#include <fstream>
#include <sstream>

#define CL_HPP_CL_1_2_DEFAULT_BUILD
#define CL_HPP_TARGET_OPENCL_VERSION 120
#define CL_HPP_MINIMUM_OPENCL_VERSION 120
#define CL_HPP_ENABLE_PROGRAM_CONSTRUCTION_FROM_ARRAY_COMPATIBILITY 1

#include "xcl2.hpp"
#include <CL/cl2.hpp>

#define OCL_CHECK(error, call)                                                                   \
    call;                                                                                        \
    if (error != CL_SUCCESS) {                                                                   \
        printf("%s:%d Error calling " #call ", error code is: %d\n", __FILE__, __LINE__, error); \
        exit(EXIT_FAILURE);                                                                      \
    }
    
using std::string;

using std::vector;

static const std::string error_message =
    "Error: Result mismatch:\n"
    "i = %d CPU result = %d Device result = %d\n";
    

// MACROS FOR TIME 
struct cPerfTimer {
    std::chrono::high_resolution_clock::time_point m_start;
    std::chrono::high_resolution_clock::time_point m_end;
    std::chrono::duration<double> m_total;

    std::string m_name;

    cPerfTimer() { initialize(); }
    void initialize() { m_total = std::chrono::duration<double>(0.0); }
    void start() { m_start = std::chrono::high_resolution_clock::now(); }
    void stop() {
        m_end = std::chrono::high_resolution_clock::now();
        m_total += (m_end - m_start);
    }
    double get_ms() { return 1000 * m_total.count(); }
};

extern cPerfTimer* _g_timer;
extern int _g_timer_last_id;

#ifndef __DISABLE_TIMERS__
#define TIMER_INIT(a)                           \
    cPerfTimer* _g_timer = new cPerfTimer[(a)]; \
    int _g_timer_last_id = 0;
#define TIMER_START(a)     \
    _g_timer[(a)].start(); \
    _g_timer_last_id = (a);
#define TIMER_STOP _g_timer[_g_timer_last_id].stop();
#define TIMER_STOP_ID(a) _g_timer[(a)].stop();
#define TIMER_REPORT_MS(a) _g_timer[(a)].get_ms()
#else
#define TIMER_INIT(a)
#define TIMER_START(a)
#define TIMER_STOP
#define TIMER_STOP_ID(a)
#define TIMER_REPORT(a)
#endif


