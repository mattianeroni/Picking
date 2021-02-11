cmake_minimum_required(VERSION 3.17)
project(TSP)

set(CMAKE_CXX_STANDARD 17)

add_executable(aco main.cc problem.h aco.h greedy.h)