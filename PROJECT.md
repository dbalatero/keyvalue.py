# Overview

Throughout the course, you will work on a capstone project, a key-value server – a program that stores and retrieves data organized by key, like an on-disk hash map. By the end of the course, we'll have a multithreaded program with an IPC interface that can set, retrieve, and delete keys concurrently without data races. Each week has a core milestone, but there will also be ample opportunities for you to customize your project.

# Week 1

Let's use filesystem APIs to implement the core operations of the key-value server. Your program should have two commands: `get` and `set`. The `set` command takes a key and a value and writes it to disk, and the `get` command takes a key and prints the value, if it exists. Store all data in a single file (hard-coded path is fine). Use whatever data format you want – this is not a class on data structures or algorithms, so we won't focus on making the key-value server efficient.

- [x] Set up CI
- [x] Add key validator
- [x] Add basic store
- [x] Wire up store to the server program

# Week 2

Modify your program to create the database file with permissions locked down to the file's owner. Change your on-disk format to use multiple files: you can have one file per key, or do something fancier like allowing keys to have multiple parts such as `a.b.c` and store all `a.*` keys in the same file. Add commands to list all keys and to delete a key from the database.

# Week 3

No milestone this week!
