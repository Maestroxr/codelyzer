#!/bin/bash
clang++ -g -fsanitize=address -fno-omit-frame-pointer sanitizer_address-stack_buffer_overflow.c -o sanitizer_address-stack_buffer_overflow
clang++ -g -fsanitize=address -fno-omit-frame-pointer sanitizer_address-global_buffer_overflow.c -o sanitizer_address-global_buffer_overflow
clang++ -g -fsanitize=address -fno-omit-frame-pointer sanitizer_address-heap_buffer_overflow.c -o sanitizer_address-heap_buffer_overflow
clang++ -g -fsanitize=address -fno-omit-frame-pointer sanitizer_address-heap_use_after_free.c -o sanitizer_address-heap_use_after_free
clang++ -g -fsanitize=memory -fsanitize-memory-track-origins -fPIE -pie -fno-omit-frame-pointer sanitizer_memory.c -o sanitizer_memory
clang++ -g -fsanitize=leak -fno-omit-frame-pointer sanitizer_leak.c -o sanitizer_leak
(time ./sanitizer_address-heap_buffer_overflow) &> sanitizer_address-heap_buffer_overflow.log
(time ./sanitizer_address-stack_buffer_overflow) &> sanitizer_address-stack_buffer_overflow.log
(time ./sanitizer_address-global_buffer_overflow) &> sanitizer_address-global_buffer_overflow.log
(time ./sanitizer_address-heap_use_after_free) &> sanitizer_address-heap_use_after_free.log
(time ./sanitizer_leak) &> sanitizer_leak.log
(time ./sanitizer_memory) &> sanitizer_memory.log

